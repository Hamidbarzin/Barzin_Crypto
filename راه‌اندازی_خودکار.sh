#!/bin/bash

# اسکریپت راه‌اندازی خودکار ربات تلگرام
# این اسکریپت یک سرویس پس‌زمینه برای ارسال گزارش‌های دوره‌ای ایجاد می‌کند
# و با کمک screen می‌توان ربات را به طور مداوم اجرا کرد

# تنظیم زبان خروجی
export LANG=fa_IR.UTF-8 2>/dev/null || export LANG=C.UTF-8 2>/dev/null || export LANG=en_US.UTF-8

# محل پروژه را به عنوان دایرکتوری فعلی تنظیم کنید
cd "$(dirname "$0")"

# ثبت لاگ شروع
echo "$(date) - شروع راه‌اندازی خودکار ربات ارز دیجیتال" > راه‌اندازی_خودکار.log

# ارسال پیام تست
echo "$(date) - ارسال پیام تست تلگرام..." >> راه‌اندازی_خودکار.log
python telegram_reporter.py test >> راه‌اندازی_خودکار.log 2>&1

# ارسال گزارش اولیه
echo "$(date) - ارسال گزارش دوره‌ای اولیه..." >> راه‌اندازی_خودکار.log
python telegram_reporter.py >> راه‌اندازی_خودکار.log 2>&1

# راه‌اندازی زمان‌بندی با screen
if command -v screen >/dev/null 2>&1; then
    echo "$(date) - راه‌اندازی زمان‌بندی با screen..." >> راه‌اندازی_خودکار.log
    # بررسی اگر screen قبلی وجود دارد، آن را متوقف کن
    screen -wipe crypto_scheduler >/dev/null 2>&1
    screen -S crypto_scheduler -X quit >/dev/null 2>&1
    
    # راه‌اندازی screen جدید
    screen -dmS crypto_scheduler bash -c "while true; do ./cron_report.sh; sleep 1800; done"
    
    echo "$(date) - زمان‌بندی با موفقیت راه‌اندازی شد. برای مشاهده وضعیت، دستور 'screen -r crypto_scheduler' را اجرا کنید." >> راه‌اندازی_خودکار.log
    echo "زمان‌بندی با موفقیت راه‌اندازی شد!"
    echo "کامندهای مفید:"
    echo "screen -ls                    # مشاهده لیست screen های در حال اجرا"
    echo "screen -r crypto_scheduler    # اتصال به screen زمان‌بندی"
    echo "screen -S crypto_scheduler -X quit    # توقف زمان‌بندی"
else
    echo "$(date) - برنامه screen پیدا نشد. راه‌اندازی با روش جایگزین..." >> راه‌اندازی_خودکار.log
    
    # توقف زمان‌بندی قبلی اگر وجود دارد
    if [ -f scheduler.pid ]; then
        if kill -0 $(cat scheduler.pid) >/dev/null 2>&1; then
            kill $(cat scheduler.pid) >/dev/null 2>&1
            echo "$(date) - زمان‌بندی قبلی متوقف شد." >> راه‌اندازی_خودکار.log
        fi
    fi
    
    # راه‌اندازی زمان‌بندی با nohup
    nohup bash -c "while true; do ./cron_report.sh; sleep 1800; done" > scheduler.log 2>&1 &
    echo $! > scheduler.pid
    
    echo "$(date) - زمان‌بندی با موفقیت راه‌اندازی شد با شناسه فرآیند $(cat scheduler.pid)" >> راه‌اندازی_خودکار.log
    echo "زمان‌بندی با موفقیت راه‌اندازی شد با شناسه فرآیند $(cat scheduler.pid)!"
    echo "کامندهای مفید:"
    echo "cat scheduler.log             # مشاهده لاگ زمان‌بندی"
    echo "kill $(cat scheduler.pid)    # توقف زمان‌بندی"
fi

echo "$(date) - پایان راه‌اندازی خودکار ربات ارز دیجیتال" >> راه‌اندازی_خودکار.log
echo ""
echo "ربات ارز دیجیتال با موفقیت راه‌اندازی شد و هر 30 دقیقه یک بار گزارش به تلگرام ارسال می‌شود."
echo "برای توقف ربات، می‌توانید از یکی از کامندهای بالا استفاده کنید."
