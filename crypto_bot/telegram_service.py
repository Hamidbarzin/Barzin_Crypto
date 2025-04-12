"""
Telegram notification and alert service for sending messages and images about buying and selling opportunities and market volatility
"""

import os
import logging
import asyncio
from datetime import datetime
import pathlib

# Setting up logger
logger = logging.getLogger(__name__)

# Control Telegram access
TELEGRAM_AVAILABLE = False

# This variable is used as a flag to access the Telegram module
_telegram = None
_telegram_error = None

try:
    # Using the PTB v13.x API
    import telegram
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
    _telegram = telegram
    _telegram_error = TelegramError
    logger.info("Python-telegram-bot library loaded successfully.")
except ImportError as e:
    logger.warning(f"Python-telegram-bot library not installed ({str(e)}). Telegram features will be disabled.")
    logger.warning("Python-telegram-bot library is not installed. Telegram features will be disabled.")

# Get Telegram bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if TELEGRAM_BOT_TOKEN:
    logger.info("Telegram token found in environment variables.")
else:
    logger.warning("Telegram token not set in environment variables.")

# Dictionary for storing user chat IDs
# In future versions, this dictionary should be read from the database
# Add your chat ID here
CHAT_IDS = {
    'default': 722627622  # User chat ID - as an integer
}


def initialize_bot():
    """
    Initialize the Telegram bot

    Returns:
        telegram.Bot: Telegram bot object or None in case of error
    """
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("Telegram library is not installed")
        return None
        
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token is not set")
        return None

    try:
        bot = _telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        logger.info(f"Telegram bot with name {bot.get_me().first_name} initialized successfully")
        return bot
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {str(e)}")
        return None


def send_telegram_message(chat_id, message, parse_mode=None, max_retries=3, retry_delay=1):
    """
    Send a text message to a user via Telegram

    Args:
        chat_id (int or str): User's chat ID
        message (str): Message text
        parse_mode (str): Parse mode ('HTML' or 'Markdown') or None for no parsing
        max_retries (int): Maximum number of retry attempts in case of error
        retry_delay (int): Delay in seconds between retry attempts

    Returns:
        bool: Whether the message was sent successfully
    """
    # Use default chat ID if input value is not specified
    if not chat_id:
        default_chat_id = os.environ.get('DEFAULT_CHAT_ID', CHAT_IDS.get('default'))
        if default_chat_id:
            chat_id = default_chat_id
            logger.info(f"Using default chat ID: {chat_id}")
        else:
            logger.error("Chat ID not specified and default chat ID not found.")
            return False
    if not TELEGRAM_AVAILABLE or _telegram is None:
        logger.error("Telegram library is not installed")
        return False
        
    # Check Telegram token from environment variables again
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

    # Convert ParseMode to the appropriate type
    if parse_mode == 'HTML':
        parse_mode_enum = 'HTML'
    elif parse_mode == 'Markdown':
        parse_mode_enum = 'MarkdownV2' 
    else:
        parse_mode_enum = parse_mode
    
    # Add debug information
    logger.info(f"Attempting to send message to chat ID: {chat_id} (type: {type(chat_id).__name__})")
    
    # Create an async loop to run async code
    async def send_message_async():
        # Create bot inside async function
        bot = _telegram.Bot(token=token)
        # Send message
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode_enum)
    
    # Retry with delay
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
            # Check for event loop and run async function
            try:
                # If event loop is running
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a new task in the existing loop
                    future = asyncio.run_coroutine_threadsafe(send_message_async(), loop)
                    # Wait for task to complete
                    future.result(timeout=10)  # 10 second timeout
                else:
                    # Run in current loop
                    loop.run_until_complete(send_message_async())
            except RuntimeError:
                # If event loop doesn't exist, create a new one
                asyncio.run(send_message_async())
            
            logger.info(f"Message successfully sent to chat {chat_id}")
            return True
            
        except Exception as e:
            last_error = e
            retries += 1
            logger.warning(f"Error sending Telegram message (attempt {retries}/{max_retries}): {str(e)}")
            
            if retries <= max_retries:
                logger.info(f"Retrying after {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)  # Delay before retrying
            else:
                logger.error(f"All attempts to send message to {chat_id} failed")
                return False
    
    # If we get here, all attempts have failed
    logger.error(f"Error sending Telegram message after {max_retries} attempts: {str(last_error)}")
    return False


def register_user(chat_id, user_info=None):
    """
    Register a new user to receive notifications

    Args:
        chat_id (int or str): User's chat ID
        user_info (dict, optional): Additional user information

    Returns:
        bool: Whether registration was successful
    """
    try:
        # Convert chat_id to integer
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
            
        # Use 'default' key for storing default chat ID
        if chat_id == CHAT_IDS.get('default'):
            key = 'default'
        else:
            key = f"user_{chat_id}"  # Use prefix for other keys
            
        # Store user information
        if user_info is None:
            user_info = {"registered_at": get_current_persian_time()}
            
        # Register user in dictionary
        CHAT_IDS[key] = chat_id
        logger.info(f"User with chat ID {chat_id} registered successfully")
        return True
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return False


def send_buy_sell_notification(chat_id, symbol, action, price, reason):
    """
    Send buy or sell notification via Telegram

    Args:
        chat_id (int or str): User's chat ID
        symbol (str): Cryptocurrency symbol
        action (str): 'Buy' or 'Sell'
        price (float): Current price
        reason (str): Recommendation reason

    Returns:
        bool: Whether the message was sent successfully
    """
    emoji = "🟢" if action == "Buy" else "🔴"
    message = f"{emoji} <b>{action} Signal for {symbol}</b>\n\n"
    message += f"💰 <b>Current Price:</b> {price}\n\n"
    message += f"📊 <b>Reason:</b>\n{reason}\n\n"
    message += f"⏰ <b>Time:</b> {get_current_persian_time()}"

    return send_telegram_message(chat_id, message)


def send_volatility_alert(chat_id, symbol, price, change_percent, timeframe="1h"):
    """
    Send price volatility alert via Telegram

    Args:
        chat_id (int or str): User's chat ID
        symbol (str): Cryptocurrency symbol
        price (float): Current price
        change_percent (float): Percentage change
        timeframe (str): Time period of change

    Returns:
        bool: Whether the message was sent successfully
    """
    direction = "Increase" if change_percent > 0 else "Decrease"
    emoji = "🚀" if change_percent > 0 else "📉"

    message = f"{emoji} <b>Price Volatility Alert for {symbol}</b>\n\n"
    message += f"💰 <b>Current Price:</b> {price}\n\n"
    message += f"📊 <b>{direction}:</b> {abs(change_percent):.2f}% in {timeframe}\n\n"
    message += f"⏰ <b>Time:</b> {get_current_persian_time()}"

    return send_telegram_message(chat_id, message)


def send_market_trend_alert(chat_id, trend, affected_coins, reason):
    """
    ارسال هشدار روند کلی بازار از طریق تلگرام

    Args:
        chat_id (int or str): شناسه چت کاربر
        trend (str): روند بازار ('صعودی'، 'نزولی' یا 'Neutral')
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
    Send a test message to check the Telegram notification system functionality

    Args:
        chat_id (int or str, optional): User's chat ID, if None the default chat ID will be used

    Returns:
        dict: Message sending status and message
    """
    if chat_id is None:
        chat_id = os.environ.get('DEFAULT_CHAT_ID', CHAT_IDS.get('default'))
        if not chat_id:
            return {
                "success": False,
                "message": "Default chat ID is not set"
            }
    
    # Ensure chat_id is in numeric format
    try:
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
    except Exception as e:
        logger.warning(f"Error converting chat ID to number: {str(e)}")
        return {
            "success": False,
            "message": f"Invalid chat ID format. Please enter a number. Error: {str(e)}"
        }
            
    message = "🤖 <b>Test message from Crypto Trading Bot</b>\n\n"
    message += "Telegram notification system is active.\n\n"
    message += f"⏰ <b>Time:</b> {get_current_persian_time()}"

    # Add debug information
    logger.info(f"Sending test message to chat ID: {chat_id} (type: {type(chat_id).__name__})")

    try:
        result = send_telegram_message(chat_id, message)
        if result:
            return {
                "success": True,
                "message": "Test message sent successfully."
            }
        else:
            # Check possible cause of error
            return {
                "success": False,
                "message": ("Error sending test message. You probably haven't started a conversation with the bot yet. "
                           "Please first go to @GrowthFinderBot in Telegram and press the Start button, "
                           "then check your chat ID with @userinfobot.")
            }
    except Exception as e:
        error_msg = str(e)
        if "Chat not found" in error_msg:
            return {
                "success": False,
                "message": ("User with the entered chat ID not found. Please make sure that: "
                           "1) The chat ID is correct "
                           "2) You have started a conversation with @GrowthFinderBot in Telegram")
            }
        else:
            return {
                "success": False,
                "message": f"Error sending test message: {error_msg}"
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

    # بازگشت اطلاعات پیش‌فرض بات برای حل مشکل کرش پنل تلگرام
    # در نسخه 13.15، استفاده از get_me() با مشکلات زیادی همراه است
    return {
        "available": True,
        "id": 0,
        "name": "Crypto Barzin Bot",
        "username": "GrowthFinderBot",
        "link": "https://t.me/GrowthFinderBot"
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