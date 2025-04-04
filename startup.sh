#!/bin/bash

# اسکریپت راه‌اندازی ربات تلگرام
# این اسکریپت در زمان شروع برنامه اجرا می‌شود
# و یک پیام تست ارسال می‌کند

echo "$(date) - شروع اجرای اسکریپت راه‌اندازی" > startup.log

# ارسال پیام تست
echo "$(date) - ارسال پیام تست تلگرام..." >> startup.log
python telegram_reporter.py test >> startup.log 2>&1

# ارسال گزارش دوره‌ای
echo "$(date) - ارسال گزارش دوره‌ای اولیه..." >> startup.log
python telegram_reporter.py >> startup.log 2>&1

echo "$(date) - پایان اجرای اسکریپت راه‌اندازی" >> startup.log