#!/bin/bash

# اسکریپت راه‌اندازی سرویس گزارش‌دهنده ۱۰ دقیقه‌ای تلگرام
# این اسکریپت برای سرور‌های Linux طراحی شده است
# بر روی Replit، از اسکریپت اجرای_گزارش_دهنده_۱۰_دقیقه‌ای.sh استفاده کنید

# مسیر کامل به فایل‌های پروژه
PROJECT_DIR=$(pwd)
REPORTER_SCRIPT="$PROJECT_DIR/ten_minute_reporter.py"
SERVICE_NAME="ten_minute_reporter"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# بررسی دسترسی روت
if [ "$(id -u)" -ne 0 ]; then
    echo "این اسکریپت نیاز به دسترسی روت دارد. لطفاً با sudo اجرا کنید."
    exit 1
fi

# بررسی وجود فایل اسکریپت
if [ ! -f "$REPORTER_SCRIPT" ]; then
    echo "خطا: فایل اسکریپت گزارش‌دهنده در مسیر $REPORTER_SCRIPT یافت نشد."
    exit 1
fi

# ایجاد فایل سرویس systemd
echo "ایجاد فایل سرویس systemd در $SERVICE_FILE..."
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Ten Minute Telegram Crypto Reporter Service
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$(which python3) $REPORTER_SCRIPT
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=$SERVICE_NAME
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# بروزرسانی سرویس‌ها
echo "بروزرسانی سرویس‌های systemd..."
systemctl daemon-reload

# فعال‌سازی سرویس
echo "فعال‌سازی سرویس $SERVICE_NAME..."
systemctl enable $SERVICE_NAME

# شروع سرویس
echo "شروع سرویس $SERVICE_NAME..."
systemctl start $SERVICE_NAME

# بررسی وضعیت
echo "بررسی وضعیت سرویس..."
systemctl status $SERVICE_NAME

echo
echo "سرویس گزارش‌دهنده ۱۰ دقیقه‌ای با موفقیت نصب و راه‌اندازی شد."
echo "برای بررسی وضعیت: systemctl status $SERVICE_NAME"
echo "برای مشاهده لاگ‌ها: journalctl -u $SERVICE_NAME -f"
echo "برای توقف سرویس: systemctl stop $SERVICE_NAME"
echo "برای راه‌اندازی مجدد: systemctl restart $SERVICE_NAME"