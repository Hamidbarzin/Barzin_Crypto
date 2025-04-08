#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
مدیریت سرویس‌های تلگرام
این اسکریپت برای مدیریت سرویس‌های مختلف تلگرام استفاده می‌شود
شامل راه‌اندازی، توقف و نمایش وضعیت سرویس‌ها
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime

# پیکربندی لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('service_manager.log')
    ]
)

logger = logging.getLogger(__name__)

# تعریف سرویس‌ها
SERVICES = {
    "ten_minute": {
        "name": "گزارش سه لایه‌ای (۱۰ دقیقه)",
        "start_script": "./start_ten_minute_reporter.sh",
        "stop_script": "./stop_ten_minute_reporter.sh",
        "test_command": "python enhanced_telegram_reporter.py --test",
        "pid_file": ".ten_minute_reporter_pid",
        "log_file": "ten_minute_scheduler.log"
    },
    "smart_ai": {
        "name": "گزارش هوشمند",
        "start_script": "./start_smart_robot.sh",
        "stop_script": "./stop_smart_robot.sh",
        "test_command": "python telegram_smart_reporter.py --test",
        "pid_file": ".smart_bot_pid",
        "log_file": "smart_ai_scheduler.log"
    },
    "simple": {
        "name": "گزارش ساده",
        "start_script": "./simple_scheduler.sh",
        "stop_script": "./stop_scheduler.sh",
        "test_command": "python telegram_reporter.py test",
        "pid_file": "scheduler.pid",
        "log_file": "scheduler.log"
    }
}

def get_service_status(service_type):
    """
    بررسی وضعیت سرویس
    
    Args:
        service_type (str): نوع سرویس
        
    Returns:
        dict: وضعیت سرویس
    """
    if service_type not in SERVICES:
        return {"status": "error", "message": "سرویس نامعتبر"}
    
    service = SERVICES[service_type]
    
    # بررسی فایل PID
    pid_file = service["pid_file"]
    pid = None
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
        except (ValueError, IOError) as e:
            logger.error(f"خطا در خواندن فایل PID: {e}")
    
    # بررسی فرآیند
    is_running = False
    if pid:
        try:
            # در لینوکس: بررسی وجود فرآیند
            if sys.platform.startswith('linux'):
                cmd = f"ps -p {pid} -o pid="
                result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                is_running = result.returncode == 0
        except Exception as e:
            logger.error(f"خطا در بررسی وضعیت فرآیند: {e}")
    
    # بررسی لاگ فایل
    last_run = "-"
    if os.path.exists(service["log_file"]):
        try:
            last_modified = os.path.getmtime(service["log_file"])
            last_run = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"خطا در بررسی زمان آخرین اجرا: {e}")
    
    return {
        "name": service["name"],
        "status": "running" if is_running else "stopped",
        "pid": pid,
        "last_run": last_run
    }

def start_service(service_type):
    """
    راه‌اندازی سرویس
    
    Args:
        service_type (str): نوع سرویس
        
    Returns:
        dict: نتیجه عملیات
    """
    if service_type not in SERVICES:
        return {"status": "error", "message": "سرویس نامعتبر"}
    
    service = SERVICES[service_type]
    
    # بررسی وضعیت فعلی
    status = get_service_status(service_type)
    if status["status"] == "running":
        return {"status": "warning", "message": f"سرویس {service['name']} در حال اجرا است"}
    
    # اجرای اسکریپت راه‌اندازی
    try:
        subprocess.run(service["start_script"], shell=True, check=True)
        time.sleep(2)  # کمی صبر کنیم تا سرویس راه‌اندازی شود
        new_status = get_service_status(service_type)
        
        if new_status["status"] == "running":
            return {"status": "success", "message": f"سرویس {service['name']} با موفقیت راه‌اندازی شد"}
        else:
            return {"status": "error", "message": f"خطا در راه‌اندازی سرویس {service['name']}"}
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در اجرای اسکریپت راه‌اندازی: {e}")
        return {"status": "error", "message": f"خطا در اجرای اسکریپت راه‌اندازی: {e}"}

def stop_service(service_type):
    """
    توقف سرویس
    
    Args:
        service_type (str): نوع سرویس
        
    Returns:
        dict: نتیجه عملیات
    """
    if service_type not in SERVICES:
        return {"status": "error", "message": "سرویس نامعتبر"}
    
    service = SERVICES[service_type]
    
    # بررسی وضعیت فعلی
    status = get_service_status(service_type)
    if status["status"] != "running":
        return {"status": "warning", "message": f"سرویس {service['name']} در حال اجرا نیست"}
    
    # اجرای اسکریپت توقف
    try:
        subprocess.run(service["stop_script"], shell=True, check=True)
        time.sleep(2)  # کمی صبر کنیم تا سرویس متوقف شود
        new_status = get_service_status(service_type)
        
        if new_status["status"] != "running":
            return {"status": "success", "message": f"سرویس {service['name']} با موفقیت متوقف شد"}
        else:
            return {"status": "error", "message": f"خطا در توقف سرویس {service['name']}"}
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در اجرای اسکریپت توقف: {e}")
        return {"status": "error", "message": f"خطا در اجرای اسکریپت توقف: {e}"}

def test_service(service_type):
    """
    تست سرویس
    
    Args:
        service_type (str): نوع سرویس
        
    Returns:
        dict: نتیجه عملیات
    """
    if service_type not in SERVICES:
        return {"status": "error", "message": "سرویس نامعتبر"}
    
    service = SERVICES[service_type]
    
    # اجرای دستور تست
    try:
        result = subprocess.run(service["test_command"], shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {
            "status": "success", 
            "message": f"دستور تست سرویس {service['name']} با موفقیت اجرا شد",
            "output": result.stdout.decode('utf-8', errors='replace')
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در اجرای دستور تست: {e}")
        return {
            "status": "error", 
            "message": f"خطا در اجرای دستور تست: {e}",
            "output": e.stderr.decode('utf-8', errors='replace')
        }

def get_all_statuses():
    """
    دریافت وضعیت تمام سرویس‌ها
    
    Returns:
        dict: وضعیت تمام سرویس‌ها
    """
    result = {}
    for service_type in SERVICES:
        result[service_type] = get_service_status(service_type)
    return result

def main():
    """
    تابع اصلی برنامه
    """
    if len(sys.argv) < 2:
        print("استفاده: python service_manager.py [status|start|stop|test] [service_type]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status" and len(sys.argv) == 2:
        # نمایش وضعیت تمام سرویس‌ها
        statuses = get_all_statuses()
        print(json.dumps(statuses, indent=2, ensure_ascii=False))
        return
    
    if len(sys.argv) < 3:
        print("خطا: لطفاً نوع سرویس را مشخص کنید")
        return
    
    service_type = sys.argv[2].lower()
    
    if service_type not in SERVICES:
        print(f"خطا: سرویس نامعتبر: {service_type}")
        print(f"سرویس‌های معتبر: {', '.join(SERVICES.keys())}")
        return
    
    if command == "status":
        status = get_service_status(service_type)
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif command == "start":
        result = start_service(service_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif command == "stop":
        result = stop_service(service_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif command == "test":
        result = test_service(service_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"خطا: دستور نامعتبر: {command}")
        print("دستورات معتبر: status, start, stop, test")

if __name__ == "__main__":
    main()