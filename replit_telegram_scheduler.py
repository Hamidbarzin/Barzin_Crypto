#!/usr/bin/env python3
"""
زمان‌بندی ارسال پیام‌های تلگرام با استفاده از API Replit

این اسکریپت به صورت دوره‌ای پیام‌های مختلف را به تلگرام ارسال می‌کند.
"""

import time
import requests
import logging
import random
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("replit_telegram_scheduler")

# آدرس اندپوینت‌های API
APP_URL = "https://456c040e-8bc3-434b-9dda-ccfefc1876f5.id.repl.co"  # آدرس برنامه روی Replit
PRICE_REPORT_ENDPOINT = f"{APP_URL}/send_price_report"
SYSTEM_REPORT_ENDPOINT = f"{APP_URL}/send_system_report"
TEST_MESSAGE_ENDPOINT = f"{APP_URL}/send_test_message_replit"

def send_request(endpoint):
    """
    ارسال درخواست به اندپوینت مورد نظر
    
    Args:
        endpoint (str): آدرس اندپوینت
        
    Returns:
        bool: موفقیت یا شکست ارسال درخواست
    """
    try:
        logger.info(f"ارسال درخواست به {endpoint}...")
        response = requests.get(endpoint, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                logger.info(f"درخواست با موفقیت ارسال شد: {result.get('message', '')}")
                return True
            else:
                logger.error(f"خطا در ارسال درخواست: {result.get('message', 'خطای ناشناخته')}")
                return False
        else:
            logger.error(f"خطا در ارسال درخواست. کد وضعیت: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"خطا در ارسال درخواست: {str(e)}")
        return False

def send_price_report():
    """
    ارسال گزارش قیمت‌ها
    
    Returns:
        bool: موفقیت یا شکست ارسال گزارش
    """
    return send_request(PRICE_REPORT_ENDPOINT)

def send_system_report():
    """
    ارسال گزارش سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال گزارش
    """
    return send_request(SYSTEM_REPORT_ENDPOINT)

def send_test_message():
    """
    ارسال پیام تست
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    return send_request(TEST_MESSAGE_ENDPOINT)

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("زمان‌بندی تلگرام Replit شروع شد")
    
    # ارسال یک پیام تست در ابتدا
    send_test_message()
    
    # شمارنده برای ارسال گزارش سیستم هر ۶ ساعت (۳۶ بار ۱۰ دقیقه)
    system_report_counter = 0
    
    try:
        while True:
            # ارسال گزارش قیمت
            success = send_price_report()
            logger.info(f"گزارش قیمت ارسال شد: {success}")
            
            # افزایش شمارنده
            system_report_counter += 1
            
            # اگر ۶ ساعت (۳۶ بار ۱۰ دقیقه) گذشته، گزارش سیستم ارسال کن
            if system_report_counter >= 36:
                send_system_report()
                system_report_counter = 0
            
            # ۱۰ دقیقه صبر کن
            logger.info("در حال انتظار برای ۱۰ دقیقه...")
            time.sleep(600)  # 10 minutes = 600 seconds
                
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()