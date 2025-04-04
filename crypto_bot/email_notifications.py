"""
سابقاً سرویس اعلان و هشدار ایمیلی - اکنون مسیردهی به تلگرام

این فایل به عنوان یک لایه میانی عمل می‌کند که تمام اعلان‌های ایمیلی را به سمت سرویس تلگرام هدایت می‌کند.
همه متدهای قبلی برای حفظ سازگاری حفظ شده‌اند، اما اکنون به جای ارسال ایمیل، از تلگرام استفاده می‌کنند.
"""

import os
import sys
import logging
from datetime import datetime
from flask import session
from crypto_bot.telegram_service import (
    send_telegram_message, 
    send_buy_sell_notification as telegram_send_buy_sell,
    send_volatility_alert as telegram_send_volatility, 
    send_market_trend_alert as telegram_send_market_trend, 
    send_test_notification as telegram_send_test, 
    get_current_persian_time
)

# تنظیم لاگر
logger = logging.getLogger(__name__)

def send_email_via_sendgrid(to_email, subject, html_content, text_content=None):
    """
    ارسال اعلان از طریق تلگرام (به جای SendGrid)

    Args:
        to_email (str): آدرس ایمیل گیرنده (استفاده نمی‌شود)
        subject (str): موضوع ایمیل
        html_content (str): محتوای HTML ایمیل
        text_content (str, optional): محتوای متنی ایمیل

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    logger.info("استفاده از تلگرام به جای SendGrid")
    
    # اگر محتوای متنی ارائه نشده باشد، از همان محتوای HTML استفاده می‌کنیم
    if text_content is None:
        import re
        # حذف تگ‌های HTML برای نسخه متنی
        text_content = re.sub(r'<.*?>', '', html_content)
    
    # ترکیب موضوع و محتوا برای پیام تلگرامی
    telegram_message = f"*{subject}*\n\n{text_content}"
    
    # دریافت چت آیدی تلگرام از SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    if not chat_id:
        logger.error("چت آیدی تلگرام یافت نشد")
        return False
    
    return send_telegram_message(chat_id, telegram_message, parse_mode='Markdown')

def send_email_via_smtp(to_email, subject, html_content, text_content=None):
    """
    ارسال اعلان از طریق تلگرام (به جای SMTP)

    Args:
        to_email (str): آدرس ایمیل گیرنده (استفاده نمی‌شود)
        subject (str): موضوع ایمیل
        html_content (str): محتوای HTML ایمیل
        text_content (str, optional): محتوای متنی ایمیل

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # اینجا هم از همان متد بالا استفاده می‌کنیم
    return send_email_via_sendgrid(to_email, subject, html_content, text_content)

def send_email_notification(to_email, subject, html_content, text_content=None):
    """
    ارسال اعلان از طریق تلگرام (به جای SendGrid یا SMTP)

    Args:
        to_email (str): آدرس ایمیل گیرنده (استفاده نمی‌شود)
        subject (str): موضوع ایمیل
        html_content (str): محتوای HTML ایمیل
        text_content (str, optional): محتوای متنی ایمیل

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # ارسال مستقیم از طریق تلگرام
    return send_email_via_sendgrid(to_email, subject, html_content, text_content)

def send_buy_sell_email(to_email=None, symbol="BTC/USDT", action="خرید", price=50000, reason="تحلیل تکنیکال"):
    """
    ارسال اعلان خرید یا فروش از طریق تلگرام (جایگزین ایمیل)

    Args:
        to_email (str, optional): آدرس ایمیل گیرنده (استفاده نمی‌شود، فقط برای سازگاری با کد قبلی)
        symbol (str): نماد ارز
        action (str): 'خرید' یا 'فروش'
        price (float): قیمت فعلی
        reason (str): دلیل توصیه

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # دریافت چت آیدی تلگرام از SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    # اگر چت آیدی نداریم، از چت آیدی پیش‌فرض استفاده می‌شود
    chat_id_to_use = chat_id if chat_id else None
    
    # استفاده از تابع ارسال اعلان خرید و فروش تلگرام
    return telegram_send_buy_sell(chat_id_to_use, symbol, action, price, reason)

def send_volatility_email(to_email=None, symbol="BTC/USDT", price=50000, change_percent=5.5, timeframe="1h"):
    """
    ارسال هشدار نوسان قیمت از طریق تلگرام

    Args:
        to_email (str, optional): آدرس ایمیل گیرنده (استفاده نمی‌شود، فقط برای سازگاری با کد قبلی)
        symbol (str): نماد ارز
        price (float): قیمت فعلی
        change_percent (float): درصد تغییر
        timeframe (str): بازه زمانی تغییر

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # دریافت چت آیدی تلگرام از SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    # اگر چت آیدی نداریم، از چت آیدی پیش‌فرض استفاده می‌شود
    chat_id_to_use = chat_id if chat_id else None
    
    # استفاده از تابع ارسال هشدار نوسان تلگرام
    return telegram_send_volatility(chat_id_to_use, symbol, price, change_percent, timeframe)

def send_market_trend_email(to_email=None, trend="صعودی", affected_coins=["BTC", "ETH", "XRP"], reason="تحلیل تکنیکال"):
    """
    ارسال هشدار روند کلی بازار از طریق تلگرام

    Args:
        to_email (str, optional): آدرس ایمیل گیرنده (استفاده نمی‌شود، فقط برای سازگاری با کد قبلی)
        trend (str): روند بازار ('صعودی'، 'نزولی' یا 'خنثی')
        affected_coins (list): لیست ارزهای تحت تأثیر
        reason (str): دلیل روند

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # دریافت چت آیدی تلگرام از SESSION
    chat_id = session.get('telegram_chat_id', None)
    
    # اگر چت آیدی نداریم، از چت آیدی پیش‌فرض استفاده می‌شود
    chat_id_to_use = chat_id if chat_id else None
    
    # استفاده از تابع ارسال هشدار روند کلی بازار تلگرام
    return telegram_send_market_trend(chat_id_to_use, trend, affected_coins, reason)

def send_test_email(to_email=None):
    """
    ارسال پیام تست تلگرامی به جای ایمیل تست
    
    Args:
        to_email (str, optional): آدرس ایمیل گیرنده (استفاده نمی‌شود، فقط برای حفظ سازگاری با کد قبلی)
        
    Returns:
        dict: وضعیت ارسال و پیام
    """
    logger.info("ارسال پیام تست تلگرامی")
    
    # دریافت چت آیدی تلگرام از SESSION یا استفاده از چت آیدی پیش‌فرض
    chat_id = session.get('telegram_chat_id', None)
    
    # استفاده از تابع تست تلگرام که قابلیت استفاده از چت آیدی پیش‌فرض را دارد
    return telegram_send_test(chat_id)

def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی

    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")