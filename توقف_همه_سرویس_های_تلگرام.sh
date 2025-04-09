#!/bin/bash

# اسکریپت توقف همه سرویس‌های تلگرام
echo "در حال توقف همه سرویس‌های تلگرام Crypto Barzin..."

# گام 1: توقف سیستم نظارت
echo ""
echo "گام 1: توقف سیستم نظارت..."
./توقف_نظارت_تلگرام.sh
echo ""

# گام 2: توقف گزارش‌دهنده هر 10 دقیقه
echo "گام 2: توقف گزارش‌دهنده هر 10 دقیقه..."
./توقف_گزارش_دهنده_هر_۱۰_دقیقه.sh
echo ""

# توقف اضطراری فرآیندهای باقیمانده
echo "گام 3: بررسی و توقف فرآیندهای باقیمانده..."

telegram_pids=$(ps aux | grep "telegram" | grep -v grep | awk '{print $2}')
if [ -n "$telegram_pids" ]; then
    echo "فرآیندهای تلگرام باقیمانده:"
    ps aux | grep "telegram" | grep -v grep
    
    echo "در حال توقف فرآیندهای باقیمانده..."
    for pid in $telegram_pids; do
        kill -9 $pid 2>/dev/null
        echo "فرآیند $pid متوقف شد."
    done
else
    echo "هیچ فرآیند تلگرام باقیمانده‌ای یافت نشد."
fi

# پاک کردن فایل‌های PID
if [ -f "telegram_service_watchdog.pid" ]; then
    rm telegram_service_watchdog.pid
    echo "فایل PID نظارت حذف شد."
fi

if [ -f "ten_minute_telegram_sender.pid" ]; then
    rm ten_minute_telegram_sender.pid
    echo "فایل PID گزارش‌دهنده حذف شد."
fi

# اطلاعات نهایی
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 همه سرویس‌های تلگرام Crypto Barzin متوقف شدند!"
echo ""
echo "🔄 برای راه‌اندازی مجدد همه سرویس‌ها:"
echo "./اجرای_خودکار_همه_سرویس_های_تلگرام.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"