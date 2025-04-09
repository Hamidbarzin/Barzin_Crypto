#!/bin/bash

# اسکریپت راه‌اندازی نظارت بر سرویس تلگرام
echo "در حال راه‌اندازی نظارت بر سرویس تلگرام..."

# بررسی وجود فایل PID
if [ -f "telegram_service_watchdog.pid" ]; then
    pid=$(cat telegram_service_watchdog.pid | python3 -c "import json,sys; print(json.load(sys.stdin).get('pid', 0))")
    
    if ps -p $pid > /dev/null; then
        echo "سرویس نظارت قبلاً در حال اجراست (PID: $pid)"
        echo "برای راه‌اندازی مجدد، ابتدا سرویس را متوقف کنید:"
        echo "./توقف_نظارت_تلگرام.sh"
        exit 1
    else
        echo "فایل PID قدیمی یافت شد. در حال حذف..."
        rm telegram_service_watchdog.pid
    fi
fi

# راه‌اندازی سرویس در پس‌زمینه
nohup python3 telegram_service_watchdog.py > telegram_service_watchdog.log 2>&1 &

echo "سرویس نظارت با موفقیت راه‌اندازی شد!"
echo "برای مشاهده لاگ‌ها:"
echo "cat telegram_service_watchdog.log"
echo "برای توقف سرویس:"
echo "./توقف_نظارت_تلگرام.sh"

echo ""
echo "این سرویس هر ساعت بررسی می‌کند که سرویس گزارش‌دهنده هر ۱۰ دقیقه فعال باشد"
echo "و در صورت غیرفعال بودن، آن را دوباره راه‌اندازی می‌کند."