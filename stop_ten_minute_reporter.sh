#!/bin/bash

# این اسکریپت زمان‌بندی ارسال گزارش هر ۱۰ دقیقه را متوقف می‌کند

echo "در حال توقف سرویس ارسال گزارش ۱۰ دقیقه‌ای..."

# بررسی وضعیت اجرا
if [ -f "ten_minute_scheduler.pid" ]; then
    pid=$(cat ten_minute_scheduler.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "زمان‌بندی با شناسه $pid در حال اجراست. در حال توقف آن..."
        kill $pid
        echo "زمان‌بندی متوقف شد."
    else
        echo "فرایندی با شناسه $pid یافت نشد."
    fi
    rm ten_minute_scheduler.pid
else
    echo "فایل شناسه فرایند یافت نشد. ممکن است سرویس در حال اجرا نباشد."
    
    # جستجوی فرایندهای مرتبط و توقف آنها
    pids=$(ps aux | grep "ten_minute_scheduler.py" | grep -v grep | awk '{print $2}')
    if [ -n "$pids" ]; then
        echo "فرایندهای مرتبط یافت شدند. در حال توقف آنها..."
        for p in $pids; do
            echo "توقف فرایند $p..."
            kill $p
        done
        echo "تمام فرایندهای مرتبط متوقف شدند."
    else
        echo "هیچ فرایند مرتبطی یافت نشد."
    fi
fi

echo "سرویس ارسال گزارش ۱۰ دقیقه‌ای متوقف شد."
