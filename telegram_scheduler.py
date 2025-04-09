#!/usr/bin/env python3
"""
زمان‌بندی ارسال پیام‌های تلگرام با استفاده از کتابخانه python-telegram-bot
این اسکریپت هر ۳۰ دقیقه یک گزارش قیمت و هر ۴ ساعت یک پیام وضعیت ارسال می‌کند
"""

import time
import logging
import random
from datetime import datetime, timedelta
import signal
import sys
import os

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_scheduler.log")
    ]
)
logger = logging.getLogger(__name__)

# واردسازی ماژول ارسال پیام تلگرام
try:
    import telegram_bot_sender as telegram
    logger.info("ماژول telegram_bot_sender با موفقیت بارگذاری شد")
except ImportError as e:
    logger.error(f"خطا در بارگذاری ماژول telegram_bot_sender: {str(e)}")
    sys.exit(1)

def get_random_price_data():
    """
    تولید داده‌های قیمت تصادفی برای تست (در نسخه نهایی باید با داده‌های واقعی جایگزین شود)
    
    Returns:
        dict: دیکشنری قیمت‌های تصادفی
    """
    coins = [
        {"symbol": "BTC/USDT", "name": "بیت‌کوین", "price": random.uniform(60000, 70000), "change": random.uniform(-3, 5)},
        {"symbol": "ETH/USDT", "name": "اتریوم", "price": random.uniform(3000, 4000), "change": random.uniform(-3, 5)},
        {"symbol": "BNB/USDT", "name": "بایننس کوین", "price": random.uniform(500, 600), "change": random.uniform(-3, 5)},
        {"symbol": "SOL/USDT", "name": "سولانا", "price": random.uniform(130, 150), "change": random.uniform(-3, 5)},
        {"symbol": "XRP/USDT", "name": "ریپل", "price": random.uniform(0.50, 0.55), "change": random.uniform(-3, 5)}
    ]
    
    prices = {}
    for coin in coins:
        prices[coin["symbol"]] = {
            "name": coin["name"],
            "price": coin["price"],
            "change_24h": coin["change"]
        }
    
    return prices

def send_system_status():
    """
    ارسال گزارش وضعیت سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - وضعیت سیستم</b>
━━━━━━━━━━━━━━━━━━

سیستم گزارش‌دهی تلگرام در حال اجرا است.
این پیام به صورت خودکار ارسال شده است.

گزارش‌های قیمت: هر ۳۰ دقیقه
تحلیل تکنیکال: هر ۱ ساعت
سیگنال‌های معاملاتی: هر ۴ ساعت

⏰ <b>زمان کنونی:</b> {current_time}
    """
    
    return telegram.test_message()

def signal_handler(sig, frame):
    """
    مدیریت سیگنال‌های سیستم عامل
    """
    logger.info("دریافت سیگنال توقف. در حال خروج...")
    sys.exit(0)

def save_pid():
    """
    ذخیره شناسه فرآیند برای کنترل اجرا
    """
    pid = os.getpid()
    with open('telegram_scheduler.pid', 'w') as f:
        f.write(str(pid))
    logger.info(f"شناسه فرآیند {pid} در فایل ذخیره شد")

def main():
    """
    تابع اصلی برنامه
    """
    # ثبت مدیریت سیگنال‌ها
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ذخیره شناسه فرآیند
    save_pid()
    
    logger.info("شروع زمان‌بندی ارسال پیام‌های تلگرام")
    
    # ارسال پیام تست اولیه
    logger.info("ارسال پیام تست اولیه")
    test_result = telegram.test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # ارسال گزارش وضعیت سیستم
    logger.info("ارسال گزارش وضعیت سیستم")
    status_result = send_system_status()
    logger.info(f"نتیجه ارسال گزارش وضعیت: {status_result}")
    
    # ارسال گزارش قیمت اولیه
    logger.info("ارسال گزارش قیمت اولیه")
    price_result = telegram.price_report()
    logger.info(f"نتیجه ارسال گزارش قیمت: {price_result}")
    
    # زمان آخرین ارسال گزارش‌ها
    last_price_report = datetime.now()
    last_status_report = datetime.now()
    report_count = 1
    
    try:
        # حلقه اصلی برنامه
        logger.info("ورود به حلقه اصلی برنامه")
        
        while True:
            # زمان فعلی
            now = datetime.now()
            
            # ارسال گزارش قیمت هر ۳۰ دقیقه
            if now - last_price_report >= timedelta(minutes=30):
                logger.info(f"ارسال گزارش قیمت شماره {report_count}")
                telegram.price_report()
                last_price_report = now
                report_count += 1
            
            # ارسال گزارش وضعیت سیستم هر ۴ ساعت
            if now - last_status_report >= timedelta(hours=4):
                logger.info("ارسال گزارش وضعیت سیستم")
                send_system_status()
                last_status_report = now
            
            # وقفه ۱ دقیقه
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        # ارسال پیام خطا به تلگرام
        error_message = f"""
⚠️ <b>Crypto Barzin - خطا</b>
━━━━━━━━━━━━━━━━━━

خطایی در اجرای سیستم رخ داده است.
لطفاً لاگ‌ها را بررسی کنید.

خطا: {str(e)}

⏰ <b>زمان:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        try:
            telegram.send_message(text=error_message, parse_mode="HTML")
        except:
            pass
        raise

if __name__ == "__main__":
    main()