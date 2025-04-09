#!/bin/bash

# اجرای سرویس تلگرام با قابلیت اطمینان بالا
echo "شروع سرویس تلگرام با قابلیت اطمینان بالا..."

# حذف لاگ‌های قبلی (اختیاری)
rm -f reliable_telegram.log

# اجرای اسکریپت در پس‌زمینه
nohup python reliable_telegram_service.py > reliable_telegram_console.log 2>&1 &

# ذخیره شناسه فرآیند
echo $! > reliable_telegram.pid

echo "سرویس تلگرام با شناسه $! شروع به کار کرد."
echo "برای مشاهده لاگ‌ها از دستور زیر استفاده کنید:"
echo "  cat reliable_telegram.log"
echo "برای توقف سرویس از دستور زیر استفاده کنید:"
echo "  ./توقف_تلگرام_قابل_اطمینان.sh"