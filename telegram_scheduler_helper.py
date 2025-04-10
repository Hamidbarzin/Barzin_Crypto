#!/usr/bin/env python3
"""
زمان‌بند پیام‌های تلگرام با امکان کنترل از طریق وب

این اسکریپت پیام‌های تلگرام را با فاصله زمانی مشخص ارسال می‌کند.
برای استفاده می‌توانید آن را به صورت دستی در یک ترمینال جدید اجرا کنید.

دستور اجرا:
python telegram_scheduler_helper.py --interval 120
"""

import time
import logging
import argparse
import signal
import sys
import os
from datetime import datetime
import random
import requests
import pytz

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_scheduler_helper.log")
    ]
)
logger = logging.getLogger("telegram_scheduler_helper")

# واردسازی ماژول ارسال پیام تلگرام
import replit_telegram_sender

# مدیریت سیگنال‌های خروج
def signal_handler(sig, frame):
    logger.info("دریافت سیگنال خروج، در حال خاتمه برنامه...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ذخیره PID برای کنترل بهتر فرآیند
def save_pid():
    """ذخیره PID در فایل"""
    with open("telegram_scheduler_helper.pid", "w") as f:
        f.write(str(os.getpid()))
    logger.info(f"PID {os.getpid()} ذخیره شد")

def cleanup_pid():
    """پاکسازی فایل PID هنگام خروج"""
    try:
        if os.path.exists("telegram_scheduler_helper.pid"):
            os.remove("telegram_scheduler_helper.pid")
            logger.info("فایل PID پاکسازی شد")
    except Exception as e:
        logger.error(f"خطا در پاکسازی فایل PID: {e}")

def send_message():
    """
    ارسال یک پیام تصادفی به تلگرام
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    # انتخاب تصادفی نوع پیام
    message_types = ["price", "technical", "signals", "test"]
    weights = [0.4, 0.3, 0.2, 0.1]  # مجموع باید 1 باشد
    
    message_type = random.choices(message_types, weights=weights, k=1)[0]
    
    logger.info(f"ارسال پیام نوع '{message_type}'...")
    
    try:
        if message_type == "price":
            return replit_telegram_sender.send_price_report()
        elif message_type == "technical":
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
                      "MATIC/USDT", "ARB/USDT", "OP/USDT", "RNDR/USDT", "FET/USDT", "WLD/USDT"]
            symbol = random.choice(symbols)
            logger.info(f"ارسال تحلیل تکنیکال برای {symbol}...")
            return replit_telegram_sender.send_technical_analysis(symbol)
        elif message_type == "signals":
            return replit_telegram_sender.send_trading_signals()
        else:
            return replit_telegram_sender.send_test_message()
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    parser = argparse.ArgumentParser(description="سرویس ارسال خودکار پیام تلگرام")
    parser.add_argument("--interval", type=int, default=120, help="فاصله زمانی ارسال پیام به ثانیه (پیش‌فرض: 120 ثانیه)")
    parser.add_argument("--single", action="store_true", help="فقط یک بار پیام ارسال کن و خارج شو")
    args = parser.parse_args()
    
    interval = args.interval
    single_run = args.single
    
    # ذخیره PID
    save_pid()
    
    # تنظیم مدیریت خروج
    import atexit
    atexit.register(cleanup_pid)
    
    # اطلاعات شروع
    if single_run:
        logger.info(f"اجرای یک بار ارسال پیام تلگرام...")
    else:
        logger.info(f"شروع سرویس ارسال خودکار پیام تلگرام هر {interval} ثانیه...")
    
    # شمارنده برای ارسال گزارش سیستم
    system_report_counter = 0
    system_report_interval = 15  # هر 30 بار ارسال پیام (معادل 60 دقیقه با interval=120)
    
    try:
        # اعلام راه‌اندازی
        replit_telegram_sender.send_test_message()
        
        while True:
            # زمان فعلی به منطقه زمانی تورنتو
            toronto_tz = pytz.timezone('America/Toronto')
            current_time = datetime.now(toronto_tz).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"زمان فعلی: {current_time} (تورنتو)")
            
            # هر 15 بار (30 دقیقه)، گزارش سیستم ارسال کن
            if system_report_counter >= system_report_interval:
                logger.info(f"ارسال گزارش سیستم ({current_time})...")
                success = replit_telegram_sender.send_system_report()
                if success:
                    logger.info("گزارش سیستم با موفقیت ارسال شد")
                else:
                    logger.error("خطا در ارسال گزارش سیستم")
                system_report_counter = 0
            else:
                # ارسال پیام تصادفی
                success = send_message()
                
                if success:
                    logger.info("پیام با موفقیت ارسال شد")
                else:
                    logger.error("خطا در ارسال پیام")
                
                system_report_counter += 1
            
            # اگر فقط یک بار اجرا می‌شود
            if single_run:
                logger.info("اجرای یک بار کامل شد، خروج از برنامه...")
                break
                
            # انتظار تا ارسال پیام بعدی
            logger.info(f"انتظار {interval} ثانیه تا ارسال پیام بعدی... (شمارنده گزارش سیستم: {system_report_counter}/{system_report_interval})")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("برنامه توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    finally:
        # پاکسازی منابع
        cleanup_pid()
        
    logger.info("پایان برنامه")

if __name__ == "__main__":
    main()