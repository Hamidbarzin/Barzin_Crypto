#!/usr/bin/env python3
"""
ارسال خودکار پیام تلگرام با فاصله زمانی منظم

این اسکریپت هر ۱۰ دقیقه یک گزارش قیمت و هر ۶ ساعت یک گزارش وضعیت سیستم 
به تلگرام ارسال می‌کند.
"""

import time
import requests
import logging
import datetime
import pytz
import os
import signal
import sys
import atexit

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("auto_telegram_sender.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auto_telegram_sender")

# تنظیم منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')

# تنظیم URL ها
BASE_URL = "http://localhost:5000"
PRICE_REPORT_URL = f"{BASE_URL}/send_price_report"
SYSTEM_REPORT_URL = f"{BASE_URL}/send_system_report"
TEST_MESSAGE_URL = f"{BASE_URL}/send_test_message_replit"

# ذخیره PID
def save_pid():
    """ذخیره PID در فایل"""
    pid = os.getpid()
    with open("auto_telegram_sender.pid", "w") as pid_file:
        pid_file.write(str(pid))
    logger.info(f"PID {pid} در فایل auto_telegram_sender.pid ذخیره شد")

# پاکسازی فایل PID
def cleanup_pid():
    """پاکسازی فایل PID هنگام خروج"""
    try:
        os.remove("auto_telegram_sender.pid")
        logger.info("فایل PID پاکسازی شد")
    except FileNotFoundError:
        pass

# تنظیم مدیریت خروج
atexit.register(cleanup_pid)

# مدیریت سیگنال های سیستم عامل
def signal_handler(sig, frame):
    """مدیریت سیگنال‌های سیستم عامل"""
    logger.info(f"سیگنال {sig} دریافت شد. در حال خروج...")
    cleanup_pid()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def call_api(url):
    """
    فراخوانی یک API
    
    Args:
        url (str): آدرس API
        
    Returns:
        dict: پاسخ API یا None در صورت خطا
    """
    try:
        logger.info(f"فراخوانی {url}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"پاسخ: {data}")
            return data
        else:
            logger.error(f"خطا در فراخوانی API. کد وضعیت: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"خطا در فراخوانی API: {str(e)}")
        return None

def main():
    """
    تابع اصلی برنامه
    """
    # ذخیره PID
    save_pid()
    
    # نمایش اطلاعات شروع
    now_toronto = datetime.datetime.now(toronto_tz)
    logger.info(f"سرویس ارسال خودکار پیام تلگرام شروع شد ({now_toronto.strftime('%Y-%m-%d %H:%M:%S')} تورنتو)")
    
    # ارسال پیام تست در ابتدا
    logger.info("ارسال پیام تست اولیه...")
    result = call_api(TEST_MESSAGE_URL)
    if result and result.get("success", False):
        logger.info("پیام تست با موفقیت ارسال شد")
    else:
        logger.error("خطا در ارسال پیام تست")
    
    # شمارنده برای گزارش سیستم (هر ۳۶ بار یا ۶ ساعت)
    system_report_counter = 0
    
    try:
        while True:
            now_toronto = datetime.datetime.now(toronto_tz)
            
            # ارسال گزارش قیمت
            logger.info("ارسال گزارش قیمت...")
            result = call_api(PRICE_REPORT_URL)
            if result and result.get("success", False):
                logger.info("گزارش قیمت با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال گزارش قیمت")
            
            # افزایش شمارنده گزارش سیستم
            system_report_counter += 1
            
            # ارسال گزارش سیستم هر ۶ ساعت
            if system_report_counter >= 36:
                logger.info("ارسال گزارش سیستم...")
                result = call_api(SYSTEM_REPORT_URL)
                if result and result.get("success", False):
                    logger.info("گزارش سیستم با موفقیت ارسال شد")
                else:
                    logger.error("خطا در ارسال گزارش سیستم")
                
                system_report_counter = 0
            
            # انتظار برای ۱۰ دقیقه بعدی
            next_run = now_toronto + datetime.timedelta(minutes=10)
            logger.info(f"انتظار برای ۱۰ دقیقه بعدی ({next_run.strftime('%H:%M:%S')} تورنتو)...")
            time.sleep(600)  # 10 دقیقه = 600 ثانیه
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())