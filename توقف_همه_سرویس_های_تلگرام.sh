#!/bin/bash

# این اسکریپت تمام سرویس‌های تلگرام را متوقف می‌کند

echo "در حال توقف تمام سرویس‌های تلگرام..."

# ابتدا ناظر را متوقف می‌کنیم
./توقف_نظارت_تلگرام.sh

# کمی صبر می‌کنیم
sleep 2

# سپس سرویس ارسال پیام هر ۱۰ دقیقه را متوقف می‌کنیم
./توقف_گزارش_دهنده_هر_۱۰_دقیقه.sh

# کمی صبر می‌کنیم
sleep 2

echo "بررسی وضعیت فعلی سرویس‌ها:"

# بررسی هر گونه فرآیند مربوط به سرویس‌های تلگرام
pids_sender=$(ps aux | grep "ten_minute_telegram_sender.py" | grep -v grep | awk '{print $2}')
pids_watchdog=$(ps aux | grep "telegram_service_watchdog.py" | grep -v grep | awk '{print $2}')

if [ -n "$pids_sender" ]; then
    echo "⚠️ فرآیندهای سرویس ارسال پیام هر ۱۰ دقیقه هنوز در حال اجرا هستند. در حال توقف اجباری..."
    for p in $pids_sender; do
        echo "توقف فرآیند با PID: $p"
        kill -9 $p
    done
else
    echo "✅ سرویس ارسال پیام هر ۱۰ دقیقه: متوقف شده"
fi

if [ -n "$pids_watchdog" ]; then
    echo "⚠️ فرآیندهای ناظر سرویس‌های تلگرام هنوز در حال اجرا هستند. در حال توقف اجباری..."
    for p in $pids_watchdog; do
        echo "توقف فرآیند با PID: $p"
        kill -9 $p
    done
else
    echo "✅ ناظر سرویس‌های تلگرام: متوقف شده"
fi

# پاکسازی فایل‌های PID اضافی
if [ -f "ten_minute_telegram_sender.pid" ]; then
    echo "پاکسازی فایل PID سرویس ارسال پیام هر ۱۰ دقیقه"
    rm ten_minute_telegram_sender.pid
fi

if [ -f "watchdog.pid" ]; then
    echo "پاکسازی فایل PID ناظر سرویس‌های تلگرام"
    rm watchdog.pid
fi

echo "تمام سرویس‌های تلگرام متوقف شدند."