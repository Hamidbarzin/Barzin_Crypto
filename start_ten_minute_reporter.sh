#!/bin/bash

# این اسکریپت زمان‌بندی ارسال گزارش هر ۱۰ دقیقه را راه‌اندازی می‌کند

echo "راه‌اندازی ارسال گزارش سه لایه‌ای هر ۱۰ دقیقه به تلگرام..."

# بررسی وضعیت اجرای قبلی
if [ -f "ten_minute_scheduler.pid" ]; then
    pid=$(cat ten_minute_scheduler.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "زمان‌بندی قبلی با شناسه $pid در حال اجراست. در حال توقف آن..."
        kill $pid
        sleep 2
    fi
    rm ten_minute_scheduler.pid
fi

# اجرای اسکریپت در پس‌زمینه
nohup python ten_minute_scheduler.py > ten_minute_scheduler.log 2>&1 &

echo "زمان‌بندی راه‌اندازی شد. ارسال گزارش هر ۱۰ دقیقه انجام خواهد شد."
echo "برای مشاهده وضعیت: tail -f ten_minute_scheduler.log"