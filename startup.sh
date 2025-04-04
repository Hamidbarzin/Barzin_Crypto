#!/bin/bash

# بررسی و توقف نمونه‌های در حال اجرا
echo "بررسی و توقف نمونه‌های قبلی scheduler..."
pkill -f "python scheduler.py" || echo "هیچ نمونه در حال اجرا یافت نشد."
sleep 1

# راه‌اندازی اسکریپت زمان‌بندی در پس‌زمینه
echo "شروع راه‌اندازی برنامه زمان‌بندی ربات ارز دیجیتال..."
nohup python scheduler.py > scheduler.log 2>&1 &
PID=$!
echo "برنامه زمان‌بندی با PID $PID در پس‌زمینه اجرا شد."
echo "لاگ‌ها در فایل scheduler.log ذخیره می‌شوند."

# بررسی اینکه آیا فرآیند هنوز در حال اجراست
sleep 2
if ps -p $PID > /dev/null; then
    echo "تایید: برنامه زمان‌بندی با موفقیت اجرا شد و در حال اجراست."
else
    echo "خطا: فرآیند زمان‌بندی بلافاصله متوقف شد. برای دیدن جزئیات خطا، فایل scheduler.log را بررسی کنید."
fi

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
