#!/usr/bin/env python3
"""
سیستم مدیریت زبان برای برنامه

این ماژول تنظیمات و توابع لازم برای پشتیبانی چندزبانگی در برنامه را فراهم می‌کند.
"""

import os
from typing import Dict, Any, List

# زبان‌های پشتیبانی شده
SUPPORTED_LANGUAGES = {
    'fa': {
        'name': 'فارسی',
        'direction': 'rtl',
        'flag': '🇮🇷'
    },
    'en': {
        'name': 'English',
        'direction': 'ltr',
        'flag': '🇬🇧'
    }
}

# زبان پیش‌فرض
DEFAULT_LANGUAGE = 'fa'

# ترجمه‌های متن‌های رابط کاربری
UI_TRANSLATIONS = {
    'fa': {
        'title': 'Crypto Barzin',
        'dashboard': 'داشبورد',
        'cryptocurrencies': 'ارزهای دیجیتال',
        'price_alerts': 'هشدارهای قیمت',
        'news': 'اخبار',
        'telegram_control': 'کنترل تلگرام',
        'voice_notification': 'اعلان‌های صوتی',
        'settings': 'تنظیمات',
        
        # برچسب‌های منوی موبایل
        'mobile_cryptocurrencies': 'ارزها',
        'mobile_alerts': 'هشدارها',
        'mobile_news': 'اخبار',
        'mobile_telegram': 'تلگرام',
        
        # ترجمه‌های مربوط به تغییر زبان
        'language_settings': 'تنظیمات زبان',
        'current_language': 'زبان فعلی',
        'language_changed': 'زبان به {language_name} تغییر یافت.',
        'language_change_error': 'کد زبان نامعتبر است.',
        'language_persian': 'فارسی (راست به چپ)',
        'language_english': 'انگلیسی (چپ به راست)',
        'app_language': 'زبان برنامه',
        
        # منوی اصلی
        'home': 'خانه',
        'help': 'راهنما',
        'about': 'درباره ما',
        
        # داشبورد
        'market_overview': 'نمای کلی بازار',
        'top_currencies': 'ارزهای برتر',
        'price_changes': 'تغییرات قیمت',
        'market_cap': 'ارزش بازار',
        
        # نام ارزهای دیجیتال
        'bitcoin': 'بیت‌کوین',
        'ethereum': 'اتریوم',
        'ripple': 'ریپل',
        'solana': 'سولانا',
        'binance_coin': 'بایننس کوین',
        'tether': 'تتر',
        'chainlink': 'چین‌لینک',
        'avax': 'آواکس',
        'render': 'رندر',
        'fetch': 'فچر',
        'worldcoin': 'ورلدکوین',
        'polygon': 'پلیگان',
        'arbitrum': 'آربیتروم',
        'optimism': 'اپتیمیسم',
        'technical_analysis': 'تحلیل تکنیکال',
        'technical_analysis_bitcoin': 'تحلیل تکنیکال بیت‌کوین (تایم‌فریم ساعتی)',
        'trading_signals': 'سیگنال‌های معاملاتی',
        'btc_hourly_chart': 'نمودار قیمت BTC/USDT',
        
        # سیگنال‌های معاملاتی
        'buy': 'خرید',
        'sell': 'فروش',
        'strong_buy': 'خرید قوی',
        'strong_sell': 'فروش قوی',
        'hold': 'نگهداری',
        'wait': 'انتظار',
        
        # صفحه هشدارهای قیمت
        'add_alert': 'افزودن هشدار',
        'alert_type': 'نوع هشدار',
        'price_target': 'قیمت هدف',
        'alert_status': 'وضعیت هشدار',
        'active': 'فعال',
        'inactive': 'غیرفعال',
        'delete': 'حذف',
        'save': 'ذخیره',
        'cancel': 'انصراف',
        
        # اعلان‌های صوتی
        'voice_notification_title': 'اعلان صوتی چندزبانه',
        'voice_settings': 'تنظیمات اعلان',
        'preview_sound': 'پیش‌نمایش صدا',
        'notification_history': 'تاریخچه اعلان‌ها',
        'crypto': 'ارز دیجیتال',
        'event_type': 'نوع رویداد',
        'price_change': 'میزان تغییر قیمت',
        'language': 'زبان اعلان',
        'voice_gender': 'جنسیت صدا',
        'male': 'مرد',
        'female': 'زن',
        'preview': 'پیش‌نمایش صدا',
        'save_settings': 'ذخیره تنظیمات',
        'no_history': 'تاریخچه‌ای موجود نیست',
        'price_increase': 'افزایش قیمت',
        'price_decrease': 'کاهش قیمت',
        'target_reached': 'رسیدن به قیمت هدف',
        'stop_loss': 'رسیدن به حد ضرر',
        'high_volatility': 'نوسان بالا',
        
        # اطلاعات قیمت و معاملات
        'current_price': 'قیمت فعلی',
        'suggested_volume': 'حجم پیشنهادی',
        'take_profit': 'حد سود',
        'stop_loss': 'حد ضرر',
        'monitoring_level': 'سطح نظارت',
        'price_target_bullish': 'هدف قیمتی (صعودی)',
        'price_target_bearish': 'هدف قیمتی (نزولی)',
        'share': 'اشتراک‌گذاری',
        'set_alert': 'تنظیم هشدار',
        'show_signals_directly': 'نمایش مستقیم سیگنال‌ها',
        'show_technical_directly': 'نمایش مستقیم تحلیل تکنیکال',
        
        # توضیحات سیگنال‌ها
        'eth_sell_signal': 'اتریوم در نزدیکی مقاومت کلیدی قرار گرفته و شاخص‌های تکنیکال نشان‌دهنده اشباع خرید هستند. RSI بالای ۷۰ قرار دارد و الگوی واگرایی منفی با MACD مشاهده می‌شود. احتمال اصلاح قیمت وجود دارد.',
        'sol_buy_signal': 'سولانا در حال شکستن یک الگوی مقاومتی کلیدی است و با حجم معاملات بالا در حال حرکت است. میانگین‌های متحرک حمایت قوی را نشان می‌دهند و پتانسیل رشد قابل توجهی وجود دارد.',
        'bnb_wait_signal': 'بایننس کوین در یک محدوده قیمتی باریک در حال معامله است. در صورت شکست سطح مقاومت ۵۸۰ دلار، سیگنال خرید فعال می‌شود. پیشنهاد می‌شود تا زمان شکست این سطح، معامله‌ای انجام نشود.',
        'signal_validity': 'ایجاد شده: امروز {time} | اعتبار: {hours} ساعت',
        
        # عمومی
        'loading': 'در حال بارگذاری...',
        'loading_technical_analysis': 'در حال بارگذاری تحلیل تکنیکال...',
        'loading_trading_signals': 'در حال بارگذاری سیگنال‌های معاملاتی...',
        'loading_news': 'در حال بارگذاری اخبار...',
        'error': 'خطا',
        'success': 'موفقیت',
        'warning': 'هشدار',
        'info': 'اطلاعات',
        'search': 'جستجو',
        'play': 'پخش',
        'download': 'دانلود',
        'close': 'بستن',
    },
    'en': {
        'title': 'Crypto Barzin',
        'dashboard': 'Dashboard',
        'cryptocurrencies': 'Cryptocurrencies',
        'price_alerts': 'Price Alerts',
        'news': 'News',
        'telegram_control': 'Telegram Control',
        'voice_notification': 'Voice Notifications',
        'settings': 'Settings',
        
        # Mobile menu labels
        'mobile_cryptocurrencies': 'Crypto',
        'mobile_alerts': 'Alerts',
        'mobile_news': 'News',
        'mobile_telegram': 'Telegram',
        
        # Language change translations
        'language_settings': 'Language Settings',
        'current_language': 'Current Language',
        'language_changed': 'Language changed to {language_name}.',
        'language_change_error': 'Invalid language code.',
        'language_persian': 'Persian (Right to Left)',
        'language_english': 'English (Left to Right)',
        'app_language': 'Application Language',
        
        # Main Menu
        'home': 'Home',
        'help': 'Help',
        'about': 'About',
        
        # Dashboard
        'market_overview': 'Market Overview',
        'top_currencies': 'Top Currencies',
        'price_changes': 'Price Changes',
        'market_cap': 'Market Cap',
        
        # Cryptocurrency names
        'bitcoin': 'Bitcoin',
        'ethereum': 'Ethereum',
        'ripple': 'Ripple',
        'solana': 'Solana',
        'binance_coin': 'Binance Coin',
        'tether': 'Tether',
        'chainlink': 'Chainlink',
        'avax': 'Avalanche',
        'render': 'Render',
        'fetch': 'Fetch.ai',
        'worldcoin': 'Worldcoin',
        'polygon': 'Polygon',
        'arbitrum': 'Arbitrum',
        'optimism': 'Optimism',
        'technical_analysis': 'Technical Analysis',
        'technical_analysis_bitcoin': 'Bitcoin Technical Analysis (Hourly Timeframe)',
        'trading_signals': 'Trading Signals',
        'btc_hourly_chart': 'BTC/USDT Price Chart',
        
        # Trading signals
        'buy': 'Buy',
        'sell': 'Sell',
        'strong_buy': 'Strong Buy',
        'strong_sell': 'Strong Sell',
        'hold': 'Hold',
        'wait': 'Wait',
        
        # Price Alerts Page
        'add_alert': 'Add Alert',
        'alert_type': 'Alert Type',
        'price_target': 'Price Target',
        'alert_status': 'Alert Status',
        'active': 'Active',
        'inactive': 'Inactive',
        'delete': 'Delete',
        'save': 'Save',
        'cancel': 'Cancel',
        
        # Voice Notifications
        'voice_notification_title': 'Multilingual Voice Notification',
        'voice_settings': 'Notification Settings',
        'preview_sound': 'Sound Preview',
        'notification_history': 'Notification History',
        'crypto': 'Cryptocurrency',
        'event_type': 'Event Type',
        'price_change': 'Price Change',
        'language': 'Language',
        'voice_gender': 'Voice Gender',
        'male': 'Male',
        'female': 'Female',
        'preview': 'Preview Sound',
        'save_settings': 'Save Settings',
        'no_history': 'No history available',
        'price_increase': 'Price Increase',
        'price_decrease': 'Price Decrease',
        'target_reached': 'Target Price Reached',
        'stop_loss': 'Stop Loss Reached',
        'high_volatility': 'High Volatility',
        
        # Price and Trading Information
        'current_price': 'Current Price',
        'suggested_volume': 'Suggested Volume',
        'take_profit': 'Take Profit',
        'stop_loss': 'Stop Loss',
        'monitoring_level': 'Monitoring Level',
        'price_target_bullish': 'Price Target (Bullish)',
        'price_target_bearish': 'Price Target (Bearish)',
        'share': 'Share',
        'set_alert': 'Set Alert',
        'show_signals_directly': 'Show Signals Directly',
        'show_technical_directly': 'Show Technical Analysis Directly',
        
        # Signal descriptions
        'eth_sell_signal': 'Ethereum is near a key resistance level and technical indicators show overbought conditions. RSI is above 70 and a negative divergence pattern with MACD is observed. A price correction is likely.',
        'sol_buy_signal': 'Solana is breaking through a key resistance pattern with high trading volume. Moving averages show strong support and there is significant growth potential.',
        'bnb_wait_signal': 'Binance Coin is trading in a narrow price range. If it breaks the $580 resistance level, a buy signal will be activated. It is recommended not to trade until this level is broken.',
        'signal_validity': 'Created: Today {time} | Valid for: {hours} hours',
        
        # General
        'loading': 'Loading...',
        'loading_technical_analysis': 'Loading Technical Analysis...',
        'loading_trading_signals': 'Loading Trading Signals...',
        'loading_news': 'Loading News...',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Information',
        'search': 'Search',
        'play': 'Play',
        'download': 'Download',
        'close': 'Close',
    }
}

def get_language_code(language_code: str = "") -> str:
    """
    دریافت کد زبان معتبر
    
    Args:
        language_code (str, optional): کد زبان درخواستی
        
    Returns:
        str: کد زبان معتبر
    """
    if language_code and language_code in SUPPORTED_LANGUAGES:
        return language_code
    return DEFAULT_LANGUAGE


def get_ui_text(language_code: str, key: str, default: str = "") -> str:
    """
    دریافت متن ترجمه شده برای رابط کاربری
    
    Args:
        language_code (str): کد زبان
        key (str): کلید متن
        default (str, optional): متن پیش‌فرض در صورت عدم وجود ترجمه
        
    Returns:
        str: متن ترجمه شده
    """
    language = get_language_code(language_code)
    if key in UI_TRANSLATIONS.get(language, {}):
        return UI_TRANSLATIONS[language][key]
    
    # اگر ترجمه وجود نداشت، از متن پیش‌فرض یا کلید استفاده کن
    return default or key


def get_language_info(language_code: str = "") -> Dict[str, Any]:
    """
    دریافت اطلاعات زبان
    
    Args:
        language_code (str, optional): کد زبان
        
    Returns:
        Dict[str, Any]: اطلاعات زبان
    """
    language = get_language_code(language_code)
    return SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])


def get_all_languages() -> List[Dict[str, Any]]:
    """
    دریافت لیست تمام زبان‌های پشتیبانی شده
    
    Returns:
        List[Dict[str, Any]]: لیست زبان‌ها
    """
    result = []
    for code, info in SUPPORTED_LANGUAGES.items():
        language_info = info.copy()
        language_info['code'] = code
        result.append(language_info)
    return result