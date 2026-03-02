#!/bin/bash
# Script cấu hình iptables cho IDS - Dùng interface ens33, ens37, ens38

echo "🔄 Đang cấu hình iptables..."

# Reset tất cả rules
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -X

# Policy mặc định
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Cho phép loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Cho phép các kết nối đã thiết lập
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 🔴 QUAN TRỌNG: Cho phép ping từ Kali vào IDS
sudo iptables -A INPUT -i ens33 -s 172.16.212.0/24 -p icmp --icmp-type echo-request -j ACCEPT

# Cho phép SSH từ Kali (nếu cần)
sudo iptables -A INPUT -i ens33 -s 172.16.212.0/24 -p tcp --dport 22 -j ACCEPT

# NAT ra Internet - dùng ens38
sudo iptables -t nat -A POSTROUTING -o ens38 -j MASQUERADE

# FORWARD rules
sudo iptables -A FORWARD -i ens33 -o ens38 -j ACCEPT   # Kali ra Internet
sudo iptables -A FORWARD -i ens37 -o ens38 -j ACCEPT   # Victim ra Internet
sudo iptables -A FORWARD -i ens33 -o ens37 -j ACCEPT   # Kali → Victim
sudo iptables -A FORWARD -i ens37 -o ens33 -j ACCEPT   # Victim → Kali

echo "✅ Cấu hình iptables hoàn tất!"

# Hiển thị kết quả
echo ""
echo "📊 INPUT rules:"
sudo iptables -L INPUT -v --line-numbers | head -10

echo ""
echo "📊 FORWARD rules:"
sudo iptables -L FORWARD -v --line-numbers | head -10

echo ""
echo "📊 NAT rules:"
sudo iptables -t nat -L POSTROUTING -v
