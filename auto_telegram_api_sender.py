#!/usr/bin/env python3
"""
ارسال خودکار پیام تلگرام با استفاده از API وب برنامه

این اسکریپت هر ۲ دقیقه یک بار API مناسب وب برنامه را فراخوانی می‌کند 
تا پیام به تلگرام ارسال شود. این روش با Replit سازگارتر است.
"""

import time
import logging
import random
import argparse
import signal
import sys
import os
import json
from datetime import datetime
import requests

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("auto_telegram_api.log")
    ]
)
logger = logging.getLogger("auto_telegram_api")

# در صورتی که از SSL با آدرس دامنه استفاده می‌کنید، این مقدار را تغییر دهید
API_BASE_URL = "http://localhost:5000"

# مدیریت سیگنال‌های خروج
def signal_handler(sig, frame):
    logger.info("دریافت سیگنال خروج، در حال خاتمه برنامه...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def call_api(endpoint, method="GET", data=None):
    """
    فراخوانی API وب برنامه
    
    Args:
        endpoint (str): آدرس API
        method (str): متد HTTP (GET یا POST)
        data (dict): داده‌های ارسالی در متد POST
        
    Returns:
        dict: پاسخ API یا None در صورت خطا
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            logger.error(f"متد {method} پشتیبانی نمی‌شود")
            return None
            
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except:
                return {"success": True, "text": response.text}
        else:
            logger.error(f"خطا در فراخوانی API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"خطا در فراخوانی API: {str(e)}")
        return None

def send_random_message():
    """
    ارسال یک پیام تصادفی از طریق API
    
    Returns:
        dict: نتیجه فراخوانی API یا None در صورت خطا
    """
    # انتخاب تصادفی نوع پیام
    message_types = [
        "/api/telegram_price_report",
        "/api/telegram_technical_analysis",
        "/api/telegram_trading_signals",
        "/api/telegram_test"
    ]
    
    # هر پیام وزنی متفاوت دارد
    weights = [0.4, 0.3, 0.2, 0.1]  # مجموع باید 1 باشد
    endpoint = random.choices(message_types, weights=weights, k=1)[0]
    
    if endpoint == "/api/telegram_technical_analysis":
        # برای تحلیل تکنیکال، یک ارز تصادفی انتخاب می‌کنیم
        coins = ["BTC", "ETH", "SOL", "BNB", "XRP", "MATIC", "ARB", "OP", "RNDR", "FET", "WLD"]
        symbol = random.choice(coins) + "/USDT"
        data = {"symbol": symbol}
        logger.info(f"ارسال تحلیل تکنیکال برای {symbol}...")
        return call_api(endpoint, "POST", data)
    else:
        # برای سایر پیام‌ها، فقط فراخوانی API کافی است
        logger.info(f"ارسال پیام نوع '{endpoint}'...")
        return call_api(endpoint)

def main():
    """
    تابع اصلی برنامه
    """
    parser = argparse.ArgumentParser(description="سرویس ارسال خودکار پیام تلگرام با API")
    parser.add_argument("--interval", type=int, default=120, help="فاصله زمانی ارسال پیام به ثانیه (پیش‌فرض: 120 ثانیه)")
    parser.add_argument("--single", action="store_true", help="فقط یک بار پیام ارسال کن و خارج شو")
    args = parser.parse_args()
    
    interval = args.interval
    single_run = args.single
    
    # نمایش اطلاعات شروع
    if single_run:
        logger.info(f"اجرای یک بار ارسال پیام تلگرام...")
    else:
        logger.info(f"شروع سرویس ارسال خودکار پیام تلگرام هر {interval} ثانیه...")
    
    # حلقه اصلی
    try:
        while True:
            # ارسال پیام
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"ارسال پیام در {now}...")
            
            result = send_random_message()
            
            if result and result.get("success", False):
                logger.info("پیام با موفقیت ارسال شد")
            else:
                error_msg = result.get("message", "خطای نامشخص") if result else "عدم دریافت پاسخ از API"
                logger.error(f"خطا در ارسال پیام: {error_msg}")
            
            # اگر فقط یک بار اجرا شود، خروج از برنامه
            if single_run:
                logger.info("اجرای یک بار کامل شد، خروج از برنامه...")
                break
                
            # انتظار تا ارسال پیام بعدی
            logger.info(f"انتظار {interval} ثانیه تا ارسال پیام بعدی...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("برنامه توسط کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    
    logger.info("پایان برنامه")

if __name__ == "__main__":
    main()