#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اعلان خاموش شدن سیستم به تلگرام

این اسکریپت در زمان خاموش شدن سیستم اجرا می‌شود و یک پیام به تلگرام ارسال می‌کند.
این اسکریپت باید در LaunchAgents سیستم ثبت شود با RunAtLoad=false و QuitOnTerm=true.
"""

import os
import time
import datetime
import requests
import platform
import logging
import subprocess
import signal
import sys

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/shutdown_notifier.log')
)

logger = logging.getLogger('shutdown_notifier')

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
        
        response = requests.post(url, json=payload, timeout=3)
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

def get_battery_status():
    """دریافت وضعیت باتری (فقط برای مک)"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=2)
            output = result.stdout.strip()
            
            # پردازش خروجی برای استخراج درصد شارژ و وضعیت شارژ
            battery_info = {}
            
            # جستجوی درصد شارژ
            import re
            percent_match = re.search(r'(\d+)%', output)
            if percent_match:
                battery_info['percent'] = percent_match.group(1)
            else:
                battery_info['percent'] = "نامشخص"
            
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

def get_shutdown_reason():
    """تلاش برای دریافت دلیل خاموش شدن سیستم"""
    reason = "نامشخص"
    try:
        # بررسی آخرین لاگ‌های سیستم برای یافتن علت خاموش شدن
        result = subprocess.run(['log', 'show', '--last', '5m', '--predicate', 'eventMessage contains "shutdown"'], 
                               capture_output=True, text=True, timeout=2)
        
        if 'initiated by' in result.stdout.lower():
            reason = "خاموش شدن توسط کاربر"
        elif 'battery' in result.stdout.lower():
            reason = "شارژ باتری به پایان رسیده"
        elif 'power' in result.stdout.lower():
            reason = "قطع برق"
        elif 'update' in result.stdout.lower():
            reason = "به‌روزرسانی سیستم عامل"
    except Exception:
        pass
    
    return reason

def signal_handler(sig, frame):
    """پردازش سیگنال‌های سیستمی"""
    if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        logger.info(f"سیگنال {sig} دریافت شد. ارسال اعلان خاموش شدن...")
        send_shutdown_notification()
    sys.exit(0)

def send_shutdown_notification():
    """ارسال اعلان خاموش شدن"""
    now = datetime.datetime.now()
    uptime = get_uptime()
    battery = get_battery_status()
    reason = get_shutdown_reason()
    
    message = f"""⚠️ <b>سیستم در حال خاموش شدن است</b>

⏰ <b>زمان خاموش شدن:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}
⌛ <b>مدت زمان روشن بودن:</b> {uptime}

🔋 <b>وضعیت باتری:</b>
  - شارژ: {battery['percent']}%
  - وضعیت: {battery['status']}

🧐 <b>دلیل احتمالی خاموش شدن:</b> {reason}

🔄 <b>پیام راه‌اندازی مجدد پس از روشن شدن سیستم ارسال خواهد شد.</b>
"""
    
    send_telegram_message(message)

def main():
    """تابع اصلی برنامه"""
    logger.info("شروع برنامه اعلان خاموش شدن سیستم")
    
    # ثبت پردازش‌کننده‌های سیگنال
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    
    # ارسال پیام در حالت معمول (فراخوانی مستقیم)
    send_shutdown_notification()
    
    logger.info("پایان اجرای برنامه")

if __name__ == "__main__":
    main()
