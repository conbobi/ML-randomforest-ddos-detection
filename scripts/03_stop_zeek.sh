#!/bin/bash
# File: scripts/03_stop_zeek.sh
# Mục đích: Dừng Zeek và kiểm tra logs

DATA_DIR="/home/server-ubuntu/zeek_flow/data"

cd "$DATA_DIR" || exit 1

echo "========================================="
echo "Dừng Zeek"
echo "========================================="

# Dừng Zeek
sudo pkill zeek
sleep 2

# Kiểm tra logs
echo "[+] Các file log đã tạo:"
ls -lh *.log 2>/dev/null || echo "   Không có file log nào"

# Kiểm tra số dòng trong conn.log
if [ -f "conn.log" ]; then
    LINES=$(grep -v "^#" conn.log | wc -l)
    echo "[+] conn.log: $LINES flows (không tính header)"
    
    # Hiển thị 5 dòng đầu tiên (không header)
    echo ""
    echo "5 dòng đầu tiên trong conn.log:"
    grep -v "^#" conn.log | head -5 | cut -f1,2,3,4,5 | column -t
fi

# Kiểm tra file marker
if [ -f "attack_timestamps.txt" ]; then
    echo ""
    echo "[+] attack_timestamps.txt: tồn tại"
    echo "    Nội dung:"
    cat attack_timestamps.txt
else
    echo "[-] attack_timestamps.txt: KHÔNG tồn tại"
fi

echo "========================================="
