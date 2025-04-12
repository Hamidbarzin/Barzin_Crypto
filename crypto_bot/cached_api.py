"""
API با حافظه نهان (Cached API) برای بهبود سرعت و کاهش درخواست‌های شبکه

این ماژول شامل توابعی برای دریافت داده‌های API با استفاده از سیستم حافظه نهان (cache)
است که به کاهش تعداد درخواست‌های شبکه و افزایش سرعت بارگذاری صفحات کمک می‌کند.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from crypto_bot.cache_manager import price_cache
from crypto_bot import market_data
from crypto_bot import market_api

logger = logging.getLogger(__name__)

def get_cached_price(symbol: str, max_age_seconds: int = 180) -> Tuple[Dict[str, Any], bool]:
    """
    دریافت قیمت از حافظه نهان یا API
    
    Args:
        symbol: نماد ارز دیجیتال
        max_age_seconds: حداکثر سن مجاز داده در حافظه نهان (ثانیه)
        
    Returns:
        داده قیمت و آیا از حافظه نهان بود
    """
    cache_key = f"price_{symbol.upper()}"
    
    # بررسی حافظه نهان
    cached_data = price_cache.get(cache_key)
    if cached_data:
        logger.debug(f"Using cached price data for {symbol}")
        return cached_data, True
    
    # دریافت از API
    symbol_formats = []
    
    # فرمت‌های مختلف را امتحان کنید
    if '/' in symbol:
        symbol_formats.append(symbol)
        symbol_formats.append(symbol.replace('/', '-'))
    elif '-' in symbol:
        symbol_formats.append(symbol)
        symbol_formats.append(symbol.replace('-', '/'))
    else:
        # برای نمادهای ساده مانند "BTC"، هر دو BTC/USDT و BTC-USDT را امتحان کنید
        symbol_formats.append(f"{symbol}/USDT")
        symbol_formats.append(f"{symbol}-USDT")
    
    logger.info(f"Trying to get prices for symbols: {symbol_formats}")
    
    # دریافت داده قیمت برای نماد
    try:
        price_data = market_data.get_price_data(symbol_formats, timeout=2)
        
        # یافتن اولین فرمت نماد که داده برگرداند
        found_symbol = None
        for sym in symbol_formats:
            if sym in price_data:
                found_symbol = sym
                break
        
        if found_symbol:
            logger.info(f"Found price data for {found_symbol}")
            
            result = {
                'price': price_data[found_symbol]['price'],
                'change_24h': price_data[found_symbol]['change_24h'] if price_data[found_symbol]['change_24h'] is not None else 0,
                'source': price_data[found_symbol].get('source', 'api'),
                'timestamp': time.time()
            }
            
            # ذخیره در حافظه نهان
            price_cache.set(cache_key, result, ttl_seconds=max_age_seconds)
            
            return result, False
    except Exception as e:
        logger.error(f"Error fetching API price for {symbol}: {str(e)}")
    
    # اگر به اینجا رسیدیم، هیچ داده‌ای نیافتیم
    return {}, False

def get_cached_prices(symbols: List[str], max_age_seconds: int = 180) -> Dict[str, Any]:
    """
    دریافت قیمت‌های چندین ارز دیجیتال با استفاده از حافظه نهان
    
    Args:
        symbols: لیست نمادهای ارز دیجیتال
        max_age_seconds: حداکثر سن مجاز داده در حافظه نهان (ثانیه)
        
    Returns:
        دیکشنری از نمادها و قیمت‌ها
    """
    result = {}
    
    # ابتدا همه داده‌های حافظه نهان را دریافت کنید
    cache_keys = [f"price_{s.upper()}" for s in symbols]
    cached_data = price_cache.get_multiple(cache_keys)
    
    # برای هر نماد، داده را از حافظه نهان یا API دریافت کنید
    for i, symbol in enumerate(symbols):
        cache_key = cache_keys[i]
        
        if cache_key in cached_data:
            logger.debug(f"Using cached price data for {symbol}")
            result[symbol] = cached_data[cache_key]
        else:
            # برای نمادهای بدون حافظه نهان، از API دریافت کنید
            data, _ = get_cached_price(symbol, max_age_seconds)
            if data:
                result[symbol] = data
    
    return result

def get_special_coin_price(coin: str, max_age_seconds: int = 180) -> Tuple[Dict[str, Any], bool]:
    """
    دریافت قیمت ارزهای دیجیتال خاص (میم کوین‌ها، هوش مصنوعی، کم هزینه)
    
    Args:
        coin: نام ارز دیجیتال
        max_age_seconds: حداکثر سن مجاز داده در حافظه نهان (ثانیه)
        
    Returns:
        داده قیمت و آیا از حافظه نهان بود
    """
    cache_key = f"price_{coin.upper()}/USDT"
    
    # بررسی حافظه نهان
    cached_data = price_cache.get(cache_key)
    if cached_data:
        logger.debug(f"Using cached price data for special coin {coin}")
        return cached_data, True
    
    # دریافت از API
    try:
        result = market_api.get_price_from_cryptocompare(f"{coin}/USDT")
        
        # اگر نتیجه معتبر دریافت کردیم، آن را برگردانید
        if not result.get('error', False) and 'price' in result:
            logger.info(f"Using CryptoCompare direct API for {coin}")
            
            # افزودن change_24h پیش‌فرض اگر وجود نداشته باشد
            if 'change_24h' not in result:
                result['change_24h'] = 0
            
            # ذخیره در حافظه نهان
            price_cache.set(cache_key, result, ttl_seconds=max_age_seconds)
            
            return result, False
    except Exception as e:
        logger.error(f"Error fetching special coin price for {coin}: {str(e)}")
    
    # اگر به اینجا رسیدیم، هیچ داده‌ای نیافتیم
    return {}, False