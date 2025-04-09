#!/bin/bash

# اسکریپت برای توقف تست تلگرام
# این اسکریپت فرآیند تست تلگرام را متوقف می‌کند

echo "توقف اسکریپت تست تلگرام..."

# بررسی وجود فایل PID
if [ ! -f "telegram_test_sender.pid" ]; then
    echo "خطا: فایل PID پیدا نشد. به نظر می‌رسد اسکریپت تست در حال اجرا نیست."
    exit 1
fi

# خواندن PID از فایل
PID=$(cat telegram_test_sender.pid)

# بررسی اینکه آیا فرآیند هنوز در حال اجراست
if ! ps -p $PID > /dev/null; then
    echo "هشدار: فرآیند با PID $PID پیدا نشد."
    echo "حذف فایل PID قدیمی..."
    rm -f telegram_test_sender.pid
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
    rm -f telegram_test_sender.pid
    echo "فایل PID حذف شد."
    exit 0
fi