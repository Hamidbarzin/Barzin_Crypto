"""
URL Configuration for Django Multilingual App
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

from crypto_app.views import home, set_language_view, api_price_alert, api_user_messages, api_portfolio_summary

# الگوهای URL معمولی (بدون پیشوند زبان)
urlpatterns = [
    # مسیرهای API که به صورت مستقیم دسترسی خواهند بود
    path('api/price-alert/', api_price_alert, name='api_price_alert'),
    path('api/user-messages/', api_user_messages, name='api_user_messages'),
    path('api/portfolio-summary/', api_portfolio_summary, name='api_portfolio_summary'),
    path('api/set-language/', set_language_view, name='set_language'),
]

# الگوهای URL با پیشوند زبان
# این URLs با پیشوند زبان مانند /en/ یا /fa/ شروع می‌شوند
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    # URL برای تغییر زبان - در Django از view آماده استفاده می‌کنیم
    path(_('set-language/'), set_language_view, name='set_language_redirect'),
    
    # در صورت نیاز، URLs بیشتری می‌توانید اضافه کنید
    
    # اختیاری: افزودن نام‌های URL ترجمه شده
    path(_('dashboard/'), home, name='dashboard'),
    path(_('settings/'), home, name='settings'),
    
    # این پارامتر باعث می‌شود که اگر URL بدون پیشوند زبان وارد شود،
    # Django به صورت خودکار زبان را تشخیص دهد
    prefix_default_language=True,
)