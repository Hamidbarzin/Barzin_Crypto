#!/usr/bin/env python3
"""
سرویس اعلان صوتی چندزبانه

این ماژول امکان تولید اعلان‌های صوتی به زبان‌های مختلف را فراهم می‌کند.
از قابلیت تبدیل متن به گفتار (TTS) برای ساخت فایل‌های صوتی استفاده می‌کند.
"""

import os
import json
import logging
import datetime
import uuid
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

import gtts
from gtts import gTTS
import pyttsx3
from crypto_bot.config import DEFAULT_VOICE_SETTINGS

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("voice_notification")

# ساختار دایرکتوری برای ذخیره فایل‌های صوتی
AUDIO_DIR = Path('./static/audio/notifications')
# اطمینان از وجود دایرکتوری
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# لیست زبان‌های پشتیبانی شده
SUPPORTED_LANGUAGES = {
    'fa': 'فارسی (Persian)',
    'en': 'English',
    'ar': 'العربية (Arabic)',
    'tr': 'Türkçe (Turkish)',
    'fr': 'Français (French)',
    'de': 'Deutsch (German)',
    'es': 'Español (Spanish)',
    'ru': 'Русский (Russian)',
    'zh-cn': '中文 (Chinese)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'hi': 'हिन्दी (Hindi)',
    'it': 'Italiano (Italian)',
    'pt': 'Português (Portuguese)'
}

# دیکشنری متن‌های اعلان برای هر زبان
NOTIFICATION_TEXTS = {
    'fa': {
        'price_increase': '{crypto} با {percent}٪ افزایش به قیمت {price} دلار رسید.',
        'price_decrease': 'قیمت {crypto} با {percent}٪ کاهش به {price} دلار رسید.',
        'target_reached': 'هشدار: {crypto} به قیمت هدف {price} دلار رسید.',
        'stop_loss': 'هشدار: {crypto} به قیمت حد ضرر {price} دلار رسید.',
        'high_volatility': 'هشدار: {crypto} با {percent}٪ تغییر، نوسان بالایی دارد.'
    },
    'en': {
        'price_increase': '{crypto} has increased by {percent}% to {price} dollars.',
        'price_decrease': '{crypto} price has decreased by {percent}% to {price} dollars.',
        'target_reached': 'Alert: {crypto} has reached the target price of {price} dollars.',
        'stop_loss': 'Alert: {crypto} has reached the stop loss price of {price} dollars.',
        'high_volatility': 'Alert: {crypto} is showing high volatility with a {percent}% change.'
    },
    'ar': {
        'price_increase': 'ارتفع سعر {crypto} بنسبة {percent}٪ إلى {price} دولار.',
        'price_decrease': 'انخفض سعر {crypto} بنسبة {percent}٪ إلى {price} دولار.',
        'target_reached': 'تنبيه: وصل {crypto} إلى السعر المستهدف {price} دولار.',
        'stop_loss': 'تنبيه: وصل {crypto} إلى سعر وقف الخسارة {price} دولار.',
        'high_volatility': 'تنبيه: يظهر {crypto} تقلبات عالية مع تغيير بنسبة {percent}٪.'
    }
}

# قیمت‌های نمونه برای هر ارز (برای تست)
SAMPLE_PRICES = {
    'BTC': 82500,
    'ETH': 1670,
    'SOL': 175,
    'BNB': 620,
    'XRP': 0.58
}

class VoiceNotificationService:
    """
    کلاس سرویس اعلان صوتی
    
    این کلاس وظیفه ایجاد و مدیریت اعلان‌های صوتی را بر عهده دارد.
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس
        """
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """
        بارگذاری تنظیمات از فایل یا استفاده از تنظیمات پیش‌فرض
        
        Returns:
            Dict[str, Any]: تنظیمات بارگذاری شده
        """
        settings_path = Path('./data/voice_settings.json')
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"خطا در بارگذاری تنظیمات صوتی: {str(e)}")
        
        # در صورت عدم وجود فایل، ایجاد مسیر
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # برگرداندن تنظیمات پیش‌فرض
        return DEFAULT_VOICE_SETTINGS
    
    def _save_settings(self) -> bool:
        """
        ذخیره تنظیمات در فایل
        
        Returns:
            bool: وضعیت ذخیره‌سازی
        """
        settings_path = Path('./data/voice_settings.json')
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"خطا در ذخیره تنظیمات صوتی: {str(e)}")
            return False
    
    def save_user_settings(self, settings: Dict[str, Any]) -> bool:
        """
        ذخیره تنظیمات کاربر
        
        Args:
            settings (Dict[str, Any]): تنظیمات جدید
            
        Returns:
            bool: وضعیت ذخیره‌سازی
        """
        # تنظیمات معتبر را اعمال می‌کنیم
        if 'crypto' in settings:
            self.settings['crypto'] = settings['crypto']
        if 'event_type' in settings:
            self.settings['event_type'] = settings['event_type']
        if 'price_change' in settings:
            self.settings['price_change'] = float(settings['price_change'])
        if 'language' in settings and settings['language'] in SUPPORTED_LANGUAGES:
            self.settings['language'] = settings['language']
        if 'voice_gender' in settings and settings['voice_gender'] in ['male', 'female']:
            self.settings['voice_gender'] = settings['voice_gender']
        
        return self._save_settings()
    
    def get_notification_text(self, params: Dict[str, Any]) -> str:
        """
        ایجاد متن اعلان بر اساس پارامترهای ورودی
        
        Args:
            params (Dict[str, Any]): پارامترهای متن
                - crypto: نام ارز
                - event_type: نوع رویداد
                - price_change: میزان تغییر قیمت
                - language: زبان متن
                
        Returns:
            str: متن اعلان
        """
        crypto = params.get('crypto', 'BTC')
        event_type = params.get('event_type', 'price_increase')
        price_change = params.get('price_change', 5)
        language = params.get('language', 'fa')
        
        # اگر زبان پشتیبانی نشده باشد، از فارسی استفاده می‌کنیم
        if language not in NOTIFICATION_TEXTS:
            language = 'fa'
        
        # اگر نوع رویداد پشتیبانی نشده باشد، از افزایش قیمت استفاده می‌کنیم
        if event_type not in NOTIFICATION_TEXTS[language]:
            event_type = 'price_increase'
        
        # قیمت نمونه برای ارز
        price = SAMPLE_PRICES.get(crypto, 1000)
        
        # متن اعلان را ایجاد می‌کنیم
        return NOTIFICATION_TEXTS[language][event_type].format(
            crypto=crypto,
            percent=price_change,
            price=price
        )
    
    def generate_voice(self, text: str, language: str = 'fa', voice_gender: str = 'male') -> Optional[str]:
        """
        تبدیل متن به گفتار و ذخیره آن به عنوان فایل صوتی
        
        Args:
            text (str): متن برای تبدیل به گفتار
            language (str): کد زبان
            voice_gender (str): جنسیت صدا (male یا female)
            
        Returns:
            Optional[str]: آدرس فایل صوتی ذخیره شده یا None در صورت بروز خطا
        """
        # Initialize filepath and relative_path before try block
        filename = f"{uuid.uuid4()}.mp3"
        filepath = AUDIO_DIR / filename
        relative_path = f"/static/audio/notifications/{filename}"
        
        try:
            # تبدیل متن به گفتار با استفاده از gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(str(filepath))
            
            logger.info(f"فایل صوتی با موفقیت ایجاد شد: {filepath}")
            return relative_path
            
        except Exception as e:
            logger.error(f"خطا در تبدیل متن به گفتار: {str(e)}")
            
            # تلاش برای استفاده از موتور پشتیبان
            try:
                return self._fallback_tts(text, filepath, relative_path)
            except Exception as fallback_error:
                logger.error(f"خطا در موتور پشتیبان TTS: {str(fallback_error)}")
                return None
    
    def _fallback_tts(self, text: str, filepath: Path, relative_path: str) -> Optional[str]:
        """
        موتور پشتیبان TTS برای مواقعی که gTTS با خطا مواجه می‌شود
        
        Args:
            text (str): متن برای تبدیل به گفتار
            filepath (Path): مسیر فایل برای ذخیره
            relative_path (str): مسیر نسبی فایل
            
        Returns:
            Optional[str]: آدرس فایل صوتی ذخیره شده یا None در صورت بروز خطا
        """
        # These variables should be defined in the calling method
        if filepath is None or relative_path is None:
            # ایجاد نام فایل منحصر به فرد در صورتی که فایل‌پث تعریف نشده باشد
            filename = f"{uuid.uuid4()}.mp3"
            filepath = AUDIO_DIR / filename
            relative_path = f"/static/audio/notifications/{filename}"
            
        engine = pyttsx3.init()
        
        # تنظیم ویژگی‌های صدا
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # صدای اول
        
        # تنظیم سرعت
        engine.setProperty('rate', 150)
        
        # ذخیره به فایل
        engine.save_to_file(text, str(filepath))
        engine.runAndWait()
        
        return relative_path
    
    def preview_notification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ایجاد پیش‌نمایش اعلان صوتی
        
        Args:
            params (Dict[str, Any]): پارامترهای اعلان
                - crypto: نام ارز
                - event_type: نوع رویداد
                - price_change: میزان تغییر قیمت
                - language: زبان متن
                - voice_gender: جنسیت صدا
                
        Returns:
            Dict[str, Any]: نتیجه پیش‌نمایش شامل:
                - success: وضعیت
                - text: متن اعلان
                - audio_url: آدرس فایل صوتی
                - error: پیام خطا (در صورت بروز)
        """
        try:
            # ایجاد متن اعلان
            text = self.get_notification_text(params)
            
            # تبدیل متن به گفتار
            audio_url = self.generate_voice(
                text=text,
                language=params.get('language', 'fa'),
                voice_gender=params.get('voice_gender', 'male')
            )
            
            if audio_url:
                return {
                    'success': True,
                    'text': text,
                    'audio_url': audio_url
                }
            else:
                return {
                    'success': False,
                    'error': 'خطا در تبدیل متن به گفتار'
                }
                
        except Exception as e:
            logger.error(f"خطا در پیش‌نمایش اعلان: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# نمونه سرویس برای استفاده در برنامه
voice_notification_service = VoiceNotificationService()