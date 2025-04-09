#!/bin/bash
# اسکریپت اجرای ورک‌فلوی تلگرام در Replit

echo "در حال راه‌اندازی ورک‌فلوی تلگرام..."

# حذف پیدی قدیمی اگر وجود داشته باشد
pid_file="telegram_replit_workflow.pid"
if [ -f "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if ps -p $pid > /dev/null 2>&1; then
        echo "در حال متوقف کردن فرآیند قبلی با PID $pid..."
        kill $pid
    fi
    rm -f "$pid_file"
fi

# اجرای اسکریپت در پس‌زمینه
nohup python3 telegram_replit_workflow.py > telegram_replit_workflow.log 2>&1 &
new_pid=$!
echo $new_pid > "$pid_file"

echo "ورک‌فلوی تلگرام با PID $new_pid شروع شد."
echo "لاگ‌ها در فایل telegram_replit_workflow.log ذخیره می‌شوند."