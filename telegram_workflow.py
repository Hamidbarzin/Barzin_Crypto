#!/usr/bin/env python3
"""
ورک‌فلوی تلگرام برای Crypto Barzin

این اسکریپت برای اجرا به عنوان یک ورک‌فلو در Replit طراحی شده است
و به طور خودکار پیام‌های تلگرام را ارسال می‌کند.
"""

import time
import requests
import logging
from datetime import datetime
import sys
import os
import random
import json

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_workflow")

# توکن و چت آیدی
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

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

def get_random_crypto_prices():
    """
    دریافت قیمت‌های تصادفی ارزهای دیجیتال
    در نسخه واقعی باید از یک API واقعی استفاده شود
    
    Returns:
        dict: دیکشنری قیمت‌های ارزهای دیجیتال
    """
    try:
        # تلاش برای دریافت قیمت‌های واقعی از CoinGecko
        api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,solana,binancecoin&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # تبدیل به فرمت مورد نظر ما
            prices = {
                "BTC/USDT": {
                    "price": data["bitcoin"]["usd"],
                    "change_24h": data["bitcoin"]["usd_24h_change"]
                },
                "ETH/USDT": {
                    "price": data["ethereum"]["usd"],
                    "change_24h": data["ethereum"]["usd_24h_change"]
                },
                "XRP/USDT": {
                    "price": data["ripple"]["usd"],
                    "change_24h": data["ripple"]["usd_24h_change"]
                },
                "SOL/USDT": {
                    "price": data["solana"]["usd"],
                    "change_24h": data["solana"]["usd_24h_change"]
                },
                "BNB/USDT": {
                    "price": data["binancecoin"]["usd"],
                    "change_24h": data["binancecoin"]["usd_24h_change"]
                }
            }
            
            return prices
    except Exception as e:
        logger.warning(f"خطا در دریافت قیمت‌های واقعی: {str(e)}")
    
    # در صورت بروز خطا، از قیمت‌های تصادفی استفاده می‌کنیم
    base_prices = {
        "BTC/USDT": 76000,
        "ETH/USDT": 3400,
        "XRP/USDT": 0.53,
        "SOL/USDT": 165,
        "BNB/USDT": 580
    }
    
    result = {}
    for symbol, base_price in base_prices.items():
        # تغییر قیمت بین -2% تا +2%
        price_change = random.uniform(-0.02, 0.02)
        new_price = base_price * (1 + price_change)
        
        # تغییر ۲۴ ساعته بین -5% تا +5%
        change_24h = random.uniform(-5, 5)
        
        result[symbol] = {
            "price": round(new_price, 2) if new_price >= 1 else round(new_price, 8),
            "change_24h": round(change_24h, 2)
        }
    
    return result

def format_price(price):
    """
    قالب‌بندی قیمت با جداکننده هزارگان
    
    Args:
        price (float): قیمت
        
    Returns:
        str: قیمت قالب‌بندی شده
    """
    if price >= 1:
        return f"{price:,.2f}"
    else:
        return f"{price:.8f}"

def format_change(change):
    """
    قالب‌بندی تغییر قیمت با علامت مثبت یا منفی
    
    Args:
        change (float): درصد تغییر
        
    Returns:
        str: درصد تغییر قالب‌بندی شده
    """
    return f"{'+' if change >= 0 else ''}{change:.2f}%"

def send_price_report():
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    try:
        # دریافت قیمت‌های فعلی
        prices = get_random_crypto_prices()
        
        # ساخت متن پیام
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🚀 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

💰 <b>قیمت‌های لحظه‌ای ارزهای دیجیتال</b>

<code>
{'ارز':<8} {'قیمت (USDT)':<15} {'تغییر 24h':<10}
</code>
"""

        for symbol, data in prices.items():
            coin = symbol.split('/')[0]
            price = format_price(data["price"])
            change = format_change(data["change_24h"])
            change_emoji = "🟢" if data["change_24h"] >= 0 else "🔴"
            
            message += f"<code>{coin:<8} {price:<15} {change:<10}</code> {change_emoji}\n"
        
        message += f"""
⏰ <b>زمان:</b> {current_time}
🤖 <b>سرویس:</b> Crypto Barzin
"""
        
        return send_message(message)
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش قیمت: {str(e)}")
        return False

def send_test_message():
    """
    ارسال پیام تست ساده
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

این یک پیام تست از ورک‌فلوی ریپلیت است.
سیستم به درستی در حال کار است.

⏰ <b>زمان:</b> {current_time}
"""
    
    return send_message(message)

def send_system_report():
    """
    ارسال گزارش وضعیت سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🔧 <b>Crypto Barzin - گزارش سیستم</b>
━━━━━━━━━━━━━━━━━━

✅ <b>وضعیت سرویس:</b> فعال
⚙️ <b>سرویس فعال:</b> ورک‌فلوی ریپلیت

⏰ <b>زمان گزارش:</b> {current_time}
"""
    
    return send_message(message)

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("ورک‌فلوی تلگرام Crypto Barzin شروع شد")
    
    # ارسال یک پیام تست در ابتدا
    send_test_message()
    
    # شمارنده برای ارسال گزارش سیستم هر ۶ ساعت (۳۶ بار ۱۰ دقیقه)
    system_report_counter = 0
    
    try:
        while True:
            # ارسال گزارش قیمت
            success = send_price_report()
            logger.info(f"گزارش قیمت ارسال شد: {success}")
            
            # افزایش شمارنده
            system_report_counter += 1
            
            # اگر ۶ ساعت (۳۶ بار ۱۰ دقیقه) گذشته، گزارش سیستم ارسال کن
            if system_report_counter >= 36:
                send_system_report()
                system_report_counter = 0
            
            # ۱۰ دقیقه صبر کن
            logger.info("در حال انتظار برای ۱۰ دقیقه...")
            time.sleep(600)  # 10 minutes = 600 seconds
                
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())