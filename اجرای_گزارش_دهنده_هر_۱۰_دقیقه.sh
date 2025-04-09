#!/bin/bash

# این اسکریپت سرویس ارسال پیام هر ۱۰ دقیقه را شروع می‌کند

echo "در حال شروع سرویس ارسال پیام تلگرام هر ۱۰ دقیقه..."

# بررسی وجود فایل PID
if [ -f "ten_minute_telegram_sender.pid" ]; then
    pid=$(cat ten_minute_telegram_sender.pid)
    if ps -p $pid > /dev/null; then
        echo "سرویس قبلاً در حال اجراست (PID: $pid)"
        exit 1
    else
        echo "فایل PID قدیمی پیدا شد. در حال پاکسازی..."
        rm ten_minute_telegram_sender.pid
    fi
fi

# اجرای سرویس در پس‌زمینه
nohup python3 ten_minute_telegram_sender.py > /dev/null 2>&1 &

echo "سرویس شروع شد."