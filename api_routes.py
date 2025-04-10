"""
روت‌های API برای کنترل و مدیریت سرویس‌های Crypto Barzin

این ماژول API‌های REST برای کنترل سرویس‌ها، دریافت وضعیت، و پیکربندی
اجزای مختلف سیستم را فراهم می‌کند.
"""

from flask import Blueprint, jsonify, request, current_app
import os
import sys
import logging
import time
from datetime import datetime
import pytz

# ماژول‌های داخلی
from replit_telegram_sender import send_message, send_test_message, send_price_report, send_system_report
from telegram_scheduler_service import start_scheduler, stop_scheduler, get_scheduler_status, update_scheduler_settings
from crypto_bot.price_alert_service import get_price_alerts, set_price_alert, remove_price_alert, check_price_alerts

# تنظیم لاگر
logger = logging.getLogger(__name__)

# ایجاد Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# مبدل تایم‌زون
def get_toronto_time():
    """
    دریافت زمان فعلی در تایم‌زون تورنتو
    
    Returns:
        str: زمان فعلی به فرمت HH:MM:SS
    """
    toronto_tz = pytz.timezone('America/Toronto')
    now = datetime.now(toronto_tz)
    return now.strftime("%H:%M:%S")

# روت‌های مربوط به سرویس تلگرام
@api.route('/telegram/start', methods=['GET'])
def telegram_start():
    """
    راه‌اندازی سرویس زمان‌بندی تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        result = start_scheduler()
        return jsonify({
            'success': result,
            'time': get_toronto_time(),
            'message': 'سرویس تلگرام با موفقیت راه‌اندازی شد.' if result else 'خطا در راه‌اندازی سرویس تلگرام.'
        })
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی سرویس تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در راه‌اندازی سرویس تلگرام: {str(e)}'
        })

@api.route('/telegram/stop', methods=['GET'])
def telegram_stop():
    """
    توقف سرویس زمان‌بندی تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        result = stop_scheduler()
        return jsonify({
            'success': result,
            'time': get_toronto_time(),
            'message': 'سرویس تلگرام با موفقیت متوقف شد.' if result else 'خطا در توقف سرویس تلگرام.'
        })
    except Exception as e:
        logger.error(f"خطا در توقف سرویس تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در توقف سرویس تلگرام: {str(e)}'
        })

@api.route('/telegram/status', methods=['GET'])
def telegram_status():
    """
    دریافت وضعیت سرویس زمان‌بندی تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        status = get_scheduler_status()
        # اضافه کردن فیلد running برای سازگاری با always_on_service
        status['running'] = status.get('active', False)
        return jsonify(status)
    except Exception as e:
        logger.error(f"خطا در دریافت وضعیت سرویس تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'running': False,
            'time': get_toronto_time(),
            'message': f'خطا در دریافت وضعیت سرویس تلگرام: {str(e)}'
        })

@api.route('/telegram/test', methods=['GET'])
def telegram_test():
    """
    ارسال پیام تست تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        result = send_test_message()
        return jsonify({
            'success': result,
            'time': get_toronto_time(),
            'message': 'پیام تست با موفقیت ارسال شد.' if result else 'خطا در ارسال پیام تست.'
        })
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تست تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در ارسال پیام تست تلگرام: {str(e)}'
        })

@api.route('/telegram/settings', methods=['POST'])
def telegram_settings():
    """
    بروزرسانی تنظیمات زمان‌بندی تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        data = request.json
        result = update_scheduler_settings(data)
        return jsonify({
            'success': True,
            'settings': result,
            'time': get_toronto_time(),
            'message': 'تنظیمات تلگرام با موفقیت بروزرسانی شد.'
        })
    except Exception as e:
        logger.error(f"خطا در بروزرسانی تنظیمات تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در بروزرسانی تنظیمات تلگرام: {str(e)}'
        })

# روت‌های مربوط به هشدارهای قیمت
@api.route('/price-alerts', methods=['GET'])
def api_get_price_alerts():
    """
    دریافت لیست هشدارهای قیمت
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        alerts = get_price_alerts()
        return jsonify({
            'success': True,
            'alerts': alerts,
            'time': get_toronto_time()
        })
    except Exception as e:
        logger.error(f"خطا در دریافت هشدارهای قیمت: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در دریافت هشدارهای قیمت: {str(e)}'
        })

@api.route('/price-alerts/set', methods=['POST'])
def api_set_price_alert():
    """
    تنظیم هشدار قیمت جدید
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        price = data.get('price')
        condition = data.get('condition')
        
        if not all([symbol, price, condition]):
            return jsonify({
                'success': False,
                'time': get_toronto_time(),
                'message': 'پارامترهای ناقص. symbol، price و condition الزامی هستند.'
            })
            
        alert_id = set_price_alert(symbol, float(price), condition)
        return jsonify({
            'success': True,
            'alert_id': alert_id,
            'time': get_toronto_time(),
            'message': f'هشدار قیمت برای {symbol} با موفقیت تنظیم شد.'
        })
    except Exception as e:
        logger.error(f"خطا در تنظیم هشدار قیمت: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در تنظیم هشدار قیمت: {str(e)}'
        })

@api.route('/price-alerts/remove', methods=['POST'])
def api_remove_price_alert():
    """
    حذف هشدار قیمت
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        data = request.json
        alert_id = data.get('alert_id')
        
        if not alert_id:
            return jsonify({
                'success': False,
                'time': get_toronto_time(),
                'message': 'شناسه هشدار (alert_id) الزامی است.'
            })
            
        success = remove_price_alert(alert_id)
        return jsonify({
            'success': success,
            'time': get_toronto_time(),
            'message': f'هشدار قیمت با موفقیت حذف شد.' if success else 'هشدار قیمت یافت نشد.'
        })
    except Exception as e:
        logger.error(f"خطا در حذف هشدار قیمت: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در حذف هشدار قیمت: {str(e)}'
        })

@api.route('/price-alerts/check', methods=['GET'])
def api_check_price_alerts():
    """
    بررسی هشدارهای قیمت
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        triggered = check_price_alerts()
        return jsonify({
            'success': True,
            'triggered': triggered,
            'count': len(triggered),
            'time': get_toronto_time(),
            'message': f'{len(triggered)} هشدار قیمت فعال شده است.'
        })
    except Exception as e:
        logger.error(f"خطا در بررسی هشدارهای قیمت: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در بررسی هشدارهای قیمت: {str(e)}'
        })

# روت‌های ارسال گزارش تلگرام
@api.route('/telegram/price-report', methods=['GET'])
def api_telegram_price_report():
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال به تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        result = send_price_report()
        return jsonify({
            'success': result,
            'time': get_toronto_time(),
            'message': 'گزارش قیمت با موفقیت ارسال شد.' if result else 'خطا در ارسال گزارش قیمت.'
        })
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش قیمت به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در ارسال گزارش قیمت به تلگرام: {str(e)}'
        })

@api.route('/telegram/system-report', methods=['GET'])
def api_telegram_system_report():
    """
    ارسال گزارش وضعیت سیستم به تلگرام
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        result = send_system_report()
        return jsonify({
            'success': result,
            'time': get_toronto_time(),
            'message': 'گزارش سیستم با موفقیت ارسال شد.' if result else 'خطا در ارسال گزارش سیستم.'
        })
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش سیستم به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در ارسال گزارش سیستم به تلگرام: {str(e)}'
        })

@api.route('/system/restart', methods=['GET'])
def api_system_restart():
    """
    راه‌اندازی مجدد سرویس‌های سیستم
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        # توقف سرویس تلگرام
        stop_scheduler()
        time.sleep(1)
        
        # راه‌اندازی مجدد سرویس تلگرام
        start_result = start_scheduler()
        
        return jsonify({
            'success': start_result,
            'time': get_toronto_time(),
            'message': 'سیستم با موفقیت راه‌اندازی مجدد شد.' if start_result else 'خطا در راه‌اندازی مجدد سیستم.'
        })
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی مجدد سیستم: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'message': f'خطا در راه‌اندازی مجدد سیستم: {str(e)}'
        })

# روت‌های سلامت سیستم
@api.route('/health', methods=['GET'])
def api_health_check():
    """
    بررسی سلامت سیستم
    
    Returns:
        jsonify: پاسخ JSON
    """
    try:
        # بررسی وضعیت سرویس‌های مختلف
        telegram_status = get_scheduler_status()
        
        return jsonify({
            'success': True,
            'time': get_toronto_time(),
            'system_status': 'online',
            'telegram_service': telegram_status,
            'version': '1.0.0',
            'uptime': 'Unknown'  # نیاز به پیاده‌سازی جداگانه دارد
        })
    except Exception as e:
        logger.error(f"خطا در بررسی سلامت سیستم: {str(e)}")
        return jsonify({
            'success': False,
            'time': get_toronto_time(),
            'system_status': 'partial_failure',
            'message': f'خطا در بررسی سلامت سیستم: {str(e)}'
        })