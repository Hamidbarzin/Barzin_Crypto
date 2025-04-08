#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اعلان روشن شدن سیستم به تلگرام

این اسکریپت در زمان روشن شدن سیستم اجرا می‌شود و یک پیام به تلگرام ارسال می‌کند.
این اسکریپت باید در LaunchAgents سیستم ثبت شود تا در زمان روشن شدن اجرا شود.
"""

import os
import time
import datetime
import requests
import platform
import socket
import subprocess
import logging
from pathlib import Path

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/boot_notifier.log')
)

logger = logging.getLogger('boot_notifier')

# دریافت متغیرهای محیطی
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEFAULT_CHAT_ID = os.environ.get('DEFAULT_CHAT_ID')

def send_telegram_message(message):
    """ارسال پیام به تلگرام"""
    if not TELEGRAM_BOT_TOKEN or not DEFAULT_CHAT_ID:
        logger.error("توکن بات تلگرام یا شناسه چت تنظیم نشده است.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": DEFAULT_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("پیام با موفقیت ارسال شد.")
            return True
        else:
            logger.error(f"خطا در ارسال پیام: {response.text}")
            return False
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def get_uptime():
    """دریافت زمان روشن بودن سیستم"""
    try:
        uptime_process = subprocess.Popen(["uptime"], stdout=subprocess.PIPE)
        uptime_output = uptime_process.communicate()[0].decode('utf-8').strip()
        return uptime_output
    except Exception as e:
        logger.error(f"خطا در دریافت uptime: {str(e)}")
        return "نامشخص"

def get_ip_address():
    """دریافت آدرس IP سیستم"""
    try:
        # تلاش برای دریافت IP خارجی
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception:
        try:
            # روش جایگزین برای دریافت IP
            result = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            try:
                # دریافت IP داخلی
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
            except Exception:
                return "نامشخص"

def get_system_info():
    """دریافت اطلاعات سیستم"""
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "uptime": get_uptime(),
        "ip": get_ip_address()
    }
    
def get_service_status():
    """بررسی وضعیت سرویس‌های ربات ارز دیجیتال"""
    services_status = {}
    
    # بررسی scheduler
    try:
        result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)
        output = result.stdout
        
        if 'com.user.crypto.scheduler' in output:
            services_status['scheduler'] = 'فعال'
        else:
            services_status['scheduler'] = 'غیرفعال'
            
        if 'com.user.crypto.telegram' in output:
            services_status['telegram'] = 'فعال'
        else:
            services_status['telegram'] = 'غیرفعال'
    except Exception as e:
        logger.error(f"خطا در بررسی وضعیت سرویس‌ها: {str(e)}")
        services_status['scheduler'] = 'نامشخص'
        services_status['telegram'] = 'نامشخص'
    
    return services_status

def main():
    """تابع اصلی برنامه"""
    logger.info("شروع برنامه اعلان روشن شدن سیستم")
    
    # مکث کوتاه برای اطمینان از اتصال به اینترنت
    time.sleep(10)
    
    now = datetime.datetime.now()
    system_info = get_system_info()
    services = get_service_status()
    
    # ساخت پیام
    message = f"""✅ <b>سیستم روشن شد</b>

⏰ <b>زمان روشن شدن:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}

🖥️ <b>اطلاعات سیستم:</b>
  - نام سیستم: {system_info['hostname']}
  - سیستم عامل: {system_info['os']} {system_info['os_version']}
  - پردازنده: {system_info['processor']}
  - IP: {system_info['ip']}
  - مدت روشن بودن: {system_info['uptime']}

🤖 <b>وضعیت سرویس‌ها:</b>
  - زمان‌بندی (scheduler): {services['scheduler']}
  - گزارش‌دهی تلگرام: {services['telegram']}

⚡️ <b>اقدامات در حال انجام:</b>
  - بررسی وضعیت سرویس‌ها
  - راه‌اندازی خودکار گزارش‌دهی تلگرام
"""
    
    # ارسال پیام به تلگرام
    send_telegram_message(message)
    
    # تلاش برای راه‌اندازی سرویس‌ها در صورت غیرفعال بودن
    if services['scheduler'] == 'غیرفعال' or services['telegram'] == 'غیرفعال':
        try:
            if services['scheduler'] == 'غیرفعال':
                subprocess.run(['launchctl', 'load', os.path.expanduser('~/Library/LaunchAgents/com.user.crypto.scheduler.plist')])
                
            if services['telegram'] == 'غیرفعال':
                subprocess.run(['launchctl', 'load', os.path.expanduser('~/Library/LaunchAgents/com.user.crypto.telegram.plist')])
                
            # ارسال پیام تأیید راه‌اندازی
            time.sleep(5)
            services = get_service_status()
            restart_message = f"""🔄 <b>وضعیت سرویس‌ها پس از تلاش مجدد</b>

  - زمان‌بندی (scheduler): {services['scheduler']}
  - گزارش‌دهی تلگرام: {services['telegram']}
"""
            send_telegram_message(restart_message)
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی مجدد سرویس‌ها: {str(e)}")
            error_message = f"""⚠️ <b>خطا در راه‌اندازی مجدد سرویس‌ها</b>

خطا: {str(e)}

لطفاً به صورت دستی سرویس‌ها را راه‌اندازی کنید.
"""
            send_telegram_message(error_message)
    
    logger.info("پایان اجرای برنامه")

if __name__ == "__main__":
    main()
