#!/bin/bash

# اسکریپت ارسال گزارش‌های دوره‌ای برای اجرا توسط cron
# این اسکریپت می‌تواند هر 30 دقیقه یک بار اجرا شود
# برای تنظیم cron می‌توانید از دستور زیر استفاده کنید:
# */30 * * * * /path/to/cron_report.sh > /tmp/cron_report.log 2>&1

# محل پروژه را به عنوان دایرکتوری فعلی تنظیم کنید
cd "$(dirname "$0")"

# لاگ‌گذاری
echo "$(date) - شروع اجرای اسکریپت گزارش‌های دوره‌ای" >> cron_report.log

# ارسال گزارش دوره‌ای کامل به تلگرام
echo "$(date) - ارسال گزارش دوره‌ای به تلگرام..." >> cron_report.log
python telegram_reporter.py >> cron_report.log 2>&1

# انتخاب تصادفی یک ارز از لیست برای تحلیل تکنیکال
COINS=("BTC/USDT" "ETH/USDT" "XRP/USDT" "BNB/USDT" "ADA/USDT" "SOL/USDT" "DOT/USDT" "DOGE/USDT")
RANDOM_INDEX=$((RANDOM % ${#COINS[@]}))
SELECTED_COIN=${COINS[$RANDOM_INDEX]}

# ارسال تحلیل تکنیکال برای ارز انتخاب شده
echo "$(date) - ارسال تحلیل تکنیکال برای $SELECTED_COIN..." >> cron_report.log
python telegram_reporter.py technical "$SELECTED_COIN" >> cron_report.log 2>&1

echo "$(date) - پایان اجرای اسکریپت گزارش‌های دوره‌ای" >> cron_report.log
