#!/usr/bin/env python3
"""
مثال پیاده‌سازی چندزبانگی در Flask با Flask-Babel
"""

from flask import Flask, request, jsonify, g, render_template
from flask_babel import Babel, gettext as _
import os

app = Flask(__name__)

# پیکربندی برنامه
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-key')

# پیکربندی Babel
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fa']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

@babel.localeselector
def get_locale():
    """
    تعیین زبان برای هر درخواست
    
    روال‌های تعیین زبان به ترتیب اولویت:
    1. بررسی پارامتر درخواست lang
    2. بررسی کوکی lang
    3. بررسی هدر Accept-Language
    4. بازگشت به زبان پیش‌فرض
    """
    # 1. بررسی پارامتر درخواست
    if request.args.get('lang'):
        return request.args.get('lang')
    
    # 2. بررسی کوکی
    if request.cookies.get('lang'):
        return request.cookies.get('lang')
    
    # 3. بررسی هدر زبان
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])


# مسیرهای وب
@app.route('/')
def index():
    """
    صفحه اصلی
    """
    return render_template('index.html')


# مسیرهای API
@app.route('/api/price-alert', methods=['POST'])
def create_price_alert():
    """
    ایجاد هشدار قیمت جدید با پشتیبانی چندزبانگی در پیام‌های خطا
    """
    try:
        data = request.json
        
        # اعتبارسنجی با خطاهای ترجمه شده
        if not data.get('symbol'):
            return jsonify({
                'status': 'error',
                'message': _('Symbol is required')
            }), 400
            
        if not data.get('price'):
            return jsonify({
                'status': 'error',
                'message': _('Target price is required')
            }), 400
            
        # شبیه‌سازی ایجاد هشدار قیمت
        # در برنامه واقعی، هشدار در پایگاه داده ذخیره می‌شود
        
        # پاسخ موفقیت
        response = jsonify({
            'status': 'success',
            'message': _('Price alert created successfully'),
            'data': {
                'id': 123,
                'symbol': data.get('symbol'),
                'price': data.get('price'),
                'type': data.get('type', 'above'),
                'created_at': '2025-04-10T12:00:00Z'
            }
        })
        
        # تنظیم کوکی زبان اگر در هدر درخواست زبان مشخص شده باشد
        if request.headers.get('Accept-Language'):
            lang = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
            if lang:
                response.set_cookie('lang', lang, max_age=30*24*60*60)  # 30 روز
                
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': _('An error occurred: %(error)s', error=str(e))
        }), 500


@app.route('/api/user-messages')
def get_user_messages():
    """
    دریافت پیام‌های کاربر با ترجمه مناسب بر اساس زبان درخواست
    """
    # شبیه‌سازی پیام‌های ترجمه شده
    messages = [
        {'id': 1, 'text': _('Welcome to Crypto Advisor')},
        {'id': 2, 'text': _('Your BTC alert was triggered')},
        {'id': 3, 'text': _('System maintenance scheduled for tomorrow')}
    ]
    
    return jsonify({
        'status': 'success',
        'data': messages
    })


@app.route('/api/portfolio-summary')
def get_portfolio_summary():
    """
    دریافت خلاصه پورتفولیو با ترجمه مناسب بر اساس زبان درخواست
    """
    # شبیه‌سازی داده‌های پورتفولیو با ترجمه
    portfolio = {
        'total_value': 15240.50,
        'daily_change': 3.2,
        'total_assets': 5,
        'summary': _('Your portfolio has grown by %(percent)s%% in the last 24 hours', percent='3.2'),
        'recommendation': _('Consider taking some profits'),
        'assets': [
            {
                'symbol': 'BTC',
                'name': _('Bitcoin'),
                'amount': 0.25,
                'value': 10625.75,
                'change': 2.8,
                'status': _('Performing well')
            },
            {
                'symbol': 'ETH',
                'name': _('Ethereum'),
                'amount': 2.5,
                'value': 4614.75,
                'change': 4.2,
                'status': _('Strong buy signal')
            }
        ]
    }
    
    return jsonify({
        'status': 'success',
        'data': portfolio
    })


@app.route('/api/change-language', methods=['POST'])
def change_language():
    """
    تغییر زبان کاربر
    """
    try:
        data = request.json
        language = data.get('language', 'en')
        
        # بررسی معتبر بودن زبان
        if language not in app.config['BABEL_SUPPORTED_LOCALES']:
            return jsonify({
                'status': 'error',
                'message': _('Invalid language code')
            }), 400
            
        # در اینجا می‌توان زبان را در پروفایل کاربر ذخیره کرد
        # ...
        
        # تنظیم کوکی زبان
        response = jsonify({
            'status': 'success',
            'message': _('Language changed successfully')
        })
        
        response.set_cookie('lang', language, max_age=30*24*60*60)  # 30 روز
        
        return response
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': _('An error occurred: %(error)s', error=str(e))
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)