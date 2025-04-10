#!/usr/bin/env python3
"""
ورک‌فلوی ارسال پیام تلگرام برای Crypto Barzin

این اسکریپت به عنوان یک ورک‌فلو در Replit اجرا می‌شود و
به طور منظم گزارش‌های قیمت را به تلگرام ارسال می‌کند.
"""

import os
import time
import logging
import requests
import datetime
import pytz

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_workflow")

# تعیین URL پایه
BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")

# لیست API endpoint های قابل فراخوانی
API_ENDPOINTS = {
    "price_report": f"{BASE_URL}/api/telegram/price_report",
    "system_report": f"{BASE_URL}/api/telegram/system_report",
    "technical_analysis": f"{BASE_URL}/api/telegram/technical_analysis",
    "trading_signals": f"{BASE_URL}/api/telegram/trading_signals",
    "news": f"{BASE_URL}/api/telegram/send_news",
    "check_alerts": f"{BASE_URL}/api/price-alerts/check"
}

# منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')

def call_endpoint(url):
    """
    فراخوانی یک endpoint از API
    
    Args:
        url (str): آدرس API
        
    Returns:
        bool: موفقیت یا شکست
    """
    try:
        logger.info(f"فراخوانی {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                logger.info(f"فراخوانی {url} با موفقیت انجام شد")
                return True
            else:
                logger.error(f"خطا در فراخوانی {url}: {data.get('message', 'خطای ناشناخته')}")
                return False
        else:
            logger.error(f"خطا در فراخوانی {url}. کد وضعیت: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"استثنا در فراخوانی {url}: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("ورک‌فلوی ارسال پیام تلگرام آغاز شد")
    
    # بررسی زمان فعلی در تورنتو
    toronto_time = datetime.datetime.now(toronto_tz)
    hour = toronto_time.hour
    
    # بررسی ساعات فعال (8 صبح تا 10 شب تورنتو)
    if 8 <= hour < 22:
        logger.info(f"زمان فعلی تورنتو: {toronto_time.strftime('%H:%M:%S')} - در محدوده ساعات فعال")
        
        # ارسال گزارش قیمت
        call_endpoint(API_ENDPOINTS["price_report"])
        
        # بررسی هشدارهای قیمت
        call_endpoint(API_ENDPOINTS["check_alerts"])
        
        # بر اساس ساعت، گزارش‌های دیگر را ارسال کن
        if hour % 6 == 0:  # هر 6 ساعت
            call_endpoint(API_ENDPOINTS["system_report"])
            
        if hour % 2 == 0:  # هر 2 ساعت
            call_endpoint(API_ENDPOINTS["technical_analysis"])
            
        if hour % 4 == 0:  # هر 4 ساعت
            call_endpoint(API_ENDPOINTS["trading_signals"])
            
        if hour % 8 == 0:  # هر 8 ساعت
            call_endpoint(API_ENDPOINTS["news"])
    else:
        logger.info(f"زمان فعلی تورنتو: {toronto_time.strftime('%H:%M:%S')} - خارج از محدوده ساعات فعال")
    
    logger.info("اجرای ورک‌فلو به پایان رسید")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"خطا در اجرای ورک‌فلو: {str(e)}")