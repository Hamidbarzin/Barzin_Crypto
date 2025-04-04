#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
زمان‌بندی ساده برای ارسال گزارش‌های دوره‌ای تلگرام

این اسکریپت به طور خودکار گزارش‌های دوره‌ای، تحلیل تکنیکال و سیگنال‌های معاملاتی را
با فاصله‌های زمانی مشخص به تلگرام ارسال می‌کند.
"""

import time
import schedule
import logging
import traceback
import random
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scheduler.log")
    ]
)
logger = logging.getLogger("simple_scheduler")

# لیست ارزهای مورد پایش
WATCHED_CURRENCIES = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT"]

def send_price_report():
    """
    ارسال گزارش قیمت‌ها هر ساعت
    """
    try:
        logger.info("در حال ارسال گزارش قیمت‌ها...")
        import telegram_reporter
        return telegram_reporter.send_periodic_report()
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش قیمت‌ها: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_technical_analysis():
    """
    ارسال تحلیل تکنیکال یک ارز تصادفی هر 4 ساعت
    """
    try:
        # انتخاب یک ارز تصادفی
        symbol = random.choice(WATCHED_CURRENCIES)
        
        logger.info(f"در حال ارسال تحلیل تکنیکال {symbol}...")
        import telegram_reporter
        return telegram_reporter.send_technical_analysis(symbol)
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل تکنیکال: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_market_overview():
    """
    ارسال گزارش کلی بازار هر 2 ساعت
    """
    try:
        logger.info("در حال ارسال گزارش کلی بازار...")
        import telegram_reporter
        
        # دریافت گزارش کلی بازار
        market_report = telegram_reporter.get_market_overview()
        
        # ارسال گزارش به تلگرام
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        return telegram_reporter.send_telegram_message(chat_id, market_report)
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش کلی بازار: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_alive_message():
    """
    ارسال پیام زنده بودن سیستم هر 12 ساعت
    """
    try:
        logger.info("در حال ارسال پیام زنده بودن سیستم...")
        import telegram_reporter
        
        message = "🤖 *وضعیت سیستم*\n\n"
        message += "سیستم ربات معامله ارز دیجیتال در حال اجرا است.\n"
        message += f"زمان کنونی: {telegram_reporter.get_current_persian_time()}\n"
        message += "این پیام به صورت خودکار هر 12 ساعت ارسال می‌شود."
        
        # ارسال پیام به تلگرام
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        return telegram_reporter.send_telegram_message(chat_id, message)
    except Exception as e:
        logger.error(f"خطا در ارسال پیام زنده بودن سیستم: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def setup_schedule():
    """
    تنظیم زمان‌بندی وظایف
    """
    logger.info("در حال تنظیم زمان‌بندی وظایف...")
    
    # ارسال گزارش قیمت‌ها هر 30 دقیقه
    schedule.every(30).minutes.do(send_price_report)
    
    # ارسال تحلیل تکنیکال هر 4 ساعت
    schedule.every(4).hours.do(send_technical_analysis)
    
    # ارسال گزارش کلی بازار هر 2 ساعت
    schedule.every(2).hours.do(send_market_overview)
    
    # ارسال پیام زنده بودن سیستم هر 12 ساعت
    schedule.every(12).hours.do(send_alive_message)
    
    logger.info("زمان‌بندی وظایف با موفقیت تنظیم شد")
    
    # ارسال اولین گزارش قیمت‌ها بلافاصله
    send_price_report()
    
    # ارسال اولین گزارش کلی بازار بلافاصله
    send_market_overview()

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع اجرای برنامه زمان‌بندی ساده")
    
    # تنظیم زمان‌بندی وظایف
    setup_schedule()
    
    # اجرای زمان‌بندی
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # بررسی هر دقیقه
    except KeyboardInterrupt:
        logger.info("برنامه زمان‌بندی با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه زمان‌بندی: {str(e)}")
        logger.error(traceback.format_exc())
    
    logger.info("پایان اجرای برنامه زمان‌بندی ساده")

if __name__ == "__main__":
    import os  # برای دسترسی به متغیرهای محیطی
    main()