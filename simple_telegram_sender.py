#!/usr/bin/env python3
"""
ارسال ساده پیام به تلگرام با استفاده از درخواست HTTP
این روش نیازی به کتابخانه python-telegram-bot ندارد و فقط از requests استفاده می‌کند
"""

import os
import requests
import logging
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("simple_telegram")

# توکن و چت آیدی پیش‌فرض
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

def send_message(chat_id=None, text="", parse_mode=None, disable_notification=False):
    """
    ارسال پیام متنی به تلگرام با استفاده از درخواست HTTP ساده
    
    Args:
        chat_id (str or int): شناسه چت (اگر None باشد از مقدار پیش‌فرض استفاده می‌شود)
        text (str): متن پیام
        parse_mode (str): نوع پارس متن (HTML, Markdown یا None)
        disable_notification (bool): غیرفعال کردن نوتیفیکیشن
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if not chat_id:
        chat_id = DEFAULT_CHAT_ID
        
    # API endpoint
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # پارامترهای درخواست
    params = {
        "chat_id": chat_id,
        "text": text,
        "disable_notification": disable_notification
    }
    
    # اضافه کردن parse_mode اگر مشخص شده باشد
    if parse_mode in ["HTML", "Markdown", "MarkdownV2"]:
        params["parse_mode"] = parse_mode
    
    try:
        logger.info(f"ارسال پیام به چت آیدی {chat_id}")
        response = requests.post(url, params=params)
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"پیام با موفقیت ارسال شد. شناسه پیام: {message_id}")
                return True
            else:
                error = result.get("description", "خطای ناشناخته")
                logger.error(f"خطا در ارسال پیام: {error}")
                return False
        else:
            logger.error(f"خطا در ارسال پیام: کد وضعیت {response.status_code}")
            logger.error(f"پاسخ: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def send_photo(chat_id=None, photo_path=None, photo_url=None, caption="", parse_mode=None):
    """
    ارسال تصویر به تلگرام
    
    Args:
        chat_id (str or int): شناسه چت (اگر None باشد از مقدار پیش‌فرض استفاده می‌شود)
        photo_path (str): مسیر فایل تصویر محلی
        photo_url (str): آدرس URL تصویر آنلاین
        caption (str): توضیحات تصویر
        parse_mode (str): نوع پارس متن توضیحات (HTML, Markdown یا None)
        
    Returns:
        bool: موفقیت یا شکست ارسال تصویر
    """
    if not chat_id:
        chat_id = DEFAULT_CHAT_ID
        
    # حداقل یکی از photo_path یا photo_url باید مشخص شده باشد
    if not photo_path and not photo_url:
        logger.error("خطا: هیچ تصویری برای ارسال مشخص نشده است")
        return False
        
    # API endpoint
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    # پارامترهای درخواست
    params = {
        "chat_id": chat_id,
        "caption": caption
    }
    
    # اضافه کردن parse_mode اگر مشخص شده باشد
    if parse_mode in ["HTML", "Markdown", "MarkdownV2"]:
        params["parse_mode"] = parse_mode
    
    try:
        logger.info(f"ارسال تصویر به چت آیدی {chat_id}")
        
        if photo_path:
            # ارسال فایل محلی
            with open(photo_path, "rb") as photo_file:
                response = requests.post(url, params=params, files={"photo": photo_file})
        else:
            # ارسال از طریق URL
            params["photo"] = photo_url
            response = requests.post(url, params=params)
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"تصویر با موفقیت ارسال شد. شناسه پیام: {message_id}")
                return True
            else:
                error = result.get("description", "خطای ناشناخته")
                logger.error(f"خطا در ارسال تصویر: {error}")
                return False
        else:
            logger.error(f"خطا در ارسال تصویر: کد وضعیت {response.status_code}")
            logger.error(f"پاسخ: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال تصویر: {str(e)}")
        return False

def get_bot_info():
    """
    دریافت اطلاعات بات تلگرام
    
    Returns:
        dict: اطلاعات بات یا None در صورت خطا
    """
    # API endpoint
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        logger.info("دریافت اطلاعات بات")
        response = requests.get(url)
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                logger.info(f"اطلاعات بات با موفقیت دریافت شد: {bot_info.get('first_name')} (@{bot_info.get('username')})")
                return bot_info
            else:
                error = result.get("description", "خطای ناشناخته")
                logger.error(f"خطا در دریافت اطلاعات بات: {error}")
                return None
        else:
            logger.error(f"خطا در دریافت اطلاعات بات: کد وضعیت {response.status_code}")
            logger.error(f"پاسخ: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات بات: {str(e)}")
        return None

def send_test_message():
    """
    ارسال یک پیام تست ساده
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>پیام تست از ربات معاملاتی</b>

سیستم اعلان‌های تلگرام فعال است.
این پیام با استفاده از روش ساده ارسال شده است.

⏰ <b>زمان:</b> {current_time}
    """
    
    return send_message(text=message, parse_mode="HTML")

def send_price_report(prices=None):
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال
    
    Args:
        prices (dict): دیکشنری قیمت‌ها (اختیاری)
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
📊 <b>گزارش قیمت‌های ارزهای دیجیتال</b>
━━━━━━━━━━━━━━━━━━

"""
    
    # اگر قیمت‌ها ارائه شده باشند، از آنها استفاده می‌کنیم
    if prices:
        for symbol, data in prices.items():
            price = data.get('price', 0)
            change = data.get('change_24h', 0)
            emoji = "🟢" if change >= 0 else "🔴"
            
            if isinstance(price, (int, float)):
                price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
            else:
                price_str = f"${price}"
                
            change_str = f"{change:+.2f}%" if isinstance(change, (int, float)) else f"{change}"
            
            message += f"• {symbol}: {price_str} ({emoji} {change_str})\n"
    else:
        # نمونه قیمت‌ها
        message += "• بیت‌کوین (BTC): $65,433.45 (🟢 +2.34%)\n"
        message += "• اتریوم (ETH): $3,458.12 (🟢 +1.76%)\n"
        message += "• بایننس کوین (BNB): $548.67 (🔴 -0.85%)\n"
        message += "• ریپل (XRP): $0.5247 (🟢 +0.32%)\n"
        message += "• سولانا (SOL): $142.35 (🟢 +3.56%)\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return send_message(text=message, parse_mode="HTML")

# اگر این فایل به صورت مستقیم اجرا شود
if __name__ == "__main__":
    import sys
    import time
    
    # بررسی پارامترهای خط فرمان
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "info":
            # نمایش اطلاعات بات
            bot_info = get_bot_info()
            if bot_info:
                print("\n" + "="*50)
                print(f"نام بات: {bot_info.get('first_name')}")
                print(f"نام کاربری: @{bot_info.get('username')}")
                print(f"آیدی بات: {bot_info.get('id')}")
                print(f"لینک بات: https://t.me/{bot_info.get('username')}")
                print("="*50 + "\n")
        
        elif command == "test":
            # ارسال پیام تست
            send_test_message()
            
        elif command == "prices":
            # ارسال گزارش قیمت‌ها
            send_price_report()
            
        elif command == "loop":
            # ارسال پیام هر دقیقه برای تست
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            
            print(f"ارسال {count} پیام با فاصله {interval} ثانیه...")
            
            for i in range(count):
                send_test_message()
                if i < count - 1:  # برای آخرین تکرار تاخیر نداریم
                    time.sleep(interval)
        
        else:
            print(f"دستور ناشناخته: {command}")
            print("دستورات قابل قبول: info, test, prices, loop")
    else:
        # بدون پارامتر، فقط یک پیام تست ارسال می‌کنیم
        send_test_message()