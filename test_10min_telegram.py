"""
تست ارسال پیام به تلگرام هر ۱۰ دقیقه

این اسکریپت یک نسخه ساده از اسکریپت ten_minute_reporter است
که برای دیباگ مشکل ارسال گزارش‌های ۱۰ دقیقه‌ای طراحی شده است.
"""

import os
import time
import logging
from datetime import datetime

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_10min_telegram.log"),
    ]
)

logger = logging.getLogger("test_10min_telegram")

# بررسی متغیرهای محیطی
logger.info(f"TELEGRAM_BOT_TOKEN: {os.environ.get('TELEGRAM_BOT_TOKEN', 'تنظیم نشده')[:10]}...")
logger.info(f"DEFAULT_CHAT_ID: {os.environ.get('DEFAULT_CHAT_ID', 'تنظیم نشده')}")

# وارد کردن ماژول‌های مورد نیاز برای گزارش‌دهی
from crypto_bot.telegram_service import send_telegram_message

def get_current_time():
    """
    دریافت زمان فعلی به فرمت مناسب
    
    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def send_test_message():
    """
    ارسال پیام تست به تلگرام
    
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    try:
        chat_id = os.environ.get('DEFAULT_CHAT_ID')
        if not chat_id:
            logger.error("چت آیدی پیش‌فرض تنظیم نشده است")
            return False
            
        message = f"🧪 پیام تست از اسکریپت دیباگ تلگرام\n\n"
        message += f"این یک پیام تست ساده برای دیباگ مشکل ارسال گزارش‌های ۱۰ دقیقه‌ای است.\n\n"
        message += f"⏱ زمان: {get_current_time()}\n"
        message += f"🆔 چت آیدی: {chat_id}\n"
        message += f"🔄 اجرا: {int(datetime.now().timestamp())}"
        
        success = send_telegram_message(chat_id=int(chat_id), message=message)
        if success:
            logger.info(f"پیام تست با موفقیت به چت {chat_id} ارسال شد")
        else:
            logger.error(f"خطا در ارسال پیام تست به چت {chat_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تست: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع تست دیباگ تلگرام...")
    
    # ارسال یک پیام اولیه
    logger.info("ارسال پیام تست اولیه...")
    send_test_message()
    
    # شمارنده برای ارسال پیام‌ها
    counter = 1
    
    # حلقه بی‌نهایت
    try:
        while True:
            # اطلاعات انتظار
            delay = 5 * 60  # 5 دقیقه
            logger.info(f"انتظار برای {delay} ثانیه تا ارسال پیام بعدی...")
            time.sleep(delay)
            
            # ارسال پیام بعدی
            counter += 1
            logger.info(f"ارسال پیام تست شماره {counter}...")
            send_test_message()
            
    except KeyboardInterrupt:
        logger.info("تست با درخواست کاربر متوقف شد")
    except Exception as e:
        logger.critical(f"خطای جدی در اجرای تست: {str(e)}")

if __name__ == "__main__":
    main()