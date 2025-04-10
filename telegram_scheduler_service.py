#!/usr/bin/env python3
"""
سرویس زمان‌بندی تلگرام داخلی

این ماژول یک سرویس زمان‌بندی برای ارسال خودکار پیام‌های تلگرام
با استفاده از ماژول replit_telegram_sender فراهم می‌کند.
"""

import threading
import time
import logging
import datetime
import pytz
import replit_telegram_sender
import os
import json
from crypto_bot.price_alert_service import check_price_alerts

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_scheduler")

# منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')

# مسیر ذخیره فایل تنظیمات
SETTINGS_FILE = "telegram_scheduler_settings.json"

class TelegramSchedulerService:
    """
    کلاس سرویس زمان‌بندی تلگرام
    
    این کلاس یک ترد جداگانه برای زمان‌بندی پیام‌های تلگرام ایجاد می‌کند
    که به صورت خودکار پیام‌های تلگرام را ارسال می‌کند.
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس
        """
        self.thread = None
        self.running = False
        self.system_report_counter = 0
        self.technical_analysis_counter = 0
        self.trading_signals_counter = 0
        self.crypto_news_counter = 0
        self.interval = 1800  # 30 دقیقه = 1800 ثانیه
        self.system_report_interval = 12  # هر 12 بار (6 ساعت)
        self.technical_analysis_interval = 4  # هر 4 بار (2 ساعت)
        self.trading_signals_interval = 8  # هر 8 بار (4 ساعت)
        self.crypto_news_interval = 16  # هر 16 بار (8 ساعت)
        
        # تنظیمات قابل تغییر توسط کاربر
        self.active_hours_start = 8  # ساعت شروع (8 صبح)
        self.active_hours_end = 22   # ساعت پایان (10 شب)
        self.message_sending_enabled = True  # آیا ارسال پیام فعال است؟
        self.auto_start_on_boot = True  # آیا سرویس به صورت خودکار در راه‌اندازی برنامه شروع شود؟
        
        # ارزهای مهم برای تحلیل تکنیکال
        self.important_coins = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
        self.current_coin_index = 0
    
    def start(self):
        """
        شروع سرویس زمان‌بندی
        
        Returns:
            bool: وضعیت راه‌اندازی سرویس
        """
        if self.running:
            logger.warning("سرویس از قبل در حال اجراست")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"سرویس زمان‌بندی تلگرام شروع شد ({now_toronto.strftime('%Y-%m-%d %H:%M:%S')} تورنتو)")
        
        # ارسال پیام تست در ابتدا
        self._send_test_message()
        
        return True
    
    def stop(self):
        """
        توقف سرویس زمان‌بندی
        
        Returns:
            bool: وضعیت توقف سرویس
        """
        if not self.running:
            logger.warning("سرویس در حال اجرا نیست")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(1.0)  # انتظار حداکثر 1 ثانیه برای پایان ترد
            
        logger.info("سرویس زمان‌بندی تلگرام متوقف شد")
        return True
    
    def status(self):
        """
        دریافت وضعیت سرویس
        
        Returns:
            dict: وضعیت سرویس
        """
        return {
            "running": self.running,
            "message_sending_enabled": self.message_sending_enabled,
            "active_hours_start": self.active_hours_start,
            "active_hours_end": self.active_hours_end,
            "interval": self.interval,
            "system_report_counter": self.system_report_counter,
            "technical_analysis_counter": self.technical_analysis_counter,
            "trading_signals_counter": self.trading_signals_counter,
            "crypto_news_counter": self.crypto_news_counter,
            "next_price_report": self._get_next_report_time(),
            "next_system_report": self._get_next_system_report_time(),
            "next_technical_analysis": self._get_next_technical_analysis_time(),
            "next_trading_signals": self._get_next_trading_signals_time(),
            "next_crypto_news": self._get_next_crypto_news_time(),
            "next_coin_for_analysis": self.important_coins[self.current_coin_index]
        }
    
    def _scheduler_loop(self):
        """
        حلقه اصلی زمان‌بندی
        
        این متد در یک ترد جداگانه اجرا می‌شود و مسئول ارسال
        پیام‌های زمان‌بندی شده است.
        
        برای محیط replit، از بازه‌های زمانی کوچکتر استفاده می‌کنیم تا
        در صورت قطع شدن ترد، زودتر به مشکل پی ببریم
        """
        try:
            # ارسال گزارش قیمت اولیه
            logger.info("ارسال گزارش قیمت اولیه...")
            self._send_price_report()
            
            # شمارنده برای ارسال پیام هر نیم ساعت
            counter = 0
            # بازه زمانی کوچکتر برای بررسی وضعیت
            small_interval = 60  # 1 دقیقه
            ticks_for_report = 30  # 30 دقیقه / 1 دقیقه = 30 تیک
            
            while self.running:
                # خواب با بازه کوچکتر برای کنترل بهتر
                time.sleep(small_interval)
                
                if not self.running:
                    break
                
                # بررسی زمان فعلی در تورنتو
                now_toronto = datetime.datetime.now(toronto_tz)
                current_hour = now_toronto.hour
                
                # فقط بین ساعت‌های تعیین شده ارسال کن
                is_active_hours = self.active_hours_start <= current_hour < self.active_hours_end
                
                # اگر ارسال پیام غیرفعال شده، فعال نیست
                is_active_hours = is_active_hours and self.message_sending_enabled
                
                counter += 1
                logger.info(f"تیک شماره {counter} از {ticks_for_report} برای ارسال گزارش بعدی")
                
                # هر نیم ساعت گزارش قیمت ارسال کن (اگر در ساعات فعال هستیم)
                if counter >= ticks_for_report and is_active_hours:
                    logger.info("زمان ارسال گزارش قیمت فرا رسیده...")
                    self._send_price_report()
                    counter = 0
                # اگر به تعداد تیک لازم رسیدیم ولی در ساعات غیرفعال هستیم، فقط شمارنده را ریست کن
                elif counter >= ticks_for_report and not is_active_hours:
                    if not self.message_sending_enabled:
                        logger.info("ارسال پیام غیرفعال شده، گزارش ارسال نمی‌شود")
                    else:
                        logger.info(f"خارج از ساعات فعال ({self.active_hours_start} صبح تا {self.active_hours_end} شب) هستیم، گزارش ارسال نمی‌شود")
                    counter = 0
                
                # بررسی هشدارهای قیمت در هر تیک
                try:
                    self._check_price_alerts()
                except Exception as e:
                    logger.error(f"خطا در بررسی هشدارهای قیمت: {str(e)}")
                
                # افزایش شمارنده‌ها
                self.system_report_counter += 1
                self.technical_analysis_counter += 1
                self.trading_signals_counter += 1
                self.crypto_news_counter += 1
                
                # ارسال گزارش سیستم هر ۶ ساعت
                if self.system_report_counter >= self.system_report_interval:
                    self._send_system_report()
                    self.system_report_counter = 0
                
                # ارسال تحلیل تکنیکال هر ۲ ساعت
                if self.technical_analysis_counter >= self.technical_analysis_interval:
                    self._send_technical_analysis()
                    self.technical_analysis_counter = 0
                
                # ارسال سیگنال‌های معاملاتی هر ۴ ساعت
                if self.trading_signals_counter >= self.trading_signals_interval:
                    self._send_trading_signals()
                    self.trading_signals_counter = 0
                    
                # ارسال اخبار ارزهای دیجیتال هر ۸ ساعت
                if self.crypto_news_counter >= self.crypto_news_interval:
                    self._send_crypto_news()
                    self.crypto_news_counter = 0
        
        except Exception as e:
            logger.error(f"خطا در حلقه زمان‌بندی: {str(e)}")
            self.running = False
    
    def _send_price_report(self):
        """
        ارسال گزارش قیمت
        
        Returns:
            bool: موفقیت یا شکست ارسال پیام
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"ارسال گزارش قیمت ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            success = replit_telegram_sender.send_price_report()
            if success:
                logger.info("گزارش قیمت با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال گزارش قیمت")
            return success
        except Exception as e:
            logger.error(f"استثنا در ارسال گزارش قیمت: {str(e)}")
            return False
    
    def _send_system_report(self):
        """
        ارسال گزارش سیستم
        
        Returns:
            bool: موفقیت یا شکست ارسال پیام
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"ارسال گزارش سیستم ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            success = replit_telegram_sender.send_system_report()
            if success:
                logger.info("گزارش سیستم با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال گزارش سیستم")
            return success
        except Exception as e:
            logger.error(f"استثنا در ارسال گزارش سیستم: {str(e)}")
            return False
    
    def _send_test_message(self):
        """
        ارسال پیام تست
        
        Returns:
            bool: موفقیت یا شکست ارسال پیام
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"ارسال پیام تست ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            success = replit_telegram_sender.send_test_message()
            if success:
                logger.info("پیام تست با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال پیام تست")
            return success
        except Exception as e:
            logger.error(f"استثنا در ارسال پیام تست: {str(e)}")
            return False
    
    def _get_next_report_time(self):
        """
        محاسبه زمان گزارش بعدی
        
        Returns:
            str: زمان گزارش بعدی
        """
        if not self.running:
            return "سرویس در حال اجرا نیست"
        
        now = datetime.datetime.now(toronto_tz)
        next_time = now + datetime.timedelta(seconds=self.interval)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_next_system_report_time(self):
        """
        محاسبه زمان گزارش سیستم بعدی
        
        Returns:
            str: زمان گزارش سیستم بعدی
        """
        if not self.running:
            return "سرویس در حال اجرا نیست"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.system_report_interval - self.system_report_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_next_technical_analysis_time(self):
        """
        محاسبه زمان تحلیل تکنیکال بعدی
        
        Returns:
            str: زمان تحلیل تکنیکال بعدی
        """
        if not self.running:
            return "سرویس در حال اجرا نیست"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.technical_analysis_interval - self.technical_analysis_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_next_trading_signals_time(self):
        """
        محاسبه زمان سیگنال‌های معاملاتی بعدی
        
        Returns:
            str: زمان سیگنال‌های معاملاتی بعدی
        """
        if not self.running:
            return "سرویس در حال اجرا نیست"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.trading_signals_interval - self.trading_signals_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
        
    def _send_technical_analysis(self):
        """
        ارسال تحلیل تکنیکال یک ارز
        
        Returns:
            bool: موفقیت یا شکست ارسال تحلیل
        """
        # انتخاب ارز مورد نظر برای تحلیل
        symbol = self.important_coins[self.current_coin_index]
        
        # بروزرسانی شاخص برای دفعه بعد
        self.current_coin_index = (self.current_coin_index + 1) % len(self.important_coins)
        
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"ارسال تحلیل تکنیکال برای {symbol} ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            success = replit_telegram_sender.send_technical_analysis(symbol)
            if success:
                logger.info(f"تحلیل تکنیکال {symbol} با موفقیت ارسال شد")
            else:
                logger.error(f"خطا در ارسال تحلیل تکنیکال {symbol}")
            return success
        except Exception as e:
            logger.error(f"استثنا در ارسال تحلیل تکنیکال {symbol}: {str(e)}")
            return False
    
    def _send_trading_signals(self):
        """
        ارسال سیگنال‌های معاملاتی
        
        Returns:
            bool: موفقیت یا شکست ارسال سیگنال‌ها
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"ارسال سیگنال‌های معاملاتی ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            success = replit_telegram_sender.send_trading_signals()
            if success:
                logger.info("سیگنال‌های معاملاتی با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال سیگنال‌های معاملاتی")
            return success
        except Exception as e:
            logger.error(f"استثنا در ارسال سیگنال‌های معاملاتی: {str(e)}")
            return False
            
    def _check_price_alerts(self):
        """
        بررسی هشدارهای قیمت
        
        Returns:
            list: لیست هشدارهای فعال شده
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"بررسی هشدارهای قیمت ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            triggered_alerts = check_price_alerts()
            if triggered_alerts:
                logger.info(f"{len(triggered_alerts)} هشدار قیمت فعال شد")
            return triggered_alerts
        except Exception as e:
            logger.error(f"استثنا در بررسی هشدارهای قیمت: {str(e)}")
            return []
            
    def _send_crypto_news(self):
        """
        ارسال اخبار ارزهای دیجیتال
        
        Returns:
            bool: موفقیت یا شکست ارسال اخبار
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"ارسال اخبار ارزهای دیجیتال ({now_toronto.strftime('%H:%M:%S')} تورنتو)...")
        
        try:
            # استفاده از api_telegram_send_news در main.py
            # این متد از ماژول get_crypto_news_formatted_for_telegram استفاده می‌کند
            success = replit_telegram_sender.send_crypto_news()
            if success:
                logger.info("اخبار ارزهای دیجیتال با موفقیت ارسال شد")
            else:
                logger.error("خطا در ارسال اخبار ارزهای دیجیتال")
            return success
        except Exception as e:
            logger.error(f"استثنا در ارسال اخبار ارزهای دیجیتال: {str(e)}")
            return False
            
    def _get_next_crypto_news_time(self):
        """
        محاسبه زمان اخبار ارزهای دیجیتال بعدی
        
        Returns:
            str: زمان اخبار ارزهای دیجیتال بعدی
        """
        if not self.running:
            return "سرویس در حال اجرا نیست"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.crypto_news_interval - self.crypto_news_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")

# نمونه سرویس که در main.py استفاده خواهد شد
telegram_scheduler = TelegramSchedulerService()


def start_scheduler():
    """
    شروع زمان‌بندی تلگرام
    
    Returns:
        bool: وضعیت راه‌اندازی
    """
    return telegram_scheduler.start()


def stop_scheduler():
    """
    توقف زمان‌بندی تلگرام
    
    Returns:
        bool: وضعیت توقف
    """
    return telegram_scheduler.stop()


def get_scheduler_status():
    """
    دریافت وضعیت زمان‌بندی
    
    Returns:
        dict: وضعیت فعلی زمان‌بندی
    """
    return telegram_scheduler.status()


def update_scheduler_settings(settings):
    """
    بروزرسانی تنظیمات زمان‌بندی
    
    Args:
        settings (dict): تنظیمات جدید
        
    Returns:
        dict: وضعیت بروزرسانی شده
    """
    if 'message_sending_enabled' in settings:
        telegram_scheduler.message_sending_enabled = bool(settings['message_sending_enabled'])
        
    if 'active_hours_start' in settings:
        try:
            # اطمینان از اینکه مقدار بین 0 تا 23 است
            active_hours_start = int(settings['active_hours_start'])
            if 0 <= active_hours_start <= 23:
                telegram_scheduler.active_hours_start = active_hours_start
        except (ValueError, TypeError):
            pass
            
    if 'active_hours_end' in settings:
        try:
            # اطمینان از اینکه مقدار بین 0 تا 24 است
            active_hours_end = int(settings['active_hours_end'])
            if 1 <= active_hours_end <= 24:
                telegram_scheduler.active_hours_end = active_hours_end
        except (ValueError, TypeError):
            pass
            
    if 'interval' in settings:
        try:
            # اطمینان از اینکه مقدار حداقل 60 ثانیه است
            interval = int(settings['interval'])
            if interval >= 60:
                telegram_scheduler.interval = interval
        except (ValueError, TypeError):
            pass
    
    # بازگرداندن وضعیت فعلی
    return telegram_scheduler.status()


# اگر این فایل به تنهایی اجرا شود، زمان‌بندی را شروع و به مدت ۱ دقیقه اجرا می‌کند
if __name__ == "__main__":
    print("شروع تست سرویس زمان‌بندی تلگرام...")
    
    if start_scheduler():
        print("سرویس با موفقیت شروع شد")
        print("در حال اجرا برای ۱ دقیقه...")
        
        # اجرای تست به مدت ۱ دقیقه
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("تست با دستور کاربر متوقف شد")
        
        # توقف سرویس
        if stop_scheduler():
            print("سرویس با موفقیت متوقف شد")
        else:
            print("خطا در توقف سرویس")
    else:
        print("خطا در شروع سرویس")