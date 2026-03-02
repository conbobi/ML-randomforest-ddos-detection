#!/bin/bash
# File: scripts/02_generate_traffic_kali.sh
# Mục đích: Chạy trên Kali (172.16.212.10), sinh traffic tới Victim (172.16.213.20)

# Cấu hình
VICTIM_IP="172.16.213.20"  # Victim IP
MARKER_FILE="attack_timestamps.txt"

# Các tham số thời gian
NORMAL_DURATION=20   # 20 giây normal
ATTACK_DURATION=8     # 8 giây attack
LOOPS=3              # Lặp lại 3 lần

# Thông tin IDS để ghi marker
IDS_USER="server-ubuntu"
IDS_HOST="172.16.212.1"
IDS_PATH="/home/server-ubuntu/zeek_flow/data/"

# Xóa file marker cũ trên IDS
ssh "$IDS_USER@$IDS_HOST" "rm -f $IDS_PATH$MARKER_FILE"

echo "========================================="
echo "Kali Attacker - Traffic Generator"
echo "========================================="
echo "Victim: $VICTIM_IP"
echo "Normal duration: $NORMAL_DURATION s"
echo "Attack duration: $ATTACK_DURATION s"
echo "Loops: $LOOPS"
echo "========================================="

for ((i=1; i<=LOOPS; i++)); do
    echo ""
    echo "===== PHASE $i/$LOOPS ====="
    
    # === PHASE 1: NORMAL TRAFFIC ===
    echo "[*] Phase $i - Normal traffic (${NORMAL_DURATION}s)"
    
    # Ghi marker NORMAL lên IDS
    ssh "$IDS_USER@$IDS_HOST" "echo 'NORMAL_START_$i' >> $IDS_PATH$MARKER_FILE && date +%s >> $IDS_PATH$MARKER_FILE"
    
    # Sinh normal traffic
    echo "   Sending HTTP requests..."
    
    # Curl nhiều lần để tạo normal traffic
    for j in {1..20}; do
        curl -s "http://$VICTIM_IP/" > /dev/null &
        sleep 0.3
    done
    
    # Apache bench để tạo nhiều connection hơn
    ab -n 200 -c 10 "http://$VICTIM_IP/" 2>/dev/null &
    
    # Chạy normal traffic trong NORMAL_DURATION
    sleep $NORMAL_DURATION
    
    # Kill các background process
    kill $(jobs -p) 2>/dev/null
    
    # === PHASE 2: ATTACK TRAFFIC ===
    echo "[!] Phase $i - SYN Flood attack (${ATTACK_DURATION}s)"
    
    # Ghi marker ATTACK lên IDS
    ssh "$IDS_USER@$IDS_HOST" "echo 'ATTACK_START_$i' >> $IDS_PATH$MARKER_FILE && date +%s >> $IDS_PATH$MARKER_FILE"
    
    # SYN Flood attack
    echo "   Launching SYN flood..."
    sudo hping3 -S -p 80 --flood "$VICTIM_IP" 2>/dev/null &
    HPING_PID=$!
    
    sleep $ATTACK_DURATION
    
    # Kill hping3
    sudo kill -9 $HPING_PID 2>/dev/null
    
    # Ghi marker ATTACK END
    ssh "$IDS_USER@$IDS_HOST" "echo 'ATTACK_END_$i' >> $IDS_PATH$MARKER_FILE && date +%s >> $IDS_PATH$MARKER_FILE"
    
    # Nghỉ giữa các phase
    echo "[*] Cooling down 5s..."
    sleep 5
done

echo ""
echo "========================================="
echo "[✅] Hoàn thành sinh traffic"
echo "[+] File marker đã được ghi tại IDS: $IDS_PATH$MARKER_FILE"
echo "========================================="

# Hiển thị nội dung file marker
echo ""
echo "Nội dung file marker:"
ssh "$IDS_USER@$IDS_HOST" "cat $IDS_PATH$MARKER_FILE"
