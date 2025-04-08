# سیستم مانیتورینگ وضعیت روشن/خاموش برای ارسال به تلگرام

## مقدمه

این سیستم برای نظارت بر وضعیت روشن یا خاموش بودن سیستم طراحی شده است و در موارد زیر گزارش‌های مناسب را به تلگرام ارسال می‌کند:

1. **زمان روشن شدن سیستم**: یک پیام اطلاع‌رسانی از روشن شدن سیستم به همراه اطلاعات کامل سیستم
2. **زمان خاموش شدن سیستم**: یک پیام هشدار از خاموش شدن احتمالی سیستم به همراه دلیل خاموش شدن
3. **گزارش‌های دوره‌ای**: هر 6 ساعت یک گزارش از وضعیت سیستم شامل اطلاعات سخت‌افزاری، وضعیت باتری، زمان روشن بودن و وضعیت اتصال به اینترنت

## پیش‌نیازها

برای استفاده از این سیستم به موارد زیر نیاز دارید:

1. **سیستم عامل macOS** (نسخه 10.15 یا بالاتر)
2. **پایتون 3** (نسخه 3.6 یا بالاتر)
3. **توکن بات تلگرام** (`TELEGRAM_BOT_TOKEN`)
4. **شناسه چت تلگرام** (`DEFAULT_CHAT_ID`)

## نصب و راه‌اندازی

### نصب خودکار (توصیه شده)

ساده‌ترین روش برای نصب، استفاده از اسکریپت نصب خودکار است:

```bash
cd deploy/mac/system_monitor
chmod +x setup_monitor.sh
./setup_monitor.sh
```

این اسکریپت تمامی فایل‌های لازم را نصب کرده و سرویس‌های مورد نیاز را راه‌اندازی می‌کند.

### نصب دستی

اگر می‌خواهید به صورت دستی نصب کنید، مراحل زیر را دنبال کنید:

1. **کپی اسکریپت‌ها به مسیر دلخواه**:
   ```bash
   mkdir -p ~/crypto_system_monitor
   cp power_monitor.py boot_notifier.py shutdown_notifier.py ~/crypto_system_monitor/
   chmod +x ~/crypto_system_monitor/*.py
   ```

2. **ایجاد فایل‌های LaunchAgent**:
   ```bash
   mkdir -p ~/Library/LaunchAgents
   
   # فایل اعلان روشن شدن سیستم
   cat > ~/Library/LaunchAgents/com.user.crypto.boot_notifier.plist << EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.user.crypto.boot_notifier</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>${HOME}/crypto_system_monitor/boot_notifier.py</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>EnvironmentVariables</key>
       <dict>
           <key>TELEGRAM_BOT_TOKEN</key>
           <string>YOUR_TELEGRAM_BOT_TOKEN</string>
           <key>DEFAULT_CHAT_ID</key>
           <string>YOUR_CHAT_ID</string>
       </dict>
       <key>StandardErrorPath</key>
       <string>${HOME}/boot_notifier_error.log</string>
       <key>StandardOutPath</key>
       <string>${HOME}/boot_notifier.log</string>
   </dict>
   </plist>
   EOF
   
   # فایل مانیتورینگ دوره‌ای
   cat > ~/Library/LaunchAgents/com.user.crypto.power_monitor.plist << EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.user.crypto.power_monitor</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>${HOME}/crypto_system_monitor/power_monitor.py</string>
       </array>
       <key>StartInterval</key>
       <integer>21600</integer>
       <key>RunAtLoad</key>
       <true/>
       <key>EnvironmentVariables</key>
       <dict>
           <key>TELEGRAM_BOT_TOKEN</key>
           <string>YOUR_TELEGRAM_BOT_TOKEN</string>
           <key>DEFAULT_CHAT_ID</key>
           <string>YOUR_CHAT_ID</string>
       </dict>
       <key>StandardErrorPath</key>
       <string>${HOME}/power_monitor_error.log</string>
       <key>StandardOutPath</key>
       <string>${HOME}/power_monitor.log</string>
   </dict>
   </plist>
   EOF
   ```

3. **بارگذاری سرویس‌ها**:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.user.crypto.boot_notifier.plist
   launchctl load ~/Library/LaunchAgents/com.user.crypto.power_monitor.plist
   ```

## تست سیستم

پس از نصب، می‌توانید با اجرای دستورات زیر سیستم را تست کنید:

```bash
# تست اعلان روشن شدن سیستم
python3 ~/crypto_system_monitor/boot_notifier.py

# تست گزارش دوره‌ای
python3 ~/crypto_system_monitor/power_monitor.py

# تست اعلان خاموش شدن سیستم (اختیاری)
python3 ~/crypto_system_monitor/shutdown_notifier.py
```

## نکات مهم

1. **متغیرهای محیطی**:
   - اطمینان حاصل کنید که متغیرهای محیطی `TELEGRAM_BOT_TOKEN` و `DEFAULT_CHAT_ID` به درستی تنظیم شده‌اند.
   - می‌توانید این متغیرها را در فایل `~/.zshrc` یا `~/.bash_profile` تنظیم کنید.

2. **سرویس خاموش شدن سیستم**:
   - اعلان خاموش شدن سیستم نیاز به دسترسی‌های ویژه دارد و ممکن است همیشه کار نکند.
   - برای اطمینان بیشتر، از اسکریپت نصب خودکار استفاده کنید.

3. **لاگ‌ها**:
   - لاگ‌های سیستم در مسیرهای زیر ذخیره می‌شوند:
     - `~/power_monitor.log`
     - `~/boot_notifier.log`
     - `~/shutdown_notifier.log`

4. **مشکلات احتمالی**:
   - اگر پیام‌ها دریافت نمی‌شوند، فایل‌های لاگ را بررسی کنید.
   - اطمینان حاصل کنید که بات تلگرام فعال است و دسترسی ارسال پیام دارد.
   - بررسی کنید که شناسه چت صحیح است (می‌توانید با ارسال یک پیام تست به صورت دستی بررسی کنید).

## راه‌اندازی مجدد سیستم

اگر نیاز به راه‌اندازی مجدد سیستم دارید، می‌توانید از دستورات زیر استفاده کنید:

```bash
# توقف سرویس‌ها
launchctl unload ~/Library/LaunchAgents/com.user.crypto.boot_notifier.plist
launchctl unload ~/Library/LaunchAgents/com.user.crypto.power_monitor.plist

# راه‌اندازی مجدد سرویس‌ها
launchctl load ~/Library/LaunchAgents/com.user.crypto.boot_notifier.plist
launchctl load ~/Library/LaunchAgents/com.user.crypto.power_monitor.plist
```

یا اگر از اسکریپت نصب خودکار استفاده کرده‌اید، می‌توانید از اسکریپت راه‌اندازی مجدد استفاده کنید:

```bash
~/crypto_system_monitor/restart_monitor.sh
```

---

برای اطلاعات بیشتر یا در صورت بروز مشکل، به راهنمای کامل مراجعه کنید یا از طریق تلگرام با من در تماس باشید.
