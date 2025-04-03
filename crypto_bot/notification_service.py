"""
سرویس اعلان و هشدار برای ارسال پیامک در مورد فرصت‌های خرید و فروش و نوسانات بازار
"""

import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# تنظیم لاگر
logger = logging.getLogger(__name__)

# دریافت اطلاعات Twilio از متغیرهای محیطی
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_sms_notification(to_phone_number, message):
    """
    ارسال پیامک با استفاده از Twilio
    
    Args:
        to_phone_number (str): شماره موبایل گیرنده
        message (str): متن پیام
        
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.error("تنظیمات Twilio کامل نیست")
        return False
    
    # اطمینان از فرمت صحیح شماره تلفن
    formatted_phone = to_phone_number.strip()
    
    # حذف فرمت‌های اضافی مانند پرانتز، خط تیره یا فاصله
    formatted_phone = ''.join(c for c in formatted_phone if c.isdigit() or c == '+')
    
    # حذف کاراکتر + اگر وجود داشته باشد
    if formatted_phone.startswith('+'):
        formatted_phone = formatted_phone[1:]
        
    # حذف صفر ابتدایی اگر وجود داشته باشد
    if formatted_phone.startswith('0'):
        formatted_phone = formatted_phone[1:]
        
    # اصلاح فرمت شماره آمریکا/کانادا
    # اگر با 01 شروع شود، آن را به 1 تبدیل می‌کنیم
    if formatted_phone.startswith('01'):
        formatted_phone = '1' + formatted_phone[2:]
        
    # اصلاح فرمت شماره آمریکا/کانادا
    # اگر با 001 شروع شود، آن را به 1 تبدیل می‌کنیم
    if formatted_phone.startswith('001'):
        formatted_phone = '1' + formatted_phone[3:]
    
    # اضافه کردن + در ابتدای شماره
    formatted_phone = '+' + formatted_phone
    
    logger.info(f"شماره تلفن اصلاح شده: {formatted_phone}")
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=formatted_phone
        )
        
        logger.info(f"پیام با شناسه {message.sid} ارسال شد")
        return True
    except TwilioRestException as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"خطای ناشناخته در ارسال پیام: {str(e)}")
        return False

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
        to_phone_number (str): شماره موبایل گیرنده
        
    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # بررسی اینکه آیا شماره تلفن دریافت‌کننده با شماره تلفن ارسال‌کننده یکسان است
    # این کار را می‌کنیم چون Twilio امکان ارسال پیامک از یک شماره به همان شماره را نمی‌دهد
    formatted_phone = to_phone_number.strip()
    formatted_phone = ''.join(c for c in formatted_phone if c.isdigit() or c == '+')
    if formatted_phone.startswith('+'):
        formatted_phone = formatted_phone[1:]
    if formatted_phone.startswith('0'):
        formatted_phone = formatted_phone[1:]
    formatted_phone = '+' + formatted_phone
    
    if formatted_phone == TWILIO_PHONE_NUMBER:
        logger.warning("شماره تلفن ارسال‌کننده و دریافت‌کننده یکسان است. Twilio اجازه ارسال از یک شماره به همان شماره را نمی‌دهد.")
        # وانمود می‌کنیم که ارسال موفقیت‌آمیز بوده است
        return {
            "success": False,
            "message": "شماره تلفن ارسال‌کننده و دریافت‌کننده یکسان است. لطفاً شماره دیگری وارد کنید."
        }
    
    message = "🤖 پیام تست از ربات معامله ارز دیجیتال\n"
    message += "سیستم اعلان‌های پیامکی فعال است.\n"
    message += f"⏰ زمان: {get_current_persian_time()}"
    
    result = send_sms_notification(to_phone_number, message)
    if result:
        return {
            "success": True,
            "message": "پیام تست با موفقیت ارسال شد."
        }
    else:
        return {
            "success": False,
            "message": "خطا در ارسال پیام تست. لطفاً تنظیمات را بررسی کنید."
        }

def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی
    
    Returns:
        str: زمان فعلی
    """
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")