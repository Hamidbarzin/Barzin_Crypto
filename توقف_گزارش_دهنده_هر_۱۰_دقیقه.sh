#!/bin/bash

# این اسکریپت سرویس ارسال پیام هر ۱۰ دقیقه را متوقف می‌کند

echo "در حال توقف سرویس ارسال پیام تلگرام هر ۱۰ دقیقه..."

# بررسی وجود فایل PID
if [ -f "ten_minute_telegram_sender.pid" ]; then
    pid=$(cat ten_minute_telegram_sender.pid)
    
    if ps -p $pid > /dev/null; then
        echo "در حال توقف سرویس با PID: $pid"
        kill $pid
        
        # منتظر می‌ماند تا فرآیند متوقف شود
        for i in {1..10}; do
            if ! ps -p $pid > /dev/null; then
                echo "سرویس با موفقیت متوقف شد."
                
                # پاکسازی فایل PID اگر هنوز وجود داشته باشد
                if [ -f "ten_minute_telegram_sender.pid" ]; then
                    rm ten_minute_telegram_sender.pid
                fi
                
                exit 0
            fi
            
            echo "در حال انتظار برای توقف سرویس..."
            sleep 1
        done
        
        echo "سرویس در مدت زمان انتظار متوقف نشد. در حال اعمال سیگنال kill -9..."
        kill -9 $pid
        
        # پاکسازی فایل PID
        if [ -f "ten_minute_telegram_sender.pid" ]; then
            rm ten_minute_telegram_sender.pid
        fi
    else
        echo "فرآیند مربوط به PID $pid یافت نشد. در حال پاکسازی فایل PID..."
        rm ten_minute_telegram_sender.pid
    fi
else
    echo "فایل PID یافت نشد. ممکن است سرویس در حال اجرا نباشد."
    
    # بررسی و توقف هر فرآیندی که با این نام اجرا شده است
    pids=$(ps aux | grep "ten_minute_telegram_sender.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$pids" ]; then
        echo "فرآیندهای مربوط به سرویس یافت شد. در حال توقف..."
        
        for p in $pids; do
            echo "توقف فرآیند با PID: $p"
            kill $p
        done
        
        echo "تمام فرآیندهای سرویس متوقف شدند."
    else
        echo "هیچ فرآیندی برای سرویس یافت نشد."
    fi
fi

echo "عملیات توقف سرویس به پایان رسید."