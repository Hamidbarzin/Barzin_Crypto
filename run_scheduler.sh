#!/bin/bash

# اسکریپت راه‌اندازی زمان‌بندی خودکار ربات تلگرام
# این اسکریپت، زمان‌بندی ارسال پیام‌های دوره‌ای را آغاز می‌کند

echo "$(date) - شروع اجرای اسکریپت زمان‌بندی" > scheduler.log

# بررسی وجود فایل simple_scheduler.py
if [ ! -f simple_scheduler.py ]; then
    echo "$(date) - خطا: فایل simple_scheduler.py یافت نشد" >> scheduler.log
    exit 1
fi

# اجرای اسکریپت زمان‌بندی در پس‌زمینه
echo "$(date) - در حال راه‌اندازی زمان‌بندی دوره‌ای..." >> scheduler.log
nohup python simple_scheduler.py >> scheduler.log 2>&1 &

# ذخیره شناسه فرآیند
PID=$!
echo "$(date) - زمان‌بندی با شناسه فرآیند $PID شروع شد" >> scheduler.log

# ذخیره شناسه فرآیند برای استفاده‌های بعدی
echo $PID > scheduler.pid

echo "$(date) - پایان اجرای اسکریپت زمان‌بندی" >> scheduler.log

echo "زمان‌بندی دوره‌ای با موفقیت راه‌اندازی شد"
echo "شناسه فرآیند: $PID"
echo "لاگ را می‌توانید در فایل scheduler.log مشاهده کنید"
