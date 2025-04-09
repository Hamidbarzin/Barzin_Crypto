#!/usr/bin/env python3
"""
سیستم بسیار ساده ارسال پیام تلگرام با استفاده از درخواست HTTP مستقیم
"""

import requests
import logging
from datetime import datetime
import sys
import os

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("super_simple_telegram")

# توکن و چت آیدی
TOKEN = "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk"
CHAT_ID = "722627622"

def send_message(text):
    """
    ارسال پیام به تلگرام با استفاده از API رسمی تلگرام
    
    Args:
        text (str): متن پیام
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        logger.info("در حال ارسال پیام به تلگرام...")
        response = requests.post(url, data=payload)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get("ok"):
            logger.info("پیام با موفقیت ارسال شد")
            return True
        else:
            logger.error(f"خطا در ارسال پیام: {response_json.get('description', 'خطای ناشناخته')}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def send_simple_test():
    """
    ارسال یک پیام تست ساده
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - تست جدید</b>
━━━━━━━━━━━━━━━━━━

این پیام با روش بسیار ساده ارسال شده است.
کد کاملاً ساده‌سازی شده و فقط از درخواست HTTP استفاده می‌کند.

⏰ <b>زمان:</b> {current_time}
"""
    
    return send_message(message)

def main():
    """
    تابع اصلی
    """
    result = send_simple_test()
    print(f"نتیجه ارسال پیام: {result}")

if __name__ == "__main__":
    main()