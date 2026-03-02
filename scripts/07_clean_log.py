#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: scripts/07_clean_log.py
Mục đích:
- Xóa 10 file log cũ nhất
- Xóa file log cũ hơn 7 ngày
- KHÔNG xóa:
    - dataset.csv
    - conn.log (file đang ghi)
    - live_state.json
"""

import os
import time
from datetime import datetime, timedelta

# ====== CẤU HÌNH ======
DATA_DIR = "/home/server-ubuntu/zeek_flow/data"
KEEP_FILES = {"dataset.csv", "conn.log", "live_state.json"}
LOG_EXT = ".log"
DAYS_TO_KEEP = 7
DELETE_OLDEST_COUNT = 10


def get_log_files():
    """Lấy tất cả file .log hợp lệ trong DATA_DIR"""
    files = []
    for f in os.listdir(DATA_DIR):
        full_path = os.path.join(DATA_DIR, f)

        if not os.path.isfile(full_path):
            continue

        # Không xóa file cần giữ
        if f in KEEP_FILES:
            continue

        # Chỉ xử lý file .log
        if f.endswith(LOG_EXT):
            files.append(full_path)

    return files


def delete_oldest_logs(log_files):
    """Xóa 10 file log cũ nhất (theo thời gian sửa đổi)"""
    log_files_sorted = sorted(log_files, key=lambda x: os.path.getmtime(x))

    to_delete = log_files_sorted[:DELETE_OLDEST_COUNT]

    print(f"\n[1] Deleting {len(to_delete)} oldest logs...")

    for f in to_delete:
        try:
            print(f"   🗑 Deleting: {os.path.basename(f)}")
            os.remove(f)
        except Exception as e:
            print(f"   ❌ Failed: {f} - {e}")


def delete_logs_older_than_days(log_files, days):
    """Xóa log cũ hơn N ngày"""
    cutoff_time = time.time() - (days * 86400)

    print(f"\n[2] Deleting logs older than {days} days...")

    for f in log_files:
        try:
            file_mtime = os.path.getmtime(f)

            if file_mtime < cutoff_time:
                print(f"   🗑 Deleting (>{days}d): {os.path.basename(f)}")
                os.remove(f)

        except Exception as e:
            print(f"   ❌ Failed: {f} - {e}")


def main():
    print("=" * 50)
    print("🧹 ZEEK LOG CLEANER")
    print("=" * 50)

    if not os.path.exists(DATA_DIR):
        print(f"❌ DATA_DIR not found: {DATA_DIR}")
        return

    log_files = get_log_files()

    print(f"📂 Total log files found: {len(log_files)}")

    if not log_files:
        print("✅ No log files to clean.")
        return

    # Bước 1: Xóa 10 file cũ nhất
    delete_oldest_logs(log_files)

    # Refresh list sau khi xóa
    log_files = get_log_files()

    # Bước 2: Xóa log > 7 ngày
    delete_logs_older_than_days(log_files, DAYS_TO_KEEP)

    print("\n✅ Log cleanup completed.")


if __name__ == "__main__":
    main()
