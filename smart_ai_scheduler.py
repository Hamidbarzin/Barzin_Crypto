#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
زمان‌بندی هوشمند برای ارسال گزارش‌های دوره‌ای با استفاده از حالت ساده هوش مصنوعی

این اسکریپت به طور خودکار گزارش‌های دوره‌ای، تحلیل تکنیکال و سیگنال‌های معاملاتی را
با فاصله‌های زمانی مشخص به تلگرام ارسال می‌کند.
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
        logging.FileHandler("smart_ai_scheduler.log")
    ]
)
logger = logging.getLogger("smart_ai_scheduler")

# لیست ارزهای مورد پایش
WATCHED_CURRENCIES = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT", "ADA/USDT", "DOT/USDT", "DOGE/USDT"]

def send_market_overview():
    """
    ارسال نمای کلی بازار هر 30 دقیقه
    """
    try:
        logger.info("در حال ارسال نمای کلی بازار...")
        # استفاده از ماژول simple_ai_mode
        import simple_ai_mode
        result = simple_ai_mode.send_market_overview()
        logger.info(f"نتیجه ارسال نمای کلی بازار: {result}")
        return result
    except Exception as e:
        logger.error(f"خطا در ارسال نمای کلی بازار: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_coin_analysis():
    """
    ارسال تحلیل یک ارز تصادفی هر 2 ساعت
    """
    try:
        # انتخاب یک ارز تصادفی
        symbol = random.choice(WATCHED_CURRENCIES)
        
        logger.info(f"در حال ارسال تحلیل ارز {symbol}...")
        # استفاده از ماژول simple_ai_mode
        import simple_ai_mode
        result = simple_ai_mode.send_coin_analysis(symbol)
        logger.info(f"نتیجه ارسال تحلیل ارز {symbol}: {result}")
        return result
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل ارز: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_trading_opportunities():
    """
    ارسال فرصت‌های معاملاتی هر 4 ساعت
    """
    try:
        logger.info("در حال ارسال فرصت‌های معاملاتی...")
        # استفاده از ماژول simple_ai_mode
        import simple_ai_mode
        result = simple_ai_mode.send_trading_opportunities()
        logger.info(f"نتیجه ارسال فرصت‌های معاملاتی: {result}")
        return result
    except Exception as e:
        logger.error(f"خطا در ارسال فرصت‌های معاملاتی: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def send_alive_message():
    """
    ارسال پیام زنده بودن سیستم هر 12 ساعت
    """
    try:
        logger.info("در حال ارسال پیام زنده بودن سیستم...")
        # استفاده از ماژول simple_ai_mode
        import simple_ai_mode
        
        message = f"""
🤖 *وضعیت سیستم*

سیستم ربات هوشمند تحلیل ارز دیجیتال در حال اجرا است.
زمان کنونی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

این پیام به صورت خودکار هر 12 ساعت ارسال می‌شود.
        """
        
        # ارسال پیام به تلگرام
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        # اگر چت آیدی در متغیرهای محیطی نباشد، از مقدار پیش‌فرض استفاده می‌کنیم
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        from crypto_bot.telegram_service import send_telegram_message
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
    
    # ارسال نمای کلی بازار هر 30 دقیقه
    schedule.every(30).minutes.do(send_market_overview)
    
    # ارسال تحلیل ارز هر 2 ساعت
    schedule.every(2).hours.do(send_coin_analysis)
    
    # ارسال فرصت‌های معاملاتی هر 4 ساعت
    schedule.every(4).hours.do(send_trading_opportunities)
    
    # ارسال پیام زنده بودن سیستم هر 12 ساعت
    schedule.every(12).hours.do(send_alive_message)
    
    logger.info("زمان‌بندی وظایف با موفقیت تنظیم شد")
    
    # ارسال اولین نمای کلی بازار بلافاصله
    send_market_overview()
    
    # ارسال اولین فرصت‌های معاملاتی بلافاصله
    send_trading_opportunities()

def save_pid():
    """
    ذخیره شناسه فرآیند برای کنترل اجرا
    """
    with open("smart_ai_scheduler.pid", "w") as f:
        f.write(str(os.getpid()))
    logger.info(f"شناسه فرآیند ذخیره شد: {os.getpid()}")

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع اجرای برنامه زمان‌بندی هوشمند")
    
    # ذخیره شناسه فرآیند
    save_pid()
    
    # ارسال یک پیام تست برای اطمینان از عملکرد صحیح
    import simple_ai_mode
    logger.info("در حال ارسال پیام تست...")
    test_result = simple_ai_mode.send_test_message()
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
    
    logger.info("پایان اجرای برنامه زمان‌بندی هوشمند")

if __name__ == "__main__":
    main()