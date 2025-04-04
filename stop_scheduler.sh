#!/bin/bash

# اسکریپت توقف زمان‌بندی خودکار ربات تلگرام
# این اسکریپت، فرآیند زمان‌بندی ارسال پیام‌های دوره‌ای را متوقف می‌کند

echo "$(date) - شروع اجرای اسکریپت توقف زمان‌بندی" >> scheduler.log

# بررسی وجود فایل scheduler.pid
if [ ! -f scheduler.pid ]; then
    echo "$(date) - خطا: فایل scheduler.pid یافت نشد" >> scheduler.log
    echo "فرآیند زمان‌بندی در حال اجرا نیست یا به درستی راه‌اندازی نشده است"
    exit 1
fi

# خواندن شناسه فرآیند
PID=$(cat scheduler.pid)

# بررسی وجود فرآیند
if ! ps -p $PID > /dev/null; then
    echo "$(date) - خطا: فرآیند با شناسه $PID در حال اجرا نیست" >> scheduler.log
    echo "فرآیند زمان‌بندی قبلاً متوقف شده است"
    rm -f scheduler.pid
    exit 1
fi

# توقف فرآیند
echo "$(date) - در حال توقف فرآیند زمان‌بندی با شناسه $PID..." >> scheduler.log
kill $PID

# بررسی نتیجه توقف
sleep 2
if ! ps -p $PID > /dev/null; then
    echo "$(date) - فرآیند زمان‌بندی با موفقیت متوقف شد" >> scheduler.log
    rm -f scheduler.pid
    echo "زمان‌بندی دوره‌ای با موفقیت متوقف شد"
else
    echo "$(date) - خطا: توقف فرآیند با شناسه $PID ناموفق بود" >> scheduler.log
    echo "توقف زمان‌بندی ناموفق بود. لطفاً دوباره تلاش کنید"
    exit 1
fi

echo "$(date) - پایان اجرای اسکریپت توقف زمان‌بندی" >> scheduler.log
