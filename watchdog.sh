#!/bin/bash

# اسکریپت نگهبان برای اطمینان از اجرای مداوم scheduler.py
# این اسکریپت را می‌توان با cron هر 5 دقیقه اجرا کرد تا مطمئن شد که همیشه scheduler.py در حال اجراست

LOG_FILE="watchdog.log"

echo "$(date) - شروع بررسی وضعیت scheduler.py" >> $LOG_FILE

# بررسی اینکه آیا فرآیند scheduler.py در حال اجراست
if pgrep -f "python scheduler.py" > /dev/null; then
    echo "$(date) - scheduler.py در حال اجراست. نیازی به اقدام نیست." >> $LOG_FILE
else
    echo "$(date) - scheduler.py در حال اجرا نیست! راه‌اندازی مجدد..." >> $LOG_FILE
    
    # توقف هر نمونه قبلی که ممکن است هنوز در حال اجرا باشد اما پاسخگو نیست
    pkill -f "python scheduler.py" >> $LOG_FILE 2>&1 || echo "هیچ فرآیندی برای توقف وجود ندارد"
    
    # راه‌اندازی مجدد scheduler.py
    cd "$(dirname "$0")"  # رفتن به دایرکتوری اسکریپت
    nohup python scheduler.py >> scheduler.log 2>&1 &
    
    # بررسی موفقیت راه‌اندازی
    sleep 2
    if pgrep -f "python scheduler.py" > /dev/null; then
        echo "$(date) - scheduler.py با موفقیت مجدداً راه‌اندازی شد." >> $LOG_FILE
    else
        echo "$(date) - خطا در راه‌اندازی مجدد scheduler.py!" >> $LOG_FILE
    fi
fi

# بررسی وضعیت فایل لاگ scheduler.log
LAST_LOG_TIME=$(stat -c %Y scheduler.log 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
TIME_DIFF=$((CURRENT_TIME - LAST_LOG_TIME))

# اگر بیش از 10 دقیقه از آخرین به‌روزرسانی لاگ گذشته باشد، هشدار می‌دهیم
if [ $TIME_DIFF -gt 600 ]; then
    echo "$(date) - هشدار: فایل لاگ scheduler.log بیش از 10 دقیقه به‌روزرسانی نشده است!" >> $LOG_FILE
    
    # راه‌اندازی مجدد در این حالت هم
    echo "$(date) - راه‌اندازی مجدد scheduler.py به دلیل عدم فعالیت..." >> $LOG_FILE
    pkill -f "python scheduler.py" >> $LOG_FILE 2>&1 || echo "هیچ فرآیندی برای توقف وجود ندارد"
    sleep 1
    nohup python scheduler.py >> scheduler.log 2>&1 &
fi

echo "$(date) - پایان بررسی وضعیت scheduler.py" >> $LOG_FILE
echo "-------------------------------------------" >> $LOG_FILE
