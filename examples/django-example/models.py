"""
Models for Django Multilingual App
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserProfile(models.Model):
    """
    مدل پروفایل کاربر با پشتیبانی از زبان ترجیحی
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(
        max_length=10, 
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        verbose_name=_('Preferred Language')
    )
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_preferred_language_display()}"


class PriceAlert(models.Model):
    """
    مدل هشدار قیمت با عناوین ترجمه شده
    """
    # انواع هشدار قیمت
    ALERT_TYPE_CHOICES = [
        ('above', _('Price Above')),
        ('below', _('Price Below')),
        ('percent_change', _('Percent Change')),
        ('volatility', _('High Volatility')),
    ]
    
    # وضعیت‌های هشدار
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('triggered', _('Triggered')),
        ('inactive', _('Inactive')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_alerts')
    symbol = models.CharField(max_length=20, verbose_name=_('Cryptocurrency Symbol'))
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Target Price'))
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, default='above', verbose_name=_('Alert Type'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    triggered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Triggered At'))
    notification_sent = models.BooleanField(default=False, verbose_name=_('Notification Sent'))
    
    class Meta:
        verbose_name = _('Price Alert')
        verbose_name_plural = _('Price Alerts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.symbol} - {self.get_alert_type_display()} {self.price} - {self.get_status_display()}"


class CryptoNewsArticle(models.Model):
    """
    مدل اخبار ارز دیجیتال با عنوان و محتوای چندزبانه
    
    در اینجا از مدل ساده استفاده می‌کنیم که برای هر زبان
    فیلدهای جداگانه دارد. در برنامه‌های پیچیده‌تر می‌توان از
    django-modeltranslation یا ساختار مدل پیچیده‌تر استفاده کرد.
    """
    title_en = models.CharField(max_length=200, verbose_name=_('Title (English)'))
    title_fa = models.CharField(max_length=200, verbose_name=_('Title (Persian)'))
    content_en = models.TextField(verbose_name=_('Content (English)'))
    content_fa = models.TextField(verbose_name=_('Content (Persian)'))
    source_url = models.URLField(verbose_name=_('Source URL'))
    published_at = models.DateTimeField(verbose_name=_('Published At'))
    
    class Meta:
        verbose_name = _('Crypto News Article')
        verbose_name_plural = _('Crypto News Articles')
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title_en
    
    def get_title(self, language_code):
        """
        دریافت عنوان با توجه به زبان
        """
        if language_code == 'fa':
            return self.title_fa
        return self.title_en
    
    def get_content(self, language_code):
        """
        دریافت محتوا با توجه به زبان
        """
        if language_code == 'fa':
            return self.content_fa
        return self.content_en