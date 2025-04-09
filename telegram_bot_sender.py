#!/usr/bin/env python3
"""
ماژول ارسال پیام تلگرام با استفاده از کتابخانه python-telegram-bot
این روش از API رسمی تلگرام استفاده می‌کند و پایدارتر است
"""

import os
import logging
from telegram import Bot, ParseMode
from telegram.error import TelegramError
import asyncio
from datetime import datetime
import random

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن و چت آیدی پیش‌فرض
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

# ایجاد یک نمونه از بات
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_message(chat_id=None, text="", parse_mode=None):
    """
    ارسال پیام متنی به تلگرام
    
    Args:
        chat_id (str or int): شناسه چت (اگر None باشد از مقدار پیش‌فرض استفاده می‌شود)
        text (str): متن پیام
        parse_mode (str): نوع پارس متن (HTML, Markdown یا None)
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if not chat_id:
        chat_id = DEFAULT_CHAT_ID
    
    try:
        logger.info(f"ارسال پیام به چت آیدی {chat_id}")
        
        # تبدیل چت آیدی به عدد اگر به صورت رشته باشد
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
        
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode
        )
        
        logger.info("پیام با موفقیت ارسال شد")
        return True
    
    except TelegramError as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {str(e)}")
        return False

async def send_photo(chat_id=None, photo_path=None, caption="", parse_mode=None):
    """
    ارسال تصویر به تلگرام
    
    Args:
        chat_id (str or int): شناسه چت (اگر None باشد از مقدار پیش‌فرض استفاده می‌شود)
        photo_path (str): مسیر فایل تصویر محلی
        caption (str): توضیحات تصویر
        parse_mode (str): نوع پارس متن توضیحات (HTML, Markdown یا None)
        
    Returns:
        bool: موفقیت یا شکست ارسال تصویر
    """
    if not chat_id:
        chat_id = DEFAULT_CHAT_ID
    
    if not photo_path:
        logger.error("خطا: هیچ تصویری برای ارسال مشخص نشده است")
        return False
    
    try:
        logger.info(f"ارسال تصویر به چت آیدی {chat_id}")
        
        # تبدیل چت آیدی به عدد اگر به صورت رشته باشد
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
        
        with open(photo_path, "rb") as photo_file:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=caption,
                parse_mode=parse_mode
            )
        
        logger.info("تصویر با موفقیت ارسال شد")
        return True
    
    except TelegramError as e:
        logger.error(f"خطا در ارسال تصویر: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {str(e)}")
        return False

async def get_bot_info():
    """
    دریافت اطلاعات بات تلگرام
    
    Returns:
        dict: اطلاعات بات یا None در صورت خطا
    """
    try:
        logger.info("دریافت اطلاعات بات")
        bot_info = await bot.get_me()
        logger.info(f"اطلاعات بات با موفقیت دریافت شد: {bot_info.first_name} (@{bot_info.username})")
        
        return {
            "id": bot_info.id,
            "first_name": bot_info.first_name,
            "username": bot_info.username,
            "can_join_groups": bot_info.can_join_groups,
            "can_read_all_group_messages": bot_info.can_read_all_group_messages,
            "supports_inline_queries": bot_info.supports_inline_queries
        }
    
    except TelegramError as e:
        logger.error(f"خطا در دریافت اطلاعات بات: {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {str(e)}")
        return None

async def send_test_message():
    """
    ارسال یک پیام تست ساده
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

سیستم اعلان‌های تلگرام با کتابخانه python-telegram-bot فعال است.
این پیام با استفاده از API رسمی تلگرام ارسال شده است.

⏰ <b>زمان:</b> {current_time}
    """
    
    return await send_message(text=message, parse_mode=ParseMode.HTML)

async def send_price_report():
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # مقادیر تصادفی برای نمایش (در نسخه نهایی باید با داده‌های واقعی جایگزین شود)
    coins = [
        {"symbol": "BTC", "name": "بیت‌کوین", "price": random.uniform(60000, 70000), "change": random.uniform(-3, 5)},
        {"symbol": "ETH", "name": "اتریوم", "price": random.uniform(3000, 4000), "change": random.uniform(-3, 5)},
        {"symbol": "BNB", "name": "بایننس کوین", "price": random.uniform(500, 600), "change": random.uniform(-3, 5)},
        {"symbol": "SOL", "name": "سولانا", "price": random.uniform(130, 150), "change": random.uniform(-3, 5)},
        {"symbol": "XRP", "name": "ریپل", "price": random.uniform(0.50, 0.55), "change": random.uniform(-3, 5)}
    ]
    
    message = f"""
💰 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

"""
    
    for coin in coins:
        symbol = coin["symbol"]
        name = coin["name"]
        price = coin["price"]
        change = coin["change"]
        
        emoji = "🟢" if change >= 0 else "🔴"
        price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
        change_str = f"{change:+.2f}%"
        
        message += f"• {name} ({symbol}): {price_str} ({emoji} {change_str})\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return await send_message(text=message, parse_mode=ParseMode.HTML)

# اجرای توابع غیرهمزمان
def run_async(coro):
    """
    اجرای یک تابع غیرهمزمان به صورت همزمان
    
    Args:
        coro: تابع غیرهمزمان
        
    Returns:
        نتیجه تابع غیرهمزمان
    """
    return asyncio.run(coro)

# تابع‌های همزمان برای فراخوانی از بیرون
def test_message():
    """
    ارسال پیام تست
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    return run_async(send_test_message())

def price_report():
    """
    ارسال گزارش قیمت‌ها
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    return run_async(send_price_report())

def bot_info():
    """
    دریافت اطلاعات بات
    
    Returns:
        dict: اطلاعات بات یا None در صورت خطا
    """
    return run_async(get_bot_info())

# اگر این فایل به صورت مستقیم اجرا شود
if __name__ == "__main__":
    import sys
    
    # دستور پیش‌فرض
    command = "test" if len(sys.argv) < 2 else sys.argv[1].lower()
    
    if command == "test":
        print("ارسال پیام تست...")
        result = run_async(send_test_message())
        print(f"نتیجه: {result}")
    
    elif command == "prices":
        print("ارسال گزارش قیمت‌ها...")
        result = run_async(send_price_report())
        print(f"نتیجه: {result}")
    
    elif command == "info":
        print("دریافت اطلاعات بات...")
        result = run_async(get_bot_info())
        if result:
            print("\n" + "="*50)
            print(f"نام بات: {result.get('first_name')}")
            print(f"نام کاربری: @{result.get('username')}")
            print(f"آیدی بات: {result.get('id')}")
            print("="*50 + "\n")
        else:
            print("خطا در دریافت اطلاعات بات")
    
    else:
        print(f"دستور ناشناخته: {command}")
        print("دستورات قابل قبول: test, prices, info")