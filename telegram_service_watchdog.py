#!/usr/bin/env python3
"""
ناظر سرویس‌های تلگرام

این اسکریپت وضعیت سرویس‌های تلگرام را بررسی می‌کند و
در صورت نیاز آن‌ها را مجدداً راه‌اندازی می‌کند.
"""

import os
import time
import logging
import signal
import subprocess
import sys
import json
import requests
from datetime import datetime, timedelta
import pytz  # برای کار با منطقه‌های زمانی مختلف

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("watchdog.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("telegram_watchdog")

# تنظیمات PID
PID_FILE = "watchdog.pid"

# تنظیمات سرویس
SERVICES = [
    {
        "name": "ten_minute_sender",
        "pid_file": "ten_minute_telegram_sender.pid",
        "log_file": "ten_minute_telegram_sender.log",
        "start_script": "./اجرای_گزارش_دهنده_هر_۱۰_دقیقه.sh",
        "process_name": "ten_minute_telegram_sender.py"
    }
]

# تنظیمات API
BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")
TEST_MESSAGE_URL = f"{BASE_URL}/send_test_message_replit"

def is_process_running(pid):
    """
    بررسی می‌کند که آیا فرآیند با PID مشخص در حال اجراست یا خیر
    
    Args:
        pid (int): شناسه فرآیند
        
    Returns:
        bool: وضعیت اجرای فرآیند
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def find_process_by_name(name):
    """
    جستجوی فرآیند بر اساس نام
    
    Args:
        name (str): نام فرآیند
        
    Returns:
        list: لیست PIDs فرآیندهای مطابق با نام
    """
    try:
        output = subprocess.check_output(["pgrep", "-f", name]).decode().strip()
        return [int(pid) for pid in output.split("\n") if pid]
    except subprocess.CalledProcessError:
        return []

def start_service(service):
    """
    شروع یک سرویس
    
    Args:
        service (dict): اطلاعات سرویس
        
    Returns:
        bool: موفقیت یا شکست راه‌اندازی سرویس
    """
    try:
        logger.info(f"تلاش برای راه‌اندازی سرویس {service['name']}...")
        subprocess.call(service['start_script'], shell=True)
        logger.info(f"دستور راه‌اندازی سرویس {service['name']} اجرا شد")
        return True
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی سرویس {service['name']}: {str(e)}")
        return False

def check_service(service):
    """
    بررسی وضعیت یک سرویس و راه‌اندازی مجدد آن در صورت نیاز
    
    Args:
        service (dict): اطلاعات سرویس
        
    Returns:
        bool: وضعیت سرویس (True: در حال اجرا، False: متوقف شده)
    """
    logger.info(f"بررسی وضعیت سرویس {service['name']}...")
    
    # بررسی فایل PID
    if os.path.exists(service['pid_file']):
        try:
            with open(service['pid_file'], 'r') as f:
                pid = int(f.read().strip())
                
            if is_process_running(pid):
                logger.info(f"سرویس {service['name']} در حال اجراست (PID: {pid})")
                return True
            else:
                logger.warning(f"سرویس {service['name']} با PID {pid} در حال اجرا نیست")
        except Exception as e:
            logger.error(f"خطا در خواندن فایل PID برای سرویس {service['name']}: {str(e)}")
    else:
        logger.warning(f"فایل PID برای سرویس {service['name']} یافت نشد")
    
    # تلاش برای یافتن فرآیند بر اساس نام
    pids = find_process_by_name(service['process_name'])
    if pids:
        logger.info(f"سرویس {service['name']} در حال اجراست با PIDs: {pids}")
        return True
    
    # سرویس در حال اجرا نیست، راه‌اندازی مجدد
    logger.warning(f"سرویس {service['name']} در حال اجرا نیست. تلاش برای راه‌اندازی مجدد...")
    return start_service(service)

def test_telegram_api():
    """
    تست API تلگرام با ارسال یک پیام تست
    
    Returns:
        bool: موفقیت یا شکست تست
    """
    try:
        logger.info("تست API تلگرام...")
        response = requests.get(TEST_MESSAGE_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                logger.info("API تلگرام به درستی کار می‌کند")
                return True
            else:
                logger.error(f"خطا در API تلگرام: {data.get('message', 'خطای ناشناخته')}")
                return False
        else:
            logger.error(f"خطا در فراخوانی API تلگرام. کد وضعیت: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"خطا در تست API تلگرام: {str(e)}")
        return False

def save_pid():
    """
    ذخیره شناسه فرآیند برای کنترل اجرا
    """
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))
    logger.info(f"PID {pid} در فایل {PID_FILE} ذخیره شد")

def cleanup_pid():
    """
    پاکسازی فایل PID هنگام خروج
    """
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logger.info(f"فایل PID {PID_FILE} پاک شد")

def signal_handler(sig, frame):
    """
    مدیریت سیگنال‌های سیستم عامل
    """
    logger.info(f"سیگنال {sig} دریافت شد. در حال خروج...")
    cleanup_pid()
    sys.exit(0)

def main():
    """
    تابع اصلی برنامه
    """
    # ثبت هندلر سیگنال‌ها
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ذخیره PID
    save_pid()
    
    logger.info("ناظر سرویس‌های تلگرام شروع شد")
    
    try:
        while True:
            try:
                # بررسی API تلگرام
                api_status = test_telegram_api()
                
                # بررسی تمام سرویس‌ها
                for service in SERVICES:
                    service_status = check_service(service)
                    logger.info(f"وضعیت سرویس {service['name']}: {service_status}")
                
                # مدت زمان خواب
                sleep_time = 300  # هر 5 دقیقه
                # استفاده از زمان تورنتو
                toronto_timezone = pytz.timezone('America/Toronto')
                toronto_time = datetime.now(toronto_timezone)
                logger.info(f"وضعیت ناظر: API={api_status}, زمان فعلی تورنتو: {toronto_time.strftime('%H:%M:%S')}, انتظار {sleep_time} ثانیه تا بررسی بعدی...")
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"خطا در چرخه اصلی ناظر: {str(e)}")
                time.sleep(60)  # در صورت خطا، 1 دقیقه صبر کن و دوباره تلاش کن
    
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    finally:
        cleanup_pid()
    
    return 0

if __name__ == "__main__":
    main()