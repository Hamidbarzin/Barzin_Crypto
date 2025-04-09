#!/bin/bash

# اجرای سرویس تلگرام بسیار ساده
echo "شروع سرویس تلگرام بسیار ساده..."

# حذف لاگ‌های قبلی (اختیاری)
rm -f super_simple_scheduler.log super_simple_scheduler.pid

# اجرای اسکریپت در پس‌زمینه
nohup python super_simple_scheduler.py > /dev/null 2>&1 &

# منتظر ماندن برای ایجاد فایل PID
sleep 2

# نمایش اطلاعات
if [ -f super_simple_scheduler.pid ]; then
    PID=$(cat super_simple_scheduler.pid)
    echo "سرویس تلگرام با شناسه $PID شروع به کار کرد."
else
    echo "سرویس شروع شده اما فایل PID ایجاد نشده است."
fi

echo ""
echo "برای بررسی وضعیت سرویس، از دستور زیر استفاده کنید:"
echo "  cat super_simple_scheduler.log"
echo ""
echo "برای توقف سرویس، از دستور زیر استفاده کنید:"
echo "  ./توقف_تلگرام_ساده.sh"
echo ""
echo "برای ارسال یک پیام تست سریع، از دستور زیر استفاده کنید:"
echo "  python super_simple_telegram.py"