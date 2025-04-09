"""
نسخه ساده‌سازی شده ماژول نشانگر قابلیت اطمینان تلگرام

این نسخه برای عیب‌یابی مشکلات به صورت ساده‌تر طراحی شده است.
"""

import os
import json
import logging
from datetime import datetime
import pytz

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیم منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')

# مسیر فایل ذخیره‌سازی داده‌ها
DATA_FILE = "simple_reliability_data.json"

# کلاس ساده‌شده
class SimpleReliabilityMonitor:
    """
    نسخه ساده‌شده کلاس نشانگر قابلیت اطمینان
    """
    
    def __init__(self, file_path=DATA_FILE):
        """مقداردهی اولیه"""
        self.file_path = file_path
        self.data = self._load_data()
        
        # اطمینان از وجود داده‌های اولیه
        if 'messages' not in self.data:
            self.data['messages'] = {
                'total_sent': 0,
                'successful': 0,
                'failed': 0,
                'history': []
            }
        
        if 'uptime' not in self.data:
            self.data['uptime'] = {
                'start_time': datetime.now(toronto_tz).isoformat(),
                'last_restart': datetime.now(toronto_tz).isoformat(),
                'restarts': 0
            }
            
        # ذخیره‌سازی تغییرات اولیه
        self._save_data()
    
    def _load_data(self):
        """بارگذاری داده‌ها از فایل"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"خطا در بارگذاری داده‌ها: {str(e)}")
            return {}
    
    def _save_data(self):
        """ذخیره‌سازی داده‌ها در فایل"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطا در ذخیره‌سازی داده‌ها: {str(e)}")
    
    def record_message_attempt(self, message_type, success, error_message=None):
        """ثبت تلاش برای ارسال پیام"""
        now = datetime.now(toronto_tz)
        
        # ثبت در آمار کلی
        self.data['messages']['total_sent'] += 1
        if success:
            self.data['messages']['successful'] += 1
        else:
            self.data['messages']['failed'] += 1
        
        # افزودن به تاریخچه
        event = {
            'message_type': message_type,
            'success': success,
            'timestamp': now.isoformat()
        }
        
        if not success and error_message:
            event['error'] = error_message
        
        self.data['messages']['history'].append(event)
        
        # ذخیره‌سازی تغییرات
        self._save_data()
    
    def record_service_restart(self):
        """ثبت راه‌اندازی مجدد سرویس"""
        now = datetime.now(toronto_tz)
        
        # افزایش شمارنده راه‌اندازی‌های مجدد
        self.data['uptime']['restarts'] += 1
        
        # به‌روزرسانی آخرین زمان راه‌اندازی مجدد
        self.data['uptime']['last_restart'] = now.isoformat()
        
        # ذخیره‌سازی تغییرات
        self._save_data()
    
    def get_reliability_stats(self):
        """دریافت آمار قابلیت اطمینان"""
        # محاسبه نرخ موفقیت
        total = self.data['messages']['total_sent']
        success_rate = 0
        if total > 0:
            success_rate = (self.data['messages']['successful'] / total) * 100
            
        # محاسبه زمان کارکرد سیستم
        now = datetime.now(toronto_tz)
        start_time = datetime.fromisoformat(self.data['uptime']['start_time'])
        uptime_seconds = (now - start_time).total_seconds()
        uptime_days = uptime_seconds / (60 * 60 * 24)
        
        # محاسبه آخرین راه‌اندازی مجدد
        last_restart = datetime.fromisoformat(self.data['uptime']['last_restart'])
        last_restart_hours_ago = (now - last_restart).total_seconds() / 3600
        
        return {
            'overall': {
                'total_sent': total,
                'successful': self.data['messages']['successful'],
                'failed': self.data['messages']['failed'],
                'success_rate': round(success_rate, 2)
            },
            'uptime': {
                'days': round(uptime_days, 2),
                'restarts': self.data['uptime']['restarts'],
                'last_restart_hours_ago': round(last_restart_hours_ago, 2)
            },
            'recent_events': self.data['messages']['history'][-5:] if self.data['messages']['history'] else []
        }
    
    def get_reliability_summary(self):
        """دریافت خلاصه قابلیت اطمینان"""
        stats = self.get_reliability_stats()
        
        # تعیین ایموجی وضعیت بر اساس نرخ موفقیت
        success_rate = stats['overall']['success_rate']
        if success_rate >= 95:
            status_emoji = "🟢"  # سبز - عالی
        elif success_rate >= 80:
            status_emoji = "🟡"  # زرد - خوب
        elif success_rate >= 60:
            status_emoji = "🟠"  # نارنجی - متوسط
        else:
            status_emoji = "🔴"  # قرمز - ضعیف
        
        summary = f"""
{status_emoji} وضعیت سیستم تلگرام

• ارسال موفق: {stats['overall']['successful']} از {stats['overall']['total_sent']} ({stats['overall']['success_rate']}%)
• زمان کارکرد: {stats['uptime']['days']} روز
• راه‌اندازی‌های مجدد: {stats['uptime']['restarts']}
• آخرین راه‌اندازی مجدد: {round(stats['uptime']['last_restart_hours_ago'])} ساعت پیش
"""
        
        return summary


# نمونه سینگلتون برای استفاده در کل برنامه
reliability_monitor = SimpleReliabilityMonitor()


def record_message_attempt(message_type, success, error_message=None):
    """ثبت تلاش برای ارسال پیام"""
    reliability_monitor.record_message_attempt(message_type, success, error_message)


def record_service_restart():
    """ثبت راه‌اندازی مجدد سرویس"""
    reliability_monitor.record_service_restart()


def get_reliability_stats():
    """دریافت آمار قابلیت اطمینان"""
    return reliability_monitor.get_reliability_stats()


def get_reliability_summary():
    """دریافت خلاصه قابلیت اطمینان"""
    return reliability_monitor.get_reliability_summary()


if __name__ == "__main__":
    # تست ماژول
    print("تست ماژول نشانگر قابلیت اطمینان ساده شده")
    
    # ثبت چند رویداد تستی
    record_message_attempt("test_message", True)
    record_message_attempt("price_report", True)
    record_message_attempt("system_report", True)
    record_message_attempt("technical_analysis", False, "خطای تست")
    
    # ثبت راه‌اندازی مجدد سرویس
    record_service_restart()
    
    # دریافت آمار
    stats = get_reliability_stats()
    print("آمار قابلیت اطمینان:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # دریافت خلاصه
    summary = get_reliability_summary()
    print("\nخلاصه قابلیت اطمینان:")
    print(summary)
    
    print("\nتست نشانگر قابلیت اطمینان ساده شده به پایان رسید.")