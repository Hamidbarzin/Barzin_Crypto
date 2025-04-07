#!/bin/bash
# اسکریپت توقف ربات تحلیل هوشمند ارزهای دیجیتال

# تنظیم تاریخ و زمان
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# ایجاد فایل لاگ
LOG_FILE="smart_robot_stop.log"
echo "[$DATE] شروع توقف ربات تحلیل هوشمند ارزهای دیجیتال" > $LOG_FILE

# خواندن شناسه فرآیند
if [ -f "smart_scheduler.pid" ]; then
    PID=$(cat smart_scheduler.pid)
    echo "[$DATE] شناسه فرآیند یافت شد: $PID" >> $LOG_FILE
    
    # بررسی وجود فرآیند
    if ps -p $PID > /dev/null; then
        echo "[$DATE] در حال توقف فرآیند با شناسه $PID..." >> $LOG_FILE
        kill $PID
        sleep 2
        
        # بررسی موفقیت‌آمیز بودن توقف
        if ! ps -p $PID > /dev/null; then
            echo "[$DATE] ربات با موفقیت متوقف شد" >> $LOG_FILE
            echo "✅ ربات تحلیل هوشمند ارزهای دیجیتال با موفقیت متوقف شد"
            rm smart_scheduler.pid
        else
            echo "[$DATE] هشدار: ربات هنوز در حال اجراست، در حال استفاده از kill -9..." >> $LOG_FILE
            kill -9 $PID
            echo "✅ ربات تحلیل هوشمند ارزهای دیجیتال با اجبار متوقف شد"
            rm smart_scheduler.pid
        fi
    else
        echo "[$DATE] هشدار: فرآیندی با شناسه $PID یافت نشد" >> $LOG_FILE
        echo "⚠️ فرآیندی با شناسه $PID یافت نشد"
        echo "در حال جستجو برای فرآیندهای مشابه..."
        
        # جستجو برای فرآیندهای مشابه
        PIDS=$(pgrep -f "python3 smart_scheduler.py")
        if [ -n "$PIDS" ]; then
            echo "[$DATE] فرآیندهای مشابه یافت شد: $PIDS" >> $LOG_FILE
            echo "در حال توقف فرآیندهای مشابه..."
            pkill -f "python3 smart_scheduler.py"
            echo "✅ تمام فرآیندهای مرتبط با ربات متوقف شد"
        else
            echo "[$DATE] هیچ فرآیندی یافت نشد" >> $LOG_FILE
            echo "❌ هیچ فرآیند در حال اجرای رباتی یافت نشد"
        fi
        
        rm -f smart_scheduler.pid
    fi
else
    echo "[$DATE] هشدار: فایل PID یافت نشد" >> $LOG_FILE
    echo "⚠️ فایل شناسه فرآیند یافت نشد"
    echo "در حال جستجو برای فرآیندهای مشابه..."
    
    # جستجو برای فرآیندهای مشابه
    PIDS=$(pgrep -f "python3 smart_scheduler.py")
    if [ -n "$PIDS" ]; then
        echo "[$DATE] فرآیندهای مشابه یافت شد: $PIDS" >> $LOG_FILE
        echo "در حال توقف فرآیندهای مشابه..."
        pkill -f "python3 smart_scheduler.py"
        echo "✅ تمام فرآیندهای مرتبط با ربات متوقف شد"
    else
        echo "[$DATE] هیچ فرآیندی یافت نشد" >> $LOG_FILE
        echo "❌ هیچ فرآیند در حال اجرای رباتی یافت نشد"
    fi
fi

echo "[$DATE] پایان توقف ربات تحلیل هوشمند ارزهای دیجیتال" >> $LOG_FILE
