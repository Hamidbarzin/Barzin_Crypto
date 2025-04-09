"""
تست ساده نشانگر قابلیت اطمینان تلگرام
"""

import json
import os
import logging

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_reliability")

try:
    # تلاش برای بارگذاری کلاس نشانگر
    from crypto_bot.telegram_reliability_monitor import TelegramReliabilityMonitor
    
    logger.info("کلاس TelegramReliabilityMonitor با موفقیت بارگذاری شد")
    
    # ایجاد یک نمونه
    data_file = "test_reliability_data.json"
    monitor = TelegramReliabilityMonitor(file_path=data_file)
    
    # ثبت یک پیام موفق
    monitor.record_message_attempt("test_message", True)
    logger.info("یک پیام موفق ثبت شد")
    
    # دریافت آمار
    stats = monitor.get_reliability_stats()
    logger.info("آمار با موفقیت دریافت شد")
    
    # بررسی فایل
    if os.path.exists(data_file):
        file_size = os.path.getsize(data_file)
        logger.info(f"فایل داده‌ها ایجاد شده است: {data_file} (اندازه: {file_size} بایت)")
    else:
        logger.error(f"فایل داده‌ها ایجاد نشده است: {data_file}")
        
except ImportError as e:
    logger.error(f"خطا در بارگذاری ماژول: {e}")
except Exception as e:
    logger.error(f"خطا در تست: {e}")

logger.info("تست به پایان رسید.")