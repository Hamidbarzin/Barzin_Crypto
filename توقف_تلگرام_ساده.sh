#!/bin/bash

# اسکریپت ساده برای توقف سرویس تلگرام ساده
# این اسکریپت سرویس گزارش‌دهی ساده تلگرام را متوقف می‌کند

echo "توقف سرویس تلگرام ساده..."

# بررسی وجود فایل PID
if [ ! -f "new_ten_minute_reporter.pid" ]; then
    echo "خطا: فایل PID یافت نشد!"
    echo "به نظر می‌رسد سرویس در حال اجرا نیست."
    
    # بررسی فرآیندهای در حال اجرا به صورت دستی
    echo "جستجوی فرآیندهای مرتبط..."
    PIDS=$(ps aux | grep "new_ten_minute_reporter.py" | grep -v grep | awk '{print $2}')
    
    if [ -z "$PIDS" ]; then
        echo "هیچ فرآیند مرتبطی یافت نشد."
        exit 1
    else
        echo "فرآیندهای مرتبط یافت شد: $PIDS"
        echo "آیا مایل به توقف این فرآیندها هستید؟ (y/n)"
        read -p "> " CONFIRM
        
        if [ "$CONFIRM" == "y" ] || [ "$CONFIRM" == "Y" ]; then
            for PID in $PIDS; do
                echo "در حال توقف فرآیند $PID..."
                kill -15 $PID
            done
            echo "فرآیندها متوقف شدند."
        else
            echo "عملیات توقف لغو شد."
            exit 1
        fi
    fi
else
    # خواندن PID از فایل
    PID=$(cat new_ten_minute_reporter.pid)
    
    # بررسی وجود فرآیند
    if ps -p $PID > /dev/null; then
        echo "در حال توقف سرویس تلگرام ساده با PID: $PID"
        kill -15 $PID
        sleep 2
        
        # بررسی مجدد وجود فرآیند
        if ps -p $PID > /dev/null; then
            echo "فرآیند هنوز در حال اجراست. استفاده از سیگنال اجباری برای توقف..."
            kill -9 $PID
            sleep 1
        fi
        
        # بررسی نهایی
        if ps -p $PID > /dev/null; then
            echo "خطا: نمی‌توان فرآیند را متوقف کرد!"
            exit 1
        else
            echo "سرویس با موفقیت متوقف شد."
        fi
    else
        echo "فرآیند با PID $PID یافت نشد."
        echo "به نظر می‌رسد سرویس قبلاً متوقف شده است."
    fi
    
    # حذف فایل PID
    rm new_ten_minute_reporter.pid
    echo "فایل PID حذف شد."
fi

echo "سرویس تلگرام ساده متوقف شد."