#!/usr/bin/env python3
"""
فرستنده پیام تلگرام هر ۱۰ دقیقه

این اسکریپت هر ۱۰ دقیقه یک گزارش قیمت را به تلگرام ارسال می‌کند.
همچنین هر ۶ ساعت یک گزارش وضعیت سیستم ارسال می‌کند.
"""

import time
import requests
import logging
import random
import os
import signal
import sys
from datetime import datetime
import pytz  # برای کار با منطقه‌های زمانی مختلف

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("ten_minute_telegram_sender.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ten_minute_telegram_sender")

# تنظیمات API
BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")
PRICE_REPORT_URL = f"{BASE_URL}/send_price_report"
SYSTEM_REPORT_URL = f"{BASE_URL}/send_system_report"
TEST_MESSAGE_URL = f"{BASE_URL}/send_test_message_replit"

# تنظیمات PID
PID_FILE = "ten_minute_telegram_sender.pid"

def send_request(url):
    """
    ارسال درخواست به API
    
    Args:
        url (str): آدرس API
        
    Returns:
        bool: موفقیت یا شکست ارسال درخواست
    """
    try:
        logger.info(f"ارسال درخواست به {url}...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                logger.info(f"درخواست با موفقیت ارسال شد: {data.get('message', '')}")
                return True
            else:
                logger.error(f"خطا در ارسال درخواست: {data.get('message', 'خطای ناشناخته')}")
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
    return send_request(PRICE_REPORT_URL)

def send_system_report():
    """
    ارسال گزارش سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال گزارش
    """
    return send_request(SYSTEM_REPORT_URL)

def send_test_message():
    """
    ارسال پیام تست
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    return send_request(TEST_MESSAGE_URL)

def save_pid():
    """
    ذخیره شناسه فرآیند برای کنترل اجرا
    """
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))
    logger.info(f"PID {pid} در فایل {PID_FILE} ذخیره شد")

def cleanup_pid():
    """
    پاکسازی فایل PID هنگام خروج
    """
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logger.info(f"فایل PID {PID_FILE} پاک شد")

def signal_handler(sig, frame):
    """
    مدیریت سیگنال‌های سیستم عامل
    """
    logger.info(f"سیگنال {sig} دریافت شد. در حال خروج...")
    cleanup_pid()
    sys.exit(0)

def main():
    """
    تابع اصلی برنامه
    """
    # ثبت هندلر سیگنال‌ها
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ذخیره PID
    save_pid()
    
    logger.info("سرویس ارسال پیام تلگرام هر ۱۰ دقیقه شروع شد")
    
    # ارسال پیام تست در ابتدا
    send_test_message()
    
    # شمارنده برای ارسال گزارش سیستم هر ۶ ساعت (۳۶ بار ۱۰ دقیقه)
    system_report_counter = 0
    
    try:
        while True:
            try:
                # ارسال گزارش قیمت
                success = send_price_report()
                logger.info(f"گزارش قیمت ارسال شد: {success}")
                
                # افزایش شمارنده
                system_report_counter += 1
                
                # اگر ۶ ساعت (۳۶ بار ۱۰ دقیقه) گذشته، گزارش سیستم ارسال کن
                if system_report_counter >= 36:
                    send_system_report()
                    system_report_counter = 0
                
                # ۱۰ دقیقه صبر کن - نمایش زمان تورنتو
                toronto_timezone = pytz.timezone('America/Toronto')
                toronto_time = datetime.now(toronto_timezone)
                logger.info(f"انتظار برای ۱۰ دقیقه بعدی ({toronto_time.strftime('%H:%M:%S')} تورنتو)...")
                time.sleep(600)  # 10 minutes = 600 seconds
            except Exception as e:
                logger.error(f"خطا در اجرای چرخه اصلی: {str(e)}")
                time.sleep(60)  # در صورت خطا، ۱ دقیقه صبر کن و دوباره تلاش کن
    
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    finally:
        cleanup_pid()
    
    return 0

if __name__ == "__main__":
    main()