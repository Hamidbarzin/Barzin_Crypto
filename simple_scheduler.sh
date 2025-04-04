#!/bin/bash

# اسکریپت زمان‌بندی ساده برای اجرای گزارش‌دهی دوره‌ای
# این اسکریپت باید به صورت نامحدود اجرا شود تا گزارش‌ها را به طور منظم ارسال کند

LOG_FILE="simple_scheduler.log"

echo "$(date) - شروع اجرای برنامه زمان‌بندی ساده" | tee -a $LOG_FILE

# تابع ارسال گزارش دوره‌ای
function send_periodic_report() {
    echo "$(date) - در حال ارسال گزارش دوره‌ای..." | tee -a $LOG_FILE
    python telegram_reporter.py >> $LOG_FILE 2>&1
    echo "$(date) - گزارش دوره‌ای ارسال شد." | tee -a $LOG_FILE
}

# تابع ارسال پیام تست
function send_test_message() {
    echo "$(date) - در حال ارسال پیام تست..." | tee -a $LOG_FILE
    python telegram_reporter.py test >> $LOG_FILE 2>&1
    echo "$(date) - پیام تست ارسال شد." | tee -a $LOG_FILE
}

# ارسال یک پیام تست برای اطمینان از عملکرد صحیح سیستم
send_test_message

# حلقه اصلی برنامه
echo "$(date) - برنامه زمان‌بندی فعال شد. گزارش‌ها هر 30 دقیقه ارسال خواهند شد." | tee -a $LOG_FILE
echo "$(date) - برای توقف برنامه، کلید Ctrl+C را فشار دهید." | tee -a $LOG_FILE

# گزارش دوره‌ای اولیه را ارسال می‌کنیم
send_periodic_report

COUNTER=0
try_count=0
while true; do
    try_count=$((try_count + 1))
    
    # هر 5 دقیقه تلاش می‌کنیم تا اطلاع حاصل کنیم که برنامه هنوز در حال اجراست
    if [ $try_count -ge 5 ]; then
        echo "$(date) - تایید ادامه اجرای برنامه" | tee -a $LOG_FILE
        try_count=0
    fi

    # هر 30 دقیقه (counter=30) گزارش دوره‌ای ارسال می‌کنیم
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -ge 30 ]; then
        send_periodic_report
        COUNTER=0
    fi
    
    # انتظار 1 دقیقه تا چک مجدد
    sleep 60
done