"""
تست ماژول replit_telegram_sender با استفاده از ماژول نشانگر قابلیت اطمینان ساده‌سازی شده
"""

import logging
from replit_telegram_sender import send_test_message, get_reliability_summary

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_replit_telegram")

def main():
    """تست ارسال پیام و دریافت خلاصه قابلیت اطمینان"""
    
    logger.info("شروع تست ارسال پیام...")
    
    # ارسال پیام تست
    result = send_test_message()
    
    if result:
        logger.info("پیام تست با موفقیت ارسال شد")
    else:
        logger.error("خطا در ارسال پیام تست")
        
    # دریافت و نمایش خلاصه قابلیت اطمینان
    try:
        summary = get_reliability_summary()
        print("\nخلاصه قابلیت اطمینان:")
        print(summary)
    except Exception as e:
        logger.error(f"خطا در دریافت خلاصه قابلیت اطمینان: {e}")
    
    logger.info("تست به پایان رسید")

if __name__ == "__main__":
    main()