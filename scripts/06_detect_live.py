#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: scripts/06_detect_live.py
Mục đích: Phát hiện DDoS real-time và kích hoạt chế độ phòng thủ
ĐÃ SỬA LẦN CUỐI:
- Fix lỗi UnboundLocalError trong check_defense_status()
- Cải thiện rate limiting cho spoofed SYN flood
- Thêm kiểm tra IDS inline
- Logging chi tiết hơn
- Thêm ghi live_state.json cho FastAPI dashboard
- Tự động reset state về NORMAL khi không có tấn công trong 10 giây
- Dọn dẹp iptables và reset state khi nhấn Ctrl+C
"""

import pandas as pd
import numpy as np
import joblib
import json
import time
import os
import subprocess
from collections import defaultdict
from datetime import datetime
import sys
import socket

# === CẤU HÌNH ===
DATA_DIR = "/home/server-ubuntu/zeek_flow/data"
MODEL_DIR = "/home/server-ubuntu/zeek_flow/model"
VICTIM_IP = "172.16.213.20"
VICTIM_PORT = 80
WINDOW_SIZE = 3
CONFIDENCE_THRESHOLD = 0.7
CHECK_INTERVAL = 2
ATTACK_TIMEOUT = 10  # seconds - reset to normal after this long without attacks

LOG_FILE = f"{DATA_DIR}/conn.log"
MODEL_PATH = f"{MODEL_DIR}/rf_model_best.pkl"
FEATURE_PATH = f"{MODEL_DIR}/feature_list.json"
LIVE_STATE_PATH = f"{DATA_DIR}/live_state.json"

# === TRẠNG THÁI PHÒNG THỦ ===
defense_mode = False
defense_start_time = 0
defense_cooldown = 300  # 5 phút
consecutive_attacks = 0
attack_history = []  # Lưu lịch sử tấn công
last_attack_timestamp = 0  # Track last time an attack was detected

# === BIẾN LƯU TRỮ TRẠNG THÁI HIỆN TẠI CHO DASHBOARD ===
current_state = {
    "timestamp": 0,
    "label": 0,
    "confidence": 0.0,
    "defense_mode": False,
    "features": {
        "total_connections": 0,
        "syn_connections": 0,
        "unique_src_ips": 0,
        "connections_per_second": 0.0,
        "failed_ratio": 0.0
    },
    "consecutive_attacks": 0
}

def write_live_state():
    """Ghi trạng thái hiện tại vào live_state.json cho FastAPI"""
    global current_state, defense_mode, consecutive_attacks
    
    try:
        # Cập nhật defense_mode và consecutive_attacks vào current_state
        current_state["defense_mode"] = defense_mode
        current_state["consecutive_attacks"] = consecutive_attacks
        current_state["timestamp"] = int(time.time())
        
        # Ghi vào file
        with open(LIVE_STATE_PATH, 'w') as f:
            json.dump(current_state, f, indent=2)
            
    except Exception as e:
        print(f"   ⚠️ Không thể ghi live_state.json: {e}")

def reset_to_normal_state():
    """Reset current_state to NORMAL values when no attack detected"""
    global current_state, consecutive_attacks, last_attack_timestamp
    
    print(f"\n🔄 Resetting state to NORMAL (no attacks for {ATTACK_TIMEOUT}s)")
    
    current_state["label"] = 0
    current_state["confidence"] = 0.0
    current_state["features"]["total_connections"] = 0
    current_state["features"]["syn_connections"] = 0
    current_state["features"]["unique_src_ips"] = 0
    current_state["features"]["connections_per_second"] = 0.0
    current_state["features"]["failed_ratio"] = 0.0
    consecutive_attacks = 0
    current_state["consecutive_attacks"] = 0
    
    write_live_state()
    print("   ✅ State reset complete")

# === LOAD MODEL ===
print("[1] Loading model...")
try:
    if not os.path.exists(MODEL_PATH):
        print(f"   ❌ Không tìm thấy model tại: {MODEL_PATH}")
        print(f"   Các file có sẵn trong {MODEL_DIR}:")
        for f in os.listdir(MODEL_DIR):
            print(f"      - {f}")
        sys.exit(1)
    
    rf_model = joblib.load(MODEL_PATH)
    with open(FEATURE_PATH, 'r') as f:
        feature_names = json.load(f)
    
    print(f"   ✅ Model loaded: {os.path.basename(MODEL_PATH)}")
    print(f"   ✅ Features ({len(feature_names)}): {feature_names}")
    
    if 'window_size' in feature_names:
        print(f"   ✅ Feature window_size = {WINDOW_SIZE}s (khớp với training)")
        
except Exception as e:
    print(f"   ❌ ERROR loading model: {e}")
    sys.exit(1)

# === STATE MANAGEMENT ===
last_position = 0
current_window_flows = defaultdict(list)

def get_file_size():
    try:
        return os.path.getsize(LOG_FILE)
    except:
        return 0

def parse_zeek_line(line):
    parts = line.split('\t')
    if len(parts) < 21:
        return None
    
    try:
        duration = parts[8] if parts[8] != '-' else '0'
        orig_bytes = parts[9] if parts[9] != '-' else '0'
        orig_pkts = parts[16] if parts[16] != '-' else '0'
        
        return {
            'ts': float(parts[0]),
            'orig_h': parts[2],
            'resp_h': parts[4],
            'duration': float(duration),
            'orig_bytes': float(orig_bytes),
            'orig_pkts': int(float(orig_pkts)),
            'conn_state': parts[11],
            'to_victim': 1 if parts[4] == VICTIM_IP else 0
        }
    except Exception as e:
        return None

def read_new_lines():
    global last_position
    current_size = get_file_size()
    
    if current_size < last_position:
        print("   [*] Log rotated, resetting position")
        last_position = 0
    
    if current_size > last_position:
        with open(LOG_FILE, 'r') as f:
            f.seek(last_position)
            new_data = f.read()
            last_position = f.tell()
        
        lines = new_data.strip().split('\n')
        return [l for l in lines if l and not l.startswith('#')]
    
    return []

def extract_window_features(flows):
    if not flows:
        return None
    
    df_window = pd.DataFrame(flows)
    attack_flows = df_window[df_window['to_victim'] == 1]
    
    if len(attack_flows) == 0:
        return None
    
    syn_flows = attack_flows[attack_flows['conn_state'].isin(['S0', 'REJ'])]
    failed_ratio = len(syn_flows) / max(len(attack_flows), 1)
    
    features = {
        'window_size': WINDOW_SIZE,
        'total_connections': len(attack_flows),
        'syn_connections': len(syn_flows),
        'unique_src_ips': attack_flows['orig_h'].nunique(),
        'connections_per_second': len(attack_flows) / WINDOW_SIZE,
        'avg_duration': attack_flows['duration'].mean(),
        'min_duration': attack_flows['duration'].min(),
        'max_duration': attack_flows['duration'].max(),
        'duration_std': attack_flows['duration'].std() if len(attack_flows) > 1 else 0,
        'avg_orig_pkts': attack_flows['orig_pkts'].mean(),
        'total_orig_pkts': attack_flows['orig_pkts'].sum(),
        'min_orig_pkts': attack_flows['orig_pkts'].min(),
        'max_orig_pkts': attack_flows['orig_pkts'].max(),
        'orig_pkts_std': attack_flows['orig_pkts'].std() if len(attack_flows) > 1 else 0,
        'avg_orig_bytes': attack_flows['orig_bytes'].mean(),
        'total_orig_bytes': attack_flows['orig_bytes'].sum(),
        'min_orig_bytes': attack_flows['orig_bytes'].min(),
        'max_orig_bytes': attack_flows['orig_bytes'].max(),
        'orig_bytes_std': attack_flows['orig_bytes'].std() if len(attack_flows) > 1 else 0,
        'byte_rate': attack_flows['orig_bytes'].sum() / WINDOW_SIZE,
        'failed_ratio': failed_ratio
    }
    
    return features

def verify_features(features):
    missing_features = [f for f in feature_names if f not in features]
    if missing_features:
        return False
    return True

# === KIỂM TRA IDS INLINE ===
def check_ids_inline():
    """Kiểm tra xem IDS có đang inline không"""
    try:
        # Ping từ Kali đến Victim qua IDS
        response = subprocess.run(
            f"ping -c 1 -W 2 {VICTIM_IP}",
            shell=True, capture_output=True
        )
        return response.returncode == 0
    except:
        return False

# === KIỂM TRA RULES ===
def check_iptables_rules():
    """Kiểm tra xem rules đã được áp dụng chưa"""
    try:
        result = subprocess.run(
            "sudo iptables -L FORWARD -n | grep -c 'DROP\\|ACCEPT'",
            shell=True, capture_output=True, text=True
        )
        return int(result.stdout.strip())
    except:
        return 0

# === TEST VICTIM ACCESS ===
def test_victim_access():
    """Test xem có truy cập được victim không"""
    try:
        # Thử curl với timeout ngắn
        result = subprocess.run(
            f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 2 http://{VICTIM_IP}:{VICTIM_PORT}",
            shell=True, capture_output=True, text=True
        )
        return result.stdout.strip() == "200"
    except:
        return False

# === 🛡️ CÁC HÀM PHÒNG THỦ ===

def enable_defense_mode():
    """Kích hoạt chế độ phòng thủ khi phát hiện DDoS"""
    global defense_mode, defense_start_time, consecutive_attacks
    
    if defense_mode:
        return False
    
    print(f"\n🛡️🛡️🛡️ KÍCH HOẠT CHẾ ĐỘ PHÒNG THỦ 🛡️🛡️🛡️")
    print(f"   Thời gian: {datetime.now().strftime('%H:%M:%S')}")
    
    # Kiểm tra xem IDS có inline không
    if not check_ids_inline():
        print("   ⚠️ CẢNH BÁO: IDS có thể không inline!")
        print("   Traffic có thể bypass IDS")
    
    try:
        # 1. BẬT SYN COOKIES
        subprocess.run("sudo sysctl -w net.ipv4.tcp_syncookies=1", shell=True, check=True)
        print("   ✅ Đã bật SYN cookies")
        
        # 2. XÓA RULES CŨ
        subprocess.run("sudo iptables -F FORWARD", shell=True)
        
        # 3. RATE LIMITING MẠNH HƠN CHO SPOOFED SYN FLOOD
        # Với --rand-source, mỗi IP chỉ gửi 1-2 SYN, nên hashlimit theo srcip không hiệu quả
        # Chuyển sang giới hạn tổng SYN packets đến port 80
        
        # Giới hạn tổng SYN packets đến port 80
        subprocess.run(
            "sudo iptables -A FORWARD -p tcp --syn --dport 80 -m limit --limit 1000/sec --limit-burst 2000 -j ACCEPT",
            shell=True, check=True
        )
        print("   ✅ Đã áp dụng rate limiting tổng (1000 SYN/s)")
        
        # DROP SYN packets vượt ngưỡng
        subprocess.run(
            "sudo iptables -A FORWARD -p tcp --syn --dport 80 -j DROP",
            shell=True, check=True
        )
        print("   ✅ Đã chặn SYN packets vượt ngưỡng")
        
        # 4. GIỚI HẠN KẾT NỐI MỚI
        subprocess.run(
            "sudo iptables -A FORWARD -m state --state NEW -m limit --limit 2000/sec -j ACCEPT",
            shell=True, check=True
        )
        print("   ✅ Đã giới hạn kết nối mới")
        
        # 5. CHO PHÉP CÁC KẾT NỐI ĐÃ THIẾT LẬP
        subprocess.run(
            "sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT",
            shell=True, check=True
        )
        
        # 6. CHO PHÉP TRAFFIC NỘI BỘ
        subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens37 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens33 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens38 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens38 -j ACCEPT", shell=True)
        
        # Kiểm tra rules đã được áp dụng
        rule_count = check_iptables_rules()
        print(f"   ✅ Tổng số rules: {rule_count}")
        
        defense_mode = True
        defense_start_time = time.time()
        
        # Test victim access sau khi bật defense
        time.sleep(1)
        if test_victim_access():
            print("   ✅ Victim vẫn truy cập được (phòng thủ hoạt động)")
        else:
            print("   ⚠️ Không thể truy cập victim - có thể quá tải hoặc chặn quá mạnh")
        
        # Ghi log
        with open(f"{DATA_DIR}/defense_mode.log", 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Defense mode ENABLED (rules: {rule_count})\n")
        
        # Cập nhật live_state
        write_live_state()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Lỗi khi kích hoạt phòng thủ: {e}")
        return False

def disable_defense_mode():
    """Tắt chế độ phòng thủ sau khi hết tấn công"""
    global defense_mode
    
    if not defense_mode:
        return
    
    print(f"\n🟢 TẮT CHẾ ĐỘ PHÒNG THỦ")
    print(f"   Thời gian: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Xóa tất cả rules FORWARD
        subprocess.run("sudo iptables -F FORWARD", shell=True, check=True)
        
        # Khôi phục policy mặc định
        subprocess.run("sudo iptables -P FORWARD DROP", shell=True)
        
        # Rules cơ bản
        subprocess.run("sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens37 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens33 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens38 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens38 -j ACCEPT", shell=True)
        
        rule_count = check_iptables_rules()
        print(f"   ✅ Đã khôi phục rules cơ bản ({rule_count} rules)")
        
        defense_mode = False
        
        # Ghi log
        with open(f"{DATA_DIR}/defense_mode.log", 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Defense mode DISABLED\n")
        
        # Cập nhật live_state
        write_live_state()
            
    except Exception as e:
        print(f"   ❌ Lỗi khi tắt phòng thủ: {e}")

def check_defense_status():
    """Kiểm tra trạng thái phòng thủ và tự động tắt nếu hết tấn công"""
    global defense_mode, consecutive_attacks, defense_start_time, attack_history
    
    if not defense_mode:
        return
    
    current_time = time.time()
    
    # Lưu lịch sử tấn công (chỉ giữ 10 phút gần nhất)
    attack_history.append((current_time, consecutive_attacks))
    attack_history = [(t, c) for t, c in attack_history if current_time - t < 600]
    
    # Tính tỷ lệ tấn công trong 2 phút gần nhất
    recent_attacks = sum(c for t, c in attack_history if current_time - t < 120)
    
    if recent_attacks == 0 and (current_time - defense_start_time) > defense_cooldown:
        print(f"\n📊 Không phát hiện tấn công trong {defense_cooldown//60} phút")
        disable_defense_mode()
    elif recent_attacks > 0:
        # Reset timer nếu vẫn có tấn công
        defense_start_time = current_time

def check_attack_timeout():
    """Check if no attacks detected for ATTACK_TIMEOUT seconds and reset state"""
    global last_attack_timestamp, current_state
    
    current_time = time.time()
    
    # Only reset if:
    # 1. We have recorded at least one attack timestamp
    # 2. Time since last attack exceeds timeout
    # 3. Current state is not already NORMAL (label != 0)
    if (last_attack_timestamp > 0 and 
        current_time - last_attack_timestamp > ATTACK_TIMEOUT and 
        current_state["label"] == 1):
        
        reset_to_normal_state()

# === MAIN LOOP ===
print("\n[2] Starting detection...")
print(f"   Victim IP: {VICTIM_IP}:{VICTIM_PORT}")
print(f"   Window: {WINDOW_SIZE}s")
print(f"   Confidence threshold: {CONFIDENCE_THRESHOLD}")
print(f"   Check interval: {CHECK_INTERVAL}s")
print(f"   Attack timeout: {ATTACK_TIMEOUT}s")
print(f"   Model: {os.path.basename(MODEL_PATH)}")
print(f"   Live state: {LIVE_STATE_PATH}")
print("-" * 60)

# Kiểm tra file log
if not os.path.exists(LOG_FILE):
    print(f"   ⚠️ File {LOG_FILE} chưa tồn tại. Đợi Zeek tạo file...")
    while not os.path.exists(LOG_FILE):
        time.sleep(2)
    print("   ✅ File log đã được tạo!")

# Kiểm tra IDS inline
if check_ids_inline():
    print("   ✅ IDS inline - có thể chặn traffic")
else:
    print("   ⚠️ IDS không inline - chỉ có thể cảnh báo, không chặn được!")

# Khởi tạo rules cơ bản
print("\n[3] Initializing basic iptables rules...")
try:
    subprocess.run("sudo iptables -P FORWARD DROP", shell=True)
    subprocess.run("sudo iptables -F FORWARD", shell=True)
    subprocess.run("sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT", shell=True)
    subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens37 -j ACCEPT", shell=True)
    subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens33 -j ACCEPT", shell=True)
    subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens38 -j ACCEPT", shell=True)
    subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens38 -j ACCEPT", shell=True)
    print(f"   ✅ Basic rules configured ({check_iptables_rules()} rules)")
except Exception as e:
    print(f"   ⚠️ Could not set basic rules: {e}")

print("\n   🟢 Bắt đầu theo dõi...")
print("")

# Thống kê
total_windows = 0
attack_windows = 0
last_stats_time = time.time()

try:
    while True:
        # Đọc dòng mới
        new_lines = read_new_lines()
        
        if new_lines:
            for line in new_lines:
                flow = parse_zeek_line(line)
                if flow:
                    ts_window = (flow['ts'] // WINDOW_SIZE) * WINDOW_SIZE
                    flow['window'] = ts_window
                    current_window_flows[ts_window].append(flow)
            
            # Xử lý windows đã hoàn thành
            current_time = time.time()
            completed_windows = []
            
            for ts_win in list(current_window_flows.keys()):
                if current_time - ts_win > WINDOW_SIZE:
                    completed_windows.append(ts_win)
            
            for ts_win in completed_windows:
                flows = current_window_flows.pop(ts_win)
                total_windows += 1
                
                features = extract_window_features(flows)
                
                if features and verify_features(features):
                    X = pd.DataFrame([features])[feature_names]
                    pred = rf_model.predict(X)[0]
                    proba = rf_model.predict_proba(X)[0]
                    
                    time_str = datetime.fromtimestamp(ts_win).strftime('%H:%M:%S')
                    
                    # Cập nhật current_state cho dashboard
                    current_state["timestamp"] = int(ts_win)
                    current_state["label"] = int(pred)
                    current_state["confidence"] = float(proba[1])
                    current_state["features"] = {
                        "total_connections": features["total_connections"],
                        "syn_connections": features["syn_connections"],
                        "unique_src_ips": features["unique_src_ips"],
                        "connections_per_second": features["connections_per_second"],
                        "failed_ratio": features["failed_ratio"]
                    }
                    
                    # Ghi live state mỗi khi có window mới
                    write_live_state()
                    
                    if pred == 1 and proba[1] >= CONFIDENCE_THRESHOLD:
                        attack_windows += 1
                        consecutive_attacks += 1
                        last_attack_timestamp = time.time()
                        
                        print(f"\n[⚠] {time_str} - DDoS DETECTED! (confidence: {proba[1]:.2f})")
                        print(f"   Window: {len(flows)} flows, {features['unique_src_ips']} unique IPs")
                        print(f"   Rate: {features['connections_per_second']:.1f} conns/s")
                        
                        # Kích hoạt phòng thủ nếu phát hiện đủ 2 lần liên tiếp
                        if consecutive_attacks >= 2 and not defense_mode:
                            enable_defense_mode()
                    else:
                        # Giảm counter nếu không phát hiện tấn công
                        if consecutive_attacks > 0:
                            consecutive_attacks = max(0, consecutive_attacks - 1)
        
        # Kiểm tra trạng thái phòng thủ
        check_defense_status()
        
        # Kiểm tra timeout tấn công để reset state
        check_attack_timeout()
        
        # Hiển thị thống kê mỗi 30s
        if time.time() - last_stats_time >= 30:
            last_stats_time = time.time()
            
            print(f"\n[STATS] {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Windows: {total_windows} | Attacks: {attack_windows} ({attack_windows/max(total_windows,1)*100:.1f}%)")
            print(f"   Defense mode: {'🛡️ ACTIVE' if defense_mode else '⚪ INACTIVE'}")
            print(f"   Consecutive attacks: {consecutive_attacks}")
            
            # Hiển thị rules hiện tại
            rule_count = check_iptables_rules()
            print(f"   Active rules: {rule_count}")
            
            # Test victim access nếu đang ở chế độ phòng thủ
            if defense_mode:
                if test_victim_access():
                    print(f"   Victim: ✅ Có thể truy cập")
                else:
                    print(f"   Victim: ❌ Không thể truy cập")
        
        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\n\n[!] Stopped by user")
    
    # Tắt chế độ phòng thủ nếu đang bật
    if defense_mode:
        print("\n🛑 Disabling defense mode before exit...")
        disable_defense_mode()
    
    # Force reset state to NORMAL before exiting
    print("\n🔄 Resetting state to NORMAL before exit...")
    current_state["label"] = 0
    current_state["confidence"] = 0.0
    current_state["features"]["total_connections"] = 0
    current_state["features"]["syn_connections"] = 0
    current_state["features"]["unique_src_ips"] = 0
    current_state["features"]["connections_per_second"] = 0.0
    current_state["features"]["failed_ratio"] = 0.0
    consecutive_attacks = 0
    current_state["consecutive_attacks"] = 0
    current_state["defense_mode"] = False
    
    # Ensure iptables is clean
    try:
        print("\n🧹 Cleaning up iptables rules...")
        subprocess.run("sudo iptables -F FORWARD", shell=True, check=True)
        subprocess.run("sudo iptables -P FORWARD DROP", shell=True)
        subprocess.run("sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens37 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens33 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens33 -o ens38 -j ACCEPT", shell=True)
        subprocess.run("sudo iptables -A FORWARD -i ens37 -o ens38 -j ACCEPT", shell=True)
        print("   ✅ iptables restored to basic rules")
    except Exception as e:
        print(f"   ⚠️ Error cleaning iptables: {e}")
    
    # Write final state
    write_live_state()
    print(f"\n✅ Final state written to {LIVE_STATE_PATH}")
    
    print(f"\n[SUMMARY]")
    print(f"   Total windows processed: {total_windows}")
    print(f"   Attack windows detected: {attack_windows}")
    print(f"   Detection rate: {attack_windows/max(total_windows,1)*100:.1f}%")
    print(f"   Defense mode activated: {'Yes' if defense_mode else 'No'}")
    print(f"   Max consecutive attacks: {max([c for _,c in attack_history], default=0)}")
    
    print("\n   ✅ Firewall rules cleaned up - system ready for next run")
    print("   Để xem rules hiện tại: sudo iptables -L FORWARD -v")
