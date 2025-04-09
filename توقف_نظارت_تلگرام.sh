#!/bin/bash

# این اسکریپت ناظر سرویس‌های تلگرام را متوقف می‌کند

echo "در حال توقف ناظر سرویس‌های تلگرام..."

# بررسی وجود فایل PID
if [ -f "watchdog.pid" ]; then
    pid=$(cat watchdog.pid)
    
    if ps -p $pid > /dev/null; then
        echo "در حال توقف ناظر با PID: $pid"
        kill $pid
        
        # منتظر می‌ماند تا فرآیند متوقف شود
        for i in {1..10}; do
            if ! ps -p $pid > /dev/null; then
                echo "ناظر با موفقیت متوقف شد."
                
                # پاکسازی فایل PID اگر هنوز وجود داشته باشد
                if [ -f "watchdog.pid" ]; then
                    rm watchdog.pid
                fi
                
                exit 0
            fi
            
            echo "در حال انتظار برای توقف ناظر..."
            sleep 1
        done
        
        echo "ناظر در مدت زمان انتظار متوقف نشد. در حال اعمال سیگنال kill -9..."
        kill -9 $pid
        
        # پاکسازی فایل PID
        if [ -f "watchdog.pid" ]; then
            rm watchdog.pid
        fi
    else
        echo "فرآیند مربوط به PID $pid یافت نشد. در حال پاکسازی فایل PID..."
        rm watchdog.pid
    fi
else
    echo "فایل PID یافت نشد. ممکن است ناظر در حال اجرا نباشد."
    
    # بررسی و توقف هر فرآیندی که با این نام اجرا شده است
    pids=$(ps aux | grep "telegram_service_watchdog.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$pids" ]; then
        echo "فرآیندهای مربوط به ناظر یافت شد. در حال توقف..."
        
        for p in $pids; do
            echo "توقف فرآیند با PID: $p"
            kill $p
        done
        
        echo "تمام فرآیندهای ناظر متوقف شدند."
    else
        echo "هیچ فرآیندی برای ناظر یافت نشد."
    fi
fi

echo "عملیات توقف ناظر به پایان رسید."