#!/bin/bash

# اسکریپت راه‌اندازی ربات تلگرام ارز دیجیتال روی سیستم مک
# macOS Crypto Telegram Bot Setup Script

echo "شروع نصب ربات تلگرام ارز دیجیتال روی سیستم مک..."

# تشخیص مدیر بسته‌ها
if command -v brew &> /dev/null; then
    echo "Homebrew نصب شده است."
else
    echo "نصب Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # اضافه کردن Homebrew به PATH (برای Apple Silicon)
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

# نصب پیش‌نیازها
echo "نصب پیش‌نیازها..."
brew install python git

# کلون کردن مخزن
echo "دانلود کد ربات..."
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/YOUR_USERNAME/crypto_telegram_bot.git crypto_bot || true
cd crypto_bot

# ایجاد محیط مجازی
echo "ایجاد محیط مجازی پایتون..."
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
echo "نصب وابستگی‌ها..."
pip install --upgrade pip
pip install -r requirements.txt

# ایجاد فایل محیطی
echo "ایجاد فایل محیطی..."
cat > .env << EOF
TELEGRAM_BOT_TOKEN=YOUR_TOKEN
DEFAULT_CHAT_ID=YOUR_CHAT_ID
OPENAI_API_KEY=YOUR_API_KEY
EOF

echo "لطفاً فایل .env را با مقادیر واقعی ویرایش کنید."
echo "nano ~/Projects/crypto_bot/.env"

# ایجاد فایل‌های plist برای LaunchAgent
echo "ایجاد فایل‌های LaunchAgent..."

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
</dict>
</plist>
EOF

echo "نصب به پایان رسید."
echo "برای ویرایش فایل محیطی:"
echo "nano ~/Projects/crypto_bot/.env"
echo ""
echo "برای شروع سرویس‌ها:"
echo "launchctl load ~/Library/LaunchAgents/com.user.crypto.telegram.plist"
echo "launchctl load ~/Library/LaunchAgents/com.user.crypto.scheduler.plist"
echo ""
echo "برای توقف سرویس‌ها:"
echo "launchctl unload ~/Library/LaunchAgents/com.user.crypto.telegram.plist"
echo "launchctl unload ~/Library/LaunchAgents/com.user.crypto.scheduler.plist"