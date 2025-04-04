#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت ساده برای ارسال گزارش‌های دوره‌ای به تلگرام
این اسکریپت می‌تواند به طور مستقل اجرا شود و نیازی به اجرای scheduler.py ندارد
"""

import os
import sys
import time
import logging
from datetime import datetime
import traceback

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_reporter.log")
    ]
)
logger = logging.getLogger("telegram_reporter")

# وارد کردن ماژول تلگرام
try:
    # ابتدا سعی می‌کنیم از ماژول‌های پروژه استفاده کنیم
    from crypto_bot.telegram_service import send_telegram_message, get_current_persian_time
    logger.info("ماژول‌های تلگرام با موفقیت بارگذاری شدند")
except ImportError:
    logger.error("خطا در بارگذاری ماژول‌های تلگرام از پروژه")
    sys.exit(1)

def get_price_report():
    """
    تهیه گزارش قیمت ارزهای دیجیتال
    در این نسخه ساده، از داده‌های ثابت استفاده می‌کنیم
    """
    try:
        price_report = "🤖 *گزارش قیمت ارزهای دیجیتال*\n\n"
        
        # افزودن قیمت‌های نمونه (در نسخه‌های آینده می‌توان از API واقعی استفاده کرد)
        prices = [
            "BTC/USDT: $67,345.20 (🟢 +2.3%)",
            "ETH/USDT: $3,245.80 (🟢 +1.8%)",
            "XRP/USDT: $0.5423 (🔴 -0.7%)",
            "BNB/USDT: $532.40 (🟢 +0.5%)",
            "SOL/USDT: $143.21 (🟢 +3.2%)"
        ]
            
        price_report += "\n".join(prices)
        price_report += "\n\n⏰ زمان گزارش: " + get_current_persian_time()
        
        return price_report
    except Exception as e:
        logger.error(f"خطا در تهیه گزارش قیمت: {str(e)}")
        return None

def send_periodic_report():
    """
    ارسال گزارش دوره‌ای به تلگرام
    """
    try:
        logger.info("در حال تهیه و ارسال گزارش دوره‌ای...")
        
        # دریافت گزارش قیمت
        price_report = get_price_report()
        if not price_report:
            # در صورت خطا در دریافت گزارش، یک پیام ساده ارسال می‌کنیم
            price_report = "🤖 *گزارش دوره‌ای سیستم*\n\n"
            price_report += "سیستم در حال کار است اما در حال حاضر قادر به دریافت قیمت‌های دقیق نیست.\n"
            price_report += "وضعیت فعلی: در حال اجرا ✅\n\n"
            price_report += "⏰ زمان گزارش: " + get_current_persian_time()
        
        # ارسال گزارش به تلگرام
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        result = send_telegram_message(chat_id, price_report)
        
        if result:
            logger.info("گزارش دوره‌ای با موفقیت ارسال شد")
            return True
        else:
            logger.error("خطا در ارسال گزارش دوره‌ای")
            return False
            
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در ارسال گزارش دوره‌ای: {str(e)}\n{error_text}")
        return False

def send_test_message():
    """
    ارسال پیام تست برای بررسی عملکرد سیستم
    """
    try:
        message = "🤖 *پیام تست ربات معامله ارز دیجیتال*\n\n"
        message += "این یک پیام تست است. سیستم گزارش‌دهی در حال کار است.\n\n"
        message += "⏰ زمان: " + get_current_persian_time()
        
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        result = send_telegram_message(chat_id, message)
        
        if result:
            logger.info("پیام تست با موفقیت ارسال شد")
            return True
        else:
            logger.error("خطا در ارسال پیام تست")
            return False
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در ارسال پیام تست: {str(e)}\n{error_text}")
        return False

def main():
    """
    تابع اصلی برنامه
    با پارامتر 'test' یک پیام تست ارسال می‌کند
    بدون پارامتر یک گزارش دوره‌ای ارسال می‌کند
    """
    logger.info("شروع اجرای برنامه گزارش‌دهی تلگرام")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # ارسال پیام تست
        send_test_message()
    else:
        # ارسال گزارش دوره‌ای
        send_periodic_report()
    
    logger.info("پایان اجرای برنامه گزارش‌دهی تلگرام")

if __name__ == "__main__":
    main()