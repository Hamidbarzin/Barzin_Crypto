#!/bin/bash

# اسکریپت راه‌اندازی سیستم مانیتورینگ وضعیت روشن/خاموش سیستم
# این اسکریپت اسکریپت‌های مانیتورینگ وضعیت سیستم را نصب می‌کند

# تنظیم متغیرهای رنگی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # بدون رنگ

# نمایش بنر راهنما
echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}    راه‌اندازی سیستم مانیتورینگ وضعیت سیستم    ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# مسیر اسکریپت‌ها
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET_DIR="$HOME/crypto_system_monitor"

# بررسی توکن تلگرام و شناسه چت
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$DEFAULT_CHAT_ID" ]; then
    echo -e "${RED}توکن بات تلگرام یا شناسه چت تنظیم نشده است.${NC}"
    echo -e "${YELLOW}لطفاً متغیرهای محیطی زیر را تنظیم کنید:${NC}"
    echo -e "export TELEGRAM_BOT_TOKEN=YOUR_TOKEN"
    echo -e "export DEFAULT_CHAT_ID=YOUR_CHAT_ID"
    exit 1
fi

# ایجاد مسیر نصب
echo -e "${BLUE}» ایجاد پوشه نصب...${NC}"
mkdir -p "$TARGET_DIR"

# کپی اسکریپت‌ها
echo -e "${BLUE}» کپی اسکریپت‌های مانیتورینگ...${NC}"
cp "$SCRIPT_DIR/power_monitor.py" "$TARGET_DIR/"
cp "$SCRIPT_DIR/boot_notifier.py" "$TARGET_DIR/"
cp "$SCRIPT_DIR/shutdown_notifier.py" "$TARGET_DIR/"

# تنظیم دسترسی‌ها
echo -e "${BLUE}» تنظیم دسترسی‌های اجرایی...${NC}"
chmod +x "$TARGET_DIR/power_monitor.py"
chmod +x "$TARGET_DIR/boot_notifier.py"
chmod +x "$TARGET_DIR/shutdown_notifier.py"

# ایجاد LaunchAgent برای اعلان روشن شدن سیستم
echo -e "${BLUE}» ایجاد LaunchAgent برای اعلان روشن شدن سیستم...${NC}"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$HOME/Library/LaunchAgents/com.user.crypto.boot_notifier.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.crypto.boot_notifier</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${TARGET_DIR}/boot_notifier.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>86400</integer>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>${TELEGRAM_BOT_TOKEN}</string>
        <key>DEFAULT_CHAT_ID</key>
        <string>${DEFAULT_CHAT_ID}</string>
    </dict>
    <key>StandardErrorPath</key>
    <string>${HOME}/boot_notifier_error.log</string>
    <key>StandardOutPath</key>
    <string>${HOME}/boot_notifier.log</string>
</dict>
</plist>
EOF

# ایجاد LaunchAgent برای اعلان خاموش شدن سیستم
echo -e "${BLUE}» ایجاد LaunchAgent برای اعلان خاموش شدن سیستم...${NC}"
cat > "$HOME/Library/LaunchAgents/com.user.crypto.shutdown_notifier.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.crypto.shutdown_notifier</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${TARGET_DIR}/shutdown_notifier.py</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>QuitOnTerm</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>${TELEGRAM_BOT_TOKEN}</string>
        <key>DEFAULT_CHAT_ID</key>
        <string>${DEFAULT_CHAT_ID}</string>
    </dict>
    <key>StandardErrorPath</key>
    <string>${HOME}/shutdown_notifier_error.log</string>
    <key>StandardOutPath</key>
    <string>${HOME}/shutdown_notifier.log</string>
</dict>
</plist>
EOF

# ایجاد LaunchAgent برای مانیتورینگ دوره‌ای وضعیت سیستم
echo -e "${BLUE}» ایجاد LaunchAgent برای مانیتورینگ دوره‌ای وضعیت سیستم...${NC}"
cat > "$HOME/Library/LaunchAgents/com.user.crypto.power_monitor.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.crypto.power_monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${TARGET_DIR}/power_monitor.py</string>
    </array>
    <key>StartInterval</key>
    <integer>21600</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>${TELEGRAM_BOT_TOKEN}</string>
        <key>DEFAULT_CHAT_ID</key>
        <string>${DEFAULT_CHAT_ID}</string>
    </dict>
    <key>StandardErrorPath</key>
    <string>${HOME}/power_monitor_error.log</string>
    <key>StandardOutPath</key>
    <string>${HOME}/power_monitor.log</string>
</dict>
</plist>
EOF

# ثبت hook برای اجرا در زمان خاموش شدن
echo -e "${BLUE}» تنظیم hook خاموش شدن سیستم...${NC}"
# سازگاری با روش‌های مختلف خاموش کردن سیستم

# نصب وابستگی‌های پایتون
echo -e "${BLUE}» نصب وابستگی‌های پایتون...${NC}"
pip3 install requests

# بارگذاری لانچ‌ ایجنت‌ها
echo -e "${BLUE}» بارگذاری لانچ ایجنت‌ها...${NC}"
launchctl unload "$HOME/Library/LaunchAgents/com.user.crypto.boot_notifier.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.user.crypto.boot_notifier.plist"

launchctl unload "$HOME/Library/LaunchAgents/com.user.crypto.power_monitor.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.user.crypto.power_monitor.plist"

# تنظیم هوک خاموش شدن روی سیستم
echo -e "${YELLOW}» توجه: برای خاموش شدن سیستم، هوک خاص نیاز دارد.${NC}"
echo -e "${YELLOW}» این نیاز به دسترسی sudo دارد، اگر اجرا نشود، اشکالی ندارد.${NC}"
sudo mkdir -p /etc/launchd.conf.d || true
sudo cat > /tmp/com.crypto.shutdown.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.crypto.shutdown</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${TARGET_DIR}/shutdown_notifier.py</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>LaunchOnlyOnce</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>${TELEGRAM_BOT_TOKEN}</string>
        <key>DEFAULT_CHAT_ID</key>
        <string>${DEFAULT_CHAT_ID}</string>
    </dict>
</dict>
</plist>
EOF
sudo mv /tmp/com.crypto.shutdown.plist /Library/LaunchDaemons/ 2>/dev/null || true

# ایجاد لینک سمبولیک برای sudo دسترسی
echo -e "${BLUE}» ایجاد دستور سریع برای راه‌اندازی مجدد سیستم مانیتورینگ...${NC}"
cat > "$TARGET_DIR/restart_monitor.sh" << 'EOF'
#!/bin/bash
launchctl unload "$HOME/Library/LaunchAgents/com.user.crypto.boot_notifier.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.user.crypto.boot_notifier.plist"

launchctl unload "$HOME/Library/LaunchAgents/com.user.crypto.power_monitor.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.user.crypto.power_monitor.plist"

echo "» سیستم مانیتورینگ مجدداً راه‌اندازی شد."
EOF
chmod +x "$TARGET_DIR/restart_monitor.sh"

# ایجاد ایجاد اسکریپت تست
echo -e "${BLUE}» ایجاد اسکریپت تست سیستم مانیتورینگ...${NC}"
cat > "$TARGET_DIR/test_monitor.sh" << 'EOF'
#!/bin/bash
# اسکریپت تست سیستم مانیتورینگ

echo "» ارسال تست پیام روشن شدن سیستم..."
python3 "$HOME/crypto_system_monitor/boot_notifier.py"

echo "» ارسال تست گزارش وضعیت سیستم..."
python3 "$HOME/crypto_system_monitor/power_monitor.py"

echo "» تست تکمیل شد."
EOF
chmod +x "$TARGET_DIR/test_monitor.sh"

# اعلان پایان نصب
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}✓ نصب سیستم مانیتورینگ با موفقیت انجام شد.${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${YELLOW}برای تست کردن سیستم می‌توانید دستور زیر را اجرا کنید:${NC}"
echo -e "$TARGET_DIR/test_monitor.sh"
echo ""
echo -e "${YELLOW}سیستم به صورت خودکار در مواقع زیر گزارش ارسال می‌کند:${NC}"
echo -e "✓ هنگام روشن شدن سیستم"
echo -e "✓ هنگام خاموش شدن سیستم (در صورت نصب لانچ دیمون)"
echo -e "✓ هر ۶ ساعت یکبار گزارش وضعیت"
echo ""
echo -e "${BLUE}لاگ‌های مانیتورینگ در مسیرهای زیر ذخیره می‌شوند:${NC}"
echo -e "$HOME/power_monitor.log"
echo -e "$HOME/boot_notifier.log"
echo -e "$HOME/shutdown_notifier.log"
echo ""
