#!/bin/bash

# اسکریپت برای راه‌اندازی گزارش‌دهنده ۱۰ دقیقه‌ای تلگرام
# این اسکریپت گزارش‌دهنده ۱۰ دقیقه‌ای را راه‌اندازی می‌کند و خودش را از فرآیند جدا می‌کند

echo "شروع گزارش‌دهنده ۱۰ دقیقه‌ای تلگرام..."

# بررسی وجود فایل PID قبلی
if [ -f "ten_minute_reporter.pid" ]; then
    PID=$(cat ten_minute_reporter.pid)
    if ps -p $PID > /dev/null; then
        echo "هشدار: گزارش‌دهنده از قبل در حال اجراست با PID: $PID"
        echo "برای راه‌اندازی مجدد، ابتدا فرآیند قبلی را متوقف کنید: bash توقف_گزارش_دهنده_۱۰_دقیقه‌ای.sh"
        exit 1
    else
        echo "فایل PID قدیمی پیدا شد، اما فرآیند فعال نیست. حذف فایل PID قدیمی..."
        rm -f ten_minute_reporter.pid
    fi
fi

# راه‌اندازی گزارش‌دهنده در پس‌زمینه
nohup python new_ten_minute_reporter.py > new_ten_minute_reporter.log 2>&1 &

# کمی صبر کنید تا فرآیند شروع شود و فایل PID ایجاد شود
sleep 2

# بررسی اینکه آیا فرآیند به درستی شروع شده است
if [ -f "new_ten_minute_reporter.pid" ]; then
    PID=$(cat new_ten_minute_reporter.pid)
    if ps -p $PID > /dev/null; then
        echo "گزارش‌دهنده ۱۰ دقیقه‌ای با موفقیت شروع شد با PID: $PID"
        echo "لاگ‌ها در فایل new_ten_minute_reporter.log ذخیره می‌شوند"
        echo "برای توقف، از دستور زیر استفاده کنید: bash توقف_گزارش_دهنده_۱۰_دقیقه‌ای.sh"
        exit 0
    fi
fi

# اگر به اینجا برسیم، یعنی مشکلی در راه‌اندازی وجود داشته است
echo "خطا: گزارش‌دهنده ۱۰ دقیقه‌ای راه‌اندازی نشد"
echo "لطفاً لاگ‌ها را بررسی کنید: cat ten_minute_reporter.log"
exit 1