"""
سرویس اعلان و هشدار Telegram برای ارسال پیام در مورد فرصت‌های خرید و فروش و نوسانات بازار
"""

import os
import logging
from datetime import datetime

# تنظیم لاگر
logger = logging.getLogger(__name__)

# کنترل دسترسی به تلگرام
TELEGRAM_AVAILABLE = False

# این متغیر به عنوان پرچم برای دسترسی به ماژول تلگرام استفاده می‌شود
_telegram = None
_telegram_error = None

try:
    import telegram
    import asyncio
    from telegram.error import TelegramError
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
    _telegram = telegram
    _telegram_error = TelegramError
    logger.info("کتابخانه python-telegram-bot با موفقیت بارگذاری شد.")
except ImportError:
    logger.warning("کتابخانه python-telegram-bot نصب نشده است. قابلیت‌های تلگرام غیرفعال خواهند بود.")

# دریافت توکن بات Telegram از متغیرهای محیطی
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if TELEGRAM_BOT_TOKEN:
    logger.info("توکن تلگرام در متغیرهای محیطی یافت شد.")
else:
    logger.warning("توکن تلگرام در متغیرهای محیطی تنظیم نشده است.")

# دیکشنری برای نگهداری آیدی چت کاربران
# در نسخه‌های آینده، این دیکشنری باید از دیتابیس خوانده شود
# اضافه کردن چت آیدی خودتان اینجا
CHAT_IDS = {
    'default': '722627622'  # چت آیدی کاربر
}


def initialize_bot():
    """
    مقداردهی اولیه بات تلگرام

    Returns:
        telegram.Bot: آبجکت بات تلگرام یا None در صورت خطا
    """
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("کتابخانه تلگرام نصب نشده است")
        return None
        
    if not TELEGRAM_BOT_TOKEN:
        logger.error("توکن بات تلگرام تنظیم نشده است")
        return None

    try:
        bot = _telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        logger.info(f"بات تلگرام با نام {bot.get_me().first_name} با موفقیت راه‌اندازی شد")
        return bot
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی بات تلگرام: {str(e)}")
        return None


def send_telegram_message(chat_id, message, parse_mode='HTML'):
    """
    ارسال پیام متنی به کاربر از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        message (str): متن پیام
        parse_mode (str): نوع پارس پیام ('HTML' یا 'Markdown')

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("کتابخانه تلگرام نصب نشده است")
        return False
        
    if not TELEGRAM_BOT_TOKEN:
        logger.error("توکن بات تلگرام تنظیم نشده است")
        return False

    try:
        # تبدیل ParseMode به نوع مناسب
        if parse_mode == 'HTML':
            parse_mode_enum = ParseMode.HTML
        elif parse_mode == 'Markdown':
            parse_mode_enum = ParseMode.MARKDOWN_V2
        else:
            parse_mode_enum = parse_mode
        
        # ایجاد یک لوپ آسنکرون برای اجرای کد آسنکرون
        async def send_message_async():
            # ایجاد بات داخل تابع آسنکرون
            bot = _telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            # ارسال پیام
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode_enum)
            
        # بررسی وجود لوپ رویداد و اجرای تابع آسنکرون
        try:
            # اگر لوپ رویداد در حال اجرا باشد
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # ایجاد تسک جدید در لوپ موجود
                future = asyncio.run_coroutine_threadsafe(send_message_async(), loop)
                # منتظر اتمام تسک می‌مانیم
                future.result(timeout=10)  # تایم‌اوت 10 ثانیه
            else:
                # اجرا در لوپ فعلی
                loop.run_until_complete(send_message_async())
        except RuntimeError:
            # اگر لوپ رویداد وجود نداشته باشد، یک لوپ جدید ایجاد می‌کنیم
            asyncio.run(send_message_async())
        
        logger.info(f"پیام با موفقیت به چت {chat_id} ارسال شد")
        return True
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تلگرام: {str(e)}")
        return False


def register_user(chat_id, user_info=None):
    """
    ثبت کاربر جدید برای دریافت اعلان‌ها

    Args:
        chat_id (int or str): شناسه چت کاربر
        user_info (dict, optional): اطلاعات اضافی کاربر

    Returns:
        bool: آیا ثبت موفقیت‌آمیز بود
    """
    try:
        # در نسخه‌های آینده، این اطلاعات باید در دیتابیس ذخیره شوند
        CHAT_IDS[str(chat_id)] = user_info or {"registered_at": get_current_persian_time()}
        logger.info(f"کاربر با شناسه چت {chat_id} با موفقیت ثبت شد")
        return True
    except Exception as e:
        logger.error(f"خطا در ثبت کاربر: {str(e)}")
        return False


def send_buy_sell_notification(chat_id, symbol, action, price, reason):
    """
    ارسال اعلان خرید یا فروش از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        symbol (str): نماد ارز
        action (str): 'خرید' یا 'فروش'
        price (float): قیمت فعلی
        reason (str): دلیل توصیه

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    emoji = "🟢" if action == "خرید" else "🔴"
    message = f"{emoji} <b>سیگنال {action} برای {symbol}</b>\n\n"
    message += f"💰 <b>قیمت فعلی:</b> {price}\n\n"
    message += f"📊 <b>دلیل:</b>\n{reason}\n\n"
    message += f"⏰ <b>زمان:</b> {get_current_persian_time()}"

    return send_telegram_message(chat_id, message)


def send_volatility_alert(chat_id, symbol, price, change_percent, timeframe="1h"):
    """
    ارسال هشدار نوسان قیمت از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        symbol (str): نماد ارز
        price (float): قیمت فعلی
        change_percent (float): درصد تغییر
        timeframe (str): بازه زمانی تغییر

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    direction = "افزایش" if change_percent > 0 else "کاهش"
    emoji = "🚀" if change_percent > 0 else "📉"

    message = f"{emoji} <b>هشدار نوسان قیمت {symbol}</b>\n\n"
    message += f"💰 <b>قیمت فعلی:</b> {price}\n\n"
    message += f"📊 <b>{direction}:</b> {abs(change_percent):.2f}% در {timeframe}\n\n"
    message += f"⏰ <b>زمان:</b> {get_current_persian_time()}"

    return send_telegram_message(chat_id, message)


def send_market_trend_alert(chat_id, trend, affected_coins, reason):
    """
    ارسال هشدار روند کلی بازار از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        trend (str): روند بازار ('صعودی'، 'نزولی' یا 'خنثی')
        affected_coins (list): لیست ارزهای تحت تأثیر
        reason (str): دلیل روند

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    emoji = "🚀" if trend == "صعودی" else "📉" if trend == "نزولی" else "⚖️"

    message = f"{emoji} <b>تحلیل روند بازار: {trend}</b>\n\n"
    message += f"🔍 <b>دلیل:</b>\n{reason}\n\n"
    message += f"💱 <b>ارزهای تحت تأثیر:</b>\n{', '.join(affected_coins[:5])}"
    if len(affected_coins) > 5:
        message += f" و {len(affected_coins) - 5} ارز دیگر"
    message += f"\n\n⏰ <b>زمان:</b> {get_current_persian_time()}"

    return send_telegram_message(chat_id, message)


def send_test_notification(chat_id=None):
    """
    ارسال پیام تست برای بررسی عملکرد سیستم اعلان تلگرام

    Args:
        chat_id (int or str, optional): شناسه چت کاربر، اگر None باشد از چت آیدی پیش‌فرض استفاده می‌شود

    Returns:
        dict: وضعیت ارسال و پیام
    """
    if chat_id is None:
        chat_id = CHAT_IDS.get('default')
        if not chat_id:
            return {
                "success": False,
                "message": "چت آیدی پیش‌فرض تنظیم نشده است"
            }
            
    message = "🤖 <b>پیام تست از ربات معامله ارز دیجیتال</b>\n\n"
    message += "سیستم اعلان‌های تلگرام فعال است.\n\n"
    message += f"⏰ <b>زمان:</b> {get_current_persian_time()}"

    result = send_telegram_message(chat_id, message)
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


def get_bot_info():
    """
    دریافت اطلاعات بات تلگرام

    Returns:
        dict: اطلاعات بات یا None در صورت خطا
    """
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("کتابخانه تلگرام نصب نشده است")
        return {
            "available": False,
            "message": "کتابخانه python-telegram-bot نصب نشده است"
        }
        
    if not TELEGRAM_BOT_TOKEN:
        logger.error("توکن بات تلگرام تنظیم نشده است")
        return {
            "available": False, 
            "message": "توکن بات تلگرام تنظیم نشده است"
        }

    try:
        # ایجاد یک تابع آسنکرون
        async def get_me_async():
            bot = _telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return await bot.get_me()
        
        # بررسی وجود لوپ رویداد و اجرای تابع آسنکرون
        try:
            # اگر لوپ رویداد در حال اجرا باشد
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # ایجاد تسک جدید در لوپ موجود
                future = asyncio.run_coroutine_threadsafe(get_me_async(), loop)
                # منتظر اتمام تسک می‌مانیم
                me = future.result(timeout=10)  # تایم‌اوت 10 ثانیه
            else:
                # اجرا در لوپ فعلی
                me = loop.run_until_complete(get_me_async())
        except RuntimeError:
            # اگر لوپ رویداد وجود نداشته باشد، یک لوپ جدید ایجاد می‌کنیم
            me = asyncio.run(get_me_async())
        
        return {
            "available": True,
            "id": me.id,
            "name": me.first_name,
            "username": me.username,
            "link": f"https://t.me/{me.username}"
        }
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات بات: {str(e)}")
        return {
            "available": False,
            "message": f"خطا در دریافت اطلاعات بات: {str(e)}"
        }


def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی

    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")