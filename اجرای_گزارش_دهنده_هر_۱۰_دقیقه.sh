#!/bin/bash

# اسکریپت راه‌اندازی گزارش‌دهنده هر ۱۰ دقیقه
echo "در حال راه‌اندازی سرویس گزارش‌دهنده هر ۱۰ دقیقه..."

# بررسی وجود فایل PID
if [ -f "ten_minute_telegram_sender.pid" ]; then
    pid=$(cat ten_minute_telegram_sender.pid | python3 -c "import json,sys; print(json.load(sys.stdin).get('pid', 0))")
    if ps -p $pid > /dev/null; then
        echo "سرویس قبلاً در حال اجراست (PID: $pid)"
        echo "برای راه‌اندازی مجدد، ابتدا سرویس را متوقف کنید:"
        echo "./توقف_گزارش_دهنده_هر_۱۰_دقیقه.sh"
        exit 1
    else
        echo "فایل PID قدیمی یافت شد. در حال حذف..."
        rm ten_minute_telegram_sender.pid
    fi
fi

# راه‌اندازی سرویس در پس‌زمینه
nohup python3 ten_minute_telegram_sender.py > ten_minute_telegram_sender.log 2>&1 &

echo "سرویس گزارش‌دهنده با موفقیت راه‌اندازی شد!"
echo "برای مشاهده لاگ‌ها:"
echo "cat ten_minute_telegram_sender.log"
echo "برای توقف سرویس:"
echo "./توقف_گزارش_دهنده_هر_۱۰_دقیقه.sh"