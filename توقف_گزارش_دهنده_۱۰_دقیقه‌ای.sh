#!/bin/bash

# اسکریپت برای توقف گزارش‌دهنده ۱۰ دقیقه‌ای تلگرام
# این اسکریپت فرآیند گزارش‌دهنده را متوقف می‌کند

echo "توقف گزارش‌دهنده ۱۰ دقیقه‌ای تلگرام..."

# بررسی وجود فایل PID
if [ ! -f "ten_minute_reporter.pid" ]; then
    echo "خطا: فایل PID پیدا نشد. به نظر می‌رسد گزارش‌دهنده در حال اجرا نیست."
    exit 1
fi

# خواندن PID از فایل
PID=$(cat ten_minute_reporter.pid)

# بررسی اینکه آیا فرآیند هنوز در حال اجراست
if ! ps -p $PID > /dev/null; then
    echo "هشدار: فرآیند با PID $PID پیدا نشد."
    echo "حذف فایل PID قدیمی..."
    rm -f ten_minute_reporter.pid
    exit 1
fi

# توقف فرآیند
echo "توقف فرآیند با PID: $PID..."
kill $PID

# بررسی موفقیت‌آمیز بودن توقف
sleep 2
if ps -p $PID > /dev/null; then
    echo "هشدار: فرآیند به طور معمول متوقف نشد. تلاش برای توقف اجباری..."
    kill -9 $PID
    sleep 1
fi

# بررسی نهایی
if ps -p $PID > /dev/null; then
    echo "خطا: نمی‌توان فرآیند با PID $PID را متوقف کرد."
    exit 1
else
    echo "فرآیند با موفقیت متوقف شد."
    rm -f ten_minute_reporter.pid
    echo "فایل PID حذف شد."
    exit 0
fi