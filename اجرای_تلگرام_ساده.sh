#!/bin/bash

# اسکریپت ساده برای اجرای سرویس تلگرام با استفاده از روش HTTP ساده
# این اسکریپت سرویس گزارش‌دهی ساده تلگرام را اجرا می‌کند

# تنظیم متغیرهای محیطی مورد نیاز
export TELEGRAM_BOT_TOKEN="7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk"
export DEFAULT_CHAT_ID="722627622"

echo "شروع سرویس تلگرام ساده..."

# بررسی وجود فایل‌های مورد نیاز
if [ ! -f "simple_telegram_sender.py" ]; then
    echo "خطا: فایل simple_telegram_sender.py یافت نشد!"
    exit 1
fi

if [ ! -f "simple_telegram_formatter.py" ]; then
    echo "خطا: فایل simple_telegram_formatter.py یافت نشد!"
    exit 1
fi

if [ ! -f "new_ten_minute_reporter.py" ]; then
    echo "خطا: فایل new_ten_minute_reporter.py یافت نشد!"
    exit 1
fi

# بررسی وجود فایل PID
if [ -f "new_ten_minute_reporter.pid" ]; then
    PID=$(cat new_ten_minute_reporter.pid)
    if ps -p $PID > /dev/null; then
        echo "سرویس تلگرام ساده در حال حاضر در حال اجراست (PID: $PID)"
        echo "برای توقف سرویس از دستور 'bash توقف_تلگرام_ساده.sh' استفاده کنید"
        exit 1
    else
        echo "فایل PID قدیمی پیدا شد، اما فرآیند فعال نیست. حذف فایل PID قدیمی..."
        rm new_ten_minute_reporter.pid
    fi
fi

# اجرای تست اولیه
echo "ارسال پیام تست اولیه..."
python3 simple_telegram_sender.py test

if [ $? -ne 0 ]; then
    echo "خطا در ارسال پیام تست!"
    exit 1
fi

# ارسال پیام تست فرمت شده
echo "ارسال پیام تست با قالب‌بندی..."
python3 simple_telegram_formatter.py test

if [ $? -ne 0 ]; then
    echo "خطا در ارسال پیام تست فرمت شده!"
    exit 1
fi

# اجرای سرویس اصلی در پس‌زمینه
echo "اجرای سرویس گزارش‌دهی تلگرام..."
nohup python3 new_ten_minute_reporter.py > new_ten_minute_reporter.log 2>&1 &

PID=$!
echo "سرویس تلگرام ساده با موفقیت شروع شد با PID: $PID"
echo $PID > new_ten_minute_reporter.pid
echo "لاگ‌ها در فایل new_ten_minute_reporter.log ذخیره می‌شوند"
echo "برای توقف سرویس از دستور 'bash توقف_تلگرام_ساده.sh' استفاده کنید"

# نمایش لاگ‌های اولیه
echo ""
echo "بخشی از لاگ‌ها:"
echo "----------------"
sleep 2  # انتظار برای ایجاد فایل لاگ
tail -n 15 new_ten_minute_reporter.log
echo "----------------"
echo ""
echo "برای مشاهده لاگ‌ها به صورت زنده:"
echo "tail -f new_ten_minute_reporter.log"