#!/bin/bash

# راه‌اندازی اسکریپت زمان‌بندی در پس‌زمینه
echo "شروع راه‌اندازی برنامه زمان‌بندی ربات ارز دیجیتال..."
nohup python scheduler.py > scheduler.log 2>&1 &
echo "برنامه زمان‌بندی در پس‌زمینه اجرا شد. لاگ‌ها در فایل scheduler.log ذخیره می‌شوند."

# نمایش راهنمای استفاده از اسکریپت تست تلگرام
echo ""
echo "============= راهنمای استفاده از اسکریپت تست تلگرام ============="
echo "برای ارسال پیام تست به چت آیدی پیش‌فرض:"
echo "python test_telegram.py"
echo ""
echo "برای ارسال پیام تست به چت آیدی مشخص:"
echo "python test_telegram.py 722627622"
echo ""
echo "برای دریافت اطلاعات بات تلگرام:"
echo "python test_telegram.py --info"
echo ""
echo "برای بررسی معتبر بودن چت آیدی:"
echo "python test_telegram.py --check 722627622"
echo ""
echo "برای نمایش این راهنما:"
echo "python test_telegram.py --help"
echo "================================================================="
