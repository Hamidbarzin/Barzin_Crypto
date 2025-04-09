#!/usr/bin/env python3
"""
برنامه مراقبت از سرویس تلگرام

این اسکریپت به صورت دوره‌ای بررسی می‌کند که سرویس تلگرام فعال باشد
و در صورت غیرفعال بودن، آن را دوباره راه‌اندازی می‌کند
"""

import os
import subprocess
import logging
import time
import json
from datetime import datetime
import sys

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_service_watchdog")

# مسیر فایل PID
SERVICE_PID_FILE = "ten_minute_telegram_sender.pid"
WATCHDOG_PID_FILE = "telegram_service_watchdog.pid"
WATCHDOG_LOG_FILE = "telegram_service_watchdog.log"

def is_service_running():
    """
    بررسی اینکه آیا سرویس تلگرام در حال اجراست
    
    Returns:
        bool: وضعیت اجرای سرویس
    """
    if not os.path.exists(SERVICE_PID_FILE):
        logger.info("فایل PID سرویس یافت نشد")
        return False
    
    try:
        with open(SERVICE_PID_FILE, 'r') as f:
            pid_data = json.load(f)
            pid = pid_data.get('pid', 0)
        
        if not pid:
            logger.warning("PID نامعتبر در فایل")
            return False
        
        # بررسی وجود فرآیند با PID داده شده
        try:
            os.kill(pid, 0)  # سیگنال 0 فقط برای بررسی وجود فرآیند است
            return True
        except OSError:
            logger.info(f"فرآیند با PID {pid} یافت نشد")
            return False
            
    except Exception as e:
        logger.error(f"خطا در بررسی وضعیت سرویس: {str(e)}")
        return False

def start_service():
    """
    راه‌اندازی سرویس تلگرام
    
    Returns:
        bool: موفقیت یا شکست راه‌اندازی
    """
    try:
        # اگر فایل PID قدیمی وجود دارد، آن را حذف کن
        if os.path.exists(SERVICE_PID_FILE):
            os.remove(SERVICE_PID_FILE)
        
        # اجرای سرویس با nohup
        subprocess.Popen(
            ["nohup", "python3", "ten_minute_telegram_sender.py", ">", "ten_minute_telegram_sender.log", "2>&1", "&"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        # صبر کوتاه برای اطمینان از راه‌اندازی
        time.sleep(2)
        
        # بررسی وضعیت
        if is_service_running():
            logger.info("سرویس با موفقیت راه‌اندازی شد")
            return True
        else:
            # تلاش مستقیم با python
            subprocess.Popen(
                ["python3", "ten_minute_telegram_sender.py", ">", "ten_minute_telegram_sender.log", "2>&1", "&"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            time.sleep(2)
            
            if is_service_running():
                logger.info("سرویس با روش جایگزین راه‌اندازی شد")
                return True
                
            logger.error("خطا در راه‌اندازی سرویس")
            return False
            
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی سرویس: {str(e)}")
        return False

def save_pid():
    """
    ذخیره شناسه فرآیند و زمان شروع
    """
    pid_data = {
        'pid': os.getpid(),
        'start_time': datetime.now().timestamp()
    }
    
    with open(WATCHDOG_PID_FILE, 'w') as f:
        json.dump(pid_data, f)

def redirect_output_to_file():
    """
    هدایت خروجی استاندارد و خطا به فایل لاگ
    """
    sys.stdout = open(WATCHDOG_LOG_FILE, 'a')
    sys.stderr = open(WATCHDOG_LOG_FILE, 'a')

def main():
    """
    تابع اصلی برنامه
    """
    # ذخیره PID
    save_pid()
    
    # هدایت خروجی به فایل لاگ
    redirect_output_to_file()
    
    logger.info("نظارت بر سرویس تلگرام آغاز شد")
    
    try:
        while True:
            # بررسی وضعیت سرویس
            if not is_service_running():
                logger.warning("سرویس تلگرام غیرفعال است. تلاش برای راه‌اندازی مجدد...")
                start_service()
                
                # ارسال یک پیام گزارش راه‌اندازی مجدد
                try:
                    import super_simple_telegram
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    message = f"""
🔄 <b>Crypto Barzin - راه‌اندازی مجدد</b>
━━━━━━━━━━━━━━━━━━

سرویس گزارش‌دهنده هر ۱۰ دقیقه مجدداً راه‌اندازی شد.

⏰ <b>زمان:</b> {current_time}
"""
                    super_simple_telegram.send_message(message)
                except Exception as e:
                    logger.error(f"خطا در ارسال پیام راه‌اندازی مجدد: {str(e)}")
            else:
                logger.info("سرویس تلگرام فعال است")
            
            # یک ساعت صبر کن
            time.sleep(3600)  # 1 hour = 3600 seconds
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())