"""
سرویس اعلان و هشدار برای فرصت‌های خرید و فروش و نوسانات بازار - مسیردهی به تلگرام

این فایل به عنوان یک لایه میانی عمل می‌کند که تمام اعلان‌ها را به سمت سرویس تلگرام هدایت می‌کند.
همه متدهای قبلی برای حفظ سازگاری حفظ شده‌اند، اما اکنون به جای ارسال پیامک، از تلگرام استفاده می‌کنند.
"""

import os
import logging
from datetime import datetime
from flask import session
from crypto_bot.telegram_service import send_telegram_message, send_buy_sell_notification as telegram_send_buy_sell, send_volatility_alert as telegram_send_volatility, send_market_trend_alert as telegram_send_market_trend, send_test_notification as telegram_send_test, get_current_persian_time

# تنظیم لاگر
logger = logging.getLogger(__name__)

def send_sms_notification(to_phone_number, message):
    """
    هدایت پیام به تلگرام به جای پیامک
    
    Args:
        to_phone_number (str): شماره موبایل گیرنده (دیگر استفاده نمی‌شود)
        message (str): متن پیام
        
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    logger.info("هدایت پیام به سمت تلگرام...")
    
    # دریافت چت آیدی تلگرام از SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    if not chat_id:
        logger.error("چت آیدی تلگرام یافت نشد")
        return False
        
    return send_telegram_message(chat_id, message)

def send_buy_sell_notification(to_phone_number, symbol, action, price, reason):
    """
    ارسال اعلان خرید یا فروش
    
    Args:
        to_phone_number (str): شماره موبایل گیرنده
        symbol (str): نماد ارز
        action (str): 'خرید' یا 'فروش'
        price (float): قیمت فعلی
        reason (str): دلیل توصیه
        
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    message = f"🔔 سیگنال {action} برای {symbol}\n"
    message += f"💰 قیمت فعلی: {price}\n"
    message += f"📊 دلیل: {reason}\n"
    message += f"⏰ زمان: {get_current_persian_time()}"
    
    return send_sms_notification(to_phone_number, message)

def send_volatility_alert(to_phone_number, symbol, price, change_percent, timeframe="1h"):
    """
    ارسال هشدار نوسان قیمت
    
    Args:
        to_phone_number (str): شماره موبایل گیرنده
        symbol (str): نماد ارز
        price (float): قیمت فعلی
        change_percent (float): درصد تغییر
        timeframe (str): بازه زمانی تغییر
        
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    direction = "افزایش" if change_percent > 0 else "کاهش"
    emoji = "🚀" if change_percent > 0 else "📉"
    
    message = f"{emoji} هشدار نوسان قیمت {symbol}\n"
    message += f"💰 قیمت فعلی: {price}\n"
    message += f"📊 {direction} {abs(change_percent):.2f}% در {timeframe}\n"
    message += f"⏰ زمان: {get_current_persian_time()}"
    
    return send_sms_notification(to_phone_number, message)

def send_market_trend_alert(to_phone_number, trend, affected_coins, reason):
    """
    ارسال هشدار روند کلی بازار
    
    Args:
        to_phone_number (str): شماره موبایل گیرنده
        trend (str): روند بازار ('صعودی'، 'نزولی' یا 'خنثی')
        affected_coins (list): لیست ارزهای تحت تأثیر
        reason (str): دلیل روند
        
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    emoji = "🚀" if trend == "صعودی" else "📉" if trend == "نزولی" else "⚖️"
    
    message = f"{emoji} تحلیل روند بازار: {trend}\n"
    message += f"🔍 دلیل: {reason}\n"
    message += f"💱 ارزهای تحت تأثیر: {', '.join(affected_coins[:5])}"
    if len(affected_coins) > 5:
        message += f" و {len(affected_coins) - 5} ارز دیگر"
    message += f"\n⏰ زمان: {get_current_persian_time()}"
    
    return send_sms_notification(to_phone_number, message)

def send_test_notification(to_phone_number):
    """
    ارسال پیام تست برای بررسی عملکرد سیستم اعلان
    
    Args:
        to_phone_number (str): شماره موبایل گیرنده (استفاده نمی‌شود)
        
    Returns:
        dict: وضعیت ارسال و پیام
    """
    # دریافت چت آیدی تلگرام از SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    if not chat_id:
        logger.error("چت آیدی تلگرام یافت نشد")
        return {
            "success": False,
            "message": "چت آیدی تلگرام یافت نشد. لطفاً ابتدا تنظیمات تلگرام را انجام دهید."
        }
    
    # ارسال پیام تست از طریق تلگرام
    return telegram_send_test(chat_id)

def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی
    
    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")