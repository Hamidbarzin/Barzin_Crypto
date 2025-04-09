#!/usr/bin/env python3
"""
تست ارسال پیام تلگرام یکباره - برای تست رفع مشکل تلگرام
"""

import os
import requests
import logging
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("telegram_test")

# توکن و چت آیدی پیش‌فرض
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

def send_message(text, parse_mode="HTML"):
    """
    ارسال پیام به تلگرام
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    params = {
        "chat_id": DEFAULT_CHAT_ID,
        "text": text,
        "disable_notification": False
    }
    
    if parse_mode:
        params["parse_mode"] = parse_mode
    
    try:
        logger.info(f"ارسال پیام به چت آیدی {DEFAULT_CHAT_ID}")
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info("پیام با موفقیت ارسال شد")
                return True
            else:
                logger.error(f"خطا در ارسال پیام: {result.get('description')}")
                return False
        else:
            logger.error(f"خطا در ارسال پیام: کد وضعیت {response.status_code}")
            logger.error(f"پاسخ: {response.text}")
            return False
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def main():
    """
    تابع اصلی
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🛠️ <b>Crypto Barzin - پیام بررسی عملکرد</b>
━━━━━━━━━━━━━━━━━━

این پیام برای بررسی عملکرد سیستم تلگرام ارسال شده است.
سیستم ارسال پیام تلگرام با موفقیت اصلاح شد.

⏰ <b>زمان:</b> {current_time}
    """
    
    result = send_message(message)
    logger.info(f"نتیجه ارسال پیام: {result}")

if __name__ == "__main__":
    main()