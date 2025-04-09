"""
ماژول نشانگر قابلیت اطمینان پیام‌های تلگرام

این ماژول برای پیگیری و نمایش وضعیت قابلیت اطمینان ارسال پیام‌های تلگرام استفاده می‌شود.
اطلاعات آماری مربوط به موفقیت و شکست پیام‌ها را جمع‌آوری و نمایش می‌دهد.
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
import pytz

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیم منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')

# مسیر فایل ذخیره‌سازی داده‌ها
DATA_FILE = "telegram_reliability_data.json"

# قفل برای دسترسی همزمان
data_lock = threading.Lock()

class TelegramReliabilityMonitor:
    """
    کلاس برای پیگیری و تحلیل قابلیت اطمینان پیام‌های تلگرام
    """

    def __init__(self, file_path=DATA_FILE):
        """
        مقداردهی اولیه کلاس
        
        Args:
            file_path (str): مسیر فایل ذخیره‌سازی داده‌ها
        """
        self.file_path = file_path
        self.data = self._load_data()
        
        # اطمینان از وجود داده‌های اولیه
        if 'messages' not in self.data:
            self.data['messages'] = {
                'total_sent': 0,
                'successful': 0,
                'failed': 0,
                'last_24h': {
                    'total_sent': 0,
                    'successful': 0,
                    'failed': 0
                },
                'history': []
            }
        
        if 'uptime' not in self.data:
            self.data['uptime'] = {
                'start_time': datetime.now(toronto_tz).isoformat(),
                'last_restart': datetime.now(toronto_tz).isoformat(),
                'restarts': 0
            }
            
        # پاکسازی تاریخچه قدیمی
        self._clean_old_history()
    
    def _load_data(self):
        """
        بارگذاری داده‌ها از فایل
        
        Returns:
            dict: داده‌های بارگذاری شده
        """
        with data_lock:
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
        """
        ذخیره‌سازی داده‌ها در فایل
        """
        with data_lock:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"خطا در ذخیره‌سازی داده‌ها: {str(e)}")
    
    def _clean_old_history(self):
        """
        پاکسازی تاریخچه قدیمی‌تر از 7 روز
        """
        if 'history' in self.data['messages']:
            now = datetime.now(toronto_tz)
            seven_days_ago = (now - timedelta(days=7)).isoformat()
            
            # فیلتر کردن رویدادهای یک هفته اخیر
            self.data['messages']['history'] = [
                event for event in self.data['messages']['history']
                if event.get('timestamp', '0') >= seven_days_ago
            ]
            
            # محدود کردن تعداد رویدادها به 1000
            if len(self.data['messages']['history']) > 1000:
                self.data['messages']['history'] = self.data['messages']['history'][-1000:]
    
    def record_message_attempt(self, message_type, success, error_message=None):
        """
        ثبت تلاش برای ارسال پیام
        
        Args:
            message_type (str): نوع پیام (برای مثال 'price_report', 'news', 'technical')
            success (bool): آیا ارسال موفقیت‌آمیز بوده یا خیر
            error_message (str, optional): پیام خطا در صورت شکست
        """
        with data_lock:
            now = datetime.now(toronto_tz)
            
            # ثبت در آمار کلی
            self.data['messages']['total_sent'] += 1
            if success:
                self.data['messages']['successful'] += 1
            else:
                self.data['messages']['failed'] += 1
            
            # ثبت در آمار 24 ساعت اخیر
            twenty_four_hours_ago = (now - timedelta(hours=24)).isoformat()
            
            # به‌روزرسانی آمار 24 ساعت اخیر
            self._update_last_24h_stats(twenty_four_hours_ago)
            
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
    
    def _update_last_24h_stats(self, cutoff_time):
        """
        به‌روزرسانی آمار 24 ساعت اخیر
        
        Args:
            cutoff_time (str): زمان مرزی به صورت ISO format
        """
        # محاسبه مجدد آمار 24 ساعت اخیر
        recent_history = [
            event for event in self.data['messages']['history']
            if event.get('timestamp', '0') >= cutoff_time
        ]
        
        self.data['messages']['last_24h'] = {
            'total_sent': len(recent_history),
            'successful': sum(1 for event in recent_history if event.get('success', False)),
            'failed': sum(1 for event in recent_history if not event.get('success', True))
        }
    
    def record_service_restart(self):
        """
        ثبت راه‌اندازی مجدد سرویس
        """
        with data_lock:
            now = datetime.now(toronto_tz)
            
            # افزایش شمارنده راه‌اندازی‌های مجدد
            self.data['uptime']['restarts'] += 1
            
            # به‌روزرسانی آخرین زمان راه‌اندازی مجدد
            self.data['uptime']['last_restart'] = now.isoformat()
            
            # ذخیره‌سازی تغییرات
            self._save_data()
    
    def get_reliability_stats(self):
        """
        دریافت آمار قابلیت اطمینان
        
        Returns:
            dict: آمار قابلیت اطمینان
        """
        with data_lock:
            # به‌روزرسانی آمار 24 ساعت اخیر قبل از بازگرداندن داده‌ها
            now = datetime.now(toronto_tz)
            twenty_four_hours_ago = (now - timedelta(hours=24)).isoformat()
            self._update_last_24h_stats(twenty_four_hours_ago)
            
            # محاسبه نرخ موفقیت
            total = self.data['messages']['total_sent']
            success_rate = 0
            if total > 0:
                success_rate = (self.data['messages']['successful'] / total) * 100
                
            total_24h = self.data['messages']['last_24h']['total_sent']
            success_rate_24h = 0
            if total_24h > 0:
                success_rate_24h = (self.data['messages']['last_24h']['successful'] / total_24h) * 100
            
            # محاسبه زمان کارکرد سیستم
            start_time = datetime.fromisoformat(self.data['uptime']['start_time'])
            uptime_seconds = (now - start_time).total_seconds()
            uptime_days = uptime_seconds / (60 * 60 * 24)
            
            # محاسبه آخرین راه‌اندازی مجدد
            last_restart = datetime.fromisoformat(self.data['uptime']['last_restart'])
            last_restart_hours_ago = (now - last_restart).total_seconds() / 3600
            
            # آمار اخیر (10 رویداد آخر)
            recent_events = self.data['messages']['history'][-10:] if self.data['messages']['history'] else []
            
            # آمار نوع پیام‌ها
            message_types = {}
            for event in self.data['messages']['history']:
                msg_type = event.get('message_type', 'unknown')
                if msg_type not in message_types:
                    message_types[msg_type] = {'total': 0, 'successful': 0, 'failed': 0}
                
                message_types[msg_type]['total'] += 1
                if event.get('success', False):
                    message_types[msg_type]['successful'] += 1
                else:
                    message_types[msg_type]['failed'] += 1
            
            # تبدیل آمار نوع پیام‌ها به لیست
            message_type_stats = []
            for msg_type, stats in message_types.items():
                success_rate_type = 0
                if stats['total'] > 0:
                    success_rate_type = (stats['successful'] / stats['total']) * 100
                
                message_type_stats.append({
                    'type': msg_type,
                    'total': stats['total'],
                    'successful': stats['successful'],
                    'failed': stats['failed'],
                    'success_rate': round(success_rate_type, 2)
                })
            
            # مرتب‌سازی بر اساس تعداد کل
            message_type_stats.sort(key=lambda x: x['total'], reverse=True)
            
            return {
                'overall': {
                    'total_sent': total,
                    'successful': self.data['messages']['successful'],
                    'failed': self.data['messages']['failed'],
                    'success_rate': round(success_rate, 2)
                },
                'last_24h': {
                    'total_sent': total_24h,
                    'successful': self.data['messages']['last_24h']['successful'],
                    'failed': self.data['messages']['last_24h']['failed'],
                    'success_rate': round(success_rate_24h, 2)
                },
                'uptime': {
                    'days': round(uptime_days, 2),
                    'restarts': self.data['uptime']['restarts'],
                    'last_restart_hours_ago': round(last_restart_hours_ago, 2)
                },
                'message_types': message_type_stats,
                'recent_events': recent_events
            }
    
    def get_reliability_summary(self):
        """
        دریافت خلاصه قابلیت اطمینان برای نمایش در پیام‌های تلگرام
        
        Returns:
            str: خلاصه قابلیت اطمینان
        """
        stats = self.get_reliability_stats()
        
        # تعیین ایموجی وضعیت بر اساس نرخ موفقیت
        success_rate_24h = stats['last_24h']['success_rate']
        if success_rate_24h >= 95:
            status_emoji = "🟢"  # سبز - عالی
        elif success_rate_24h >= 80:
            status_emoji = "🟡"  # زرد - خوب
        elif success_rate_24h >= 60:
            status_emoji = "🟠"  # نارنجی - متوسط
        else:
            status_emoji = "🔴"  # قرمز - ضعیف
        
        summary = f"""
{status_emoji} <b>وضعیت سیستم تلگرام</b>

• ارسال موفق (24 ساعت اخیر): {stats['last_24h']['successful']} از {stats['last_24h']['total_sent']} ({stats['last_24h']['success_rate']}%)
• زمان کارکرد: {stats['uptime']['days']} روز
• راه‌اندازی‌های مجدد: {stats['uptime']['restarts']}
• آخرین راه‌اندازی مجدد: {round(stats['uptime']['last_restart_hours_ago'])} ساعت پیش
"""
        
        # اضافه کردن وضعیت انواع پیام‌ها (حداکثر 3 مورد پرتکرار)
        if stats['message_types']:
            summary += "\n<b>انواع پیام‌ها:</b>\n"
            for i, msg_type in enumerate(stats['message_types'][:3]):
                type_emoji = "🟢" if msg_type['success_rate'] >= 90 else ("🟡" if msg_type['success_rate'] >= 70 else "🔴")
                summary += f"• {type_emoji} {msg_type['type']}: {msg_type['success_rate']}% موفق ({msg_type['successful']}/{msg_type['total']})\n"
        
        return summary


# نمونه سینگلتون برای استفاده در کل برنامه
reliability_monitor = TelegramReliabilityMonitor()


def record_message_attempt(message_type, success, error_message=None):
    """
    ثبت تلاش برای ارسال پیام
    
    Args:
        message_type (str): نوع پیام
        success (bool): آیا ارسال موفقیت‌آمیز بوده یا خیر
        error_message (str, optional): پیام خطا در صورت شکست
    """
    reliability_monitor.record_message_attempt(message_type, success, error_message)


def record_service_restart():
    """
    ثبت راه‌اندازی مجدد سرویس
    """
    reliability_monitor.record_service_restart()


def get_reliability_stats():
    """
    دریافت آمار قابلیت اطمینان
    
    Returns:
        dict: آمار قابلیت اطمینان
    """
    return reliability_monitor.get_reliability_stats()


def get_reliability_summary():
    """
    دریافت خلاصه قابلیت اطمینان برای نمایش در پیام‌های تلگرام
    
    Returns:
        str: خلاصه قابلیت اطمینان
    """
    return reliability_monitor.get_reliability_summary()


if __name__ == "__main__":
    # تست ماژول
    print("تست ماژول نشانگر قابلیت اطمینان پیام‌های تلگرام")
    
    # ثبت چند رویداد تستی
    record_message_attempt("price_report", True)
    record_message_attempt("news", True)
    record_message_attempt("technical", False, "خطای دسترسی به API")
    record_message_attempt("price_report", True)
    
    # نمایش آمار
    stats = get_reliability_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # نمایش خلاصه
    summary = get_reliability_summary()
    print(summary)