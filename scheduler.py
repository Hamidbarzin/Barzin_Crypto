#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
برنامه زمان‌بندی اتوماتیک برای اجرای وظایف دوره‌ای ربات ارز دیجیتال
این اسکریپت باعث می‌شود که ربات به صورت خودکار و بدون نیاز به دخالت کاربر کار کند.

اجرا به صورت مستقل:
python scheduler.py

اجرا به عنوان سرویس در پس‌زمینه:
nohup python scheduler.py > /tmp/crypto_scheduler.log 2>&1 &
"""

import logging
import os
import sys
import time
from datetime import datetime
import schedule
import requests

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scheduler.log')
    ]
)

logger = logging.getLogger('crypto_scheduler')

# آدرس پایه برنامه
BASE_URL = "http://localhost:5000"
REPLIT_DOMAIN = os.environ.get('REPLIT_SLUG', 'localhost')
REPLIT_PROXY = f"https://{REPLIT_DOMAIN}.replit.app"

# لیست API های مهم برای بررسی دوره‌ای
IMPORTANT_APIS = [
    "/api/price/BTC-USDT",
    "/api/market-trend",
    "/api/buy-sell-opportunities",
    "/api/market-volatility",
    "/dashboard"
]

def check_server_status():
    """بررسی وضعیت سرور برنامه"""
    try:
        # سعی می‌کنیم ابتدا به آدرس محلی و سپس به آدرس Replit دسترسی پیدا کنیم
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                logger.info("سرور محلی در دسترس است")
                return True
        except requests.exceptions.RequestException:
            logger.warning("سرور محلی در دسترس نیست، تلاش برای دسترسی به دامنه Replit")
            
        response = requests.get(f"{REPLIT_PROXY}/", timeout=10)
        if response.status_code == 200:
            logger.info("سرور Replit در دسترس است")
            return True
        else:
            logger.error(f"سرور در دسترس نیست. کد وضعیت: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"خطا در بررسی وضعیت سرور: {str(e)}")
        return False

def keep_alive():
    """
    این تابع با درخواست به صفحات مختلف برنامه، باعث می‌شود که سرور همیشه فعال بماند
    """
    if not check_server_status():
        logger.warning("سرور در دسترس نیست، لذا keep_alive انجام نمی‌شود")
        return
    
    for api in IMPORTANT_APIS:
        try:
            if api == "/dashboard":
                response = requests.get(f"{REPLIT_PROXY}{api}", timeout=10)
            else:
                response = requests.get(f"{REPLIT_PROXY}{api}", timeout=10)
                
            if response.status_code == 200:
                logger.info(f"درخواست به {api} با موفقیت انجام شد")
            else:
                logger.warning(f"درخواست به {api} با کد وضعیت {response.status_code} مواجه شد")
        except Exception as e:
            logger.error(f"خطا در ارسال درخواست به {api}: {str(e)}")
    
    logger.info("عملیات keep_alive با موفقیت انجام شد")

def check_buy_sell_opportunities():
    """بررسی فرصت‌های خرید و فروش و ارسال اعلان در صورت نیاز"""
    try:
        response = requests.get(f"{REPLIT_PROXY}/api/buy-sell-opportunities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and len(data.get('data', [])) > 0:
                # در اینجا می‌توان منطق اضافی برای ارسال اعلان‌ها قرار داد
                logger.info(f"تعداد {len(data.get('data'))} فرصت خرید و فروش یافت شد")
            else:
                logger.info("فرصت خرید و فروش جدیدی یافت نشد")
        else:
            logger.warning(f"خطا در دریافت فرصت‌های خرید و فروش: {response.status_code}")
    except Exception as e:
        logger.error(f"خطا در بررسی فرصت‌های خرید و فروش: {str(e)}")

def check_market_volatility():
    """بررسی نوسانات بازار و ارسال اعلان در صورت نیاز"""
    try:
        response = requests.get(f"{REPLIT_PROXY}/api/market-volatility", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and len(data.get('data', [])) > 0:
                logger.info(f"تعداد {len(data.get('data'))} نوسان بازار یافت شد")
            else:
                logger.info("نوسان مهمی در بازار مشاهده نشد")
        else:
            logger.warning(f"خطا در دریافت نوسانات بازار: {response.status_code}")
    except Exception as e:
        logger.error(f"خطا در بررسی نوسانات بازار: {str(e)}")

def check_market_trend():
    """بررسی روند کلی بازار و ارسال اعلان در صورت نیاز"""
    try:
        response = requests.get(f"{REPLIT_PROXY}/api/market-trend", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                trend = data.get('data', {}).get('trend', 'نامشخص')
                logger.info(f"روند فعلی بازار: {trend}")
            else:
                logger.info("اطلاعات روند بازار در دسترس نیست")
        else:
            logger.warning(f"خطا در دریافت روند بازار: {response.status_code}")
    except Exception as e:
        logger.error(f"خطا در بررسی روند بازار: {str(e)}")

def log_status():
    """ثبت وضعیت برنامه در فایل لاگ"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"زمان‌بندی وظایف فعال است - {current_time}")

def setup_schedule():
    """تنظیم زمان‌بندی وظایف دوره‌ای"""
    # هر 5 دقیقه یکبار برنامه را فعال نگه می‌داریم
    schedule.every(5).minutes.do(keep_alive)
    
    # بررسی فرصت‌های خرید و فروش هر ساعت
    schedule.every(1).hours.do(check_buy_sell_opportunities)
    
    # بررسی نوسانات بازار هر 30 دقیقه
    schedule.every(30).minutes.do(check_market_volatility)
    
    # بررسی روند کلی بازار روزانه
    schedule.every().day.at("12:00").do(check_market_trend)
    
    # ثبت وضعیت برنامه در لاگ هر 15 دقیقه
    schedule.every(15).minutes.do(log_status)
    
    logger.info("زمان‌بندی وظایف با موفقیت تنظیم شد")

def run_schedule():
    """اجرای زمان‌بندی تنظیم شده"""
    setup_schedule()
    
    # در اجرای اولیه آزمایش کنیم که آیا سرور در دسترس است
    check_server_status()
    
    # یک بار همه وظایف را اجرا کنیم تا از صحت آنها مطمئن شویم
    keep_alive()
    check_buy_sell_opportunities()
    check_market_volatility()
    check_market_trend()
    log_status()
    
    logger.info("برنامه زمان‌بندی در حال اجرا است...")
    
    # حلقه اصلی برنامه
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("برنامه زمان‌بندی متوقف شد")
            break
        except Exception as e:
            logger.error(f"خطا در اجرای زمان‌بندی: {str(e)}")
            # با وجود خطا، برنامه را متوقف نمی‌کنیم
            time.sleep(10)  # کمی صبر می‌کنیم و دوباره تلاش می‌کنیم

if __name__ == "__main__":
    logger.info("شروع برنامه زمان‌بندی ربات ارز دیجیتال")
    run_schedule()