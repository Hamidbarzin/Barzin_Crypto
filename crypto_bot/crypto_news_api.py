"""
Cryptocurrency News API Module

This module is used to access cryptocurrency news APIs.
"""

import os
import logging
import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

# Set API key - try to get from environment variable first
CRYPTO_NEWS_API_KEY = os.environ.get("CRYPTO_NEWS_API_KEY", "")

# Check if API key is available
HAS_VALID_API_KEY = bool(CRYPTO_NEWS_API_KEY.strip())
if not HAS_VALID_API_KEY:
    logger.warning("No CRYPTO_NEWS_API_KEY found in environment variables. News API functionality will be limited.")

# Cache paths
CACHE_DIR = "data/news_cache"
NEWS_API_CACHE_FILE = f"{CACHE_DIR}/news_api_cache.json"
CACHE_EXPIRY = 60 * 30  # 30 minutes in seconds

# API URLs
API_BASE_URL = "https://cryptonews-api.com/api/v1"

def get_crypto_news_from_api(categories: List[str] = None, regions: List[str] = None, 
                             items_per_page: int = 10, page: int = 1,
                             use_cache: bool = True, ignore_cache_expiry: bool = False) -> List[Dict[str, Any]]:
    """
    Get cryptocurrency news from API
    
    Args:
        categories (List[str]): List of news categories (such as "Bitcoin", "Ethereum", ...)
        regions (List[str]): List of geographic regions (such as "en", "canada", ...)
        items_per_page (int): Number of news items per page
        page (int): Page number
        use_cache (bool): Use cache
        ignore_cache_expiry (bool): Ignore cache expiry time in case of error
        
    Returns:
        List[Dict[str, Any]]: List of news items
    """
    cache_key = f"news_api_{'-'.join(categories or [])}-{'-'.join(regions or [])}-{page}"
    
    # Check cache
    if use_cache:
        cached_data = _get_cached_data(cache_key, ignore_cache_expiry)
        if cached_data:
            return cached_data
    
    # Check if we have a valid API key
    if not HAS_VALID_API_KEY:
        logger.warning("Cannot fetch news from API: No API key available")
        return []
    
    # Setup API parameters
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
        # Request to API
        url = f"{API_BASE_URL}/category"
        logger.info(f"Fetching news from {url} with categories={categories} and regions={regions}")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"News API returned error: {response.status_code}")
            return []
        
        # Process response
        data = response.json()
        
        if data.get('status') != "success":
            logger.error(f"News API error: {data.get('message')}")
            return []
        
        news_items = data.get('data', [])
        
        # Convert to standard format
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
        
        # Store in cache
        _cache_data(cache_key, standardized_news)
        
        return standardized_news
    
    except Exception as e:
        logger.error(f"Error getting news from API: {str(e)}")
        return []

def get_canadian_crypto_news_from_api(items_per_page: int = 10, page: int = 1, 
                                     use_cache: bool = True, ignore_cache_expiry: bool = False) -> List[Dict[str, Any]]:
    """
    Get cryptocurrency news related to Canada from API
    
    Args:
        items_per_page (int): Number of news items per page
        page (int): Page number
        use_cache (bool): Use cache
        ignore_cache_expiry (bool): Ignore cache expiry time in case of error
        
    Returns:
        List[Dict[str, Any]]: List of news items
    """
    return get_crypto_news_from_api(regions=["canada"], items_per_page=items_per_page, 
                                   page=page, use_cache=use_cache, ignore_cache_expiry=ignore_cache_expiry)

def get_news_by_category_from_api(category: str, items_per_page: int = 10, page: int = 1,
                                 use_cache: bool = True, ignore_cache_expiry: bool = False) -> List[Dict[str, Any]]:
    """
    Get cryptocurrency news by category from API
    
    Args:
        category (str): News category (such as "Bitcoin", "Ethereum", ...)
        items_per_page (int): Number of news items per page
        page (int): Page number
        use_cache (bool): Use cache
        ignore_cache_expiry (bool): Ignore cache expiry time in case of error
        
    Returns:
        List[Dict[str, Any]]: List of news items
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
    Get cached data
    
    Args:
        cache_key (str): Cache key
        ignore_expiry (bool): Ignore cache expiry time
        
    Returns:
        Optional[List[Dict[str, Any]]]: Cached data or None
    """
    try:
        if os.path.exists(NEWS_API_CACHE_FILE):
            cache_age = time.time() - os.path.getmtime(NEWS_API_CACHE_FILE)
            
            # Check cache validity
            if cache_age < CACHE_EXPIRY or ignore_expiry:
                with open(NEWS_API_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    if cache_key in cache_data:
                        cache_status = "valid" if cache_age < CACHE_EXPIRY else "expired"
                        logger.info(f"Data for '{cache_key}' loaded from {cache_status} cache (age: {int(cache_age/60)} minutes)")
                        return cache_data[cache_key]['data']
    
    except Exception as e:
        logger.error(f"Error reading cache: {str(e)}")
    
    return None

def _cache_data(cache_key: str, data: List[Dict[str, Any]]) -> None:
    """
    Store data in cache
    
    Args:
        cache_key (str): Cache key
        data (List[Dict[str, Any]]): Data to be stored
    """
    try:
        # Create cache directory if it doesn't exist
        os.makedirs(os.path.dirname(NEWS_API_CACHE_FILE), exist_ok=True)
        
        # Read existing cache or create a new one
        cache_data = {}
        if os.path.exists(NEWS_API_CACHE_FILE):
            with open(NEWS_API_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        
        # Update cache
        cache_data[cache_key] = {
            'timestamp': time.time(),
            'data': data
        }
        
        # Save cache
        with open(NEWS_API_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"{len(data)} news items for '{cache_key}' stored in cache")
        
    except Exception as e:
        logger.error(f"Error storing cache: {str(e)}")