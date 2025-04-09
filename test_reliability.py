"""
تست نشانگر قابلیت اطمینان تلگرام

این اسکریپت برای تست مستقیم ماژول نشانگر قابلیت اطمینان استفاده می‌شود.
"""

import json
import os
import logging

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_reliability")

try:
    from crypto_bot.telegram_reliability_monitor import (
        record_message_attempt,
        record_service_restart,
        get_reliability_stats,
        get_reliability_summary
    )
    
    logger.info("ماژول نشانگر قابلیت اطمینان با موفقیت بارگذاری شد")
    
    # ثبت چند رویداد تستی
    record_message_attempt("test_message", True)
    record_message_attempt("price_report", True)
    record_message_attempt("system_report", True)
    record_message_attempt("technical_analysis", False, "خطای تست")
    
    # ثبت راه‌اندازی مجدد سرویس
    record_service_restart()
    
    # دریافت آمار
    stats = get_reliability_stats()
    print("آمار قابلیت اطمینان:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # دریافت خلاصه
    summary = get_reliability_summary()
    print("\nخلاصه قابلیت اطمینان:")
    print(summary)
    
    # بررسی فایل ذخیره‌سازی
    data_file = "telegram_reliability_data.json"
    if os.path.exists(data_file):
        file_size = os.path.getsize(data_file)
        print(f"\nفایل داده‌ها ایجاد شده است: {data_file}")
        print(f"اندازه فایل: {file_size} بایت")
        
        # نمایش محتوای فایل
        with open(data_file, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
            print("\nمحتوای فایل:")
            print(json.dumps(file_content, ensure_ascii=False, indent=2))
    else:
        print(f"\nفایل داده‌ها ایجاد نشده است: {data_file}")
    
except ImportError as e:
    logger.error(f"خطا در بارگذاری ماژول نشانگر قابلیت اطمینان: {e}")
except Exception as e:
    logger.error(f"خطا در تست نشانگر قابلیت اطمینان: {e}")

print("\nتست نشانگر قابلیت اطمینان به پایان رسید.")