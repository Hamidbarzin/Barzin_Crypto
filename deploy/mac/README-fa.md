# راهنمای نصب ربات تلگرام ارز دیجیتال روی مک (macOS)

## مقدمه

این راهنما چگونگی نصب و راه‌اندازی ربات تلگرام تحلیل ارز دیجیتال روی سیستم عامل macOS را توضیح می‌دهد. این روش برای کاربرانی که دارای سیستم مک هستند و می‌خواهند ربات را روی سیستم شخصی خود اجرا کنند، مناسب است.

## پیش‌نیازها

1. سیستم عامل macOS 10.15 (Catalina) یا بالاتر
2. توکن بات تلگرام (از طریق [BotFather](https://t.me/BotFather) ایجاد شده)
3. شناسه چت تلگرام شما (پیش‌فرض: 722627622)
4. دسترسی به خط فرمان (Terminal)

## روش نصب سریع (توصیه شده)

ساده‌ترین روش برای نصب، استفاده از اسکریپت خودکار است:

```bash
# دانلود فایل‌های پروژه
git clone https://github.com/yourusername/crypto-telegram-bot.git
cd crypto-telegram-bot

# اجرای اسکریپت نصب
bash deploy/mac/setup_mac.sh
```

اسکریپت نصب به صورت خودکار تمام مراحل زیر را انجام می‌دهد:
1. نصب وابستگی‌های مورد نیاز (Homebrew، Python)
2. ایجاد محیط مجازی Python
3. نصب کتابخانه‌های مورد نیاز
4. تنظیم فایل‌های پیکربندی (.env)
5. ایجاد سرویس‌های LaunchAgent برای اجرای خودکار
6. نصب سیستم مانیتورینگ وضعیت روشن/خاموش

## نصب دستی

اگر می‌خواهید به صورت دستی نصب کنید، می‌توانید مراحل زیر را دنبال کنید:

### 1. نصب Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

اگر از مک با پردازنده Apple Silicon (M1/M2/M3) استفاده می‌کنید:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2. نصب Python و Git

```bash
brew install python git
```

### 3. کلون کردن پروژه

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/yourusername/crypto-telegram-bot.git crypto_bot
cd crypto_bot
```

### 4. ایجاد محیط مجازی و نصب وابستگی‌ها

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot ccxt pandas matplotlib mplfinance numpy requests schedule trafilatura openai ta
```

### 5. ایجاد فایل .env

```bash
cat > .env << EOF
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
DEFAULT_CHAT_ID=722627622
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
EOF
```

### 6. ایجاد سرویس‌های LaunchAgent

```bash
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.user.crypto.telegram.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.crypto.telegram</string>
    <key>ProgramArguments</key>
    <array>
        <string>${HOME}/Projects/crypto_bot/venv/bin/python</string>
        <string>${HOME}/Projects/crypto_bot/ten_minute_scheduler.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>${HOME}/Projects/crypto_bot/telegram_error.log</string>
    <key>StandardOutPath</key>
    <string>${HOME}/Projects/crypto_bot/telegram.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
    <key>WorkingDirectory</key>
    <string>${HOME}/Projects/crypto_bot</string>
</dict>
</plist>
EOF

cat > ~/Library/LaunchAgents/com.user.crypto.scheduler.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.crypto.scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>${HOME}/Projects/crypto_bot/venv/bin/python</string>
        <string>${HOME}/Projects/crypto_bot/scheduler.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>${HOME}/Projects/crypto_bot/scheduler_error.log</string>
    <key>StandardOutPath</key>
    <string>${HOME}/Projects/crypto_bot/scheduler.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
    <key>WorkingDirectory</key>
    <string>${HOME}/Projects/crypto_bot</string>
</dict>
</plist>
EOF
```

### 7. بارگذاری سرویس‌ها

```bash
launchctl load ~/Library/LaunchAgents/com.user.crypto.telegram.plist
launchctl load ~/Library/LaunchAgents/com.user.crypto.scheduler.plist
```

## نصب سیستم مانیتورینگ وضعیت روشن/خاموش

برای نصب سیستم مانیتورینگ که وضعیت روشن یا خاموش شدن سیستم را به تلگرام گزارش می‌دهد:

```bash
cd ~/Projects/crypto_bot
cp -r deploy/mac/system_monitor .
cd system_monitor
chmod +x setup_monitor.sh
./setup_monitor.sh
```

برای اطلاعات بیشتر در مورد این سیستم، به [راهنمای سیستم مانیتورینگ](system_monitor/README-fa.md) مراجعه کنید.

## دستورات مدیریتی

### راه‌اندازی سرویس‌ها

```bash
launchctl load ~/Library/LaunchAgents/com.user.crypto.telegram.plist
launchctl load ~/Library/LaunchAgents/com.user.crypto.scheduler.plist
```

### توقف سرویس‌ها

```bash
launchctl unload ~/Library/LaunchAgents/com.user.crypto.telegram.plist
launchctl unload ~/Library/LaunchAgents/com.user.crypto.scheduler.plist
```

### مشاهده لاگ‌ها

```bash
tail -f ~/Projects/crypto_bot/telegram.log
tail -f ~/Projects/crypto_bot/scheduler.log
```

### تست ارسال پیام تلگرام

```bash
cd ~/Projects/crypto_bot
python test_telegram.py
```

## نکات مهم

1. **جلوگیری از خواب رفتن سیستم**:
   - برای اطمینان از اجرای مداوم ربات، نیاز است که سیستم مک شما به حالت خواب نرود.
   - می‌توانید از برنامه [Amphetamine](https://apps.apple.com/us/app/amphetamine/id937984704) که در App Store رایگان است استفاده کنید.

2. **به‌روزرسانی سیستم**:
   - پس از به‌روزرسانی macOS، ممکن است نیاز باشد سرویس‌ها را مجدداً راه‌اندازی کنید.

3. **مصرف باتری**:
   - توجه داشته باشید که اجرای مداوم این سرویس‌ها می‌تواند مصرف باتری را افزایش دهد.
   - در صورت امکان، سیستم را به برق متصل نگه دارید.

4. **مسائل امنیتی**:
   - فایل `.env` حاوی اطلاعات حساس است، از امنیت آن اطمینان حاصل کنید.
   - مطمئن شوید که دسترسی‌های لازم برای اجرای اسکریپت‌ها فراهم شده است.

## عیب‌یابی

### مشکل: سرویس‌ها اجرا نمی‌شوند

بررسی کنید که آیا فایل‌های plist به درستی در مسیر `~/Library/LaunchAgents` قرار دارند و با دستور زیر وضعیت آن‌ها را بررسی کنید:

```bash
launchctl list | grep crypto
```

### مشکل: پیام‌های تلگرام ارسال نمی‌شوند

1. بررسی کنید که توکن بات و شناسه چت در فایل `.env` به درستی تنظیم شده باشند.
2. با اجرای `python test_telegram.py` به صورت دستی، صحت ارسال پیام را بررسی کنید.
3. لاگ‌های خطا را در فایل‌های `telegram_error.log` و `scheduler_error.log` بررسی کنید.

### مشکل: خطای وابستگی‌ها

اگر با خطای وابستگی‌های پایتون مواجه شدید، می‌توانید با فعال کردن محیط مجازی و نصب مجدد وابستگی‌ها مشکل را حل کنید:

```bash
cd ~/Projects/crypto_bot
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## مستندات بیشتر

- [راهنمای سیستم مانیتورینگ وضعیت روشن/خاموش](system_monitor/README-fa.md)
- [راهنمای استقرار](../راهنمای_استقرار.md)
- [راهنمای ربات هوشمند](../../راهنمای_ربات_هوشمند.md)

---

برای اطلاعات بیشتر یا در صورت بروز مشکل، از طریق تلگرام با من در تماس باشید.