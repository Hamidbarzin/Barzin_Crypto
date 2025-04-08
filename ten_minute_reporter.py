"""
گزارش‌گر ۱۰ دقیقه‌ای تلگرام

این اسکریپت هر ۱۰ دقیقه یک گزارش از قیمت‌ها و وضعیت بازار را به تلگرام ارسال می‌کند.
این اسکریپت باید به‌صورت مستقل اجرا شود (ترجیحاً به‌عنوان یک سرویس دائمی).

اجرا به‌صورت مستقل:
python ten_minute_reporter.py

اجرا به‌عنوان سرویس در پس‌زمینه:
nohup python ten_minute_reporter.py > ten_minute_reporter.log 2>&1 &
"""

import os
import time
import logging
import threading
import schedule
from datetime import datetime

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ten_minute_reporter.log"),
    ]
)

logger = logging.getLogger("ten_minute_reporter")

# ذخیره PID برای کنترل بهتر فرآیند
with open("ten_minute_reporter.pid", "w") as f:
    f.write(str(os.getpid()))
    logger.info(f"PID: {os.getpid()} ذخیره شد در ten_minute_reporter.pid")

# ثبت زمان شروع
start_time = datetime.now()
logger.info(f"گزارش‌دهی ۱۰ دقیقه‌ای شروع شد در {start_time}")

# وارد کردن ماژول‌های مورد نیاز برای گزارش‌دهی
try:
    from crypto_bot.market_data import get_current_prices
    from crypto_bot.telegram_service import send_telegram_message
    logger.info("ماژول‌های مورد نیاز با موفقیت بارگذاری شدند")
except Exception as e:
    logger.error(f"خطا در بارگذاری ماژول‌ها: {str(e)}")
    raise

# تعریف توابع گزارش‌دهی
def send_price_report():
    """ارسال گزارش قیمت‌ها هر ۱۰ دقیقه"""
    try:
        # لیست ارزهای دیجیتال برای گزارش
        symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", "BNB/USDT"]
        
        # دریافت قیمت‌ها
        prices = get_current_prices(symbols=symbols)
        
        # تهیه متن گزارش
        message = "🔟 گزارش ۱۰ دقیقه‌ای قیمت‌ها\n\n"
        
        for symbol in symbols:
            if symbol in prices:
                data = prices[symbol]
                if isinstance(data, dict) and 'price' in data:
                    price = data['price']
                    change_24h = data.get('change_24h', 0)
                    
                    # نمایش تغییرات با فرمت مناسب
                    change_emoji = "🟢" if change_24h >= 0 else "🔴"
                    change_sign = "+" if change_24h > 0 else ""
                    
                    message += f"{symbol}: {price:,.2f} USDT {change_emoji} {change_sign}{change_24h:.2f}%\n"
        
        # اضافه کردن زمان گزارش
        message += f"\n⏱ زمان گزارش: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # اضافه کردن مدت زمان فعالیت
        uptime = datetime.now() - start_time
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        message += f"\n🕒 مدت فعالیت: {uptime.days} روز، {hours} ساعت، {minutes} دقیقه"
        
        # ارسال به تلگرام
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if chat_id:
            send_telegram_message(chat_id=int(chat_id), message=message)
            logger.info(f"گزارش ۱۰ دقیقه‌ای با موفقیت به چت {chat_id} ارسال شد")
        else:
            logger.error("چت آیدی پیش‌فرض تنظیم نشده است")
    
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش ۱۰ دقیقه‌ای: {str(e)}")

def exit_handler():
    """مدیریت خروج از برنامه"""
    logger.info("درخواست خروج دریافت شد. در حال خروج از برنامه...")
    try:
        if os.path.exists("ten_minute_reporter.pid"):
            os.remove("ten_minute_reporter.pid")
            logger.info("فایل PID با موفقیت حذف شد")
    except Exception as e:
        logger.error(f"خطا در حذف فایل PID: {str(e)}")

# مسیر اصلی برنامه
def main():
    """اجرای اصلی برنامه"""
    try:
        # پاک کردن تمام زمان‌بندی‌های قبلی
        schedule.clear()
        
        # تنظیم زمان‌بندی دقیق ۱۰ دقیقه‌ای
        schedule.every(10).minutes.do(send_price_report)
        
        # ارسال یک گزارش اولیه برای تأیید عملکرد
        logger.info("ارسال گزارش اولیه برای تأیید عملکرد")
        send_price_report()
        
        # حلقه اصلی برنامه
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
        exit_handler()
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {str(e)}")
        exit_handler()
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"خطای بحرانی در اجرای برنامه: {str(e)}")
        exit_handler()