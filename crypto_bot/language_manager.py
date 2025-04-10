"""
ماژول مدیریت زبان برای پشتیبانی از چندزبانگی در سیستم

این ماژول امکان ترجمه متن‌ها را در بخش‌های مختلف برنامه (وب، API و تلگرام) فراهم می‌کند.
"""

import os
import json
import logging
from functools import lru_cache

# تنظیم لاگر
logger = logging.getLogger(__name__)

# زبان‌های پشتیبانی شده
SUPPORTED_LANGUAGES = ['en', 'fa', 'fr']

# زبان پیش‌فرض
DEFAULT_LANGUAGE = 'fa'

# مسیر فایل‌های ترجمه
LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')

# دیکشنری‌های ترجمه
translations = {}

# توابع افزوده برای استفاده در main.py
def get_language_code(lang_name):
    """
    دریافت کد زبان بر اساس نام آن
    
    Args:
        lang_name (str): نام زبان (مثلاً English یا فارسی)
    
    Returns:
        str: کد زبان (مثلاً en یا fa)
    """
    lang_map = {
        'english': 'en',
        'انگلیسی': 'en',
        'persian': 'fa',
        'فارسی': 'fa',
        'french': 'fr',
        'français': 'fr',
        'فرانسوی': 'fr'
    }
    
    # اگر lang_name دقیقاً برابر با یکی از کدهای زبان باشد، همان را برگردان
    if lang_name.lower() in [code.lower() for code in SUPPORTED_LANGUAGES]:
        return lang_name.lower()
        
    return lang_map.get(lang_name.lower(), DEFAULT_LANGUAGE)

def get_ui_text(key, default="", language=None):
    """
    دریافت متن ترجمه شده برای رابط کاربری
    
    Args:
        key (str): کلید ترجمه
        default (str, optional): متن پیش‌فرض در صورت عدم وجود ترجمه
        language (str, optional): زبان ترجمه
    
    Returns:
        str: متن ترجمه شده یا متن پیش‌فرض
    """
    result = get_translation(key, language)
    return result if result != key else default

def get_language_info(language_code):
    """
    دریافت اطلاعات زبان بر اساس کد آن
    
    Args:
        language_code (str): کد زبان
    
    Returns:
        dict: اطلاعات زبان
    """
    lang_info = {
        'en': {
            'code': 'en',
            'name': 'English',
            'native_name': 'English',
            'direction': 'ltr',
            'icon': '🇺🇸'
        },
        'fa': {
            'code': 'fa',
            'name': 'Persian',
            'native_name': 'فارسی',
            'direction': 'rtl',
            'icon': '🇮🇷'
        },
        'fr': {
            'code': 'fr',
            'name': 'French',
            'native_name': 'Français',
            'direction': 'ltr',
            'icon': '🇫🇷'
        }
    }
    return lang_info.get(language_code, lang_info[DEFAULT_LANGUAGE])

def get_all_languages():
    """
    دریافت لیست همه زبان‌های پشتیبانی شده
    
    Returns:
        list: لیست دیکشنری‌های اطلاعات زبان
    """
    return [get_language_info(lang) for lang in SUPPORTED_LANGUAGES]


def load_translations():
    """بارگذاری تمام فایل‌های ترجمه"""
    global translations
    
    try:
        # اطمینان از وجود دایرکتوری‌های لازم
        if not os.path.exists(LOCALES_DIR):
            os.makedirs(LOCALES_DIR)
            logger.info(f"Created locales directory at {LOCALES_DIR}")
        
        # بارگذاری فایل‌های ترجمه برای هر زبان
        for lang in SUPPORTED_LANGUAGES:
            translations[lang] = {}
            
            # مسیر فایل‌های ترجمه برای این زبان
            lang_dir = os.path.join(LOCALES_DIR, lang)
            if not os.path.exists(lang_dir):
                os.makedirs(lang_dir)
                logger.info(f"Created language directory for {lang}")
            
            # بررسی فایل‌های ترجمه موجود
            for filename in ['common.json', 'dashboard.json', 'crypto.json', 'telegram.json', 'settings.json']:
                file_path = os.path.join(lang_dir, filename)
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # استخراج فضای نام از نام فایل (حذف پسوند .json)
                            namespace = filename.rsplit('.', 1)[0]
                            translations[lang][namespace] = json.load(f)
                            logger.info(f"Loaded {lang}/{namespace} translations")
                    except Exception as e:
                        logger.error(f"Error loading {file_path}: {e}")
                else:
                    logger.warning(f"Translation file {file_path} does not exist")
                    
                    # ایجاد فایل خالی برای استفاده بعدی
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('{}')
                    logger.info(f"Created empty translation file at {file_path}")
    
    except Exception as e:
        logger.error(f"Error in load_translations: {e}")


@lru_cache(maxsize=128)
def get_translation(key, language=None, namespace='common', **kwargs):
    """
    ترجمه کلید به زبان مشخص شده
    
    Args:
        key (str): کلید ترجمه، می‌تواند به صورت ساده ('title') یا نقطه‌گذاری شده ('app.title') باشد
        language (str, optional): زبان ترجمه (en یا fa)
        namespace (str, optional): فضای نام ترجمه (common, dashboard, crypto و ...)
        **kwargs: متغیرهای جایگزین در متن ترجمه
    
    Returns:
        str: متن ترجمه شده
    """
    # بررسی وجود زبان و تنظیم مقدار پیش‌فرض
    if not language or language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    # اطمینان از بارگذاری ترجمه‌ها
    if not translations:
        load_translations()
    
    # استخراج کلید ترجمه و فضای نام
    if '.' in key and namespace == 'common':
        parts = key.split('.', 1)
        if len(parts) == 2:
            namespace, key = parts
    
    # جستجوی ترجمه در دیکشنری ترجمه‌ها
    try:
        # اگر کلید چندبخشی با نقطه باشد، آن را بخش‌بخش بررسی می‌کنیم
        if '.' in key:
            parts = key.split('.')
            current = translations.get(language, {}).get(namespace, {})
            
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    # کلید یافت نشد، برگشت به متن اصلی
                    return key
                current = current[part]
            
            result = current
        else:
            # کلید ساده
            result = translations.get(language, {}).get(namespace, {}).get(key, key)
        
        # اگر ترجمه یافت نشد، از زبان پیش‌فرض استفاده می‌کنیم
        if result == key and language != DEFAULT_LANGUAGE:
            result = get_translation(key, DEFAULT_LANGUAGE, namespace, **kwargs)
        
        # جایگزینی متغیرها در متن ترجمه
        if isinstance(result, str) and kwargs:
            try:
                result = result.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format key in translation: {e}")
            except Exception as e:
                logger.error(f"Error formatting translation: {e}")
        
        return result
    
    except Exception as e:
        logger.error(f"Translation error for key '{key}' in {language}/{namespace}: {e}")
        return key


def save_translation(key, text, language, namespace='common'):
    """
    ذخیره یا به‌روزرسانی یک ترجمه در فایل
    
    Args:
        key (str): کلید ترجمه
        text (str): متن ترجمه
        language (str): زبان ترجمه
        namespace (str, optional): فضای نام ترجمه
    
    Returns:
        bool: موفقیت یا شکست ذخیره‌سازی
    """
    try:
        # اطمینان از بارگذاری ترجمه‌ها
        if not translations:
            load_translations()
        
        # مسیر فایل ترجمه
        file_path = os.path.join(LOCALES_DIR, language, f"{namespace}.json")
        
        # بارگذاری ترجمه‌های فعلی
        current_translations = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                current_translations = json.load(f)
        
        # اگر کلید چندبخشی با نقطه باشد، آن را بخش‌بخش در دیکشنری قرار می‌دهیم
        if '.' in key:
            parts = key.split('.')
            current = current_translations
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = text
                else:
                    if part not in current or not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]
        else:
            # کلید ساده
            current_translations[key] = text
        
        # ذخیره ترجمه‌های به‌روز شده
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(current_translations, f, ensure_ascii=False, indent=2)
        
        # به‌روزرسانی دیکشنری ترجمه‌ها در حافظه
        if namespace not in translations.get(language, {}):
            if language not in translations:
                translations[language] = {}
            translations[language][namespace] = {}
        
        translations[language][namespace] = current_translations
        
        # حذف کش
        get_translation.cache_clear()
        
        logger.info(f"Saved translation for key '{key}' in {language}/{namespace}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving translation for key '{key}' in {language}/{namespace}: {e}")
        return False


def get_language_dir(language):
    """
    تعیین جهت متن بر اساس زبان
    
    Args:
        language (str): کد زبان
    
    Returns:
        str: جهت متن ('rtl' یا 'ltr')
    """
    rtl_languages = ['fa', 'ar', 'he']
    return 'rtl' if language in rtl_languages else 'ltr'


def get_user_language(user_id=None, request=None):
    """
    تشخیص زبان کاربر از منابع مختلف
    
    Args:
        user_id (any, optional): شناسه کاربر (برای تلگرام)
        request (flask.Request, optional): درخواست HTTP (برای وب)
    
    Returns:
        str: کد زبان تشخیص داده شده
    """
    # اولویت 1: زبان ذخیره شده کاربر در دیتابیس (اگر شناسه کاربر داده شده باشد)
    if user_id:
        # این قسمت باید با دیتابیس واقعی پیاده‌سازی شود
        # فعلاً فرض می‌کنیم همه کاربران فارسی زبان هستند
        return DEFAULT_LANGUAGE
    
    # اولویت 2: زبان ذخیره شده در کوکی یا سشن (اگر درخواست HTTP داده شده باشد)
    if request:
        try:
            # بررسی کوکی
            if 'language' in request.cookies:
                lang = request.cookies.get('language')
                if lang in SUPPORTED_LANGUAGES:
                    return lang
            
            # بررسی پارامتر URL
            if 'lang' in request.args:
                lang = request.args.get('lang')
                if lang in SUPPORTED_LANGUAGES:
                    return lang
            
            # بررسی هدر Accept-Language
            if request.accept_languages:
                lang = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
                if lang:
                    return lang
        except Exception as e:
            logger.error(f"Error detecting language from request: {e}")
    
    # اولویت 3: زبان پیش‌فرض
    return DEFAULT_LANGUAGE


# ایجاد نسخه کوتاه‌تر برای راحتی استفاده
_ = get_translation

# بارگذاری ترجمه‌ها در شروع
load_translations()