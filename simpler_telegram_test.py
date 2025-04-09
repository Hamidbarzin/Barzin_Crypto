#!/usr/bin/env python3
"""
سیستم ارسال پیام تلگرام با استفاده از کتابخانه python-telegram-bot
این اسکریپت بسیار ساده است و فقط یک پیام تست ارسال می‌کند
"""

import os
import logging
from telegram import Bot
import asyncio
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن و چت آیدی
TELEGRAM_BOT_TOKEN = "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk" 
DEFAULT_CHAT_ID = "722627622"  # باید عدد صحیح یا رشته باشد (رشته برای کانال‌ها)

async def send_test_message():
    """
    ارسال یک پیام تست ساده
    """
    try:
        # ایجاد یک نمونه از بات
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🤖 <b>Crypto Barzin - پیام ساده تست</b>
━━━━━━━━━━━━━━━━━━

این یک پیام تست ساده برای بررسی صحت عملکرد تلگرام است.
کد کاملاً بازنویسی شده است.

⏰ <b>زمان:</b> {current_time}
        """
        
        # تبدیل چت آیدی به عدد اگر به صورت رشته باشد و رقمی باشد
        chat_id = DEFAULT_CHAT_ID
        if isinstance(chat_id, str) and chat_id.isdigit():
            chat_id = int(chat_id)
        
        logger.info(f"ارسال پیام به چت آیدی {chat_id}")
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML"
        )
        
        logger.info("پیام با موفقیت ارسال شد")
        return True
        
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

async def main():
    """
    تابع اصلی
    """
    result = await send_test_message()
    print(f"نتیجه ارسال پیام: {result}")

if __name__ == "__main__":
    # اجرای تابع اصلی به صورت غیرهمزمان
    asyncio.run(main())