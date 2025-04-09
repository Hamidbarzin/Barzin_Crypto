#!/usr/bin/env python3
"""
فراخوانی اندپوینت‌های API تلگرام

این اسکریپت برای فراخوانی اندپوینت‌های API تلگرام استفاده می‌شود.
می‌توان آن را به عنوان یک کار زمان‌بندی شده اجرا کرد.
"""

import sys
import requests
import logging
import datetime
import pytz

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("api_caller.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_caller")

# تنظیم منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')
now_toronto = datetime.datetime.now(toronto_tz)

def call_api(url):
    """
    فراخوانی یک API
    
    Args:
        url (str): آدرس API
        
    Returns:
        dict: پاسخ API
    """
    try:
        logger.info(f"فراخوانی {url}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"خطا در فراخوانی API. کد وضعیت: {response.status_code}")
            return {"success": False, "message": f"خطا در فراخوانی API. کد وضعیت: {response.status_code}"}
    except Exception as e:
        logger.error(f"خطا در فراخوانی API: {str(e)}")
        return {"success": False, "message": f"خطا در فراخوانی API: {str(e)}"}

def main():
    """
    تابع اصلی برنامه
    """
    if len(sys.argv) < 2:
        logger.error("خطا: باید یک آدرس API به عنوان آرگومان ارائه شود.")
        print("استفاده: python api_caller.py <api_url>")
        return 1
    
    api_url = sys.argv[1]
    logger.info(f"زمان اجرا: {now_toronto.strftime('%Y-%m-%d %H:%M:%S')} (تورنتو)")
    
    response = call_api(api_url)
    logger.info(f"پاسخ: {response}")
    
    if response.get("success", False):
        logger.info("فراخوانی API با موفقیت انجام شد.")
        return 0
    else:
        logger.error("خطا در فراخوانی API.")
        return 1

if __name__ == "__main__":
    sys.exit(main())