"""
Views for Django Multilingual App
"""

import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from django.utils import translation


def home(request):
    """
    نمایش صفحه اصلی برنامه با پشتیبانی چندزبانگی
    """
    # انتقال متغیرهای قالب به تمپلیت
    context = {
        'title': _('Crypto Barzin'),
        'subtitle': _('Multilingual Django Application Example'),
        'current_language': request.LANGUAGE_CODE,
    }
    return render(request, 'home.html', context)


@require_http_methods(["POST"])
def set_language_view(request):
    """
    تغییر زبان برنامه
    
    این ویو برای پاسخگویی به درخواست‌های API برای تغییر زبان استفاده می‌شود.
    """
    try:
        data = json.loads(request.body)
        language = data.get('language', 'en')
        
        # بررسی معتبر بودن زبان
        from django.conf import settings
        valid_languages = [code for code, name in settings.LANGUAGES]
        
        if language not in valid_languages:
            return JsonResponse({
                'status': 'error',
                'message': _('Invalid language code')
            }, status=400)
            
        # تغییر زبان فعال
        translation.activate(language)
        
        # ذخیره زبان در session
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        
        # تنظیم کوکی زبان
        response = JsonResponse({
            'status': 'success',
            'message': _('Language changed successfully')
        })
        
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, max_age=30*24*60*60)
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': _('An error occurred: %(error)s') % {'error': str(e)}
        }, status=500)


@require_http_methods(["POST"])
def api_price_alert(request):
    """
    API برای ایجاد هشدار قیمت با پیام‌های ترجمه شده
    """
    try:
        data = json.loads(request.body)
        
        # اعتبارسنجی با خطاهای ترجمه شده
        if not data.get('symbol'):
            return JsonResponse({
                'status': 'error',
                'message': _('Symbol is required')
            }, status=400)
            
        if not data.get('price'):
            return JsonResponse({
                'status': 'error',
                'message': _('Target price is required')
            }, status=400)
            
        # شبیه‌سازی ایجاد هشدار قیمت
        # در یک برنامه واقعی، این قسمت با مدل Django پیاده‌سازی می‌شود
        
        return JsonResponse({
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
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': _('An error occurred: %(error)s') % {'error': str(e)}
        }, status=500)


def api_user_messages(request):
    """
    API برای دریافت پیام‌های کاربر با ترجمه مناسب
    """
    # شبیه‌سازی پیام‌های ترجمه شده
    messages = [
        {'id': 1, 'text': _('Welcome to Crypto Advisor')},
        {'id': 2, 'text': _('Your BTC alert was triggered')},
        {'id': 3, 'text': _('System maintenance scheduled for tomorrow')}
    ]
    
    return JsonResponse({
        'status': 'success',
        'data': messages
    })


def api_portfolio_summary(request):
    """
    API برای دریافت خلاصه پورتفولیو با ترجمه مناسب
    """
    # شبیه‌سازی داده‌های پورتفولیو با ترجمه
    portfolio = {
        'total_value': 15240.50,
        'daily_change': 3.2,
        'total_assets': 5,
        'summary': _('Your portfolio has grown by %(percent)s%% in the last 24 hours') % {'percent': '3.2'},
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
    
    return JsonResponse({
        'status': 'success',
        'data': portfolio
    })