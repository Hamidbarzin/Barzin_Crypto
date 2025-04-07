# راهنمای انتقال ربات تحلیل ارز دیجیتال به سرور دائمی

## چرا باید ربات را به سرور دائمی منتقل کنیم؟

ربات تحلیل ارز دیجیتال برای ارائه بهترین عملکرد، نیاز به اجرای بدون وقفه دارد. در محیط‌هایی مانند Replit، به دلایل زیر امکان اجرای 24/7 وجود ندارد:

1. محدودیت‌های زمانی برای اجرای فرآیندهای پس‌زمینه (background processes)
2. خاموش شدن خودکار ربات پس از مدت زمان بی‌کاری
3. محدودیت منابع و زمان اجرا در حساب‌های رایگان

## گزینه‌های سرور دائمی

### 1. سرور مجازی خصوصی (VPS)

مناسب‌ترین گزینه برای اجرای ربات به صورت 24/7، استفاده از یک VPS لینوکسی است. برخی از گزینه‌های محبوب:

- **DigitalOcean**: پلن ساده با قیمت حدود $5-10 در ماه
- **Linode**: پلن ساده با قیمت حدود $5 در ماه
- **Vultr**: پلن ساده با قیمت حدود $3.50 در ماه
- **هتزنر (Hetzner)**: سرورهای اروپایی با قیمت مناسب (حدود €3 در ماه)

### 2. سرویس‌های ابری PaaS

- **Heroku**: دارای پلن رایگان محدود و پلن‌های پولی از $7 در ماه
- **Railway**: امکان اجرای ربات در محیط مدیریت شده با قیمت حدود $5-10 در ماه
- **Render**: مشابه Heroku با پلن‌های پولی از $7 در ماه

### 3. گزینه‌های اقتصادی دیگر

- **Oracle Cloud Free Tier**: سرور مجازی بسیار محدود اما رایگان به صورت دائمی
- **Google Cloud Platform**: $300 اعتبار رایگان برای 90 روز
- **Amazon AWS**: پلن‌های رایگان محدود برای 12 ماه

## مراحل انتقال به VPS لینوکسی

### 1. تهیه و راه‌اندازی VPS

1. یک حساب در یکی از سرویس‌های VPS ایجاد کنید
2. یک سرور مجازی با سیستم عامل Ubuntu 20.04 یا 22.04 راه‌اندازی کنید
3. با SSH به سرور متصل شوید:
   ```bash
   ssh root@آدرس_آی_پی_سرور
   ```

### 2. نصب پیش‌نیازها

```bash
# به‌روزرسانی لیست بسته‌ها
apt update && apt upgrade -y

# نصب پیش‌نیازهای اصلی
apt install -y python3 python3-pip python3-venv git screen tmux

# نصب کتابخانه‌های توسعه مورد نیاز
apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### 3. انتقال کد به سرور

**روش 1: استفاده از Git**
```bash
# ایجاد پوشه پروژه
mkdir -p /opt/crypto-bot
cd /opt/crypto-bot

# کلون کردن مخزن (اگر در گیت‌هاب یا سرویس مشابه قرار دارد)
git clone https://github.com/yourusername/crypto-bot.git .
```

**روش 2: انتقال مستقیم فایل‌ها**
```bash
# در کامپیوتر محلی، فایل‌ها را به صورت فشرده درآورید
tar -czvf crypto-bot.tar.gz ./crypto-bot

# انتقال فایل فشرده به سرور
scp crypto-bot.tar.gz root@آدرس_آی_پی_سرور:/opt/

# در سرور، فایل را از حالت فشرده خارج کنید
cd /opt
mkdir -p crypto-bot
tar -xzvf crypto-bot.tar.gz -C crypto-bot
cd crypto-bot
```

### 4. ایجاد محیط مجازی و نصب وابستگی‌ها

```bash
# ایجاد محیط مجازی
python3 -m venv venv

# فعال‌سازی محیط مجازی
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# یا نصب تک تک کتابخانه‌های مورد نیاز
pip install ccxt pandas numpy flask schedule python-telegram-bot
```

### 5. تنظیم متغیرهای محیطی

```bash
# ایجاد فایل تنظیمات محیطی
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DEFAULT_CHAT_ID=your_telegram_chat_id
OPENAI_API_KEY=your_openai_api_key
EOF

# اضافه کردن متغیرها به فایل راه‌اندازی سیستم
cat >> ~/.bashrc << 'EOF'

# Crypto Bot Environment Variables
export TELEGRAM_BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN /opt/crypto-bot/.env | cut -d '=' -f2)
export DEFAULT_CHAT_ID=$(grep DEFAULT_CHAT_ID /opt/crypto-bot/.env | cut -d '=' -f2)
export OPENAI_API_KEY=$(grep OPENAI_API_KEY /opt/crypto-bot/.env | cut -d '=' -f2)
EOF

# اعمال تغییرات
source ~/.bashrc
```

### 6. تست اولیه

```bash
# فعال‌سازی محیط مجازی
cd /opt/crypto-bot
source venv/bin/activate

# ارسال پیام تست
python -c "import simple_ai_mode; simple_ai_mode.send_test_message()"
```

### 7. راه‌اندازی با Screen یا Tmux

برای اجرای ربات در پس‌زمینه حتی پس از بستن اتصال SSH، از Screen یا Tmux استفاده کنید:

**استفاده از Screen**
```bash
# ایجاد یک جلسه Screen جدید
screen -S crypto-bot

# فعال‌سازی محیط مجازی
cd /opt/crypto-bot
source venv/bin/activate

# اجرای ربات
python smart_ai_scheduler.py

# جدا شدن از جلسه Screen: با فشردن Ctrl+A و سپس D
# اتصال مجدد به جلسه: 
# screen -r crypto-bot
```

**استفاده از Tmux**
```bash
# ایجاد یک جلسه Tmux جدید
tmux new -s crypto-bot

# فعال‌سازی محیط مجازی
cd /opt/crypto-bot
source venv/bin/activate

# اجرای ربات
python smart_ai_scheduler.py

# جدا شدن از جلسه Tmux: با فشردن Ctrl+B و سپس D
# اتصال مجدد به جلسه: 
# tmux attach -t crypto-bot
```

### 8. راه‌اندازی خودکار با سرویس systemd

برای اطمینان از راه‌اندازی خودکار ربات پس از راه‌اندازی مجدد سرور، یک سرویس systemd ایجاد کنید:

```bash
cat > /etc/systemd/system/crypto-bot.service << 'EOF'
[Unit]
Description=Cryptocurrency Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/crypto-bot
ExecStart=/opt/crypto-bot/venv/bin/python /opt/crypto-bot/smart_ai_scheduler.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=crypto-bot
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/opt/crypto-bot/.env

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی سرویس
systemctl enable crypto-bot.service

# شروع سرویس
systemctl start crypto-bot.service

# بررسی وضعیت
systemctl status crypto-bot.service
```

### 9. تنظیم Cron Job برای اطمینان از اجرای مداوم

برای اطمینان بیشتر، می‌توانید یک Cron Job تنظیم کنید که عملکرد ربات را به طور منظم بررسی کند:

```bash
# ویرایش فایل crontab
crontab -e

# اضافه کردن این خط برای بررسی هر 15 دقیقه
*/15 * * * * /opt/crypto-bot/check_bot.sh
```

و ایجاد اسکریپت بررسی:

```bash
cat > /opt/crypto-bot/check_bot.sh << 'EOF'
#!/bin/bash

# بررسی آیا فرآیند ربات در حال اجراست
if ! pgrep -f "python.*smart_ai_scheduler.py" > /dev/null; then
    # در صورت عدم اجرا، راه‌اندازی مجدد سرویس
    systemctl restart crypto-bot.service
    
    # ارسال اعلان
    source /opt/crypto-bot/venv/bin/activate
    python -c "import simple_ai_mode; simple_ai_mode.send_test_message('ربات مجدداً راه‌اندازی شد.')"
fi
EOF

# اعطای دسترسی اجرا به اسکریپت
chmod +x /opt/crypto-bot/check_bot.sh
```

## راهنمای عیب‌یابی در سرور

### مشکل: پیام‌ها ارسال نمی‌شوند
- بررسی متغیرهای محیطی:
  ```bash
  echo $TELEGRAM_BOT_TOKEN
  echo $DEFAULT_CHAT_ID
  ```
- اطمینان از دسترسی به اینترنت:
  ```bash
  ping api.telegram.org
  ```
- تست دستی ارسال پیام:
  ```bash
  source venv/bin/activate
  python -c "import simple_ai_mode; simple_ai_mode.send_test_message()"
  ```

### مشکل: ربات متوقف می‌شود
- بررسی لاگ‌ها:
  ```bash
  journalctl -u crypto-bot.service
  ```
- بررسی مصرف منابع:
  ```bash
  top
  free -h
  df -h
  ```

### مشکل: مصرف بالای CPU یا حافظه
- بررسی فرآیندهای در حال اجرا:
  ```bash
  ps aux | grep python
  ```
- محدود کردن منابع در فایل سرویس systemd

## نکات امنیتی

1. **استفاده از کاربر غیر root**: ایجاد یک کاربر اختصاصی به جای استفاده از root
2. **تنظیم فایروال**: محدود کردن دسترسی‌های ورودی به سرور
3. **به‌روزرسانی منظم**: به‌روزرسانی سیستم عامل و بسته‌های نصب شده
4. **مدیریت توکن‌ها**: محافظت از توکن‌ها و کلیدهای API

## سرویس‌های ابری جایگزین

### استفاده از Heroku

1. نصب Heroku CLI
2. ساخت فایل Procfile:
   ```
   worker: python smart_ai_scheduler.py
   ```
3. تنظیم متغیرهای محیطی در داشبورد Heroku
4. دیپلوی با دستورات:
   ```bash
   git add .
   git commit -m "Ready for Heroku"
   heroku create
   git push heroku main
   heroku ps:scale worker=1
   ```

### استفاده از Railway

1. ثبت‌نام در Railway و اتصال به مخزن گیت
2. تنظیم متغیرهای محیطی در داشبورد
3. تنظیم دستور شروع:
   ```
   python smart_ai_scheduler.py
   ```

## نتیجه‌گیری

با انتقال ربات به یک سرور دائمی، می‌توانید از اجرای بدون وقفه آن اطمینان حاصل کنید و گزارش‌های منظم و به‌موقع دریافت نمایید. سرور مجازی خصوصی (VPS) بهترین گزینه از نظر انعطاف‌پذیری، قیمت و کنترل است، اما سرویس‌های PaaS مانند Heroku یا Railway نیز گزینه‌های خوبی برای افرادی هستند که تمایلی به مدیریت سرور ندارند.

---

**یادآوری مهم**: همیشه از داده‌ها و تنظیمات خود نسخه پشتیبان تهیه کنید و قبل از انتقال به محیط تولید، در یک محیط تست عملکرد ربات را بررسی کنید.