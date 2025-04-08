#!/bin/bash

# اسکریپت استقرار ربات روی Fly.io

echo "شروع استقرار ربات روی Fly.io..."

# کپی فایل‌های مورد نیاز
echo "کپی فایل‌های پروژه..."
mkdir -p /tmp/fly-deploy
cp -r ./* /tmp/fly-deploy
cp deploy/fly/* /tmp/fly-deploy/

cd /tmp/fly-deploy

# بررسی نصب flyctl
if ! command -v flyctl &> /dev/null; then
    echo "نصب Flyctl..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/runner/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

# ورود به حساب Fly.io (نیاز به توکن API دارد)
echo "ورود به Fly.io..."
if [ -z "$FLY_API_TOKEN" ]; then
    echo "خطا: متغیر محیطی FLY_API_TOKEN تنظیم نشده است."
    echo "لطفاً با دستور زیر در ترمینال خود وارد شوید:"
    echo "flyctl auth login"
    exit 1
fi

flyctl auth token "$FLY_API_TOKEN"

# ایجاد برنامه (اگر از قبل وجود نداشته باشد)
echo "ایجاد برنامه روی Fly.io..."
flyctl apps create crypto-telegram-bot --json || true

# تنظیم متغیرهای محیطی
echo "تنظیم متغیرهای محیطی..."
flyctl secrets set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
flyctl secrets set DEFAULT_CHAT_ID="$DEFAULT_CHAT_ID"

# استقرار
echo "استقرار برنامه..."
flyctl deploy --remote-only

echo "استقرار با موفقیت انجام شد!"
echo "برای مشاهده لاگ‌های برنامه:"
echo "flyctl logs"
