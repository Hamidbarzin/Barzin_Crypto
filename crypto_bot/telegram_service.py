"""
سرویس اعلان و هشدار Telegram برای ارسال پیام و تصویر در مورد فرصت‌های خرید و فروش و نوسانات بازار
"""

import os
import logging
import asyncio
from datetime import datetime
import pathlib

# تنظیم لاگر
logger = logging.getLogger(__name__)

# کنترل دسترسی به تلگرام
TELEGRAM_AVAILABLE = False

# این متغیر به عنوان پرچم برای دسترسی به ماژول تلگرام استفاده می‌شود
_telegram = None
_telegram_error = None

try:
    # Using the PTB v13.x API
    from telegram import Bot, ParseMode
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
    _telegram = Bot
    _telegram_error = TelegramError
    logger.info("Python-telegram-bot library loaded successfully.")
except ImportError as e:
    logger.warning(f"Python-telegram-bot library not installed ({str(e)}). Telegram features will be disabled.")
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
    'default': 722627622  # چت آیدی کاربر - به صورت عدد صحیح
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


def send_telegram_message(chat_id, message, parse_mode=None, max_retries=3, retry_delay=1):
    """
    ارسال پیام متنی به کاربر از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        message (str): متن پیام
        parse_mode (str): نوع پارس پیام ('HTML' یا 'Markdown') یا None برای بدون پارس
        max_retries (int): حداکثر تعداد تلاش‌های مجدد در صورت خطا
        retry_delay (int): تاخیر به ثانیه بین تلاش‌های مجدد

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # استفاده از چت آیدی پیش‌فرض اگر مقدار ورودی مشخص نشده باشد
    if not chat_id:
        default_chat_id = os.environ.get('DEFAULT_CHAT_ID', CHAT_IDS.get('default'))
        if default_chat_id:
            chat_id = default_chat_id
            logger.info(f"استفاده از چت آیدی پیش‌فرض: {chat_id}")
        else:
            logger.error("چت آیدی مشخص نشده و چت آیدی پیش‌فرض نیز یافت نشد.")
            return False
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("کتابخانه تلگرام نصب نشده است")
        return False
        
    # بررسی مجدد توکن تلگرام از متغیرهای محیطی
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("توکن بات تلگرام تنظیم نشده است")
        return False
        
    # اطمینان از اینکه chat_id به فرمت عددی است
    try:
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
    except Exception as e:
        logger.warning(f"خطا در تبدیل چت آیدی به عدد: {str(e)}")
        # ادامه کار بدون تبدیل

    # تبدیل ParseMode به نوع مناسب
    if parse_mode == 'HTML':
        parse_mode_enum = 'HTML'
    elif parse_mode == 'Markdown':
        parse_mode_enum = 'MarkdownV2' 
    else:
        parse_mode_enum = parse_mode
    
    # اضافه کردن اطلاعات دیباگ
    logger.info(f"تلاش برای ارسال پیام به چت آیدی: {chat_id} (نوع: {type(chat_id).__name__})")
    
    # ایجاد یک لوپ آسنکرون برای اجرای کد آسنکرون
    async def send_message_async():
        # ایجاد بات داخل تابع آسنکرون
        bot = _telegram.Bot(token=token)
        # ارسال پیام
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode_enum)
    
    # تلاش مجدد با تاخیر
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
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
            last_error = e
            retries += 1
            logger.warning(f"خطا در ارسال پیام تلگرام (تلاش {retries}/{max_retries}): {str(e)}")
            
            if retries <= max_retries:
                logger.info(f"تلاش مجدد پس از {retry_delay} ثانیه...")
                import time
                time.sleep(retry_delay)  # تاخیر قبل از تلاش مجدد
            else:
                logger.error(f"همه تلاش‌ها برای ارسال پیام به {chat_id} با شکست مواجه شد")
                return False
    
    # اگر به اینجا برسیم، یعنی همه تلاش‌ها ناموفق بوده‌اند
    logger.error(f"خطا در ارسال پیام تلگرام پس از {max_retries} تلاش: {str(last_error)}")
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
        # تبدیل chat_id به عدد صحیح
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
            
        # استفاده از کلید 'default' برای ذخیره چت آیدی پیش‌فرض
        if chat_id == CHAT_IDS.get('default'):
            key = 'default'
        else:
            key = f"user_{chat_id}"  # استفاده از پیشوند برای کلیدهای دیگر
            
        # ذخیره اطلاعات کاربر
        if user_info is None:
            user_info = {"registered_at": get_current_persian_time()}
            
        # ثبت کاربر در دیکشنری
        CHAT_IDS[key] = chat_id
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
        chat_id = os.environ.get('DEFAULT_CHAT_ID', CHAT_IDS.get('default'))
        if not chat_id:
            return {
                "success": False,
                "message": "چت آیدی پیش‌فرض تنظیم نشده است"
            }
    
    # اطمینان از اینکه chat_id به فرمت عددی است
    try:
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
    except Exception as e:
        logger.warning(f"خطا در تبدیل چت آیدی به عدد: {str(e)}")
        return {
            "success": False,
            "message": f"فرمت چت آیدی نادرست است. لطفاً یک عدد وارد کنید. خطا: {str(e)}"
        }
            
    message = "🤖 <b>پیام تست از ربات معامله ارز دیجیتال</b>\n\n"
    message += "سیستم اعلان‌های تلگرام فعال است.\n\n"
    message += f"⏰ <b>زمان:</b> {get_current_persian_time()}"

    # اضافه کردن اطلاعات دیباگ
    logger.info(f"ارسال پیام تست به چت آیدی: {chat_id} (نوع: {type(chat_id).__name__})")

    try:
        result = send_telegram_message(chat_id, message)
        if result:
            return {
                "success": True,
                "message": "پیام تست با موفقیت ارسال شد."
            }
        else:
            # بررسی علت احتمالی خطا
            return {
                "success": False,
                "message": ("خطا در ارسال پیام تست. احتمالاً شما هنوز با ربات گفتگو را شروع نکرده‌اید. "
                           "لطفاً ابتدا به @GrowthFinderBot در تلگرام رفته و دکمه Start را بزنید، "
                           "سپس چت آیدی خود را با ربات @userinfobot بررسی کنید.")
            }
    except Exception as e:
        error_msg = str(e)
        if "Chat not found" in error_msg:
            return {
                "success": False,
                "message": ("کاربر با چت آیدی وارد شده پیدا نشد. لطفاً مطمئن شوید که: "
                           "1) چت آیدی صحیح است "
                           "2) گفتگو با ربات @GrowthFinderBot را در تلگرام شروع کرده‌اید")
            }
        else:
            return {
                "success": False,
                "message": f"خطا در ارسال پیام تست: {error_msg}"
            }


def get_bot_info(max_retries=2, retry_delay=1):
    """
    دریافت اطلاعات بات تلگرام

    Args:
        max_retries (int): حداکثر تعداد تلاش‌های مجدد در صورت خطا
        retry_delay (int): تاخیر به ثانیه بین تلاش‌های مجدد

    Returns:
        dict: اطلاعات بات یا اطلاعات خطا
    """
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("کتابخانه تلگرام نصب نشده است")
        return {
            "available": False,
            "message": "کتابخانه python-telegram-bot نصب نشده است"
        }
    
    # بررسی مجدد توکن تلگرام از متغیرهای محیطی
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("توکن بات تلگرام تنظیم نشده است")
        return {
            "available": False, 
            "message": "توکن بات تلگرام تنظیم نشده است. لطفاً متغیر محیطی TELEGRAM_BOT_TOKEN را تنظیم کنید."
        }

    # ایجاد یک تابع آسنکرون
    async def get_me_async():
        bot = _telegram.Bot(token=token)
        return await bot.get_me()
    
    # تلاش چندباره با تاخیر
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
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
            last_error = e
            retries += 1
            logger.warning(f"Error getting bot information (attempt {retries}/{max_retries}): {str(e)}")
            
            if retries <= max_retries:
                logger.info(f"Retrying after {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)  # Delay before retrying
    
    # If we reach here, all attempts have failed
    error_msg = str(last_error) if last_error else "unknown reason"
    logger.error(f"Error getting bot information after {max_retries} attempts: {error_msg}")
    
    # Provide default information when Telegram API is not accessible
    token_valid = bool(token and len(token) > 20)  # Quick validation of token
    return {
        "available": False,
        "token_seems_valid": token_valid,
        "message": f"Error connecting to Telegram API: {error_msg}",
        "username": "GrowthFinderBot",  # Default information when API is not accessible
        "link": "https://t.me/GrowthFinderBot",
        "name": "CryptoSage Bot",
        "id": 0
    }
        
def get_chat_debug_info(chat_id=None, max_retries=2, retry_delay=1):
    """
    دریافت اطلاعات دیباگ برای یک چت
    
    Args:
        chat_id (int or str, optional): شناسه چت مورد نظر
        max_retries (int): حداکثر تعداد تلاش‌های مجدد در صورت خطا
        retry_delay (int): تاخیر به ثانیه بین تلاش‌های مجدد
        
    Returns:
        dict: اطلاعات دیباگ
    """
    debug_info = {
        "success": False,
        "chat_info": None,
        "error": None,
        "telegram_available": TELEGRAM_AVAILABLE,
        "token_available": False,
        "token_value_preview": "",
        "default_chat_id_env": os.environ.get('DEFAULT_CHAT_ID'),
        "default_chat_id": CHAT_IDS.get('default'),
        "default_chat_id_type": type(CHAT_IDS.get('default')).__name__,
    }
    
    # بررسی مجدد توکن تلگرام از متغیرهای محیطی
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    
    # افزودن اطلاعات بیشتر درباره توکن تلگرام
    if token:
        debug_info["token_available"] = True
        # نمایش بخشی از توکن برای دیباگ (با حفظ امنیت)
        token_preview = f"{token[:5]}...{token[-4:]}" if len(token) > 10 else "توکن کوتاه (غیر معتبر)"
        debug_info["token_value_preview"] = token_preview
    else:
        debug_info["error"] = "توکن بات تلگرام تنظیم نشده است"
        return debug_info
    
    if not TELEGRAM_AVAILABLE or _telegram is None:
        debug_info["error"] = "کتابخانه تلگرام نصب نشده است"
        return debug_info
    
    if chat_id is None:
        chat_id = os.environ.get('DEFAULT_CHAT_ID', CHAT_IDS.get('default'))
        if not chat_id:
            debug_info["error"] = "چت آیدی تعیین نشده است"
            return debug_info
    
    # تبدیل chat_id به عدد صحیح در صورت نیاز
    try:
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
    except Exception as e:
        debug_info["error"] = f"خطا در تبدیل چت آیدی: {str(e)}"
        return debug_info
    
    # تابع آسنکرون برای دریافت اطلاعات چت
    async def get_chat_async():
        bot = _telegram.Bot(token=token)
        try:
            chat = await bot.get_chat(chat_id=chat_id)
            return {"success": True, "chat": chat}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # تلاش چندباره با تاخیر
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
            # استفاده از asyncio برای اجرای کد آسنکرون
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(get_chat_async(), loop)
                    result = future.result(timeout=10)
                else:
                    result = loop.run_until_complete(get_chat_async())
            except RuntimeError:
                result = asyncio.run(get_chat_async())
                
            if result["success"]:
                chat = result["chat"]
                debug_info["success"] = True
                debug_info["chat_info"] = {
                    "id": chat.id,
                    "type": chat.type,
                    "title": getattr(chat, "title", None),
                    "username": getattr(chat, "username", None),
                    "first_name": getattr(chat, "first_name", None),
                    "last_name": getattr(chat, "last_name", None),
                }
                return debug_info
            else:
                last_error = result["error"]
                retries += 1
                logger.warning(f"Error getting chat information (attempt {retries}/{max_retries}): {last_error}")
                
                if retries <= max_retries:
                    logger.info(f"Retrying after {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)  # Delay before retrying
                else:
                    debug_info["error"] = f"Error getting chat information after multiple attempts: {last_error}"
        except Exception as e:
            last_error = str(e)
            retries += 1
            logger.warning(f"Error running chat debug (attempt {retries}/{max_retries}): {last_error}")
            
            if retries <= max_retries:
                logger.info(f"Retrying after {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)  # Delay before retrying
            else:
                debug_info["error"] = f"Error running chat debug: {last_error}"
                
    # If we reach here, all attempts have failed
    error_msg = str(last_error) if last_error else "unknown reason"
    logger.error(f"Error getting chat information after {max_retries} attempts: {error_msg}")
    debug_info["error"] = error_msg
    return debug_info


def send_telegram_photo(chat_id, photo_path, caption=None, parse_mode='HTML', max_retries=3, retry_delay=1):
    """
    ارسال عکس به کاربر از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        photo_path (str): مسیر فایل عکس
        caption (str, optional): توضیحات عکس
        parse_mode (str): نوع پارس پیام ('HTML' یا 'Markdown')
        max_retries (int): حداکثر تعداد تلاش‌های مجدد در صورت خطا
        retry_delay (int): تاخیر به ثانیه بین تلاش‌های مجدد

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("Telegram library is not installed")
        return False
        
    # Check Telegram token from environment variables
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("Telegram bot token is not set")
        return False
        
    # Ensure chat_id is in numeric format
    try:
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
    except Exception as e:
        logger.warning(f"Error converting chat ID to number: {str(e)}")
        # Continue without conversion
        
    # Check if the file exists
    photo_file = pathlib.Path(photo_path)
    if not photo_file.exists():
        logger.error(f"Image file not found at path {photo_path}.")
        return False
        
    # Convert ParseMode to appropriate type
    if parse_mode == 'HTML':
        parse_mode_enum = 'HTML'
    elif parse_mode == 'Markdown':
        parse_mode_enum = 'MARKDOWN_V2'
    else:
        parse_mode_enum = parse_mode
    
    # Add debug information
    logger.info(f"Attempting to send image to chat ID: {chat_id} from path {photo_path}")
    
    # Create an async loop for executing async code
    async def send_photo_async():
        # Create bot inside async function
        bot = _telegram.Bot(token=token)
        # Open the image file
        with open(photo_path, 'rb') as photo:
            # Send image
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode_enum if caption else None
            )
    
    # Retry with delay
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
            # بررسی وجود لوپ رویداد و اجرای تابع آسنکرون
            try:
                # اگر لوپ رویداد در حال اجرا باشد
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # ایجاد تسک جدید در لوپ موجود
                    future = asyncio.run_coroutine_threadsafe(send_photo_async(), loop)
                    # منتظر اتمام تسک می‌مانیم
                    future.result(timeout=10)  # تایم‌اوت 10 ثانیه
                else:
                    # اجرا در لوپ فعلی
                    loop.run_until_complete(send_photo_async())
            except RuntimeError:
                # اگر لوپ رویداد وجود نداشته باشد، یک لوپ جدید ایجاد می‌کنیم
                asyncio.run(send_photo_async())
            
            logger.info(f"تصویر با موفقیت به چت {chat_id} ارسال شد")
            return True
            
        except Exception as e:
            last_error = e
            retries += 1
            logger.warning(f"خطا در ارسال تصویر تلگرام (تلاش {retries}/{max_retries}): {str(e)}")
            
            if retries <= max_retries:
                logger.info(f"تلاش مجدد پس از {retry_delay} ثانیه...")
                import time
                time.sleep(retry_delay)  # تاخیر قبل از تلاش مجدد
            else:
                logger.error(f"همه تلاش‌ها برای ارسال تصویر به {chat_id} با شکست مواجه شد")
                return False
    
    # اگر به اینجا برسیم، یعنی همه تلاش‌ها ناموفق بوده‌اند
    logger.error(f"خطا در ارسال تصویر تلگرام پس از {max_retries} تلاش: {str(last_error)}")
    return False


def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی

    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")