#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی خودکار برای اطمینان از اجرای سرویس‌های مهم در Replit

این اسکریپت باید به عنوان یک ورک‌فلو اجرا شود و تضمین می‌کند که سرویس‌های 
مهم حتی پس از راه‌اندازی مجدد یا خاموشی سرور اجرا می‌شوند.
"""

import os
import time
import logging
import requests
import subprocess
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("startup_script")

# تعیین URL پایه - از localhost استفاده نمی‌کنیم چون در replit محیط‌های مختلف هستند
BASE_URL = os.environ.get("APP_URL", "https://456c040e-8bc3-434b-9dda-ccfefc1876f5-00-3po21xtoto5mt.picard.replit.dev")

def check_server_ready():
    """
    بررسی اینکه آیا سرور Flask آماده است
    
    Returns:
        bool: آیا سرور آماده است
    """
    try:
        logger.info("بررسی آمادگی سرور...")
        # سعی در دسترسی به صفحه اصلی
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"سرور هنوز آماده نیست: {str(e)}")
        return False

def start_telegram_service():
    """
    راه‌اندازی سرویس تلگرام
    
    Returns:
        bool: آیا راه‌اندازی موفق بود
    """
    try:
        logger.info("راه‌اندازی سرویس تلگرام...")
        response = requests.get(f"{BASE_URL}/api/telegram/start", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                logger.info("سرویس تلگرام با موفقیت راه‌اندازی شد.")
                return True
            else:
                logger.error(f"خطا در راه‌اندازی سرویس تلگرام: {data.get('message', 'خطای ناشناخته')}")
                return False
        else:
            logger.error(f"خطا در فراخوانی API. کد وضعیت: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی سرویس تلگرام: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("اسکریپت راه‌اندازی خودکار شروع شد")
    
    # انتظار برای آماده شدن سرور
    server_ready = False
    max_retries = 15
    retry_count = 0
    
    while not server_ready and retry_count < max_retries:
        server_ready = check_server_ready()
        if not server_ready:
            retry_count += 1
            wait_time = 5  # ۵ ثانیه
            logger.info(f"انتظار برای {wait_time} ثانیه... (تلاش {retry_count}/{max_retries})")
            time.sleep(wait_time)
    
    if not server_ready:
        logger.error(f"سرور پس از {max_retries} تلاش آماده نشد. خروج از اسکریپت.")
        return 1
    
    # راه‌اندازی سرویس‌های ضروری
    logger.info("سرور آماده است. راه‌اندازی سرویس‌های ضروری...")
    
    # راه‌اندازی سرویس تلگرام
    start_telegram_service()
    
    # در اینجا می‌توانید سرویس‌های دیگر را نیز راه‌اندازی کنید
    
    logger.info("همه سرویس‌های ضروری راه‌اندازی شدند. اسکریپت راه‌اندازی با موفقیت به پایان رسید.")
    return 0

if __name__ == "__main__":
    main()