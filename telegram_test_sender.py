#!/usr/bin/env python3
"""
اسکریپت ساده تست تلگرام که هر یک دقیقه یک پیام تست ارسال می‌کند
"""

import time
import logging
from datetime import datetime
import simple_telegram_sender as telegram
import simple_telegram_formatter as formatter

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_test_sender.log")
    ]
)
logger = logging.getLogger("telegram_test_sender")

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع اسکریپت تست تلگرام")
    
    # ارسال پیام تست اولیه
    logger.info("ارسال پیام تست اولیه")
    test_result = formatter.send_test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # حلقه اصلی برنامه
    count = 1
    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"ارسال پیام شماره {count} در {current_time}")
            
            message = f"""
🔄 <b>Crypto Barzin - تست خودکار</b>
━━━━━━━━━━━━━━━━━━

این پیام شماره {count} است که به صورت خودکار ارسال شده است.
⏰ <b>زمان کنونی:</b> {current_time}

این پیام‌ها هر دقیقه ارسال می‌شوند تا از عملکرد صحیح سیستم اطمینان حاصل شود.
            """
            
            result = telegram.send_message(text=message, parse_mode="HTML")
            logger.info(f"نتیجه ارسال پیام: {result}")
            
            count += 1
            # انتظار برای یک دقیقه
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    
    logger.info("پایان اسکریپت تست تلگرام")

if __name__ == "__main__":
    main()