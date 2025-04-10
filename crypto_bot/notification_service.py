"""
Notification and Alert Service for Buy/Sell Opportunities and Market Volatility - Routing to Telegram

This file acts as a middleware layer that routes all notifications to the Telegram service.
All previous methods are maintained for compatibility, but now use Telegram instead of SMS.
"""

import os
import logging
from datetime import datetime
from flask import session
from crypto_bot.telegram_service import send_telegram_message, send_buy_sell_notification as telegram_send_buy_sell, send_volatility_alert as telegram_send_volatility, send_market_trend_alert as telegram_send_market_trend, send_test_notification as telegram_send_test, get_current_persian_time

# Configure logger
logger = logging.getLogger(__name__)

def send_sms_notification(to_phone_number, message):
    """
    Route message to Telegram instead of SMS
    
    Args:
        to_phone_number (str): Recipient phone number (no longer used)
        message (str): Message text
        
    Returns:
        bool: Whether the message was sent successfully
    """
    logger.info("Routing message to Telegram...")
    
    # Get Telegram chat ID from SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    if not chat_id:
        logger.error("Telegram chat ID not found")
        return False
        
    return send_telegram_message(chat_id, message)

def send_buy_sell_notification(to_phone_number, symbol, action, price, reason):
    """
    Send buy or sell notification
    
    Args:
        to_phone_number (str): Recipient phone number
        symbol (str): Cryptocurrency symbol
        action (str): 'buy' or 'sell' (in Persian: 'خرید' or 'فروش')
        price (float): Current price
        reason (str): Recommendation reason
        
    Returns:
        bool: Whether the notification was sent successfully
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

def send_test_notification(to_phone_number=None):
    """
    ارسال پیام تست برای بررسی عملکرد سیستم اعلان
    
    Args:
        to_phone_number (str, optional): شماره موبایل گیرنده (استفاده نمی‌شود)
        
    Returns:
        dict: وضعیت ارسال و پیام
    """
    # استفاده از چت آیدی موجود در session یا استفاده از چت آیدی پیش‌فرض
    chat_id = session.get('telegram_chat_id', None)
    
    # اگر در session چت آیدی نباشد، از تابع telegram_send_test استفاده می‌کنیم
    # که می‌تواند از چت آیدی پیش‌فرض استفاده کند
    return telegram_send_test(chat_id)

def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی
    
    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")