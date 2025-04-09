"""
تست نسخه ساده‌سازی شده نشانگر قابلیت اطمینان
"""

import json
import os
import logging

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_simple_reliability")

try:
    from crypto_bot.simple_reliability_monitor import (
        record_message_attempt,
        record_service_restart,
        get_reliability_stats,
        get_reliability_summary
    )
    
    logger.info("ماژول نشانگر قابلیت اطمینان ساده‌سازی شده با موفقیت بارگذاری شد")
    
    # ثبت چند رویداد تستی
    record_message_attempt("test_message", True)
    logger.info("رویداد تست 1 ثبت شد")
    
    record_message_attempt("price_report", True)
    logger.info("رویداد تست 2 ثبت شد")
    
    record_message_attempt("technical_analysis", False, "خطای تست")
    logger.info("رویداد تست 3 ثبت شد")
    
    # ثبت راه‌اندازی مجدد سرویس
    record_service_restart()
    logger.info("راه‌اندازی مجدد سرویس ثبت شد")
    
    # دریافت آمار
    stats = get_reliability_stats()
    logger.info("آمار دریافت شد")
    
    # نمایش آمار
    print("آمار قابلیت اطمینان:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # دریافت خلاصه
    summary = get_reliability_summary()
    logger.info("خلاصه دریافت شد")
    
    # نمایش خلاصه
    print("\nخلاصه قابلیت اطمینان:")
    print(summary)
    
    # بررسی فایل ذخیره‌سازی
    data_file = "simple_reliability_data.json"
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