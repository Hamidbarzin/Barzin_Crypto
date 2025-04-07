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
API_KEY = "pub_78941ec6a3e4b3dd8ffd55fcd83d3596516ee"
API_SECRET = "UGKJPPFACP2VOZHZ"

# آدرس پایه API
BASE_URL = "https://min-api.cryptocompare.com/data/price"

def get_current_price(symbol):
    """
    دریافت قیمت لحظه‌ای یک ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز دیجیتال (مثال: BTC/USDT)
        
    Returns:
        dict: اطلاعات قیمت و تغییرات
    """
    try:
        # تبدیل نماد به فرمت مناسب برای API
        base, quote = symbol.split('/')
        fsym = base.upper()  # ارز مبدا
        tsym = quote.upper()  # ارز مقصد
        
        # ایجاد URL درخواست
        url = f"{BASE_URL}"
        
        # ارسال درخواست به API
        params = {
            "fsym": fsym,
            "tsyms": tsym
        }
        
        response = requests.get(url, params=params)
        
        # بررسی پاسخ
        if response.status_code == 200:
            data = response.json()
            logger.info(f"داده‌های دریافتی از API برای {symbol}: {data}")
            
            if tsym in data:
                price = data[tsym]
                
                # بازگرداندن داده‌ها
                return {
                    "symbol": symbol,
                    "price": float(price),
                    "change_24h": 0,  # این API مقدار تغییر را مستقیم نمی‌دهد در این درخواست
                    "change_percent": 0,  # این API تغییرات درصدی را در این درخواست نمی‌دهد
                    "volume": 0,  # این API حجم معاملات را در این درخواست نمی‌دهد
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "CryptoCompare API"
                }
            else:
                logger.error(f"داده‌های نامعتبر از API: {data}")
                return get_fallback_price(symbol)
        else:
            logger.error(f"خطا در دریافت داده‌ها از API: {response.status_code} - {response.text}")
            return get_fallback_price(symbol)
            
    except Exception as e:
        logger.error(f"خطا در اتصال به API بازار: {str(e)}")
        return get_fallback_price(symbol)

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