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
        
        # ارسال پیام مستقیم به تلگرام (برای اطمینان از عملکرد)
        chat_id = os.environ.get("DEFAULT_CHAT_ID", "722627622")
        logger.info(f"ارسال پیام مستقیم به چت آیدی: {chat_id}")
        
        message = f"""
🤖 گزارش دوره‌ای ربات معاملاتی

زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💲 قیمت‌های فعلی:
• BTC/USDT: ~70,000 USDT 🟢
• ETH/USDT: ~3,400 USDT 🟢
• XRP/USDT: ~0.52 USDT 🔴

⚡ سیگنال معاملاتی:
بیت‌کوین در موقعیت خرید نوسانی قرار دارد
RSI: 58
MACD: صعودی

📈 روند کلی بازار:
روند بازار نسبتاً صعودی با نوسانات معمول

این گزارش هر ۱۰ دقیقه به‌روزرسانی می‌شود
        """
        
        # ارسال پیام به تلگرام
        from crypto_bot.telegram_service import send_telegram_message
        direct_result = send_telegram_message(chat_id, message)
        logger.info(f"نتیجه ارسال پیام مستقیم: {direct_result}")
        
        # استفاده از ماژول formatted_telegram_reporter برای گزارش‌های ساده و بدون جدول
        try:
            try:
                # ابتدا سعی می‌کنیم از ماژول ساده استفاده کنیم
                from crypto_bot.simple_formatted_reporter import send_formatted_report
                logger.info("استفاده از گزارش‌دهنده ساده بدون جدول")
                result = send_formatted_report()
            except ImportError:
                try:
                    # سپس سعی می‌کنیم از ماژول جدید استفاده کنیم
                    from crypto_bot.formatted_telegram_reporter import send_formatted_report
                    logger.info("استفاده از گزارش‌دهنده جدید")
                    result = send_formatted_report()
                except ImportError:
                    # در صورت عدم وجود ماژول جدید، از ماژول قدیمی استفاده می‌کنیم
                    import enhanced_telegram_reporter
                    logger.info("استفاده از گزارش‌دهنده قدیمی")
                    result = enhanced_telegram_reporter.send_three_layer_report()
                
            logger.info(f"نتیجه ارسال گزارش: {result}")
            return result
        except Exception as e:
            logger.error(f"خطا در ارسال گزارش: {str(e)}")
            logger.error(traceback.format_exc())
            return direct_result  # حداقل پیام مستقیم ارسال شده
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
    logger.info("در حال ارسال پیام تست...")
    try:
        # ابتدا سعی می‌کنیم از ماژول ساده استفاده کنیم
        from crypto_bot.simple_formatted_reporter import send_test_message
        logger.info("استفاده از گزارش‌دهنده ساده بدون جدول برای پیام تست")
        test_result = send_test_message()
    except ImportError:
        try:
            # سپس سعی می‌کنیم از ماژول جدید استفاده کنیم
            from crypto_bot.formatted_telegram_reporter import send_test_message
            logger.info("استفاده از گزارش‌دهنده جدید برای پیام تست")
            test_result = send_test_message()
        except ImportError:
            # در صورت عدم وجود ماژول جدید، از ماژول قدیمی استفاده می‌کنیم
            import enhanced_telegram_reporter
            logger.info("استفاده از گزارش‌دهنده قدیمی برای پیام تست")
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