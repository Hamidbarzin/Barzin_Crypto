#!/bin/bash

# اسکریپت برای راه‌اندازی تست تلگرام
# این اسکریپت هر دقیقه یک پیام تست به تلگرام ارسال می‌کند

echo "شروع اسکریپت تست تلگرام..."

# بررسی وجود فایل PID قبلی
if [ -f "telegram_test_sender.pid" ]; then
    PID=$(cat telegram_test_sender.pid)
    if ps -p $PID > /dev/null; then
        echo "هشدار: اسکریپت تست از قبل در حال اجراست با PID: $PID"
        echo "برای راه‌اندازی مجدد، ابتدا فرآیند قبلی را متوقف کنید."
        exit 1
    else
        echo "فایل PID قدیمی پیدا شد، اما فرآیند فعال نیست. حذف فایل PID قدیمی..."
        rm -f telegram_test_sender.pid
    fi
fi

# راه‌اندازی اسکریپت در پس‌زمینه
nohup python telegram_test_sender.py > telegram_test_sender.log 2>&1 &
echo $! > telegram_test_sender.pid

# کمی صبر کنید تا فرآیند شروع شود
sleep 2

# بررسی اینکه آیا فرآیند به درستی شروع شده است
if [ -f "telegram_test_sender.pid" ]; then
    PID=$(cat telegram_test_sender.pid)
    if ps -p $PID > /dev/null; then
        echo "اسکریپت تست تلگرام با موفقیت شروع شد با PID: $PID"
        echo "لاگ‌ها در فایل telegram_test_sender.log ذخیره می‌شوند"
        exit 0
    fi
fi

# اگر به اینجا برسیم، یعنی مشکلی در راه‌اندازی وجود داشته است
echo "خطا: اسکریپت تست تلگرام راه‌اندازی نشد"
echo "لطفاً لاگ‌ها را بررسی کنید: cat telegram_test_sender.log"
exit 1