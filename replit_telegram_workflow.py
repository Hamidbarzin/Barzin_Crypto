#!/usr/bin/env python3
"""
ارسال خودکار پیام تلگرام با استفاده از Replit Workflow

این اسکریپت برای اجرا به عنوان یک Replit Workflow طراحی شده است.
هر 2 دقیقه یک بار پیام تلگرام ارسال می‌کند.
"""

import logging
import time
import os
import sys
import json
import signal
import random
from datetime import datetime
import pytz
from replit_telegram_sender import (
    send_test_message,
    send_price_report,
    send_technical_analysis,
    send_trading_signals,
    send_system_report
)

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_workflow.log")
    ]
)
logger = logging.getLogger("telegram_workflow")

# سازگاری با Workflow Replit
# ذخیره PID برای کنترل بهتر فرآیند
def save_pid():
    """ذخیره PID در فایل"""
    with open("telegram_replit_workflow.pid", "w") as f:
        f.write(str(os.getpid()))
    logger.info(f"PID {os.getpid()} ذخیره شد")

def cleanup_pid():
    """پاکسازی فایل PID هنگام خروج"""
    try:
        if os.path.exists("telegram_replit_workflow.pid"):
            os.remove("telegram_replit_workflow.pid")
            logger.info("فایل PID پاکسازی شد")
    except Exception as e:
        logger.error(f"خطا در پاکسازی فایل PID: {e}")

# مدیریت سیگنال‌های خروج
def signal_handler(sig, frame):
    """مدیریت سیگنال‌های سیستم عامل"""
    logger.info(f"سیگنال {sig} دریافت شد. در حال خروج...")
    cleanup_pid()
    sys.exit(0)

# تنظیم مدیریت سیگنال‌ها
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def send_random_message():
    """
    ارسال یک پیام تصادفی به تلگرام
    
    Returns:
        tuple: (موفقیت/شکست, نوع پیام)
    """
    # تعیین نسبت احتمال هر نوع پیام
    weights = {
        "price_report": 40,
        "technical_analysis": 30,
        "trading_signals": 20,
        "test_message": 10
    }
    
    # انتخاب تصادفی نوع پیام بر اساس وزن‌ها
    message_types = list(weights.keys())
    weights_values = list(weights.values())
    message_type = random.choices(message_types, weights=weights_values, k=1)[0]
    
    logger.info(f"ارسال پیام نوع '{message_type}'...")
    
    try:
        if message_type == "price_report":
            result = send_price_report()
        elif message_type == "technical_analysis":
            # انتخاب تصادفی یک ارز
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", 
                       "MATIC/USDT", "ARB/USDT", "OP/USDT", "RNDR/USDT", "FET/USDT", "WLD/USDT"]
            symbol = random.choice(symbols)
            result = send_technical_analysis(symbol)
        elif message_type == "trading_signals":
            result = send_trading_signals()
        else:  # test_message
            result = send_test_message()
            
        return result, message_type
        
    except Exception as e:
        logger.error(f"خطا در ارسال پیام {message_type}: {str(e)}")
        return False, message_type

def main():
    """
    تابع اصلی برنامه
    """
    # ذخیره PID
    save_pid()
    
    # تنظیم مدیریت خروج
    import atexit
    atexit.register(cleanup_pid)
    
    # اطلاعات شروع
    logger.info("شروع Workflow ارسال پیام تلگرام هر ۲ دقیقه...")
    
    # اعلام راه‌اندازی
    send_test_message()
    
    # شمارنده برای ارسال گزارش سیستم
    system_report_counter = 0
    
    try:
        while True:
            # زمان فعلی به منطقه زمانی تورنتو
            toronto_tz = pytz.timezone('America/Toronto')
            current_time = datetime.now(toronto_tz).strftime("%Y-%m-%d %H:%M:%S")
            
            # هر ۳۰ بار (۶۰ دقیقه)، گزارش سیستم ارسال کن
            if system_report_counter >= 30:
                logger.info(f"ارسال گزارش سیستم ({current_time} تورنتو)...")
                success = send_system_report()
                if success:
                    logger.info("گزارش سیستم با موفقیت ارسال شد")
                else:
                    logger.error("خطا در ارسال گزارش سیستم")
                system_report_counter = 0
            else:
                # ارسال پیام تصادفی
                success, message_type = send_random_message()
                
                if success:
                    logger.info(f"پیام {message_type} با موفقیت ارسال شد")
                else:
                    logger.error(f"خطا در ارسال پیام {message_type}")
                
                system_report_counter += 1
            
            # انتظار ۲ دقیقه
            logger.info(f"انتظار ۲ دقیقه تا ارسال پیام بعدی... (شمارنده گزارش سیستم: {system_report_counter}/30)")
            time.sleep(120)  # ۲ دقیقه
            
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