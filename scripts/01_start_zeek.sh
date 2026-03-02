#!/bin/bash
# File: scripts/01_start_zeek.sh
# Mục đích: Khởi động Zeek trên IDS

# Cấu hình
PROJECT_DIR="/home/server-ubuntu/zeek_flow"
CONFIG_FILE="$PROJECT_DIR/config/local.zeek"
DATA_DIR="$PROJECT_DIR/data"
INTERFACE="ens33"  # ✅ SỬA: ens33 là interface kết nối Kali

# Tạo thư mục data
mkdir -p "$DATA_DIR"
cd "$DATA_DIR" || exit 1

# Kill Zeek cũ
sudo pkill zeek 2>/dev/null
sleep 2

# Copy config vào thư mục hiện tại
cp "$CONFIG_FILE" ./local.zeek

echo "========================================="
echo "Zeek 8.1.1 - DDoS Detection Lab"
echo "========================================="
echo "[+] Interface: $INTERFACE"
echo "[+] Config: local.zeek"
echo "[+] Data dir: $DATA_DIR"
echo "========================================="
echo ""
echo "⚠️  Zeek đang chạy foreground. Nhấn Ctrl+C để dừng."
echo ""

# Chạy Zeek với interface ens33
sudo /opt/zeek/bin/zeek -i "$INTERFACE" local.zeek
