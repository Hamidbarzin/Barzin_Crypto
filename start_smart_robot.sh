#!/bin/bash
# اسکریپت راه‌اندازی ربات تحلیل هوشمند ارزهای دیجیتال

# تنظیم تاریخ و زمان
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# ایجاد فایل لاگ
LOG_FILE="smart_robot.log"
echo "[$DATE] شروع راه‌اندازی ربات تحلیل هوشمند ارزهای دیجیتال" > $LOG_FILE

# بررسی وجود پایتون
if ! command -v python3 &> /dev/null; then
    echo "[$DATE] خطا: پایتون نصب نشده است" >> $LOG_FILE
    echo "لطفاً پایتون 3 را نصب کنید" >> $LOG_FILE
    exit 1
fi

# بررسی وجود کلید API هوش مصنوعی OpenAI
if [ -z "$OPENAI_API_KEY" ]; then
    echo "[$DATE] هشدار: کلید API هوش مصنوعی تنظیم نشده است" >> $LOG_FILE
    echo "برای استفاده از امکانات هوش مصنوعی، لطفاً متغیر محیطی OPENAI_API_KEY را تنظیم کنید" >> $LOG_FILE
    echo "export OPENAI_API_KEY=\"کلید-API-خود-را-اینجا-قرار-دهید\"" >> $LOG_FILE
fi

# اجرای تست اولیه
echo "[$DATE] در حال اجرای تست اولیه..." >> $LOG_FILE
python3 telegram_smart_reporter.py --test

# بررسی نتیجه اجرای تست
if [ $? -ne 0 ]; then
    echo "[$DATE] خطا: اجرای تست اولیه با شکست مواجه شد" >> $LOG_FILE
    exit 1
fi

# اجرای اسکریپت زمان‌بندی در پس‌زمینه
echo "[$DATE] در حال راه‌اندازی زمان‌بندی هوشمند در پس‌زمینه..." >> $LOG_FILE

# کشتن فرآیندهای قبلی (اگر وجود داشته باشد)
pkill -f "python3 smart_scheduler.py" &> /dev/null

# اجرای اسکریپت جدید
nohup python3 smart_scheduler.py > smart_scheduler.log 2>&1 &

# ذخیره شناسه فرآیند
PID=$!
echo $PID > smart_scheduler.pid
echo "[$DATE] زمان‌بندی هوشمند با شناسه فرآیند $PID راه‌اندازی شد" >> $LOG_FILE

# بررسی اجرای موفقیت‌آمیز
sleep 2
if ps -p $PID > /dev/null; then
    echo "[$DATE] ربات تحلیل هوشمند ارزهای دیجیتال با موفقیت راه‌اندازی شد" >> $LOG_FILE
    echo "اطلاعات بیشتر در فایل smart_scheduler.log ذخیره می‌شود" >> $LOG_FILE
    
    echo "✅ ربات تحلیل هوشمند ارزهای دیجیتال با موفقیت راه‌اندازی شد"
    echo "شناسه فرآیند: $PID"
    echo "برای مشاهده وضعیت ربات از دستور زیر استفاده کنید:"
    echo "cat smart_scheduler.log"
    echo "برای توقف ربات از دستور زیر استفاده کنید:"
    echo "./stop_smart_robot.sh"
else
    echo "[$DATE] خطا: راه‌اندازی ربات با شکست مواجه شد" >> $LOG_FILE
    echo "❌ خطا: راه‌اندازی ربات با شکست مواجه شد"
    echo "لطفاً لاگ‌ها را بررسی کنید:"
    echo "cat $LOG_FILE"
    exit 1
fi
