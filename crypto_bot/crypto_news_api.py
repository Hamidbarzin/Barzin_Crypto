"""
ماژول API اخبار ارز دیجیتال

این ماژول برای دسترسی به API های خبری ارزهای دیجیتال استفاده می‌شود.
"""

import os
import logging
import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیم API کلید
CRYPTO_NEWS_API_KEY = os.environ.get("CRYPTO_NEWS_API_KEY", "2b2f67d9892c7942447e8c14d035da36ef2f848f")

# مسیر کش
CACHE_DIR = "data/news_cache"
NEWS_API_CACHE_FILE = f"{CACHE_DIR}/news_api_cache.json"
CACHE_EXPIRY = 60 * 30  # 30 دقیقه به ثانیه

# آدرس‌های API
API_BASE_URL = "https://cryptonews-api.com/api/v1"

def get_crypto_news_from_api(categories: List[str] = None, regions: List[str] = None, 
                             items_per_page: int = 10, page: int = 1,
                             use_cache: bool = True, ignore_cache_expiry: bool = False) -> List[Dict[str, Any]]:
    """
    دریافت اخبار ارزهای دیجیتال از API
    
    Args:
        categories (List[str]): لیست دسته‌بندی‌های اخبار (مانند "Bitcoin", "Ethereum", ...)
        regions (List[str]): لیست مناطق جغرافیایی (مانند "en", "canada", ...)
        items_per_page (int): تعداد اخبار در هر صفحه
        page (int): شماره صفحه
        use_cache (bool): استفاده از کش
        ignore_cache_expiry (bool): نادیده گرفتن زمان انقضای کش در صورت خطا
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار
    """
    cache_key = f"news_api_{'-'.join(categories or [])}-{'-'.join(regions or [])}-{page}"
    
    # بررسی کش
    if use_cache:
        cached_data = _get_cached_data(cache_key, ignore_cache_expiry)
        if cached_data:
            return cached_data
    
    # تنظیم پارامترهای API
    params = {
        'toppag': str(page),
        'items': str(items_per_page),
        'token': CRYPTO_NEWS_API_KEY
    }
    
    if categories:
        params['categories'] = ','.join(categories)
    
    if regions:
        params['regions'] = ','.join(regions)
    
    try:
        # درخواست به API
        url = f"{API_BASE_URL}/category"
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"API خبری خطا برگرداند: {response.status_code}")
            return []
        
        # پردازش پاسخ
        data = response.json()
        
        if data.get('status') != "success":
            logger.error(f"خطای API خبری: {data.get('message')}")
            return []
        
        news_items = data.get('data', [])
        
        # تبدیل به فرمت استاندارد
        standardized_news = []
        for item in news_items:
            news_item = {
                "title": item.get('title', ''),
                "url": item.get('news_url', ''),
                "source": item.get('source_name', 'Crypto News API'),
                "published_at": item.get('date', datetime.now().isoformat()),
                "summary": item.get('text', ''),
                "image_url": item.get('image_url', ''),
                "categories": item.get('categories', '').split(','),
                "sentiment": item.get('sentiment', 'neutral')
            }
            standardized_news.append(news_item)
        
        # ذخیره در کش
        _cache_data(cache_key, standardized_news)
        
        return standardized_news
    
    except Exception as e:
        logger.error(f"خطا در دریافت اخبار از API: {str(e)}")
        return []

def get_canadian_crypto_news_from_api(items_per_page: int = 10, page: int = 1, 
                                     use_cache: bool = True, ignore_cache_expiry: bool = False) -> List[Dict[str, Any]]:
    """
    دریافت اخبار ارزهای دیجیتال مربوط به کانادا از API
    
    Args:
        items_per_page (int): تعداد اخبار در هر صفحه
        page (int): شماره صفحه
        use_cache (bool): استفاده از کش
        ignore_cache_expiry (bool): نادیده گرفتن زمان انقضای کش در صورت خطا
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار
    """
    return get_crypto_news_from_api(regions=["canada"], items_per_page=items_per_page, 
                                   page=page, use_cache=use_cache, ignore_cache_expiry=ignore_cache_expiry)

def get_news_by_category_from_api(category: str, items_per_page: int = 10, page: int = 1,
                                 use_cache: bool = True, ignore_cache_expiry: bool = False) -> List[Dict[str, Any]]:
    """
    دریافت اخبار ارزهای دیجیتال بر اساس دسته‌بندی از API
    
    Args:
        category (str): دسته‌بندی اخبار (مانند "Bitcoin", "Ethereum", ...)
        items_per_page (int): تعداد اخبار در هر صفحه
        page (int): شماره صفحه
        use_cache (bool): استفاده از کش
        ignore_cache_expiry (bool): نادیده گرفتن زمان انقضای کش در صورت خطا
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار
    """
    category_map = {
        "bitcoin": ["Bitcoin", "BTC"],
        "ethereum": ["Ethereum", "ETH"],
        "defi": ["DeFi", "Decentralized Finance"],
        "nft": ["NFT", "Non-Fungible Token"],
        "regulation": ["Regulation", "Law", "SEC"],
        "trading": ["Trading", "Market"],
        "mining": ["Mining", "Miner"]
    }
    
    api_categories = category_map.get(category.lower(), [category.capitalize()])
    
    return get_crypto_news_from_api(categories=api_categories, items_per_page=items_per_page, 
                                   page=page, use_cache=use_cache, ignore_cache_expiry=ignore_cache_expiry)

def _get_cached_data(cache_key: str, ignore_expiry: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    دریافت داده‌های کش شده
    
    Args:
        cache_key (str): کلید کش
        ignore_expiry (bool): نادیده گرفتن زمان انقضای کش
        
    Returns:
        Optional[List[Dict[str, Any]]]: داده‌های کش شده یا None
    """
    try:
        if os.path.exists(NEWS_API_CACHE_FILE):
            cache_age = time.time() - os.path.getmtime(NEWS_API_CACHE_FILE)
            
            # بررسی معتبر بودن کش
            if cache_age < CACHE_EXPIRY or ignore_expiry:
                with open(NEWS_API_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    if cache_key in cache_data:
                        cache_status = "valid" if cache_age < CACHE_EXPIRY else "expired"
                        logger.info(f"داده‌های '{cache_key}' از کش {cache_status} بارگذاری شد (سن: {int(cache_age/60)} دقیقه)")
                        return cache_data[cache_key]['data']
    
    except Exception as e:
        logger.error(f"خطا در خواندن کش: {str(e)}")
    
    return None

def _cache_data(cache_key: str, data: List[Dict[str, Any]]) -> None:
    """
    ذخیره داده‌ها در کش
    
    Args:
        cache_key (str): کلید کش
        data (List[Dict[str, Any]]): داده‌ها برای ذخیره‌سازی
    """
    try:
        # ساخت دایرکتوری کش اگر وجود ندارد
        os.makedirs(os.path.dirname(NEWS_API_CACHE_FILE), exist_ok=True)
        
        # خواندن کش فعلی یا ایجاد کش جدید
        cache_data = {}
        if os.path.exists(NEWS_API_CACHE_FILE):
            with open(NEWS_API_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        
        # بروزرسانی کش
        cache_data[cache_key] = {
            'timestamp': time.time(),
            'data': data
        }
        
        # ذخیره کش
        with open(NEWS_API_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"{len(data)} خبر برای '{cache_key}' در کش ذخیره شد")
        
    except Exception as e:
        logger.error(f"خطا در ذخیره کش: {str(e)}")