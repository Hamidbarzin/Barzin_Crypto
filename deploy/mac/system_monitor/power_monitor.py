#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مانیتورینگ وضعیت روشن بودن سیستم و اعلام در تلگرام

این اسکریپت زمان‌های روشن شدن سیستم را ثبت می‌کند و در صورت خاموش شدن و روشن شدن مجدد،
یک پیام به تلگرام ارسال می‌کند. همچنین در فواصل زمانی مشخص، گزارش وضعیت سیستم را ارسال می‌کند.
"""

import os
import time
import logging
import subprocess
import datetime
import requests
import platform
import json
from pathlib import Path

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/power_monitor.log')
)

logger = logging.getLogger('power_monitor')

# مسیر فایل‌های ذخیره وضعیت
STATUS_FILE = os.path.expanduser('~/power_status.json')
LAST_PING_FILE = os.path.expanduser('~/last_ping.txt')

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

def get_system_info():
    """دریافت اطلاعات سیستم"""
    system_info = {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "processor": platform.processor(),
        "uptime": get_uptime(),
        "ip_address": get_ip_address()
    }
    
    return system_info

def get_uptime():
    """دریافت زمان روشن بودن سیستم"""
    if platform.system() == "Darwin":  # macOS
        try:
            uptime_process = subprocess.Popen(["uptime"], stdout=subprocess.PIPE)
            uptime_output = uptime_process.communicate()[0].decode('utf-8').strip()
            return uptime_output
        except Exception as e:
            logger.error(f"خطا در دریافت uptime: {str(e)}")
            return "نامشخص"
    else:
        return "نامشخص"

def get_ip_address():
    """دریافت آدرس IP سیستم"""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception:
        try:
            # روش جایگزین برای دریافت IP
            result = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return "نامشخص"

def get_battery_status():
    """دریافت وضعیت باتری (فقط برای مک)"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
            output = result.stdout.strip()
            
            # پردازش خروجی برای استخراج درصد شارژ و وضعیت شارژ
            battery_info = {}
            
            # جستجوی درصد شارژ
            import re
            percent_match = re.search(r'(\d+)%', output)
            if percent_match:
                battery_info['percent'] = percent_match.group(1)
            
            # بررسی وضعیت شارژ
            if 'charging' in output.lower():
                battery_info['status'] = 'درحال شارژ'
            elif 'discharging' in output.lower():
                battery_info['status'] = 'در حال استفاده از باتری'
            elif 'charged' in output.lower():
                battery_info['status'] = 'شارژ کامل'
            else:
                battery_info['status'] = 'نامشخص'
                
            return battery_info
    except Exception as e:
        logger.error(f"خطا در دریافت وضعیت باتری: {str(e)}")
    
    return {"percent": "نامشخص", "status": "نامشخص"}

def load_status():
    """بارگذاری وضعیت از فایل"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"خطا در بارگذاری وضعیت: {str(e)}")
    
    # مقدار پیش‌فرض
    return {
        "first_start": datetime.datetime.now().isoformat(),
        "last_start": datetime.datetime.now().isoformat(),
        "start_count": 1,
        "last_report": None
    }

def save_status(status):
    """ذخیره وضعیت در فایل"""
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"خطا در ذخیره وضعیت: {str(e)}")

def update_last_ping():
    """بروزرسانی زمان آخرین پینگ"""
    try:
        with open(LAST_PING_FILE, 'w', encoding='utf-8') as f:
            f.write(datetime.datetime.now().isoformat())
    except Exception as e:
        logger.error(f"خطا در بروزرسانی زمان آخرین پینگ: {str(e)}")

def check_restart():
    """بررسی اینکه آیا سیستم ریستارت شده است"""
    status = load_status()
    now = datetime.datetime.now()
    status_changed = False
    
    # بررسی اولین اجرا
    if "first_start" not in status:
        status["first_start"] = now.isoformat()
        status_changed = True
    
    # بررسی اینکه آیا این یک ریستارت است
    if "last_start" in status:
        last_start = datetime.datetime.fromisoformat(status["last_start"])
        # اگر بیش از 10 دقیقه از آخرین استارت گذشته، این یک ریستارت است
        if (now - last_start).total_seconds() > 600:
            status["start_count"] = status.get("start_count", 0) + 1
            
            # ارسال پیام به تلگرام
            message = f"""🔄 <b>سیستم مجدداً راه‌اندازی شد</b>

⏰ <b>زمان روشن شدن:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}
📊 <b>تعداد روشن شدن‌ها:</b> {status["start_count"]}
⌛ <b>زمان قبلی روشن شدن:</b> {last_start.strftime('%Y-%m-%d %H:%M:%S')}
🖥️ <b>اطلاعات سیستم:</b>
  - نام سیستم: {platform.node()}
  - سیستم عامل: {platform.system()} {platform.version()}
  - IP: {get_ip_address()}

⚡ <b>وضعیت باتری:</b>
  {get_battery_info_text()}
"""
            send_telegram_message(message)
            status_changed = True
    
    # بروزرسانی زمان آخرین استارت
    status["last_start"] = now.isoformat()
    
    if status_changed:
        save_status(status)

def get_battery_info_text():
    """دریافت متن وضعیت باتری"""
    battery = get_battery_status()
    return f"🔋 شارژ: {battery['percent']}% - وضعیت: {battery['status']}"

def send_status_report():
    """ارسال گزارش وضعیت به تلگرام"""
    status = load_status()
    now = datetime.datetime.now()
    
    # بررسی آخرین گزارش
    should_report = True
    if "last_report" in status and status["last_report"]:
        last_report = datetime.datetime.fromisoformat(status["last_report"])
        # گزارش هر 6 ساعت
        if (now - last_report).total_seconds() < 6 * 3600:
            should_report = False
    
    if should_report:
        # دریافت اطلاعات سیستم
        system_info = get_system_info()
        battery = get_battery_status()
        first_start = datetime.datetime.fromisoformat(status["first_start"])
        
        # ساخت پیام
        message = f"""📊 <b>گزارش وضعیت سیستم</b>

⏰ <b>زمان فعلی:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}
🖥️ <b>مشخصات سیستم:</b>
  - نام سیستم: {system_info['hostname']}
  - سیستم عامل: {system_info['os']} {system_info['os_version']}
  - پردازنده: {system_info['processor']}
  - IP: {system_info['ip_address']}

⚡ <b>وضعیت باتری:</b>
  - شارژ: {battery['percent']}%
  - وضعیت: {battery['status']}

🕒 <b>اطلاعات زمانی:</b>
  - مدت روشن بودن: {system_info['uptime']}
  - اولین استارت: {first_start.strftime('%Y-%m-%d %H:%M:%S')}
  - تعداد روشن شدن‌ها: {status.get("start_count", 1)}

👨‍💻 <b>وضعیت ربات:</b>
  ربات تلگرام ارز دیجیتال در حال اجرا است
"""
        
        # ارسال پیام
        if send_telegram_message(message):
            status["last_report"] = now.isoformat()
            save_status(status)

def main():
    """تابع اصلی برنامه"""
    logger.info("شروع برنامه مانیتورینگ روشن بودن سیستم")
    
    # بررسی ریستارت سیستم
    check_restart()
    
    # ارسال گزارش وضعیت
    send_status_report()
    
    # بروزرسانی زمان آخرین پینگ
    update_last_ping()
    
    logger.info("پایان اجرای برنامه")

if __name__ == "__main__":
    main()
