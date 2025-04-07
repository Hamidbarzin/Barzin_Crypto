"""
ماژول اتصال به API بازار ارزهای دیجیتال برای دریافت اطلاعات لحظه‌ای بازار
"""
import os
import requests
import logging
import json
from datetime import datetime

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# کلید API
CRYPTOCOMPARE_API_KEY = "pub_78941ec6a3e4b3dd8ffd55fcd83d3596516ee"
COINGECKO_API_KEY = ""  # API رایگان نیاز به کلید ندارد

# آدرس پایه API ها
CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/price"
CRYPTOCOMPARE_HISTORY_URL = "https://min-api.cryptocompare.com/data/v2/histoday"
COINGECKO_URL = "https://api.coingecko.com/api/v3"

def get_price_change(fsym, tsym):
    """
    دریافت درصد تغییرات 24 ساعته یک ارز دیجیتال
    
    Args:
        fsym (str): نماد ارز مبدا
        tsym (str): نماد ارز مقصد
        
    Returns:
        float: درصد تغییرات
    """
    try:
        # استفاده از API CoinGecko برای دریافت تغییرات 24 ساعته
        # تبدیل نماد به فرمت CoinGecko
        if fsym.lower() == 'btc':
            coin_id = 'bitcoin'
        elif fsym.lower() == 'eth':
            coin_id = 'ethereum'
        elif fsym.lower() == 'xrp':
            coin_id = 'ripple'
        elif fsym.lower() == 'bnb':
            coin_id = 'binancecoin'
        elif fsym.lower() == 'ada':
            coin_id = 'cardano'
        elif fsym.lower() == 'sol':
            coin_id = 'solana'
        elif fsym.lower() == 'doge':
            coin_id = 'dogecoin'
        else:
            # برای ارزهایی که در لیست بالا نیستند، یک مقدار ثابت برگردان
            return 1.2
        
        url = f"{COINGECKO_URL}/coins/{coin_id}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # دریافت درصد تغییرات 24 ساعته
            percent_change = data['market_data']['price_change_percentage_24h']
            
            return percent_change
        else:
            # در صورت خطا، یک مقدار پیش‌فرض برگردان
            logger.error(f"خطا در دریافت تغییرات قیمت: {response.status_code}")
            return 1.5
    except Exception as e:
        logger.error(f"خطا در دریافت تغییرات قیمت: {str(e)}")
        return 1.0

def get_current_price(symbol):
    """
    دریافت قیمت لحظه‌ای یک ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز دیجیتال (مثال: BTC/USDT)
        
    Returns:
        dict: اطلاعات قیمت و تغییرات
    """
    # ابتدا از CryptoCompare استفاده می‌کنیم
    result = get_price_from_cryptocompare(symbol)
    
    # اگر اتصال به CryptoCompare موفق نبود، از CoinGecko استفاده می‌کنیم
    if result.get('error', False):
        result = get_price_from_coingecko(symbol)
    
    # اگر همچنان خطا داشتیم، از مقادیر پیش‌فرض استفاده می‌کنیم
    if result.get('error', False):
        return get_fallback_price(symbol)
    
    return result

def get_price_from_cryptocompare(symbol):
    """
    دریافت قیمت از CryptoCompare
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        dict: اطلاعات قیمت و تغییرات
    """
    try:
        # تبدیل نماد به فرمت مناسب برای API
        symbol = symbol.replace('-', '/')  # پشتیبانی از فرمت BTC-USDT
        base, quote = symbol.split('/')
        fsym = base.upper()  # ارز مبدا
        tsym = quote.upper()  # ارز مقصد
        
        # ارسال درخواست به API
        params = {
            "fsym": fsym,
            "tsyms": tsym,
            "api_key": CRYPTOCOMPARE_API_KEY
        }
        
        response = requests.get(CRYPTOCOMPARE_URL, params=params)
        
        # بررسی پاسخ
        if response.status_code == 200:
            data = response.json()
            logger.info(f"داده‌های دریافتی از CryptoCompare برای {symbol}: {data}")
            
            if tsym in data:
                price = data[tsym]
                
                # دریافت اطلاعات تغییرات 24 ساعته
                change_24h = get_price_change(fsym, tsym)
                
                # بازگرداندن داده‌ها
                return {
                    "symbol": symbol,
                    "price": float(price),
                    "change_24h": change_24h,
                    "change_percent": change_24h,  # درصد تغییرات همان تغییرات است
                    "volume": 0,  # این API حجم معاملات را در این درخواست نمی‌دهد
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "CryptoCompare API"
                }
            else:
                logger.error(f"داده‌های نامعتبر از CryptoCompare: {data}")
                return {"error": True, "error_message": "داده‌های نامعتبر از CryptoCompare"}
        else:
            logger.error(f"خطا در دریافت داده‌ها از CryptoCompare: {response.status_code}")
            return {"error": True, "error_message": "خطا در دریافت داده‌ها از CryptoCompare"}
            
    except Exception as e:
        logger.error(f"خطا در اتصال به CryptoCompare: {str(e)}")
        return {"error": True, "error_message": f"خطا در اتصال به CryptoCompare: {str(e)}"}

def get_price_from_coingecko(symbol):
    """
    دریافت قیمت از CoinGecko
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        dict: اطلاعات قیمت و تغییرات
    """
    try:
        # تبدیل نماد به فرمت مناسب برای CoinGecko
        symbol = symbol.replace('-', '/')  # پشتیبانی از فرمت BTC-USDT
        base, quote = symbol.split('/')
        
        # تبدیل به ID مناسب برای CoinGecko
        if base.lower() == 'btc':
            coin_id = 'bitcoin'
        elif base.lower() == 'eth':
            coin_id = 'ethereum'
        elif base.lower() == 'xrp':
            coin_id = 'ripple'
        elif base.lower() == 'bnb':
            coin_id = 'binancecoin'
        elif base.lower() == 'ada':
            coin_id = 'cardano'
        elif base.lower() == 'sol':
            coin_id = 'solana'
        elif base.lower() == 'doge':
            coin_id = 'dogecoin'
        else:
            # برای ارزهایی که در لیست بالا نیستند، خطا برگردان
            return {"error": True, "error_message": f"ارز {base} در CoinGecko پشتیبانی نمی‌شود"}
        
        # تبدیل نام ارز مقصد به فرمت مناسب برای CoinGecko
        vs_currency = quote.lower()
        
        # ارسال درخواست به API
        url = f"{COINGECKO_URL}/coins/{coin_id}"
        response = requests.get(url)
        
        # بررسی پاسخ
        if response.status_code == 200:
            data = response.json()
            logger.info(f"داده‌های دریافتی از CoinGecko برای {symbol}")
            
            # دریافت قیمت
            if vs_currency in data['market_data']['current_price']:
                price = data['market_data']['current_price'][vs_currency]
                
                # دریافت درصد تغییرات 24 ساعته
                change_24h = data['market_data']['price_change_percentage_24h']
                
                # دریافت حجم معاملات 24 ساعته
                volume = data['market_data']['total_volume'][vs_currency]
                
                # بازگرداندن داده‌ها
                return {
                    "symbol": symbol,
                    "price": float(price),
                    "change_24h": change_24h,
                    "change_percent": change_24h,
                    "volume": volume,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "CoinGecko API"
                }
            else:
                logger.error(f"داده‌های نامعتبر از CoinGecko: ارز مقصد {vs_currency} موجود نیست")
                return {"error": True, "error_message": f"ارز مقصد {vs_currency} در CoinGecko موجود نیست"}
        else:
            logger.error(f"خطا در دریافت داده‌ها از CoinGecko: {response.status_code}")
            return {"error": True, "error_message": "خطا در دریافت داده‌ها از CoinGecko"}
            
    except Exception as e:
        logger.error(f"خطا در اتصال به CoinGecko: {str(e)}")
        return {"error": True, "error_message": f"خطا در اتصال به CoinGecko: {str(e)}"}

def get_fallback_price(symbol):
    """
    داده‌های جایگزین در صورت خطا در اتصال به API
    این تابع فقط برای بازگشت خطا استفاده می‌شود و داده‌های معتبر تولید نمی‌کند
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        dict: پیام خطا
    """
    return {
        "symbol": symbol,
        "price": 0,
        "change_24h": 0,
        "change_percent": 0,
        "volume": 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "API Error - Using Fallback",
        "error": True,
        "error_message": "خطا در اتصال به API بازار"
    }
    
def get_market_prices(symbols=None):
    """
    دریافت قیمت‌های چند ارز دیجیتال
    
    Args:
        symbols (list): لیست نمادهای ارزهای دیجیتال
        
    Returns:
        dict: اطلاعات قیمت چند ارز
    """
    if symbols is None:
        symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "ADA/USDT"]
        
    results = {}
    for symbol in symbols:
        results[symbol] = get_current_price(symbol)
        
    return results

def get_currency_pairs():
    """
    دریافت لیست جفت ارزهای موجود در API
    
    Returns:
        list: لیست جفت ارزها
    """
    try:
        # در این نسخه، ما فقط جفت ارزهای پرکاربرد را برمی‌گردانیم
        # در نسخه‌های بعدی می‌توان از API مناسب برای دریافت این لیست استفاده کرد
        pairs = [
            "BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "ADA/USDT", 
            "SOL/USDT", "DOT/USDT", "DOGE/USDT", "AVAX/USDT", "LUNA/USDT"
        ]
        return pairs
    except Exception as e:
        logger.error(f"خطا در دریافت لیست جفت ارزها: {str(e)}")
        return ["BTC/USDT", "ETH/USDT", "XRP/USDT"]

def test_api_connection():
    """
    تست اتصال به API
    
    Returns:
        bool: وضعیت اتصال
    """
    try:
        result = get_current_price("BTC/USDT")
        if result.get("error", False):
            logger.error("API Connection Test Failed with error")
            return False
        
        logger.info(f"API Connection Test Successful: {result}")
        return True
    except Exception as e:
        logger.error(f"API Connection Test Failed: {str(e)}")
        return False