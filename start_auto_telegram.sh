#!/bin/bash
# اسکریپت راه‌اندازی سرویس ارسال خودکار پیام‌های تلگرام

echo "در حال راه‌اندازی سرویس ارسال خودکار پیام تلگرام..."

# بررسی وجود فایل PID
PID_FILE="auto_telegram_sender.pid"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "سرویس قبلی با PID $OLD_PID در حال اجراست. در حال متوقف کردن..."
        kill "$OLD_PID"
        sleep 2
    fi
    echo "پاکسازی فایل PID قدیمی..."
    rm -f "$PID_FILE"
fi

# اجرای اسکریپت در پس‌زمینه
echo "شروع سرویس جدید..."
nohup python3 auto_telegram_sender.py > /dev/null 2>&1 &

# بررسی موفقیت‌آمیز بودن راه‌اندازی
sleep 2
if [ -f "$PID_FILE" ]; then
    NEW_PID=$(cat "$PID_FILE")
    echo "سرویس با موفقیت راه‌اندازی شد (PID: $NEW_PID)"
    echo "لاگ‌ها در فایل auto_telegram_sender.log ذخیره می‌شوند"
else
    echo "خطا در راه‌اندازی سرویس"
    exit 1
fi