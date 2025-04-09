#!/usr/bin/env python3
"""
اسکریپت اجرای سرویس تلگرام برای استفاده در Replit Workflows

این اسکریپت برای اجرای سرویس به صورت دائمی در محیط Replit طراحی شده است.
"""

import time
import logging
import random
import os
import sys
from datetime import datetime, timedelta

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("telegram_workflow")

# واردسازی ماژول‌های مورد نیاز
try:
    import requests
    logger.info("ماژول requests با موفقیت بارگذاری شد")
except ImportError:
    logger.error("خطا در بارگذاری ماژول requests")
    sys.exit(1)

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

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

def send_telegram_message(text, parse_mode="HTML"):
    """
    ارسال پیام به تلگرام
    
    Args:
        text (str): متن پیام
        parse_mode (str): نوع پارس متن
        
    Returns:
        bool: وضعیت ارسال
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    params = {
        "chat_id": DEFAULT_CHAT_ID,
        "text": text,
        "disable_notification": False
    }
    
    if parse_mode in ["HTML", "Markdown", "MarkdownV2"]:
        params["parse_mode"] = parse_mode
    
    try:
        logger.info(f"ارسال پیام به تلگرام")
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info(f"پیام با موفقیت ارسال شد")
                return True
            else:
                logger.error(f"خطا در ارسال پیام: {result.get('description')}")
                return False
        else:
            logger.error(f"خطا در ارسال پیام: کد وضعیت {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def send_price_report():
    """
    ارسال گزارش قیمت‌ها
    
    Returns:
        bool: وضعیت ارسال
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prices = get_random_price_data()
    
    message = f"""
💰 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

"""
    
    for symbol, data in prices.items():
        name = data.get("name", "")
        price = data.get("price", 0)
        change = data.get("change_24h", 0)
        
        emoji = "🟢" if change >= 0 else "🔴"
        price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
        change_str = f"{change:+.2f}%"
        
        message += f"• {name} ({symbol}): {price_str} ({emoji} {change_str})\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return send_telegram_message(message, "HTML")

def send_test_message():
    """
    ارسال پیام تست
    
    Returns:
        bool: وضعیت ارسال
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

سیستم اعلان‌های تلگرام ورک‌فلو فعال است.
این پیام از طریق ورک‌فلو Replit ارسال شده است.

⏰ <b>زمان:</b> {current_time}
    """
    
    return send_telegram_message(message, "HTML")

def run_telegram_service():
    """
    اجرای سرویس تلگرام
    """
    logger.info("شروع سرویس تلگرام ورک‌فلو")
    
    # ارسال پیام تست
    logger.info("ارسال پیام تست اولیه")
    test_result = send_test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # ارسال گزارش قیمت اولیه
    logger.info("ارسال گزارش قیمت اولیه")
    price_result = send_price_report()
    logger.info(f"نتیجه ارسال گزارش قیمت: {price_result}")
    
    # زمان آخرین ارسال
    last_price_report = datetime.now()
    last_test_message = datetime.now()
    report_count = 1
    
    try:
        while True:
            now = datetime.now()
            
            # ارسال گزارش قیمت هر 30 دقیقه
            if now - last_price_report >= timedelta(minutes=30):
                logger.info(f"ارسال گزارش قیمت شماره {report_count}")
                send_price_report()
                last_price_report = now
                report_count += 1
            
            # ارسال پیام زنده بودن هر 4 ساعت
            if now - last_test_message >= timedelta(hours=4):
                logger.info("ارسال پیام زنده بودن")
                send_test_message()
                last_test_message = now
            
            # انتظار برای 1 دقیقه
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("سرویس با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای سرویس: {str(e)}")
        raise

if __name__ == "__main__":
    run_telegram_service()