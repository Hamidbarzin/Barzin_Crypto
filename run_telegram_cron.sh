#!/bin/bash
# اسکریپت اجرای کرون تلگرام هر ۱۰ دقیقه

echo "در حال راه‌اندازی کرون تلگرام..."

PID_FILE="telegram_cron.pid"

# بررسی وجود فرآیند قبلی و متوقف کردن آن
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if ps -p "$OLD_PID" > /dev/null; then
    echo "متوقف کردن فرآیند قبلی با PID $OLD_PID"
    kill "$OLD_PID" 2>/dev/null
  fi
  rm -f "$PID_FILE"
fi

# اجرای حلقه بی‌نهایت در پس‌زمینه
nohup bash -c '
  while true; do
    ./telegram_cron.sh >> telegram_cron.log 2>&1
    echo "انتظار برای ۱۰ دقیقه بعدی..."
    sleep 600
  done
' > /dev/null 2>&1 &

NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"
echo "کرون تلگرام با PID $NEW_PID شروع شد. لاگ‌ها در فایل telegram_cron.log ذخیره می‌شوند."