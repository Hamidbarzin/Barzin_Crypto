#!/usr/bin/env python3
"""
ورک‌فلوی ارسال پیام تلگرام برای Crypto Barzin

این اسکریپت به عنوان یک ورک‌فلو در Replit اجرا می‌شود و
به طور منظم گزارش‌های قیمت را به تلگرام ارسال می‌کند.
"""

import time
import requests
import logging
from datetime import datetime
import os

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_replit_workflow")

# تعیین URL
BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")
PRICE_REPORT_URL = f"{BASE_URL}/send_price_report"
SYSTEM_REPORT_URL = f"{BASE_URL}/send_system_report"
TEST_MESSAGE_URL = f"{BASE_URL}/send_test_message_replit"

def call_endpoint(url):
    """
    فراخوانی یک endpoint از API
    
    Args:
        url (str): آدرس API
        
    Returns:
        bool: موفقیت یا شکست
    """
    try:
        logger.info(f"فراخوانی {url}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                logger.info(f"موفقیت: {data.get('message', '')}")
                return True
            else:
                logger.error(f"خطا: {data.get('message', 'خطای ناشناخته')}")
                return False
        else:
            logger.error(f"خطا در فراخوانی API. کد وضعیت: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"خطا در فراخوانی API: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("ورک‌فلوی تلگرام شروع شد")
    
    # ارسال پیام تست در ابتدا
    call_endpoint(TEST_MESSAGE_URL)
    
    # شمارنده برای ارسال گزارش سیستم
    system_report_counter = 0
    
    try:
        while True:
            # ارسال گزارش قیمت
            success = call_endpoint(PRICE_REPORT_URL)
            logger.info(f"نتیجه ارسال گزارش قیمت: {success}")
            
            # افزایش شمارنده گزارش سیستم
            system_report_counter += 1
            
            # اگر ۶ ساعت (۳۶ بار ۱۰ دقیقه) گذشته، گزارش سیستم ارسال کن
            if system_report_counter >= 36:
                call_endpoint(SYSTEM_REPORT_URL)
                system_report_counter = 0
            
            # ۱۰ دقیقه صبر کن
            logger.info(f"انتظار برای ۱۰ دقیقه بعدی ({datetime.now().strftime('%H:%M:%S')})...")
            time.sleep(600)  # 10 minutes = 600 seconds
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()