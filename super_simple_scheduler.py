#!/usr/bin/env python3
"""
زمان‌بندی بسیار ساده برای ارسال پیام‌های تلگرام به صورت خودکار
"""

import time
import logging
import random
from datetime import datetime, timedelta
import os
import sys
import requests
import json
import signal

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("super_simple_scheduler.log")
    ]
)
logger = logging.getLogger(__name__)

# توکن و چت آیدی
TOKEN = "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk"
CHAT_ID = "722627622"

def send_message(text):
    """
    ارسال پیام به تلگرام با استفاده از API رسمی تلگرام
    
    Args:
        text (str): متن پیام
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        logger.info("در حال ارسال پیام به تلگرام...")
        response = requests.post(url, data=payload)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get("ok"):
            logger.info("پیام با موفقیت ارسال شد")
            return True
        else:
            logger.error(f"خطا در ارسال پیام: {response_json.get('description', 'خطای ناشناخته')}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def send_test_message():
    """
    ارسال پیام تست
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

سیستم زمان‌بندی بسیار ساده در حال اجراست.
این پیام با روش ساده ارسال شده است.

⏰ <b>زمان:</b> {current_time}
"""
    
    return send_message(message)

def send_price_report():
    """
    ارسال گزارش قیمت‌ها
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # مقادیر تصادفی برای نمایش
    coins = [
        {"symbol": "BTC", "name": "بیت‌کوین", "price": random.uniform(60000, 70000), "change": random.uniform(-3, 5)},
        {"symbol": "ETH", "name": "اتریوم", "price": random.uniform(3000, 4000), "change": random.uniform(-3, 5)},
        {"symbol": "BNB", "name": "بایننس کوین", "price": random.uniform(500, 600), "change": random.uniform(-3, 5)},
        {"symbol": "SOL", "name": "سولانا", "price": random.uniform(130, 150), "change": random.uniform(-3, 5)},
        {"symbol": "XRP", "name": "ریپل", "price": random.uniform(0.50, 0.55), "change": random.uniform(-3, 5)}
    ]
    
    message = f"""
💰 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

"""
    
    for coin in coins:
        symbol = coin["symbol"]
        name = coin["name"]
        price = coin["price"]
        change = coin["change"]
        
        emoji = "🟢" if change >= 0 else "🔴"
        price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
        change_str = f"{change:+.2f}%"
        
        message += f"• {name} ({symbol}): {price_str} ({emoji} {change_str})\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return send_message(message)

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
گزارش وضعیت: هر ۴ ساعت

⏰ <b>زمان کنونی:</b> {current_time}
    """
    
    return send_message(message)

def save_pid():
    """
    ذخیره شناسه فرآیند
    """
    pid = os.getpid()
    with open("super_simple_scheduler.pid", "w") as f:
        f.write(str(pid))
    logger.info(f"شناسه فرآیند {pid} ذخیره شد")

def signal_handler(sig, frame):
    """
    مدیریت سیگنال‌های سیستم عامل
    """
    logger.info("سیگنال توقف دریافت شد، در حال خروج...")
    sys.exit(0)

def main():
    """
    تابع اصلی
    """
    # ثبت مدیریت سیگنال‌ها
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ذخیره شناسه فرآیند
    save_pid()
    
    logger.info("شروع زمان‌بندی ارسال پیام‌های تلگرام")
    
    # ارسال پیام تست اولیه
    logger.info("ارسال پیام تست اولیه")
    test_result = send_test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # ارسال گزارش قیمت اولیه
    logger.info("ارسال گزارش قیمت اولیه")
    price_result = send_price_report()
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
                send_price_report()
                last_price_report = now
                report_count += 1
            
            # ارسال گزارش وضعیت سیستم هر ۴ ساعت
            if now - last_status_report >= timedelta(hours=4):
                logger.info("ارسال گزارش وضعیت سیستم")
                send_system_status()
                last_status_report = now
            
            # برای تست سریع‌تر، می‌توانید زمان‌ها را کوتاه‌تر کنید
            # if now - last_price_report >= timedelta(minutes=1):
            #     logger.info(f"ارسال گزارش قیمت شماره {report_count}")
            #     send_price_report()
            #     last_price_report = now
            #     report_count += 1
            
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
            send_message(error_message)
        except:
            pass
        
        raise

if __name__ == "__main__":
    main()