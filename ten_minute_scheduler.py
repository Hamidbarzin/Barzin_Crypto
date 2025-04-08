#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
زمان‌بندی ارسال گزارش‌های سه لایه‌ای هر ۱۰ دقیقه به تلگرام

این اسکریپت به طور خودکار گزارش‌های سه لایه‌ای هر ۱۰ دقیقه به تلگرام ارسال می‌کند.
"""

import os
import time
import schedule
import logging
import traceback
import random
import sys
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ten_minute_scheduler.log")
    ]
)
logger = logging.getLogger("ten_minute_scheduler")

def send_enhanced_report():
    """
    ارسال گزارش سه لایه‌ای هر ۱۰ دقیقه
    """
    try:
        logger.info("در حال ارسال گزارش سه لایه‌ای...")
        # استفاده از ماژول enhanced_telegram_reporter
        import enhanced_telegram_reporter
        result = enhanced_telegram_reporter.send_three_layer_report()
        logger.info(f"نتیجه ارسال گزارش سه لایه‌ای: {result}")
        return result
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش سه لایه‌ای: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_alive_message():
    """
    ارسال پیام زنده بودن سیستم هر 6 ساعت
    """
    try:
        logger.info("در حال ارسال پیام زنده بودن سیستم...")
        
        message = f"""
🤖 *وضعیت سیستم*

سیستم ربات گزارش‌دهی سه لایه‌ای در حال اجرا است.
زمان کنونی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

این پیام به صورت خودکار هر 6 ساعت ارسال می‌شود.
گزارش‌های اصلی هر ۱۰ دقیقه یکبار ارسال می‌شوند.
        """
        
        # ارسال پیام به تلگرام
        from crypto_bot.telegram_service import send_telegram_message
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        # اگر چت آیدی در متغیرهای محیطی نباشد، از مقدار پیش‌فرض استفاده می‌کنیم
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        result = send_telegram_message(chat_id, message)
        logger.info(f"نتیجه ارسال پیام زنده بودن سیستم: {result}")
        return result
    except Exception as e:
        logger.error(f"خطا در ارسال پیام زنده بودن سیستم: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def setup_schedule():
    """
    تنظیم زمان‌بندی وظایف
    """
    logger.info("در حال تنظیم زمان‌بندی وظایف...")
    
    # ارسال گزارش سه لایه‌ای هر ۱۰ دقیقه
    schedule.every(10).minutes.do(send_enhanced_report)
    
    # ارسال پیام زنده بودن سیستم هر 6 ساعت
    schedule.every(6).hours.do(send_alive_message)
    
    logger.info("زمان‌بندی وظایف با موفقیت تنظیم شد")
    
    # ارسال اولین گزارش بلافاصله
    send_enhanced_report()

def save_pid():
    """
    ذخیره شناسه فرآیند برای کنترل اجرا
    """
    with open("ten_minute_scheduler.pid", "w") as f:
        f.write(str(os.getpid()))
    logger.info(f"شناسه فرآیند ذخیره شد: {os.getpid()}")

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع اجرای برنامه زمان‌بندی گزارش‌های ۱۰ دقیقه‌ای")
    
    # ذخیره شناسه فرآیند
    save_pid()
    
    # ارسال یک پیام تست برای اطمینان از عملکرد صحیح
    import enhanced_telegram_reporter
    logger.info("در حال ارسال پیام تست...")
    test_result = enhanced_telegram_reporter.send_test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # تنظیم زمان‌بندی وظایف
    setup_schedule()
    
    # اجرای زمان‌بندی
    try:
        logger.info("در حال اجرای زمان‌بندی...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # بررسی هر دقیقه
    except KeyboardInterrupt:
        logger.info("برنامه زمان‌بندی با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه زمان‌بندی: {str(e)}")
        logger.error(traceback.format_exc())
    
    logger.info("پایان اجرای برنامه زمان‌بندی گزارش‌های ۱۰ دقیقه‌ای")

if __name__ == "__main__":
    main()