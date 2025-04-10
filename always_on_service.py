#!/usr/bin/env python3
"""
سرویس همیشه روشن برای Crypto Barzin

این اسکریپت زمان‌بندی تلگرام را به صورت خودکار راه‌اندازی می‌کند،
حتی بعد از راه‌اندازی مجدد سرور یا خاموش شدن آن.
"""

import os
import time
import signal
import logging
import requests
import subprocess
import atexit
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("always_on_service")

# فایل قفل برای جلوگیری از اجرای همزمان چند نسخه
LOCK_FILE = '.smart_bot_lock'
PID_FILE = '.smart_bot_pid'

# تعیین URL
BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")
TELEGRAM_STATUS_URL = f"{BASE_URL}/api/telegram/status"
TELEGRAM_START_URL = f"{BASE_URL}/api/telegram/start"

def is_service_running():
    """
    بررسی اینکه آیا سرویس در حال اجراست
    
    Returns:
        bool: آیا سرویس در حال اجراست
    """
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            # بررسی اینکه آیا پروسه با این PID در حال اجراست
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # پروسه وجود ندارد
                return False
        return False
    except Exception as e:
        logger.error(f"خطا در بررسی وضعیت سرویس: {str(e)}")
        return False

def acquire_lock():
    """
    گرفتن قفل برای جلوگیری از اجرای همزمان چند نسخه
    
    Returns:
        bool: آیا قفل گرفته شد
    """
    try:
        if os.path.exists(LOCK_FILE):
            # بررسی زمان آخرین اصلاح فایل قفل
            lock_time = os.path.getmtime(LOCK_FILE)
            current_time = time.time()
            
            # اگر قفل بیشتر از 1 ساعت قدیمی است، آن را نادیده بگیر
            if current_time - lock_time > 3600:
                logger.warning("قفل قدیمی شناسایی شد. قفل حذف می‌شود.")
                os.remove(LOCK_FILE)
            else:
                logger.warning("سرویس قبلاً در حال اجراست.")
                return False
                
        # ایجاد فایل قفل
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
            
        # ذخیره PID فرآیند فعلی
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
            
        logger.info(f"قفل سرویس با PID {os.getpid()} ایجاد شد.")
        return True
    except Exception as e:
        logger.error(f"خطا در ایجاد قفل: {str(e)}")
        return False

def release_lock():
    """
    آزاد کردن قفل
    """
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        logger.info("قفل سرویس آزاد شد.")
    except Exception as e:
        logger.error(f"خطا در آزاد کردن قفل: {str(e)}")

def check_telegram_service():
    """
    بررسی وضعیت سرویس تلگرام
    
    Returns:
        bool: آیا سرویس فعال است
    """
    try:
        logger.info("بررسی وضعیت سرویس تلگرام...")
        response = requests.get(TELEGRAM_STATUS_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('running', False)
        return False
    except Exception as e:
        logger.error(f"خطا در بررسی وضعیت سرویس تلگرام: {str(e)}")
        return False

def start_telegram_service():
    """
    راه‌اندازی سرویس تلگرام
    
    Returns:
        bool: آیا راه‌اندازی موفق بود
    """
    try:
        logger.info("راه‌اندازی سرویس تلگرام...")
        response = requests.get(TELEGRAM_START_URL, timeout=10)
        
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
    logger.info("سرویس همیشه روشن شروع شد")
    
    # ثبت تابع آزادسازی قفل در هنگام خروج
    atexit.register(release_lock)
    
    # گرفتن قفل
    if not acquire_lock():
        logger.error("ناتوانی در گرفتن قفل. سرویس متوقف می‌شود.")
        return 1
    
    try:
        # حلقه اصلی برنامه
        while True:
            # بررسی وضعیت سرویس تلگرام
            if not check_telegram_service():
                logger.warning("سرویس تلگرام فعال نیست. تلاش برای راه‌اندازی...")
                start_telegram_service()
            else:
                logger.info("سرویس تلگرام فعال است.")
                
            # انتظار برای بررسی بعدی (هر 5 دقیقه)
            logger.info(f"انتظار برای 5 دقیقه بعدی ({datetime.now().strftime('%H:%M:%S')})...")
            time.sleep(300)  # 5 minutes = 300 seconds
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        return 1
    finally:
        # آزاد کردن قفل در هنگام خروج
        release_lock()
        
    return 0

if __name__ == "__main__":
    main()