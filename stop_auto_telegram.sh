#!/bin/bash
# اسکریپت توقف سرویس ارسال خودکار پیام‌های تلگرام

echo "در حال متوقف کردن سرویس ارسال خودکار پیام تلگرام..."

# بررسی وجود فایل PID
PID_FILE="auto_telegram_sender.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "در حال متوقف کردن سرویس با PID $PID..."
        kill "$PID"
        
        # انتظار برای متوقف شدن
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "سرویس هنوز متوقف نشده... اعمال سیگنال SIGKILL"
            kill -9 "$PID"
            sleep 1
        fi
        
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "خطا: نمی‌توان سرویس را متوقف کرد"
            exit 1
        else
            echo "سرویس با موفقیت متوقف شد"
        fi
    else
        echo "سرویس در حال اجرا نیست"
    fi
    
    # پاکسازی فایل PID
    rm -f "$PID_FILE"
    echo "فایل PID پاکسازی شد"
else
    echo "سرویس در حال اجرا نیست (فایل PID یافت نشد)"
fi