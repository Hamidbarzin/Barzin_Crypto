#!/bin/bash

# اسکریپت برای راه‌اندازی تست تلگرام
# این اسکریپت برای دیباگ مشکل ارسال گزارش‌های تلگرام استفاده می‌شود

echo "شروع تست ارسال پیام تلگرام..."

# بررسی وجود فایل log قبلی
if [ -f "test_10min_telegram.log" ]; then
    echo "حذف فایل لاگ قبلی..."
    rm -f test_10min_telegram.log
fi

# راه‌اندازی در پس‌زمینه
nohup python test_10min_telegram.py > test_10min_telegram.log 2>&1 &
PID=$!

echo "تست تلگرام با موفقیت شروع شد با PID: $PID"
echo "لاگ‌ها در فایل test_10min_telegram.log ذخیره می‌شوند"
echo "برای توقف، از دستور زیر استفاده کنید: pkill -f test_10min_telegram.py"

# نمایش قسمتی از لاگ‌ها
sleep 2
if [ -f "test_10min_telegram.log" ]; then
    echo ""
    echo "بخشی از لاگ‌ها:"
    echo "----------------"
    tail -n 15 test_10min_telegram.log
    echo "----------------"
fi

echo ""
echo "برای مشاهده لاگ‌ها به صورت زنده:"
echo "tail -f test_10min_telegram.log"