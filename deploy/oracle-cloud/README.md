# راهنمای استقرار ربات روی Oracle Cloud

## مقدمه

Oracle Cloud Infrastructure (OCI) دارای یک لایه همیشه رایگان است که شامل دو ماشین مجازی با مشخصات کافی برای اجرای ربات تلگرام می‌شود. این راهنما مراحل استقرار ربات روی Oracle Cloud را توضیح می‌دهد.

## پیش‌نیازها

1. ثبت‌نام در [Oracle Cloud](https://www.oracle.com/cloud/free/)
2. یک کارت اعتباری معتبر برای تایید هویت (هزینه‌ای دریافت نمی‌شود)
3. توکن بات تلگرام و شناسه چت

## مراحل استقرار

### 1. ایجاد ماشین مجازی

1. وارد کنسول Oracle Cloud شوید
2. به بخش "Compute" > "Instances" بروید
3. روی "Create Instance" کلیک کنید
4. تنظیمات زیر را اعمال کنید:
   - نام: `crypto-bot`
   - دسته ماشین: AMD
   - شکل ماشین: VM.Standard.E2.1.Micro (1 OCPU, 1 GB RAM) - Always Free Tier
   - سیستم عامل: Oracle Linux 8 یا Ubuntu 20.04
   - VCN: یک VCN جدید ایجاد کنید یا موجود را انتخاب کنید
   - Subnet: Public Subnet
   - SSH Key: کلید SSH خود را آپلود کنید یا کلید جدیدی تولید کنید

5. روی "Create" کلیک کنید و منتظر بمانید تا ماشین مجازی ساخته شود
6. آدرس IP عمومی ماشین را یادداشت کنید

### 2. تنظیم دیواره آتش

1. در کنسول Oracle Cloud، به بخش "Networking" > "Virtual Cloud Networks" بروید
2. VCN مرتبط با ماشین مجازی خود را انتخاب کنید
3. "Security Lists" را انتخاب کنید و سپس "Default Security List" را باز کنید
4. "Add Ingress Rules" را کلیک کنید و قوانین زیر را اضافه کنید:
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: TCP
   - Destination Port Range: 22, 80, 443

### 3. اتصال به ماشین مجازی

```bash
ssh opc@YOUR_PUBLIC_IP
```

(در اوبونتو، از `ubuntu@YOUR_PUBLIC_IP` استفاده کنید)

### 4. نصب پیش‌نیازها

```bash
# بروزرسانی سیستم
sudo dnf update -y  # برای Oracle Linux
# یا
sudo apt update && sudo apt upgrade -y  # برای اوبونتو

# نصب پیش‌نیازها
sudo dnf install -y git python39 python39-pip  # برای Oracle Linux
# یا
sudo apt install -y git python3-pip python3-venv  # برای اوبونتو
```

### 5. دانلود کد ربات

```bash
git clone https://github.com/YOUR_USERNAME/crypto_telegram_bot.git ~/crypto_bot
cd ~/crypto_bot
```

### 6. نصب وابستگی‌ها

```bash
# برای Oracle Linux
python3.9 -m pip install --user -r requirements.txt

# برای اوبونتو
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7. تنظیم فایل‌های محیطی

```bash
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token
DEFAULT_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_api_key
EOF
```

### 8. تنظیم systemd برای اجرای خودکار

```bash
sudo bash -c 'cat > /etc/systemd/system/crypto-bot.service << EOF
[Unit]
Description=Crypto Telegram Bot Service
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc/crypto_bot
ExecStart=/usr/bin/python3.9 scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

sudo bash -c 'cat > /etc/systemd/system/crypto-telegram.service << EOF
[Unit]
Description=Crypto Telegram Reporting Service
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc/crypto_bot
ExecStart=/usr/bin/python3.9 ten_minute_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'
```

برای اوبونتو، `User=ubuntu` و `ExecStart=/home/ubuntu/crypto_bot/venv/bin/python` را جایگزین کنید.

### 9. فعال‌سازی و راه‌اندازی سرویس‌ها

```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-bot.service
sudo systemctl enable crypto-telegram.service
sudo systemctl start crypto-bot.service
sudo systemctl start crypto-telegram.service
```

### 10. بررسی وضعیت سرویس‌ها

```bash
sudo systemctl status crypto-bot.service
sudo systemctl status crypto-telegram.service
```

## نکات مهم

1. **امنیت**: ماشین‌های Oracle Cloud به طور مستقیم در معرض اینترنت هستند. حتماً رمز عبور قوی و کلید SSH ایمن استفاده کنید.

2. **پایداری اتصال**: برای اطمینان از اجرای مداوم ربات، systemd را تنظیم کرده‌ایم تا در صورت خرابی، سرویس‌ها را مجدداً راه‌اندازی کند.

3. **لاگ‌ها**: برای مشاهده لاگ‌های سرویس‌ها:
   ```bash
   sudo journalctl -u crypto-bot.service
   sudo journalctl -u crypto-telegram.service
   ```

4. **حد استفاده رایگان**: ماشین‌های Always Free تا زمانی که استفاده نکنید، منقضی نمی‌شوند.