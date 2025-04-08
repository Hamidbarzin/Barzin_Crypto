#!/bin/bash

# اسکریپت راه‌اندازی خودکار برای اجرای ربات در زمان شروع سیستم
# این فایل نسخه فارسی startup.sh است

echo "شروع راه‌اندازی خودکار ربات تلگرام در تاریخ $(date)" > راه‌اندازی_خودکار.log
echo "----------------------------------------" >> راه‌اندازی_خودکار.log

# بررسی وجود فایل‌های لازم
if [ ! -f "ten_minute_scheduler.py" ]; then
    echo "خطا: فایل ten_minute_scheduler.py یافت نشد!" >> راه‌اندازی_خودکار.log
    exit 1
fi

if [ ! -f "enhanced_telegram_reporter.py" ]; then
    echo "خطا: فایل enhanced_telegram_reporter.py یافت نشد!" >> راه‌اندازی_خودکار.log
    exit 1
fi

# توقف هر نمونه در حال اجرا
echo "در حال توقف نمونه‌های قبلی..." >> راه‌اندازی_خودکار.log
pids=$(ps aux | grep "ten_minute_scheduler.py" | grep -v grep | awk '{print $2}')
if [ -n "$pids" ]; then
    for p in $pids; do
        echo "توقف فرآیند $p..." >> راه‌اندازی_خودکار.log
        kill -9 $p 2>/dev/null
    done
    echo "فرآیندهای قبلی متوقف شدند." >> راه‌اندازی_خودکار.log
else
    echo "هیچ فرآیند قبلی یافت نشد." >> راه‌اندازی_خودکار.log
fi

# حذف فایل‌های PID قدیمی
rm -f ten_minute_scheduler.pid 2>/dev/null

echo "در حال راه‌اندازی ربات ارسال گزارش..." >> راه‌اندازی_خودکار.log

# راه‌اندازی اسکریپت زمان‌بندی
PYTHONUNBUFFERED=1 nohup python ten_minute_scheduler.py > ten_minute_scheduler.log 2>&1 &
echo $! > ten_minute_scheduler.pid

echo "ربات با شناسه فرآیند $(cat ten_minute_scheduler.pid) راه‌اندازی شد." >> راه‌اندازی_خودکار.log
echo "برای مشاهده وضعیت: tail -f ten_minute_scheduler.log" >> راه‌اندازی_خودکار.log
echo "پایان راه‌اندازی خودکار در تاریخ $(date)" >> راه‌اندازی_خودکار.log
echo "----------------------------------------" >> راه‌اندازی_خودکار.log

# ارسال یک پیام تایید به تلگرام
echo "در حال ارسال پیام اطلاع‌رسانی به تلگرام..." >> راه‌اندازی_خودکار.log
python -c "
import os
import sys
from datetime import datetime
try:
    from crypto_bot.telegram_service import send_telegram_message
    chat_id = os.environ.get('DEFAULT_CHAT_ID', '722627622')
    message = f'''🤖 *راه‌اندازی مجدد ربات*
    
ربات گزارش‌دهی با موفقیت راه‌اندازی شد.
زمان راه‌اندازی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

گزارش‌های دوره‌ای هر ۱۰ دقیقه ارسال خواهند شد.
وضعیت سیستم هر ۶ ساعت ارسال می‌شود.

این پیام به صورت خودکار پس از راه‌اندازی سیستم ارسال شده است.
    '''
    result = send_telegram_message(chat_id, message)
    print(f'نتیجه ارسال پیام راه‌اندازی: {result}')
except Exception as e:
    print(f'خطا در ارسال پیام اطلاع‌رسانی: {str(e)}')
" >> راه‌اندازی_خودکار.log 2>&1

echo "اسکریپت راه‌اندازی با موفقیت اجرا شد."
