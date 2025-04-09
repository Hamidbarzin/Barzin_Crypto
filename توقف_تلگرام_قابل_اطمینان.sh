#!/bin/bash

# توقف سرویس تلگرام با قابلیت اطمینان بالا
echo "توقف سرویس تلگرام با قابلیت اطمینان بالا..."

# بررسی وجود فایل pid
if [ -f reliable_telegram.pid ]; then
    # خواندن شناسه فرآیند
    PID=$(cat reliable_telegram.pid)
    
    # بررسی وجود فرآیند
    if ps -p $PID > /dev/null; then
        echo "توقف فرآیند با شناسه $PID..."
        kill $PID
        
        # انتظار برای توقف فرآیند
        sleep 2
        
        # بررسی مجدد وجود فرآیند
        if ps -p $PID > /dev/null; then
            echo "فرآیند هنوز در حال اجراست. توقف اجباری..."
            kill -9 $PID
        fi
        
        echo "سرویس تلگرام متوقف شد."
    else
        echo "فرآیند با شناسه $PID در حال اجرا نیست."
    fi
    
    # حذف فایل pid
    rm reliable_telegram.pid
else
    echo "فایل شناسه فرآیند (reliable_telegram.pid) پیدا نشد."
    echo "جستجوی دستی فرآیندها..."
    
    # جستجوی دستی فرآیندها
    RUNNING_PIDS=$(ps aux | grep "[r]eliable_telegram_service.py" | awk '{print $2}')
    
    if [ -n "$RUNNING_PIDS" ]; then
        echo "یافتن فرآیندهای در حال اجرا: $RUNNING_PIDS"
        
        # توقف تمام فرآیندهای مرتبط
        for pid in $RUNNING_PIDS; do
            echo "توقف فرآیند با شناسه $pid..."
            kill $pid
        done
        
        echo "سرویس تلگرام متوقف شد."
    else
        echo "هیچ فرآیند مرتبطی در حال اجرا نیست."
    fi
fi