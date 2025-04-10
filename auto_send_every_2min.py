#!/usr/bin/env python3
"""
ارسال خودکار پیام تلگرام هر ۲ دقیقه

این اسکریپت ساده هر ۲ دقیقه یک بار پیام به تلگرام ارسال می‌کند.
"""

import time
import logging
import random
import os
import signal
import sys
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("auto_send_2min.log")
    ]
)
logger = logging.getLogger("auto_sender_2min")

# واردسازی ماژول ارسال پیام تلگرام
import replit_telegram_sender

# مدیریت سیگنال‌های خروج
def signal_handler(sig, frame):
    logger.info("دریافت سیگنال خروج، در حال خاتمه برنامه...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def send_message():
    """
    ارسال پیام به تلگرام
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # انتخاب تصادفی نوع پیام
    message_types = ["price", "technical", "signals", "test"]
    message_type = random.choice(message_types)
    
    logger.info(f"ارسال پیام نوع '{message_type}' در {timestamp}...")
    
    if message_type == "price":
        return replit_telegram_sender.send_price_report()
    elif message_type == "technical":
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
        symbol = random.choice(symbols)
        return replit_telegram_sender.send_technical_analysis(symbol)
    elif message_type == "signals":
        return replit_telegram_sender.send_trading_signals()
    else:
        return replit_telegram_sender.send_test_message()

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع سرویس ارسال خودکار پیام تلگرام هر ۲ دقیقه...")
    
    try:
        # حلقه اصلی برنامه
        while True:
            # ارسال پیام
            result = send_message()
            
            if result:
                logger.info("پیام با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال پیام")
            
            # انتظار ۲ دقیقه
            logger.info("انتظار ۲ دقیقه تا ارسال پیام بعدی...")
            time.sleep(120)  # ۲ دقیقه = ۱۲۰ ثانیه
            
    except KeyboardInterrupt:
        logger.info("برنامه توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    
    logger.info("پایان برنامه")

if __name__ == "__main__":
    main()