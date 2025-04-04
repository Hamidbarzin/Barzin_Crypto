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
import json
import requests
import schedule

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

# ماژول‌های اطلاع‌رسانی
try:
    from crypto_bot.notification_service import send_buy_sell_notification, send_volatility_alert, send_market_trend_alert
except ImportError:
    logger.warning("ماژول notification_service در دسترس نیست")

try:
    from crypto_bot.email_notifications import send_buy_sell_email, send_volatility_email, send_market_trend_email
except ImportError:
    logger.warning("ماژول email_notifications در دسترس نیست")

# پیکربندی معادل‌های اعلان ایمیلی و پیامکی به صورت دیکشنری
# این تابع بعداً مقداردهی می‌شود (پس از import کردن ماژول‌های مورد نیاز)
notification_methods = {
    'sms': {},
    'email': {}
}

# پس از اینکه همه ماژول‌ها import شدند، پر کردن این دیکشنری
try:
    notification_methods['sms'] = {
        'buy_sell': send_buy_sell_notification,
        'volatility': send_volatility_alert,
        'market_trend': send_market_trend_alert
    }
except NameError:
    logger.warning("توابع اعلان پیامکی در دسترس نیستند")
    notification_methods['sms'] = {
        'buy_sell': None,
        'volatility': None,
        'market_trend': None
    }

try:
    notification_methods['email'] = {
        'buy_sell': send_buy_sell_email,
        'volatility': send_volatility_email,
        'market_trend': send_market_trend_email
    }
except NameError:
    logger.warning("توابع اعلان ایمیلی در دسترس نیستند")
    notification_methods['email'] = {
        'buy_sell': None,
        'volatility': None,
        'market_trend': None
    }

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
                opportunities = data.get('data', [])
                logger.info(f"تعداد {len(opportunities)} فرصت خرید و فروش یافت شد")
                
                # پیکربندی اعلان‌ها با احتمال عدم دسترسی به سرویس
                try:
                    # ارسال اعلان از طریق ایمیل
                    if notification_methods['email']['buy_sell']:
                        for opportunity in opportunities:
                            symbol = opportunity.get('symbol', 'نامشخص')
                            action = opportunity.get('action', 'نامشخص')
                            price = opportunity.get('price', 0)
                            reason = opportunity.get('reason', 'دلایل فنی')
                            
                            # دریافت اطلاعات ایمیل از تنظیمات برنامه
                            response_settings = requests.get(f"{REPLIT_PROXY}/api/notification-settings", timeout=5)
                            if response_settings.status_code == 200:
                                settings = response_settings.json().get('data', {})
                                email = settings.get('email', os.environ.get('DEFAULT_EMAIL'))
                                
                                if email:
                                    # ارسال ایمیل اعلان خرید/فروش
                                    notification_methods['email']['buy_sell'](email, symbol, action, price, reason)
                                    logger.info(f"اعلان فرصت {action} برای {symbol} به {email} ارسال شد")
                                else:
                                    logger.warning("آدرس ایمیل برای ارسال اعلان در دسترس نیست")
                            else:
                                logger.warning(f"خطا در دریافت تنظیمات اعلان: {response_settings.status_code}")
                    else:
                        logger.warning("سرویس ارسال ایمیل در دسترس نیست")
                    
                    # در صورتی که ارسال پیامک نیز فعال باشد
                    if notification_methods['sms']['buy_sell']:
                        # کد مربوط به ارسال پیامک
                        pass
                except Exception as notify_error:
                    logger.error(f"خطا در ارسال اعلان خرید و فروش: {str(notify_error)}")
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
                volatilities = data.get('data', [])
                logger.info(f"تعداد {len(volatilities)} نوسان بازار یافت شد")
                
                # پیکربندی اعلان‌ها
                try:
                    # ارسال اعلان از طریق ایمیل
                    if notification_methods['email']['volatility']:
                        for volatility in volatilities:
                            symbol = volatility.get('symbol', 'نامشخص')
                            price = volatility.get('price', 0)
                            change_percent = volatility.get('change_percent', 0)
                            timeframe = volatility.get('timeframe', '1h')
                            
                            # دریافت اطلاعات ایمیل از تنظیمات برنامه
                            response_settings = requests.get(f"{REPLIT_PROXY}/api/notification-settings", timeout=5)
                            if response_settings.status_code == 200:
                                settings = response_settings.json().get('data', {})
                                email = settings.get('email', os.environ.get('DEFAULT_EMAIL'))
                                
                                if email:
                                    # ارسال ایمیل اعلان نوسان بازار
                                    notification_methods['email']['volatility'](email, symbol, price, change_percent, timeframe)
                                    logger.info(f"اعلان نوسان {change_percent}% برای {symbol} به {email} ارسال شد")
                                else:
                                    logger.warning("آدرس ایمیل برای ارسال اعلان در دسترس نیست")
                            else:
                                logger.warning(f"خطا در دریافت تنظیمات اعلان: {response_settings.status_code}")
                    else:
                        logger.warning("سرویس ارسال ایمیل برای اعلان نوسانات در دسترس نیست")
                    
                    # در صورتی که ارسال پیامک نیز فعال باشد
                    if notification_methods['sms']['volatility']:
                        # کد مربوط به ارسال پیامک
                        pass
                except Exception as notify_error:
                    logger.error(f"خطا در ارسال اعلان نوسان بازار: {str(notify_error)}")
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
                trend_data = data.get('data', {})
                trend = trend_data.get('trend', 'نامشخص')
                affected_coins = trend_data.get('affected_coins', [])
                reason = trend_data.get('reason', 'دلایل تکنیکال و بنیادی')
                logger.info(f"روند فعلی بازار: {trend}")
                
                # ارسال اعلان روند بازار
                try:
                    # ارسال اعلان از طریق ایمیل
                    if notification_methods['email']['market_trend']:
                        # دریافت اطلاعات ایمیل از تنظیمات برنامه
                        response_settings = requests.get(f"{REPLIT_PROXY}/api/notification-settings", timeout=5)
                        if response_settings.status_code == 200:
                            settings = response_settings.json().get('data', {})
                            email = settings.get('email', os.environ.get('DEFAULT_EMAIL'))
                            
                            if email:
                                # ارسال ایمیل اعلان روند بازار
                                notification_methods['email']['market_trend'](email, trend, affected_coins, reason)
                                logger.info(f"اعلان روند {trend} بازار به {email} ارسال شد")
                            else:
                                logger.warning("آدرس ایمیل برای ارسال اعلان در دسترس نیست")
                        else:
                            logger.warning(f"خطا در دریافت تنظیمات اعلان: {response_settings.status_code}")
                    else:
                        logger.warning("سرویس ارسال ایمیل برای اعلان روند بازار در دسترس نیست")
                    
                    # در صورتی که ارسال پیامک نیز فعال باشد
                    if notification_methods['sms']['market_trend']:
                        # کد مربوط به ارسال پیامک
                        pass
                except Exception as notify_error:
                    logger.error(f"خطا در ارسال اعلان روند بازار: {str(notify_error)}")
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

# ارسال اعلان تست برای تایید عملکرد صحیح سیستم
def send_test_confirmation():
    """ارسال یک اعلان تست به کاربر برای تایید عملکرد سیستم"""
    try:
        logger.info("در حال ارسال اعلان تست تایید...")
        
        try:
            from crypto_bot.telegram_service import send_test_notification
            result = send_test_notification()
            if result['success']:
                logger.info("اعلان تست با موفقیت ارسال شد")
                return True
            else:
                logger.error(f"خطا در ارسال اعلان تست: {result['message']}")
                return False
        except Exception as e:
            logger.error(f"خطا در ارسال اعلان تست: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال اعلان تست: {str(e)}")
        return False

def setup_schedule():
    """تنظیم زمان‌بندی وظایف دوره‌ای"""
    # ارسال اعلان تست زمان‌بندی در هنگام شروع برنامه
    send_test_confirmation()
    
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
    
    # اعلان تست روزانه برای اطمینان از عملکرد صحیح سیستم
    schedule.every().day.at("09:00").do(send_test_confirmation)
    
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