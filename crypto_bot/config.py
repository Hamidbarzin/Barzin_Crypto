"""
Configuration settings for the cryptocurrency trading bot
"""
import os

# API Keys (from environment variables with defaults for development)
# Binance API Keys
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET', '')

# KuCoin API Keys
KUCOIN_API_KEY = os.environ.get('KUCOIN_API_KEY', '')
KUCOIN_API_SECRET = os.environ.get('KUCOIN_API_SECRET', '')
KUCOIN_API_PASSPHRASE = os.environ.get('KUCOIN_API_PASSPHRASE', '')

# CoinEx API Keys
COINEX_API_KEY = os.environ.get('COINEX_API_KEY', '')
COINEX_API_SECRET = os.environ.get('COINEX_API_SECRET', '')

# Other API Keys
COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY', '')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')

# Email settings
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
# Default to SMTP2GO which is more permissive for automation
EMAIL_SERVER = os.environ.get('EMAIL_SERVER', 'mail.smtp2go.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 2525))  # SMTP2GO standard port

# Default settings
DEFAULT_CURRENCIES = [
    # ارزهای اصلی و شناخته شده
    'BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BNB/USDT', 'ADA/USDT', 
    'SOL/USDT', 'DOT/USDT', 'MATIC/USDT', 'DOGE/USDT', 'AVAX/USDT',
    
    # ارزهای با پتانسیل رشد بالا
    'ARB/USDT', 'IMX/USDT', 'LINK/USDT', 'RNDR/USDT', 'ATOM/USDT',
    
    # ارزهای جدیدتر با پتانسیل رشد
    'SUI/USDT', 'APT/USDT', 'ICP/USDT', 'SEI/USDT', 'TON/USDT', 'NEAR/USDT'
]

TIMEFRAMES = {
    '5m': '5 minutes',
    '15m': '15 minutes',
    '1h': '1 hour',
    '4h': '4 hours',
    '1d': '1 day'
}

# Technical analysis parameters
TA_SETTINGS = {
    'short_sma': 9,
    'medium_sma': 20,
    'long_sma': 50,
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9
}

# News sources
NEWS_SOURCES = [
    'cointelegraph.com',
    'coindesk.com',
    'decrypt.co',
    'cryptoslate.com',
    'bitcoinist.com',
    'ramzarz.news',
    'arzdigital.com',
    'menaherald.com'
]

# Signal thresholds - used to determine buy/sell signals
SIGNAL_THRESHOLDS = {
    'strong_buy': 0.8,
    'buy': 0.6,
    'neutral': 0.4,
    'sell': 0.3,
    'strong_sell': 0.2
}

# News sentiment analysis
POSITIVE_KEYWORDS = [
    # انگلیسی - English positive keywords
    'bullish', 'surge', 'soar', 'gain', 'rally', 'jump', 'rise', 'up', 
    'grow', 'positive', 'good', 'progress', 'adopt', 'support', 'partnership',
    'breakthrough', 'advance', 'optimistic', 'innovation', 'boost',
    'potential', 'opportunity', 'recovery', 'promising', 'successful',
    'achievement', 'milestone', 'adoption', 'momentum', 'expanding',
    
    # فارسی - Persian positive keywords
    'صعودی', 'افزایش', 'رشد', 'جهش', 'سود', 'مثبت', 'بالا', 'قوی',
    'همکاری', 'پیشرفت', 'امیدوار', 'خوب', 'عالی', 'موفق', 'سرمایه‌گذاری',
    'فرصت', 'بهبود', 'توسعه', 'قدرتمند', 'تقویت', 'اوج', 'شکوفایی', 'محبوب',
    'حمایت', 'شکستن مقاومت', 'جذب سرمایه', 'برتر', 'پتانسیل', 'دستاورد',
    'گسترش', 'بازدهی', 'سوددهی', 'ارزشمند', 'ارزنده', 'استقبال', 'موفقیت‌آمیز',
    'خوش‌بینی', 'نوآوری', 'پذیرش', 'استراتژی', 'نقدینگی', 'نویدبخش'
]

NEGATIVE_KEYWORDS = [
    # انگلیسی - English negative keywords
    'bearish', 'drop', 'fall', 'plunge', 'crash', 'decline', 'down', 
    'decrease', 'negative', 'bad', 'risk', 'ban', 'regulate', 'hack', 'scam',
    'warning', 'threat', 'concern', 'problem', 'issue', 'uncertainty',
    'volatile', 'tumble', 'weak', 'collapse', 'dump', 'sell-off', 'liquidation',
    'restriction', 'penalty', 'downturn', 'bearish', 'pressure', 'fear',
    
    # فارسی - Persian negative keywords
    'نزولی', 'کاهش', 'سقوط', 'افت', 'ریزش', 'ضرر', 'منفی', 'پایین',
    'ضعیف', 'خطر', 'ریسک', 'کلاهبرداری', 'هک', 'ممنوعیت', 'بد', 'قانون‌گذاری',
    'هشدار', 'نگرانی', 'مشکل', 'تهدید', 'شکست', 'بحران', 'بی‌ثباتی', 'محدودیت',
    'جریمه', 'رکود', 'فشار', 'ترس', 'عدم اطمینان', 'بی‌اعتمادی', 'خطرناک',
    'تحریم', 'شکستن حمایت', 'خروج سرمایه', 'فروش', 'نقدشوندگی', 'اصلاح قیمت',
    'فروش هیجانی', 'زیان', 'عرضه‌های سنگین', 'دامپ', 'حفره امنیتی', 'پرخطر'
]

# Scheduler settings
DEFAULT_ANALYSIS_INTERVAL = 30 * 60  # 30 minutes
EMAIL_FREQUENCIES = {
    'hourly': 60 * 60,  # 1 hour
    'daily': 24 * 60 * 60,  # 24 hours
    'weekly': 7 * 24 * 60 * 60  # 7 days
}

# تنظیمات پیش‌فرض برای اعلان‌های صوتی
DEFAULT_VOICE_SETTINGS = {
    'crypto': 'BTC',
    'event_type': 'price_increase',
    'price_change': 5,
    'language': 'fr',
    'voice_gender': 'male',
    'enabled': True,
    'notification_types': {
        'price_increase': True,
        'price_decrease': True,
        'target_reached': True,
        'stop_loss': True,
        'high_volatility': True
    }
}
