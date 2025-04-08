# راهنمای نصب و راه‌اندازی ربات روی سیستم مک

## پیش‌نیازها

1. سیستم عامل macOS 10.15 (Catalina) یا بالاتر
2. دسترسی به ترمینال
3. توکن بات تلگرام و شناسه چت
4. کلید API هوش مصنوعی (اختیاری)

## مراحل نصب دستی

### 1. نصب Homebrew

اگر Homebrew را نصب ندارید، آن را با دستور زیر نصب کنید:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

برای سیستم‌های با پردازنده Apple Silicon (M1/M2/M3)، دستور زیر را نیز اجرا کنید:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2. نصب پیش‌نیازها

```bash
brew install python git
```

### 3. دانلود کد ربات

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/YOUR_USERNAME/crypto_telegram_bot.git crypto_bot
cd crypto_bot
```

### 4. ایجاد محیط مجازی و نصب وابستگی‌ها

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. تنظیم متغیرهای محیطی

فایل `.env` را با استفاده از ویرایشگر متنی مورد علاقه خود ایجاد کنید:

```bash
nano .env
```

محتوای زیر را در فایل قرار دهید:

```
TELEGRAM_BOT_TOKEN=your_bot_token
DEFAULT_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_api_key
```

کلیدهای `your_bot_token`، `your_chat_id` و `your_openai_api_key` را با مقادیر واقعی جایگزین کنید.

### 6. اجرای دستی برنامه

برای اجرای برنامه به صورت دستی، دستورات زیر را در دو ترمینال جداگانه اجرا کنید:

**ترمینال 1 - زمان‌بندی اصلی:**
```bash
cd ~/Projects/crypto_bot
source venv/bin/activate
python scheduler.py
```

**ترمینال 2 - گزارش‌دهی تلگرام:**
```bash
cd ~/Projects/crypto_bot
source venv/bin/activate
python ten_minute_scheduler.py
```

## راه‌اندازی خودکار با LaunchAgents

برای اجرای خودکار برنامه در هنگام بوت سیستم، می‌توانید از LaunchAgents استفاده کنید:

### 1. ایجاد فایل‌های plist

**برای سرویس اصلی:**
```bash
mkdir -p ~/Library/LaunchAgents
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
</dict>
</plist>
EOF
```

**برای سرویس گزارش‌دهی تلگرام:**
```bash
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
</dict>
</plist>
EOF
```

### 2. بارگذاری سرویس‌ها

```bash
launchctl load ~/Library/LaunchAgents/com.user.crypto.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.user.crypto.telegram.plist
```

## استفاده از اسکریپت نصب خودکار

برای نصب و راه‌اندازی خودکار، از اسکریپت زیر استفاده کنید:

```bash
bash deploy/mac/setup_mac.sh
```

این اسکریپت تمام مراحل بالا را به صورت خودکار انجام می‌دهد.

## مدیریت سرویس‌ها

### شروع سرویس‌ها

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

## نکات مهم برای کاربران مک

1. **مدیریت انرژی**: اگر مک شما به حالت خواب برود، ممکن است برنامه متوقف شود. برای جلوگیری از این مشکل:
   - برنامه [Amphetamine](https://apps.apple.com/us/app/amphetamine/id937984704) را از App Store نصب کنید
   - آن را طوری تنظیم کنید که سیستم را روشن نگه دارد

2. **اجرا در پس‌زمینه**: برای اطمینان از اجرای برنامه در پس‌زمینه، از LaunchAgents استفاده کنید

3. **به‌روزرسانی سیستم**: پس از هر به‌روزرسانی بزرگ macOS، سرویس‌ها را مجدداً بارگذاری کنید

4. **دسترسی فایل‌ها**: در نسخه‌های جدید macOS، ممکن است نیاز به دادن دسترسی به ترمینال برای پوشه‌های خاص داشته باشید

## پشتیبانی از انواع مک

این ربات با هر دو نوع پردازنده Intel و Apple Silicon (M1/M2/M3) سازگار است.