#!/usr/bin/env python3
"""
اسکریپت ساده برای تست ارسال پیام به تلگرام بدون نیاز به رابط کاربری وب

استفاده:
python test_telegram.py                # استفاده از چت آیدی پیش‌فرض
python test_telegram.py 123456789      # ارسال به چت آیدی مشخص
python test_telegram.py --info         # نمایش اطلاعات بات بدون ارسال پیام
python test_telegram.py --check 123456 # بررسی آیا یک چت آیدی معتبر است
python test_telegram.py --help         # نمایش راهنما
"""

import os
import sys
import logging
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("telegram_test")

try:
    # تلاش برای وارد کردن کتابخانه تلگرام
    import telegram
    from telegram.constants import ParseMode
    import asyncio
except ImportError:
    logger.error("کتابخانه python-telegram-bot نصب نشده است. لطفاً با دستور زیر آن را نصب کنید:")
    logger.error("pip install python-telegram-bot")
    sys.exit(1)

# دریافت توکن از متغیرهای محیطی
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("توکن بات تلگرام یافت نشد!")
    logger.error("لطفاً متغیر محیطی TELEGRAM_BOT_TOKEN را تنظیم کنید")
    sys.exit(1)

# گرفتن چت آیدی به عنوان پارامتر خط فرمان (اختیاری)
DEFAULT_CHAT_ID = 722627622  # چت آیدی پیش‌فرض
chat_id = DEFAULT_CHAT_ID
command = "send"  # دستور پیش‌فرض

def print_help():
    """نمایش راهنمای استفاده از برنامه"""
    print("""
استفاده از اسکریپت تست تلگرام:
-------------------------------
python test_telegram.py                # ارسال پیام تست به چت آیدی پیش‌فرض
python test_telegram.py 123456789      # ارسال پیام تست به چت آیدی مشخص
python test_telegram.py --info         # نمایش اطلاعات بات بدون ارسال پیام
python test_telegram.py --check 123456 # بررسی آیا یک چت آیدی معتبر است
python test_telegram.py --help         # نمایش این راهنما

چت آیدی پیش‌فرض: {DEFAULT_CHAT_ID}
    """)
    sys.exit(0)

# بررسی پارامترهای خط فرمان
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    
    # بررسی اگر کمک درخواست شده
    if arg in ["--help", "-h", "help", "کمک"]:
        print_help()
    
    # بررسی اگر اطلاعات بات درخواست شده
    elif arg in ["--info", "-i", "info", "اطلاعات"]:
        command = "info"
    
    # بررسی اگر تست چت آیدی درخواست شده
    elif arg in ["--check", "-c", "check", "بررسی"]:
        command = "check"
        if len(sys.argv) > 2:
            try:
                chat_id = int(sys.argv[2])
                logger.info(f"بررسی چت آیدی: {chat_id}")
            except ValueError:
                logger.error(f"چت آیدی '{sys.argv[2]}' معتبر نیست.")
                sys.exit(1)
        else:
            logger.error("چت آیدی برای بررسی مشخص نشده است.")
            sys.exit(1)
    
    # در غیر این صورت، فرض می‌کنیم پارامتر چت آیدی است
    else:
        try:
            chat_id = int(arg)
            logger.info(f"استفاده از چت آیدی دریافتی: {chat_id}")
        except ValueError:
            logger.warning(f"چت آیدی '{arg}' معتبر نیست. استفاده از مقدار پیش‌فرض: {DEFAULT_CHAT_ID}")

# تابع برای دریافت زمان فعلی به فرمت مناسب
def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# تابع اصلی آسنکرون
async def send_test_message():
    try:
        # ایجاد آبجکت بات
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        
        # بررسی اطلاعات بات
        me = await bot.get_me()
        logger.info(f"اطلاعات بات: {me.first_name} (@{me.username}) - آیدی: {me.id}")
        
        # ساخت پیام تست
        message = f"🤖 <b>پیام تست از اسکریپت کنسول</b>\n\n"
        message += "سیستم اعلان‌های تلگرام فعال است.\n\n"
        message += f"⏰ <b>زمان:</b> {get_current_time()}"
        
        # ارسال پیام
        logger.info(f"ارسال پیام به چت آیدی: {chat_id}")
        result = await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"پیام با موفقیت ارسال شد. شناسه پیام: {result.message_id}")
        return True
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

async def get_bot_info():
    """دریافت و نمایش اطلاعات بات تلگرام"""
    try:
        # ایجاد آبجکت بات
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        
        # دریافت اطلاعات بات
        me = await bot.get_me()
        
        print("\n" + "="*50)
        print(f"نام بات: {me.first_name}")
        print(f"نام کاربری: @{me.username}")
        print(f"آیدی بات: {me.id}")
        print(f"لینک بات: https://t.me/{me.username}")
        print("="*50 + "\n")
        
        return True
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات بات: {str(e)}")
        return False

async def check_chat_id(target_chat_id):
    """بررسی اعتبار چت آیدی"""
    try:
        # ایجاد آبجکت بات
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        
        try:
            # تلاش برای دریافت اطلاعات چت
            chat = await bot.get_chat(chat_id=target_chat_id)
            
            print("\n" + "="*50)
            print(f"✅ چت آیدی {target_chat_id} معتبر است!")
            print(f"نوع چت: {chat.type}")
            if chat.title:
                print(f"عنوان: {chat.title}")
            if chat.first_name:
                name = f"{chat.first_name}"
                if chat.last_name:
                    name += f" {chat.last_name}"
                print(f"نام: {name}")
            if chat.username:
                print(f"نام کاربری: @{chat.username}")
            print("="*50 + "\n")
            
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "chat not found" in error_msg:
                print("\n" + "="*50)
                print(f"❌ چت آیدی {target_chat_id} نامعتبر است یا بات دسترسی به آن ندارد.")
                print("دلایل احتمالی:")
                print("1. چت آیدی اشتباه است")
                print("2. کاربر هنوز گفتگو با بات را شروع نکرده است (/start)")
                print("3. کاربر بات را بلاک کرده است")
                print("="*50 + "\n")
            else:
                print("\n" + "="*50)
                print(f"❌ خطا در بررسی چت آیدی {target_chat_id}:")
                print(f"خطا: {str(e)}")
                print("="*50 + "\n")
            return False
    except Exception as e:
        logger.error(f"خطا در اتصال به تلگرام: {str(e)}")
        return False

# اجرای برنامه
if __name__ == "__main__":
    logger.info("شروع اسکریپت تلگرام...")
    
    if command == "send":
        logger.info("ارسال پیام تست...")
        asyncio.run(send_test_message())
    elif command == "info":
        logger.info("دریافت اطلاعات بات...")
        asyncio.run(get_bot_info())
    elif command == "check":
        logger.info(f"بررسی چت آیدی {chat_id}...")
        asyncio.run(check_chat_id(chat_id))
    else:
        logger.error(f"دستور ناشناخته: {command}")
        print_help()