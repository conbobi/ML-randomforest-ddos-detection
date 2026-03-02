# File: config/local.zeek
# Zeek version: 8.1.1
# Mục đích: Cấu hình tối ưu cho phát hiện DDoS

# Giảm timeout để SYN flood được log nhanh hơn
redef tcp_inactivity_timeout = 10 secs;

# Cấu hình log rotation
redef Log::default_rotation_interval = 1 mins;

# Tắt JSON, dùng TSV cho dễ xử lý
redef LogAscii::use_json = F;

# Load các script cần thiết
@load base/protocols/conn
@load base/protocols/http
@load base/frameworks/notice

# ĐÃ XÓA: redef Conn::default_duration (không tồn tại trong Zeek 8.1.1)
