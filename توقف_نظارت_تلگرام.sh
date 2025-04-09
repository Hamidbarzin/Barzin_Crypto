#!/bin/bash

# اسکریپت توقف نظارت بر سرویس تلگرام
echo "در حال توقف نظارت بر سرویس تلگرام..."

# بررسی وجود فایل PID
if [ ! -f "telegram_service_watchdog.pid" ]; then
    echo "فایل PID یافت نشد. به نظر می‌رسد سرویس نظارت در حال اجرا نیست."
    
    # بررسی وجود فرآیند به طور دستی
    pids=$(ps aux | grep "telegram_service_watchdog.py" | grep -v grep | awk '{print $2}')
    
    if [ -z "$pids" ]; then
        echo "هیچ فرآیند مربوط به نظارت تلگرام یافت نشد."
        exit 1
    else
        echo "فرآیندهای مربوط به نظارت یافت شد. در حال توقف..."
        for pid in $pids; do
            kill $pid 2>/dev/null
            echo "فرآیند $pid متوقف شد."
        done
    fi
else
    # خواندن PID از فایل
    pid=$(cat telegram_service_watchdog.pid | python3 -c "import json,sys; print(json.load(sys.stdin).get('pid', 0))")
    
    if [ "$pid" -gt 0 ]; then
        # توقف فرآیند
        kill $pid 2>/dev/null
        
        # بررسی موفقیت
        if ps -p $pid > /dev/null; then
            echo "خطا در توقف سرویس. تلاش برای توقف اجباری..."
            kill -9 $pid 2>/dev/null
        else
            echo "سرویس نظارت با موفقیت متوقف شد."
        fi
    else
        echo "PID نامعتبر در فایل"
    fi
    
    # حذف فایل PID
    rm telegram_service_watchdog.pid
fi

# بررسی نهایی
pids=$(ps aux | grep "telegram_service_watchdog.py" | grep -v grep | awk '{print $2}')
if [ -n "$pids" ]; then
    echo "هشدار: هنوز فرآیندهای نظارت در حال اجرا هستند:"
    for pid in $pids; do
        echo "PID: $pid"
    done
    echo "برای توقف کامل، از دستور زیر استفاده کنید:"
    echo "kill -9 $pids"
else
    echo "نظارت تلگرام کاملاً متوقف شد."
fi