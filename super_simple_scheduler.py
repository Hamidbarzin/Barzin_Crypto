#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
زمان‌بندی بسیار ساده برای ارسال گزارش‌های دوره‌ای تلگرام
"""

import time
import logging
import subprocess
import sys
import traceback

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("super_simple_scheduler.log")
    ]
)
logger = logging.getLogger("super_simple_scheduler")

def send_telegram_test():
    """ارسال پیام تست تلگرام"""
    try:
        logger.info("در حال ارسال پیام تست تلگرام...")
        result = subprocess.run(['python', 'telegram_reporter.py', 'test'], 
                               capture_output=True, text=True, check=True)
        logger.info(f"پیام تست با موفقیت ارسال شد: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در ارسال پیام تست: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"خطای نامشخص در ارسال پیام تست: {str(e)}")
        return False

def send_telegram_report():
    """ارسال گزارش دوره‌ای تلگرام"""
    try:
        logger.info("در حال ارسال گزارش دوره‌ای تلگرام...")
        result = subprocess.run(['python', 'telegram_reporter.py'], 
                               capture_output=True, text=True, check=True)
        logger.info(f"گزارش دوره‌ای با موفقیت ارسال شد: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در ارسال گزارش دوره‌ای: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"خطای نامشخص در ارسال گزارش دوره‌ای: {str(e)}")
        return False

def main():
    """تابع اصلی برنامه"""
    try:
        # ارسال یک پیام تست در ابتدا
        logger.info("شروع زمان‌بندی بسیار ساده...")
        send_telegram_test()
        
        # ارسال گزارش اولیه
        send_telegram_report()
        
        # شمارنده برای زمان‌بندی هر 30 دقیقه
        counter = 0
        
        # حلقه اصلی
        while True:
            # انتظار 60 ثانیه (1 دقیقه)
            time.sleep(60)
            
            # افزایش شمارنده
            counter += 1
            
            # هر 30 دقیقه یک بار گزارش ارسال کن
            if counter >= 30:
                send_telegram_report()
                counter = 0
            
            # هر 15 دقیقه یک بار وضعیت را لاگ کن
            if counter % 15 == 0:
                logger.info(f"زمان‌بندی فعال است. {30 - counter} دقیقه تا گزارش بعدی باقی مانده است.")
                
    except KeyboardInterrupt:
        logger.info("خروج از برنامه با دستور کاربر...")
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطای غیرمنتظره: {str(e)}\n{error_text}")
    finally:
        logger.info("پایان اجرای زمان‌بندی بسیار ساده.")

if __name__ == "__main__":
    main()