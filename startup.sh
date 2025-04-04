#!/bin/bash

# اسکریپت راه‌اندازی ربات تلگرام
# این اسکریپت در زمان شروع برنامه اجرا می‌شود
# و یک پیام تست ارسال می‌کند و همچنین گزارش‌های دوره‌ای را راه‌اندازی می‌کند

echo "$(date) - شروع اجرای اسکریپت راه‌اندازی" > startup.log

# ارسال پیام تست
echo "$(date) - ارسال پیام تست تلگرام..." >> startup.log
python telegram_reporter.py test >> startup.log 2>&1

# ارسال گزارش دوره‌ای
echo "$(date) - ارسال گزارش دوره‌ای اولیه..." >> startup.log
python telegram_reporter.py >> startup.log 2>&1

# ارسال تحلیل تکنیکال بیت‌کوین
echo "$(date) - ارسال تحلیل تکنیکال بیت‌کوین..." >> startup.log
python telegram_reporter.py technical BTC/USDT >> startup.log 2>&1

# ارسال تحلیل تکنیکال اتریوم
echo "$(date) - ارسال تحلیل تکنیکال اتریوم..." >> startup.log
python telegram_reporter.py technical ETH/USDT >> startup.log 2>&1

# ارسال گزارش کلی بازار
echo "$(date) - ارسال گزارش کلی بازار..." >> startup.log
python telegram_reporter.py market >> startup.log 2>&1

echo "$(date) - پایان اجرای اسکریپت راه‌اندازی" >> startup.log
