#!/bin/bash

# این اسکریپت ناظر سرویس‌های تلگرام را شروع می‌کند

echo "در حال شروع ناظر سرویس‌های تلگرام..."

# بررسی وجود فایل PID
if [ -f "watchdog.pid" ]; then
    pid=$(cat watchdog.pid)
    if ps -p $pid > /dev/null; then
        echo "ناظر قبلاً در حال اجراست (PID: $pid)"
        exit 1
    else
        echo "فایل PID قدیمی پیدا شد. در حال پاکسازی..."
        rm watchdog.pid
    fi
fi

# اجرای سرویس در پس‌زمینه
nohup python3 telegram_service_watchdog.py > /dev/null 2>&1 &

echo "ناظر شروع شد."