#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: scripts/04_feature_engineering.py
Mục đích: Tạo dataset từ conn.log với window
ĐÃ SỬA: 
- Thêm nhiều features hơn
- Window size nhỏ hơn (3s)
- Kiểm tra phân phối features
"""

import pandas as pd
import numpy as np
import warnings
import os
import sys
import glob

warnings.filterwarnings('ignore')

# === CẤU HÌNH - ĐÃ THAY ĐỔI ===
WINDOW_SIZE = 3  # seconds (giảm từ 5s xuống 3s để tăng số samples)
VICTIM_IP = "172.16.213.20"  # IP Victim
DATA_DIR = "/home/server-ubuntu/zeek_flow/data"

print("=" * 60)
print("FEATURE ENGINEERING - TẠO DATASET TỪ CONN.LOG")
print("=" * 60)
print(f"Window size: {WINDOW_SIZE}s")
print(f"Victim IP: {VICTIM_IP}")
print("=" * 60)

# === KIỂM TRA VÀ HIỂN THỊ THÔNG TIN ===
print("\n[0] Kiểm tra cấu trúc file log...")

# Lấy file mẫu
sample_files = glob.glob(f'{DATA_DIR}/conn*.log')
if sample_files:
    sample_file = sample_files[0]
    print(f"   📄 File mẫu: {os.path.basename(sample_file)}")
    
    # Đọc dòng #fields để biết tên cột
    with open(sample_file, 'r') as f:
        for line in f:
            if line.startswith('#fields'):
                fields_line = line.strip()
                print(f"   📋 Dòng fields: {fields_line}")
                column_names = fields_line.split('\t')[1:]  # Bỏ '#fields'
                print(f"   📊 Số lượng cột: {len(column_names)}")
                print(f"   📊 Các cột: {column_names}")
                break
    
    # Đọc và hiển thị 3 dòng dữ liệu đầu tiên
    with open(sample_file, 'r') as f:
        lines = []
        for line in f:
            if not line.startswith('#'):
                lines.append(line.strip())
                if len(lines) >= 3:
                    break
    
    print("\n   3 dòng dữ liệu đầu tiên:")
    for i, line in enumerate(lines, 1):
        fields = line.split('\t')
        print(f"   Dòng {i}:")
        print(f"      ts: {fields[0]}")
        print(f"      uid: {fields[1]}")
        print(f"      id.orig_h: {fields[2]}")
        print(f"      id.orig_p: {fields[3]}")
        print(f"      id.resp_h: {fields[4]}")
        print(f"      id.resp_p: {fields[5]}")
        print()

# === TÌM TẤT CẢ CÁC FILE CONN LOG ===
print("\n[1] Tìm các file conn log...")

conn_files = glob.glob(f'{DATA_DIR}/conn*.log')
conn_files.sort()

if not conn_files:
    print(f"❌ Không tìm thấy file conn log nào trong {DATA_DIR}")
    sys.exit(1)

print(f"   ✅ Tìm thấy {len(conn_files)} file conn log:")
for f in conn_files[-5:]:
    file_size = os.path.getsize(f) / 1024
    print(f"      - {os.path.basename(f)} ({file_size:.1f} KB)")

# === ĐỌC VÀ GỘP TẤT CẢ CÁC FILE ===
print("\n[2] Đọc và gộp các file...")

df_list = []

for i, file_path in enumerate(conn_files, 1):
    try:
        # Đọc header từ dòng #fields trong file hiện tại
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('#fields'):
                    fields_line = line.strip()
                    column_names = fields_line.split('\t')[1:]  # Bỏ '#fields'
                    break
        
        # Đọc dữ liệu với tên cột lấy từ header
        df_temp = pd.read_csv(file_path, 
                             sep='\t',
                             comment='#',
                             header=None,
                             names=column_names,
                             low_memory=False)
        
        flows = len(df_temp)
        df_list.append(df_temp)
        print(f"   [{i:2d}/{len(conn_files)}] {os.path.basename(file_path)}: {flows:6d} flows")
        
        # Debug: hiển thị 2 dòng đầu để kiểm tra
        if i == 1:  # Chỉ hiển thị cho file đầu tiên
            print("\n   🔍 DEBUG - 2 dòng đầu tiên của file đầu:")
            print(df_temp[['ts', 'id.orig_h', 'id.resp_h']].head(2).to_string())
        
    except Exception as e:
        print(f"   ⚠️ Lỗi đọc file {file_path}: {e}")
        continue

if not df_list:
    print("❌ Không đọc được dữ liệu từ bất kỳ file nào")
    sys.exit(1)

# Gộp tất cả dataframe
df = pd.concat(df_list, ignore_index=True)
print(f"\n   ✅ Tổng số flow sau khi gộp: {len(df):,} flows")

# Debug: kiểm tra 5 dòng đầu sau khi gộp
print("\n   🔍 DEBUG - 5 dòng đầu sau khi gộp:")
print(df[['ts', 'id.orig_h', 'id.resp_h']].head().to_string())

# === XỬ LÝ TIMESTAMP ===
print("\n[3] Xử lý timestamp...")

# Kiểm tra kiểu dữ liệu
print(f"   📊 Kiểu dữ liệu cột ts: {df['ts'].dtype}")

# Đảm bảo ts là số
df['ts'] = pd.to_numeric(df['ts'], errors='coerce')

# Kiểm tra timestamp hợp lệ
invalid_ts = df['ts'].isna().sum()
valid_ts = len(df) - invalid_ts

print(f"   📊 Kết quả:")
print(f"      - Timestamp hợp lệ: {valid_ts:,} ({valid_ts/len(df)*100:.2f}%)")
print(f"      - Timestamp không hợp lệ: {invalid_ts:,} ({invalid_ts/len(df)*100:.2f}%)")

if valid_ts == 0:
    print("\n❌ KHÔNG CÓ TIMESTAMP HỢP LỆ!")
    sys.exit(1)

# Xóa các dòng có timestamp không hợp lệ
if invalid_ts > 0:
    df = df.dropna(subset=['ts'])
    print(f"\n   ✅ Sau khi xóa timestamp không hợp lệ: {len(df):,} flows")

# Kiểm tra range timestamp
ts_min = df['ts'].min()
ts_max = df['ts'].max()
ts_range = ts_max - ts_min
print(f"   📊 Timestamp range: {ts_min:.2f} -> {ts_max:.2f} (duration: {ts_range:.2f} seconds)")

# === XỬ LÝ CÁC TRƯỜNG KHÁC ===
print("\n[4] Xử lý các trường dữ liệu...")

# XỬ LÝ DURATION
df['duration'] = df['duration'].replace('-', '0')
df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(0)

# XỬ LÝ BYTES
for col in ['orig_bytes', 'resp_bytes']:
    if col in df.columns:
        df[col] = df[col].replace('-', '0')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# XỬ LÝ PKTS
for col in ['orig_pkts', 'resp_pkts']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

print("   ✅ Đã xử lý các giá trị '-' thành 0")

# === ĐỌC ATTACK TIMESTAMPS ===
print("\n[5] Đọc attack timestamps...")

attack_periods = []
marker_file = f'{DATA_DIR}/attack_timestamps.txt'

if os.path.exists(marker_file):
    with open(marker_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    i = 0
    while i < len(lines):
        if lines[i].startswith('ATTACK_START'):
            start_time = int(lines[i+1])
            i += 2
        elif lines[i].startswith('ATTACK_END'):
            end_time = int(lines[i+1])
            attack_periods.append((start_time, end_time))
            i += 2
        else:
            i += 1
    
    print(f"   ✅ Số periods attack: {len(attack_periods)}")
    for idx, (start, end) in enumerate(attack_periods, 1):
        duration = end - start
        print(f"      Period {idx}: {start} -> {end} ({duration} seconds)")
        
        # Đếm flows trong period này
        period_flows = df[(df['ts'] >= start) & (df['ts'] <= end)]
        print(f"         Flows trong period: {len(period_flows)}")
else:
    print("   ⚠️ KHÔNG tìm thấy file attack_timestamps.txt")

# === GÁN NHÃN ===
print("\n[6] Gán nhãn flows...")

def is_attack_flow(ts):
    if not attack_periods:
        return 0
    for start, end in attack_periods:
        if start <= ts <= end:
            return 1
    return 0

df['label'] = df['ts'].apply(is_attack_flow)

normal_count = len(df[df['label'] == 0])
attack_count = len(df[df['label'] == 1])

print(f"   📊 Normal flows: {normal_count:6d} ({normal_count/len(df)*100:5.1f}%)")
print(f"   📊 Attack flows: {attack_count:6d} ({attack_count/len(df)*100:5.1f}%)")

# === TẠO WINDOW FEATURES ===
print("\n[7] Tạo window features...")

# Floor timestamp theo window
df['ts_window'] = (df['ts'] // WINDOW_SIZE) * WINDOW_SIZE

# Xác định flow hướng về victim
df['to_victim'] = (df['id.resp_h'] == VICTIM_IP).astype(int)

# Thống kê flows hướng về victim
victim_flows = df[df['to_victim'] == 1]
print(f"   📊 Flows hướng về victim ({VICTIM_IP}): {len(victim_flows)} ({len(victim_flows)/len(df)*100:.1f}%)")

# Hiển thị top destinations để kiểm tra
print(f"\n   📊 Top 10 destination IPs:")
print(df['id.resp_h'].value_counts().head(10))

# Hiển thị các conn_state phổ biến
print(f"\n   📊 Top 10 conn_state:")
print(df['conn_state'].value_counts().head(10))

# Features cho mỗi window
features = []
total_windows = df['ts_window'].nunique()
processed = 0

print(f"\n   Đang xử lý {total_windows} windows...")

for ts_win, group in df.groupby('ts_window'):
    processed += 1
    if processed % 100 == 0:
        print(f"      Đã xử lý {processed}/{total_windows} windows")
    
    attack_flows = group[group['to_victim'] == 1]
    
    if len(attack_flows) == 0:
        continue
    
    # 🔥 QUAN TRỌNG: Với SYN flood, conn_state thường là 'REJ' hoặc 'S0'
    syn_flows = attack_flows[attack_flows['conn_state'].isin(['S0', 'REJ'])]
    failed_ratio = len(syn_flows) / len(attack_flows) if len(attack_flows) > 0 else 0
    
    # === THÊM NHIỀU FEATURES HƠN ===
    feature_row = {
        # Timestamp
        'timestamp': ts_win,
        'window_size': WINDOW_SIZE,
        
        # Basic features
        'total_connections': len(attack_flows),
        'syn_connections': len(syn_flows),
        'unique_src_ips': attack_flows['id.orig_h'].nunique(),
        
        # 🆕 1. Connections per second
        'connections_per_second': len(attack_flows) / WINDOW_SIZE,
        
        # Duration features
        'avg_duration': attack_flows['duration'].mean(),
        'min_duration': attack_flows['duration'].min(),
        'max_duration': attack_flows['duration'].max(),
        # 🆕 2. Duration standard deviation
        'duration_std': attack_flows['duration'].std(),
        
        # Packet features
        'avg_orig_pkts': attack_flows['orig_pkts'].mean(),
        'total_orig_pkts': attack_flows['orig_pkts'].sum(),
        'min_orig_pkts': attack_flows['orig_pkts'].min(),
        'max_orig_pkts': attack_flows['orig_pkts'].max(),
        # 🆕 3. Packets standard deviation
        'orig_pkts_std': attack_flows['orig_pkts'].std(),
        
        # Bytes features
        'avg_orig_bytes': attack_flows['orig_bytes'].mean(),
        'total_orig_bytes': attack_flows['orig_bytes'].sum(),
        'min_orig_bytes': attack_flows['orig_bytes'].min(),
        'max_orig_bytes': attack_flows['orig_bytes'].max(),
        'orig_bytes_std': attack_flows['orig_bytes'].std(),
        
        # 🆕 4. Byte rate (bytes per second)
        'byte_rate': attack_flows['orig_bytes'].sum() / WINDOW_SIZE,
        
        # Ratio features
        'failed_ratio': failed_ratio,
        
        # Label
        'label': group['label'].max()
    }
    
    features.append(feature_row)

df_features = pd.DataFrame(features)

# === KIỂM TRA KẾT QUẢ ===
print("\n[8] Kiểm tra kết quả...")

if len(df_features) == 0:
    print("❌ KHÔNG có window nào được tạo!")
    print("\n   🔍 Debug information:")
    print(f"      - Victim IP: {VICTIM_IP}")
    print(f"      - Total flows: {len(df)}")
    print(f"      - Flows to victim: {len(df[df['id.resp_h'] == VICTIM_IP])}")
    print(f"      - Unique destination IPs: {df['id.resp_h'].nunique()}")
    sys.exit(1)

windows_attack = len(df_features[df_features['label'] == 1])
windows_normal = len(df_features[df_features['label'] == 0])

print(f"   ✅ Tổng số windows: {len(df_features)}")
print(f"   📊 Windows attack: {windows_attack:4d} ({windows_attack/len(df_features)*100:5.1f}%)")
print(f"   📊 Windows normal: {windows_normal:4d} ({windows_normal/len(df_features)*100:5.1f}%)")

# === KIỂM TRA PHÂN PHỐI FEATURES ===
print("\n[9] Kiểm tra phân phối features theo label...")

# Tách normal và attack
normal_features = df_features[df_features['label'] == 0]
attack_features = df_features[df_features['label'] == 1]

print("\n   📊 So sánh mean của các features quan trọng:")
print("   " + "-" * 50)

# Chọn các features quan trọng để so sánh
important_features = [
    'total_connections', 'syn_connections', 'unique_src_ips',
    'connections_per_second', 'duration_std', 'orig_pkts_std',
    'byte_rate', 'failed_ratio'
]

comparison_data = []
for feat in important_features:
    if feat in df_features.columns:
        normal_mean = normal_features[feat].mean() if len(normal_features) > 0 else 0
        attack_mean = attack_features[feat].mean() if len(attack_features) > 0 else 0
        diff_pct = ((attack_mean - normal_mean) / (normal_mean + 1e-10)) * 100
        comparison_data.append({
            'Feature': feat,
            'Normal Mean': f'{normal_mean:.2f}',
            'Attack Mean': f'{attack_mean:.2f}',
            'Diff %': f'{diff_pct:+.1f}%'
        })

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))

# === LƯU DATASET ===
print("\n[10] Lưu dataset...")

output_file = f'{DATA_DIR}/dataset.csv'
df_features.to_csv(output_file, index=False)
print(f"   ✅ Đã lưu dataset tại: {output_file}")
print(f"   📊 Dataset shape: {df_features.shape}")

# Hiển thị thông tin dataset
print("\n" + "=" * 60)
print("THÔNG TIN DATASET")
print("=" * 60)
print(f"\n5 dòng đầu tiên:")
print(df_features.head().to_string())

print(f"\nThống kê các features:")
print(df_features.describe())

print(f"\nKiểm tra missing values:")
missing = df_features.isnull().sum()
if missing.sum() == 0:
    print("   ✅ Không có missing values")
else:
    print(missing[missing > 0])

print("\n" + "=" * 60)
print("✅ HOÀN THÀNH FEATURE ENGINEERING")
print("=" * 60)

# Gợi ý bước tiếp theo
print("\n👉 Bước tiếp theo:")
print("   python3 scripts/05_train_model.py")
