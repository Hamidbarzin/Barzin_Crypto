#!/bin/bash

echo "شروع سرویس تلگرام Crypto Barzin..."

# اجرای اسکریپت تلگرام
echo "ارسال پیام تست اولیه..."
python telegram_test.py

# اطلاعات راهنما
echo ""
echo "سرویس تلگرام با موفقیت راه‌اندازی شد."
echo "برای استفاده از سرویس به صورت خودکار، دستور زیر را اجرا کنید:"
echo "  python run_telegram_workflow.py"
echo ""
echo "برای ارسال پیام‌های تکی، از دستورات زیر استفاده کنید:"
echo "  python simple_telegram_sender.py test      # ارسال پیام تست"
echo "  python simple_telegram_sender.py prices    # ارسال گزارش قیمت‌ها"
echo "  python simple_telegram_sender.py info      # دریافت اطلاعات بات"
echo ""
echo "برای اطلاعات بیشتر، فایل راهنمای_ارسال_تلگرام.md را مطالعه کنید."