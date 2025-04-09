"""
تست گزارش‌های قابلیت اطمینان با استفاده از ماژول نشانگر قابلیت اطمینان ساده‌سازی شده
"""

import logging
import time
from replit_telegram_sender import (
    send_price_report, 
    send_system_report, 
    send_technical_analysis, 
    send_trading_signals,
    get_reliability_stats
)
import json

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_reliability_reports")

def main():
    """تست ارسال انواع گزارش‌ها و دریافت آمار قابلیت اطمینان"""
    
    logger.info("شروع تست ارسال گزارش‌ها...")
    
    # ارسال گزارش قیمت
    logger.info("ارسال گزارش قیمت...")
    result = send_price_report()
    logger.info(f"نتیجه ارسال گزارش قیمت: {'موفق' if result else 'ناموفق'}")
    time.sleep(3)  # فاصله بین ارسال پیام‌ها
    
    # ارسال گزارش سیستم
    logger.info("ارسال گزارش سیستم...")
    result = send_system_report()
    logger.info(f"نتیجه ارسال گزارش سیستم: {'موفق' if result else 'ناموفق'}")
    time.sleep(3)  # فاصله بین ارسال پیام‌ها
    
    # ارسال تحلیل تکنیکال
    logger.info("ارسال تحلیل تکنیکال...")
    result = send_technical_analysis("BTC/USDT")
    logger.info(f"نتیجه ارسال تحلیل تکنیکال: {'موفق' if result else 'ناموفق'}")
    time.sleep(3)  # فاصله بین ارسال پیام‌ها
    
    # ارسال سیگنال‌های معاملاتی
    logger.info("ارسال سیگنال‌های معاملاتی...")
    result = send_trading_signals()
    logger.info(f"نتیجه ارسال سیگنال‌های معاملاتی: {'موفق' if result else 'ناموفق'}")
    
    # دریافت و نمایش آمار قابلیت اطمینان
    try:
        stats = get_reliability_stats()
        logger.info("آمار قابلیت اطمینان دریافت شد")
        
        print("\nآمار قابلیت اطمینان:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"خطا در دریافت آمار قابلیت اطمینان: {e}")
    
    logger.info("تست به پایان رسید")

if __name__ == "__main__":
    main()