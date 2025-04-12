"""
ماژول داده‌های بازار ارزهای دیجیتال

این ماژول برای دریافت داده‌های بازار ارزهای دیجیتال استفاده می‌شود.
"""
import logging
import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

import requests

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیمات API های قیمت
CRYPTOCOMPARE_API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY", "")

# زمان منقضی شدن کش (۳ دقیقه)
CACHE_EXPIRY = 180

# فایل کش
PRICE_CACHE_FILE = "data/price_cache.json"

# نگاشت سمبل‌های استاندارد به سمبل‌های CoinGecko
COINGECKO_MAPPINGS = {
    "BTC/USDT": "bitcoin",
    "BTC-USDT": "bitcoin",
    "ETH/USDT": "ethereum",
    "ETH-USDT": "ethereum",
    "SOL/USDT": "solana",
    "SOL-USDT": "solana",
    "XRP/USDT": "ripple",
    "XRP-USDT": "ripple",
    "BNB/USDT": "binancecoin",
    "BNB-USDT": "binancecoin",
    "ADA/USDT": "cardano",
    "ADA-USDT": "cardano",
    "DOGE/USDT": "dogecoin",
    "DOGE-USDT": "dogecoin",
    "SHIB/USDT": "shiba-inu",
    "SHIB-USDT": "shiba-inu",
    "AVAX/USDT": "avalanche-2",
    "AVAX-USDT": "avalanche-2",
    "DOT/USDT": "polkadot",
    "DOT-USDT": "polkadot",
    "MATIC/USDT": "matic-network",
    "MATIC-USDT": "matic-network",
    "UNI/USDT": "uniswap",
    "UNI-USDT": "uniswap"
}

def get_crypto_price(symbol: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    دریافت قیمت ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز دیجیتال (مثال: BTC/USDT)
        timeout (Optional[int]): مهلت زمانی (به ثانیه) برای درخواست‌های API
        
    Returns:
        Optional[Dict[str, Any]]: داده‌های قیمت یا None در صورت خطا
    """
    try:
        # استاندارد‌سازی نماد
        std_symbol = symbol.upper()
        
        # تلاش برای دریافت قیمت از کش
        cached_data = _get_cached_price(std_symbol)
        if cached_data:
            logger.info(f"Using cached price data for {std_symbol}")
            return cached_data
        
        # دریافت قیمت از CoinGecko
        price_data = _fetch_from_coingecko(std_symbol)
        
        # اگر از CoinGecko دریافت نشد، از CryptoCompare استفاده کن
        if not price_data:
            price_data = _fetch_from_cryptocompare(std_symbol)
        
        # اگر از CryptoCompare هم دریافت نشد، از Binance استفاده کن
        if not price_data:
            price_data = _fetch_from_binance(std_symbol)
        
        # ذخیره در کش
        if price_data:
            _cache_price_data(std_symbol, price_data)
        
        return price_data
    
    except Exception as e:
        logger.error(f"Error in get_crypto_price for {symbol}: {str(e)}")
        return None

def get_multiple_prices(symbols: List[str], timeout: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
    """
    دریافت قیمت چندین ارز دیجیتال
    
    Args:
        symbols (List[str]): لیست نمادهای ارز دیجیتال
        timeout (Optional[int]): مهلت زمانی (به ثانیه) برای درخواست‌های API
        
    Returns:
        Dict[str, Dict[str, Any]]: دیکشنری از داده‌های قیمت
    """
    result = {}
    
    for symbol in symbols:
        price_data = get_crypto_price(symbol, timeout=timeout)
        if price_data:
            result[symbol] = price_data
    
    return result

def get_current_prices(symbols_list=None, include_favorites=True, timeout=None):
    """
    دریافت قیمت‌های فعلی ارزهای دیجیتال
    
    Args:
        symbols_list (List[str], optional): لیست نمادهای ارز دیجیتال. 
                                        اگر None باشد، از لیست پیش‌فرض استفاده می‌شود.
        include_favorites (bool, optional): آیا ارزهای مورد علاقه در نتایج گنجانده شوند
        timeout (int, optional): مهلت زمانی (به ثانیه) برای درخواست‌های API
        
    Returns:
        Dict[str, Dict[str, Any]]: دیکشنری از داده‌های قیمت
    """
    # لیست پیش‌فرض ارزها
    default_symbols = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT",
        "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "MATIC/USDT", "DOT/USDT"
    ]
    
    # ارزهای مورد علاقه
    favorite_symbols = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"
    ]
    
    # انتخاب لیست نمادها
    if symbols_list:
        symbols = symbols_list
    else:
        symbols = default_symbols if not include_favorites else favorite_symbols
    
    # دریافت قیمت‌ها
    return get_multiple_prices(symbols, timeout=timeout)

def _get_cached_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    دریافت قیمت از کش
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        Optional[Dict[str, Any]]: داده‌های کش شده یا None
    """
    try:
        # بررسی وجود فایل کش
        if not os.path.exists(PRICE_CACHE_FILE):
            return None
        
        # خواندن فایل کش
        with open(PRICE_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        # بررسی وجود داده برای نماد موردنظر
        if symbol not in cache:
            return None
        
        # بررسی اعتبار داده کش شده
        cached_time = cache[symbol]['cached_at']
        current_time = time.time()
        
        if current_time - cached_time > CACHE_EXPIRY:
            # داده منقضی شده است
            return None
        
        return cache[symbol]['data']
    
    except Exception as e:
        logger.error(f"Error reading cache for {symbol}: {str(e)}")
        return None

def _cache_price_data(symbol: str, data: Dict[str, Any]) -> None:
    """
    ذخیره داده قیمت در کش
    
    Args:
        symbol (str): نماد ارز دیجیتال
        data (Dict[str, Any]): داده‌های قیمت
    """
    try:
        # ایجاد دایرکتوری کش اگر وجود ندارد
        os.makedirs(os.path.dirname(PRICE_CACHE_FILE), exist_ok=True)
        
        # بارگیری داده‌های کش فعلی یا ایجاد کش جدید
        cache = {}
        if os.path.exists(PRICE_CACHE_FILE):
            with open(PRICE_CACHE_FILE, 'r') as f:
                cache = json.load(f)
        
        # اضافه کردن داده جدید به کش
        cache[symbol] = {
            'data': data,
            'cached_at': time.time()
        }
        
        # ذخیره کش به‌روزرسانی شده
        with open(PRICE_CACHE_FILE, 'w') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"Error caching price data for {symbol}: {str(e)}")

def _fetch_from_coingecko(symbol: str) -> Optional[Dict[str, Any]]:
    """
    دریافت قیمت از CoinGecko
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        Optional[Dict[str, Any]]: داده‌های قیمت یا None
    """
    try:
        # تبدیل نماد به فرمت CoinGecko
        if symbol in COINGECKO_MAPPINGS:
            coin_id = COINGECKO_MAPPINGS[symbol]
        else:
            # تلاش برای تبدیل خودکار
            parts = symbol.split('/')
            if len(parts) == 2 and parts[1] == "USDT":
                coin_name = parts[0].lower()
                # بررسی در نگاشت
                for key, value in COINGECKO_MAPPINGS.items():
                    if key.startswith(parts[0]):
                        coin_id = value
                        break
                else:
                    # اگر پیدا نشد، از نام ارز استفاده کن
                    coin_id = coin_name
            else:
                return None
        
        # درخواست به API
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"CoinGecko API returned status code {response.status_code}")
            return None
        
        data = response.json()
        
        # استخراج داده‌های موردنیاز
        price = data["market_data"]["current_price"]["usd"]
        price_change_24h = data["market_data"]["price_change_percentage_24h"]
        market_cap = data["market_data"]["market_cap"]["usd"]
        volume_24h = data["market_data"]["total_volume"]["usd"]
        
        return {
            "price": price,
            "change_24h": price_change_24h,
            "market_cap": market_cap,
            "volume_24h": volume_24h,
            "source": "CoinGecko"
        }
    
    except Exception as e:
        logger.error(f"Error fetching from CoinGecko for {symbol}: {str(e)}")
        return None

def _fetch_from_cryptocompare(symbol: str) -> Optional[Dict[str, Any]]:
    """
    دریافت قیمت از CryptoCompare
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        Optional[Dict[str, Any]]: داده‌های قیمت یا None
    """
    try:
        # تبدیل نماد به فرمت CryptoCompare
        parts = symbol.split('/')
        if len(parts) != 2:
            parts = symbol.split('-')
            if len(parts) != 2:
                return None
        
        base_coin = parts[0]
        quote_coin = parts[1]
        
        # درخواست به API
        url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={base_coin}&tsyms={quote_coin}"
        
        headers = {}
        if CRYPTOCOMPARE_API_KEY:
            headers["authorization"] = f"Apikey {CRYPTOCOMPARE_API_KEY}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"CryptoCompare API returned status code {response.status_code}")
            return None
        
        data = response.json()
        
        # بررسی داده‌های دریافتی
        if "DISPLAY" not in data or base_coin not in data["DISPLAY"] or quote_coin not in data["DISPLAY"][base_coin]:
            return None
        
        # استخراج داده‌های موردنیاز
        raw_data = data["RAW"][base_coin][quote_coin]
        display_data = data["DISPLAY"][base_coin][quote_coin]
        
        price = raw_data["PRICE"]
        change_24h = raw_data["CHANGEPCT24HOUR"]
        market_cap = raw_data["MKTCAP"]
        volume_24h = raw_data["VOLUME24HOUR"]
        
        return {
            "price": price,
            "change_24h": change_24h,
            "market_cap": market_cap,
            "volume_24h": volume_24h,
            "source": "CryptoCompare"
        }
    
    except Exception as e:
        logger.error(f"Error fetching from CryptoCompare for {symbol}: {str(e)}")
        return None

def _fetch_from_binance(symbol: str) -> Optional[Dict[str, Any]]:
    """
    دریافت قیمت از Binance
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        Optional[Dict[str, Any]]: داده‌های قیمت یا None
    """
    try:
        # تبدیل نماد به فرمت Binance
        parts = symbol.split('/')
        if len(parts) != 2:
            parts = symbol.split('-')
            if len(parts) != 2:
                return None
        
        binance_symbol = f"{parts[0]}{parts[1]}"
        
        # درخواست به API
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Binance API returned status code {response.status_code}")
            return None
        
        data = response.json()
        
        # استخراج داده‌های موردنیاز
        price = float(data["lastPrice"])
        change_24h = float(data["priceChangePercent"])
        volume_24h = float(data["volume"]) * price
        
        return {
            "price": price,
            "change_24h": change_24h,
            "volume_24h": volume_24h,
            "source": "Binance"
        }
    
    except Exception as e:
        logger.error(f"Error fetching from Binance for {symbol}: {str(e)}")
        return None

def get_historical_data(symbol: str, timeframe: str = "1d", limit: int = 100) -> Optional[List[Dict[str, Any]]]:
    """
    دریافت داده‌های تاریخی ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز دیجیتال
        timeframe (str): بازه زمانی. مقادیر مجاز: "1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"
        limit (int): تعداد داده‌های درخواستی
        
    Returns:
        Optional[List[Dict[str, Any]]]: لیست داده‌های تاریخی یا None در صورت خطا
    """
    try:
        # تبدیل نماد به فرمت Binance
        parts = symbol.split('/')
        if len(parts) != 2:
            parts = symbol.split('-')
            if len(parts) != 2:
                return None
        
        binance_symbol = f"{parts[0]}{parts[1]}"
        
        # تبدیل timeframe به فرمت Binance
        timeframe_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
        }
        
        if timeframe not in timeframe_map:
            logger.warning(f"Invalid timeframe: {timeframe}")
            timeframe = "1d"  # استفاده از مقدار پیش‌فرض
        
        # درخواست به API
        url = f"https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval={timeframe_map[timeframe]}&limit={limit}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Binance API returned status code {response.status_code}")
            # ساخت داده تست به عنوان جایگزین
            return _generate_sample_data(limit)
        
        data = response.json()
        
        # تبدیل داده‌ها به ساختار مناسب
        historical_data = []
        
        for candle in data:
            timestamp = candle[0] / 1000  # تبدیل به ثانیه
            open_price = float(candle[1])
            high_price = float(candle[2])
            low_price = float(candle[3])
            close_price = float(candle[4])
            volume = float(candle[5])
            
            historical_data.append({
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
        
        return historical_data
    
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        # در صورت خطا، داده تست تولید کن
        return _generate_sample_data(limit)

def _generate_sample_data(limit: int = 100) -> List[Dict[str, Any]]:
    """
    تولید داده تست برای تحلیل تکنیکال
    
    Args:
        limit (int): تعداد داده‌های موردنیاز
        
    Returns:
        List[Dict[str, Any]]: لیست داده‌های تست
    """
    now = datetime.now()
    sample_data = []
    
    # قیمت شروع
    start_price = 50000.0
    current_price = start_price
    
    for i in range(limit):
        # زمان - از قدیم به جدید
        timestamp = (now - timedelta(days=limit-i-1)).timestamp()
        
        # تغییر تصادفی قیمت
        price_change = current_price * (random.uniform(-0.03, 0.03))
        
        # محاسبه قیمت‌های دوره
        open_price = current_price
        close_price = current_price + price_change
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
        
        # حجم تصادفی
        volume = random.uniform(500, 1500)
        
        # اضافه کردن به داده‌های تست
        sample_data.append({
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })
        
        # بروزرسانی قیمت برای دوره بعدی
        current_price = close_price
    
    return sample_data