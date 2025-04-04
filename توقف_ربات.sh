#!/bin/bash

# اسکریپت توقف ربات تلگرام
# این اسکریپت سرویس پس‌زمینه ربات را متوقف می‌کند

# محل پروژه را به عنوان دایرکتوری فعلی تنظیم کنید
cd "$(dirname "$0")"

# ثبت لاگ شروع
echo "$(date) - شروع توقف ربات ارز دیجیتال" > توقف_ربات.log

# توقف screen اگر وجود دارد
if command -v screen >/dev/null 2>&1; then
    echo "$(date) - توقف screen..." >> توقف_ربات.log
    screen -S crypto_scheduler -X quit >/dev/null 2>&1
    echo "$(date) - screen با موفقیت متوقف شد." >> توقف_ربات.log
fi

# توقف فرآیند اگر PID وجود دارد
if [ -f scheduler.pid ]; then
    echo "$(date) - توقف فرآیند با شناسه $(cat scheduler.pid)..." >> توقف_ربات.log
    if kill -0 $(cat scheduler.pid) >/dev/null 2>&1; then
        kill $(cat scheduler.pid) >/dev/null 2>&1
        echo "$(date) - فرآیند با موفقیت متوقف شد." >> توقف_ربات.log
    else
        echo "$(date) - فرآیند قبلاً متوقف شده است." >> توقف_ربات.log
    fi
    rm -f scheduler.pid
else
    echo "$(date) - فایل PID پیدا نشد. ربات احتمالاً در حال اجرا نیست." >> توقف_ربات.log
fi

# ارسال پیام توقف به تلگرام
echo "$(date) - ارسال پیام توقف به تلگرام..." >> توقف_ربات.log
python -c "
import sys
import os
from datetime import datetime
sys.path.append(os.getcwd())
try:
    from crypto_bot.telegram_service import send_telegram_message
    message = f\"🔴 ربات ارز دیجیتال متوقف شد\\n\\nزمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\nربات با دستور کاربر متوقف شد و دیگر گزارش‌های دوره‌ای ارسال نخواهد شد.\"
    send_telegram_message(message)
    print('پیام توقف با موفقیت ارسال شد.')
except Exception as e:
    print(f'خطا در ارسال پیام توقف: {str(e)}')
" >> توقف_ربات.log 2>&1

echo "$(date) - پایان توقف ربات ارز دیجیتال" >> توقف_ربات.log
echo ""
echo "ربات ارز دیجیتال با موفقیت متوقف شد و دیگر گزارش‌های دوره‌ای ارسال نخواهد شد."
