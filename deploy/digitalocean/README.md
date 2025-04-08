# راهنمای استقرار ربات روی دیجیتال اوشن

## پیش‌نیازها

1. یک دراپلت دیجیتال اوشن با اوبونتو 20.04 یا 22.04
2. دسترسی SSH به سرور
3. توکن بات تلگرام و شناسه چت

## مراحل نصب دستی

### 1. اتصال به سرور

با استفاده از SSH به سرور متصل شوید:

```bash
ssh root@your_server_ip
```

### 2. دانلود فایل‌های پروژه

```bash
git clone https://github.com/YOUR_USERNAME/crypto_telegram_bot.git /root/crypto_bot
cd /root/crypto_bot
```

### 3. تنظیم متغیرهای محیطی

فایل `.env` را ایجاد کنید:

```bash
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token
DEFAULT_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_api_key
EOF
```

### 4. نصب پیش‌نیازها

```bash
apt update && apt upgrade -y
apt install -y python3-pip python3-venv supervisor
```

### 5. ایجاد محیط مجازی و نصب وابستگی‌ها

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. تنظیم سرویس Supervisor

فایل کانفیگ Supervisor را ایجاد کنید:

```bash
cat > /etc/supervisor/conf.d/crypto_bot.conf << EOF
[program:crypto_bot]
command=/root/crypto_bot/venv/bin/python /root/crypto_bot/scheduler.py
directory=/root/crypto_bot
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/crypto_bot.log
stderr_logfile=/var/log/crypto_bot_error.log
environment=PATH="/root/crypto_bot/venv/bin"

[program:crypto_telegram_reporter]
command=/root/crypto_bot/venv/bin/python /root/crypto_bot/ten_minute_scheduler.py
directory=/root/crypto_bot
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/crypto_telegram.log
stderr_logfile=/var/log/crypto_telegram_error.log
environment=PATH="/root/crypto_bot/venv/bin"
EOF
```

### 7. راه‌اندازی سرویس‌ها

```bash
supervisorctl reread
supervisorctl update
```

## استفاده از اسکریپت خودکار

می‌توانید از اسکریپت نصب خودکار استفاده کنید:

```bash
# تنظیم متغیرهای محیطی
export TELEGRAM_BOT_TOKEN="your_bot_token"
export DEFAULT_CHAT_ID="your_chat_id"
export OPENAI_API_KEY="your_openai_api_key"

# اجرای اسکریپت نصب
bash deploy/digitalocean/install_bot.sh
```

## مدیریت سرویس‌ها

### مشاهده وضعیت

```bash
supervisorctl status
```

### راه‌اندازی مجدد

```bash
supervisorctl restart crypto_bot
supervisorctl restart crypto_telegram_reporter
```

### توقف

```bash
supervisorctl stop crypto_bot
supervisorctl stop crypto_telegram_reporter
```

## مزایای دیجیتال اوشن برای کاربران کانادایی

1. دارای مرکز داده در تورنتو با تأخیر کم
2. قیمت مناسب (از 4 دلار در ماه)
3. پهنای باند بالا
4. پشتیبانی از زبان انگلیسی
5. پرداخت با کارت‌های بین‌المللی