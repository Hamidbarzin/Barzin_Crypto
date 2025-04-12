"""
اسکنر اخبار ارزهای دیجیتال

این ماژول اخبار ارزهای دیجیتال را از منابع مختلف جمع‌آوری می‌کند،
آنها را خلاصه می‌کند و نتایج را برای استفاده در ربات تلگرام و وب‌سایت ذخیره می‌کند.
"""
import json
import logging
import os
import random
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import requests
import trafilatura
from bs4 import BeautifulSoup

# اضافه کردن ماژول جدید API اخبار
try:
    from crypto_bot.crypto_news_api import (
        get_crypto_news_from_api,
        get_canadian_crypto_news_from_api,
        get_news_by_category_from_api
    )
    HAS_NEWS_API = True
except ImportError:
    HAS_NEWS_API = False

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تعریف منابع اخبار
NEWS_SOURCES = [
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/tag/canada/",
        "type": "web",
        "selector": "article"
    },
    {
        "name": "Decrypt",
        "url": "https://decrypt.co/news",
        "type": "web",
        "selector": ".media-card"
    },
    {
        "name": "CryptoSlate",
        "url": "https://cryptoslate.com/news/",
        "type": "web",
        "selector": ".jeg_post"
    },
    {
        "name": "CoinTelegraph",
        "url": "https://cointelegraph.com/tags/canada",
        "type": "web",
        "selector": ".article"
    },
    {
        "name": "The Globe and Mail - Crypto",
        "url": "https://www.theglobeandmail.com/investing/",
        "type": "web",
        "selector": ".c-card"
    }
]

# مسیر فایل کش برای ذخیره اخبار
CACHE_FILE = "data/news_cache.json"
CACHE_EXPIRY = 60 * 60  # 1 ساعت به ثانیه

def get_combined_news(max_items=10, use_cache=True, ignore_cache_expiry=False):
    """
    دریافت اخبار ترکیبی از تمامی منابع

    Args:
        max_items (int): حداکثر تعداد اخبار برای هر منبع
        use_cache (bool): استفاده از کش
        ignore_cache_expiry (bool): نادیده گرفتن زمان انقضای کش در صورت خطا

    Returns:
        list: لیست اخبار ترکیبی
    """
    try:
        # بررسی داده‌های کش شده
        if use_cache and os.path.exists(CACHE_FILE):
            cache_age = time.time() - os.path.getmtime(CACHE_FILE)
            
            # استفاده از کش معتبر یا نادیده گرفتن انقضا اگر درخواست شده باشد
            if cache_age < CACHE_EXPIRY or ignore_cache_expiry:
                try:
                    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                        cached_news = json.load(f)
                        cache_status = "valid" if cache_age < CACHE_EXPIRY else "expired"
                        logger.info(f"Loaded {len(cached_news)} news items from {cache_status} cache (age: {int(cache_age/60)} min)")
                        
                        # اضافه کردن نشانگر برای اخبار منقضی شده
                        if cache_age >= CACHE_EXPIRY:
                            for news in cached_news:
                                if "is_stale" not in news:
                                    news["is_stale"] = True
                                    
                        return cached_news
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading cache file: {str(e)}")
                    # ادامه به جمع‌آوری اخبار جدید در صورت خطا در خواندن کش

        # جمع‌آوری اخبار از همه منابع
        combined_news = []
        error_count = 0
        
        for source in NEWS_SOURCES:
            try:
                # استخراج اخبار از منبع
                if source["type"] == "rss":
                    news_items = fetch_rss_news(source, max_items)
                else:
                    news_items = fetch_web_news(source, max_items)
                
                combined_news.extend(news_items)
                logger.info(f"Fetched {len(news_items)} news items from {source['name']}")
            except Exception as e:
                error_count += 1
                logger.error(f"Error fetching news from {source['name']}: {str(e)}")
        
        # اگر هیچ خبری جمع‌آوری نشد و خطاها وجود داشت، از کش منقضی استفاده کن
        if not combined_news and error_count > 0 and os.path.exists(CACHE_FILE) and not ignore_cache_expiry:
            logger.warning("No news fetched and errors occurred. Trying to use expired cache.")
            return get_combined_news(max_items, use_cache=True, ignore_cache_expiry=True)
            
        # اگر اخبار جمع‌آوری شد، آنها را مرتب‌سازی و ذخیره کن
        if combined_news:
            # مرتب‌سازی براساس زمان (جدیدترین اخبار اول)
            combined_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
            
            # محدود کردن به تعداد مشخص
            combined_news = combined_news[:max_items]
            
            # ذخیره در کش (فقط اگر اخبار جدید داریم)
            try:
                os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(combined_news, f, ensure_ascii=False, indent=2)
                logger.info(f"Cached {len(combined_news)} news items")
            except Exception as cache_err:
                logger.error(f"Error caching news data: {str(cache_err)}")
        
        return combined_news
    
    except Exception as e:
        logger.error(f"Error in get_combined_news: {str(e)}")
        
        # در صورت خطا، تلاش برای استفاده از کش قدیمی
        if not ignore_cache_expiry and os.path.exists(CACHE_FILE):
            logger.warning("Error occurred. Trying to use any available cache regardless of age.")
            return get_combined_news(max_items, use_cache=True, ignore_cache_expiry=True)
            
        # اگر هیچ کشی در دسترس نبود یا خطا در خواندن کش وجود داشت، آرایه خالی برگردان
        return []

def fetch_rss_news(source, max_items=5):
    """
    دریافت اخبار از فید RSS

    Args:
        source (dict): اطلاعات منبع خبری
        max_items (int): حداکثر تعداد اخبار

    Returns:
        list: لیست اخبار
    """
    try:
        import feedparser
        
        feed = feedparser.parse(source["url"])
        news_items = []
        
        for i, entry in enumerate(feed.entries[:max_items]):
            # استخراج اطلاعات خبر
            news_item = {
                "title": entry.title,
                "url": entry.link,
                "summary": entry.summary if hasattr(entry, "summary") else "",
                "published_at": entry.published if hasattr(entry, "published") else datetime.now().isoformat(),
                "source": source["name"]
            }
            
            news_items.append(news_item)
        
        return news_items
    
    except Exception as e:
        logger.error(f"Error in fetch_rss_news for {source['name']}: {str(e)}")
        return []

def fetch_web_news(source, max_items=5):
    """
    دریافت اخبار از وب‌سایت

    Args:
        source (dict): اطلاعات منبع خبری
        max_items (int): حداکثر تعداد اخبار

    Returns:
        list: لیست اخبار
    """
    try:
        # دریافت صفحه وب
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # افزایش تایم‌اوت و مدیریت خطاهای اتصال
        try:
            response = requests.get(
                source["url"], 
                headers=headers, 
                timeout=15,  # افزایش تایم‌اوت
                allow_redirects=True  # اجازه دادن به تغییر مسیر
            )
        except requests.RequestException as e:
            logger.error(f"Network error fetching {source['name']}: {str(e)}")
            return []
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {source['name']}: {response.status_code}")
            return []
        
        # استخراج اخبار
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.select(source["selector"])
        
        if not articles:
            logger.warning(f"No articles found for {source['name']} using selector: {source['selector']}")
            # تلاش با selector‌های عمومی اگر selector اصلی کار نکرد
            backup_selectors = ["article", ".article", ".post", ".news-item", ".card"]
            for backup_selector in backup_selectors:
                articles = soup.select(backup_selector)
                if articles:
                    logger.info(f"Found articles with backup selector {backup_selector} for {source['name']}")
                    break
        
        news_items = []
        for i, article in enumerate(articles[:max_items]):
            try:
                # استخراج لینک
                link_element = article.find("a")
                if not link_element:
                    continue
                
                url = link_element.get("href", "")
                if not url.startswith("http"):
                    # اضافه کردن دامنه به URL های نسبی
                    try:
                        domain = re.match(r"https?://[^/]+", source["url"]).group(0)
                        url = f"{domain}{url if url.startswith('/') else '/' + url}"
                    except (AttributeError, TypeError):
                        # اگر regex مطابقت نکرد، از URL اصلی استفاده کن
                        parts = source["url"].split('/')
                        domain = '/'.join(parts[:3])  # http(s)://domain.com
                        url = f"{domain}{url if url.startswith('/') else '/' + url}"
                
                # استخراج عنوان
                title_element = article.find("h2") or article.find("h3") or link_element
                title = title_element.get_text().strip() if title_element else "No title"
                
                # استخراج تصویر
                img_element = article.find("img")
                image_url = ""
                if img_element and img_element.has_attr("src"):
                    image_url = img_element.attrs["src"]
                    if not image_url.startswith("http"):
                        try:
                            domain = re.match(r"https?://[^/]+", source["url"]).group(0)
                            image_url = f"{domain}{image_url if image_url.startswith('/') else '/' + image_url}"
                        except (AttributeError, TypeError):
                            parts = source["url"].split('/')
                            domain = '/'.join(parts[:3])  # http(s)://domain.com
                            image_url = f"{domain}{image_url if image_url.startswith('/') else '/' + image_url}"
                
                # ساخت آیتم خبری
                news_item = {
                    "title": title,
                    "url": url,
                    "image_url": image_url,
                    "summary": "",  # در ابتدا خالی، پس از نیاز خلاصه تولید می‌شود
                    "published_at": datetime.now().isoformat(),
                    "source": source["name"]
                }
                
                news_items.append(news_item)
            
            except Exception as e:
                logger.error(f"Error processing article from {source['name']}: {str(e)}")
        
        return news_items
    
    except Exception as e:
        logger.error(f"Error in fetch_web_news for {source['name']}: {str(e)}")
        return []

def get_canadian_crypto_news(max_items=5, use_cache=True, ignore_cache_expiry=False):
    """
    دریافت اخبار ارزهای دیجیتال مربوط به کانادا

    Args:
        max_items (int): حداکثر تعداد اخبار
        use_cache (bool): استفاده از کش
        ignore_cache_expiry (bool): نادیده گرفتن زمان انقضای کش در صورت خطا

    Returns:
        list: لیست اخبار کانادایی
    """
    try:
        # ابتدا سعی کنید با استفاده از API خبری جدید، اخبار کانادایی را دریافت کنید
        if HAS_NEWS_API:
            try:
                logger.info("Getting Canadian crypto news from the new API")
                api_news = get_canadian_crypto_news_from_api(max_items, use_cache=use_cache, ignore_cache_expiry=ignore_cache_expiry)
                if api_news:
                    logger.info(f"Received {len(api_news)} Canadian crypto news items from API")
                    return api_news
                else:
                    logger.warning("No Canadian crypto news received from API, falling back to web scraping")
            except Exception as api_err:
                logger.error(f"Error getting Canadian news from API: {str(api_err)}")
                # ادامه به روش قدیمی در صورت خطا
        
        # دریافت اخبار ترکیبی از منابع عادی
        combined_news = get_combined_news(max_items * 3, use_cache, ignore_cache_expiry)
        
        # فیلتر کردن اخبار مربوط به کانادا
        canadian_keywords = ["canada", "canadian", "toronto", "ontario", "quebec", "vancouver", 
                            "montreal", "calgary", "ottawa", "edmonton", "victoria", "halifax",
                            "winnipeg", "saskatoon", "canadian dollar", "scotia", "rbc", "td bank"]
        
        canadian_news = []
        
        for news in combined_news:
            title = news.get("title", "").lower()
            summary = news.get("summary", "").lower()
            
            for keyword in canadian_keywords:
                if keyword.lower() in title or keyword.lower() in summary:
                    canadian_news.append(news)
                    break
        
        # بررسی تعداد اخبار کانادایی
        if not canadian_news:
            logger.warning("No Canadian crypto news found. Adding fallback news with Canadian context.")
            # اضافه کردن برچسب کانادا به برخی اخبار عمومی به عنوان راه حل جایگزین
            general_count = min(max_items, len(combined_news))
            for i in range(general_count):
                if i < len(combined_news):
                    news_item = combined_news[i].copy()
                    if "title" in news_item:
                        if not news_item.get("is_stale", False):
                            news_item["context"] = "Canada"
                        canadian_news.append(news_item)
        
        # اگر اخبار کانادایی کمتر از حد انتظار یافت شد، از اخبار عمومی استفاده کن
        if len(canadian_news) < max_items:
            remaining = max_items - len(canadian_news)
            general_news = [n for n in combined_news if n not in canadian_news]
            canadian_news.extend(general_news[:remaining])
        
        return canadian_news[:max_items]
    
    except Exception as e:
        logger.error(f"Error in get_canadian_crypto_news: {str(e)}")
        # در صورت خطا، تلاش برای بدست آوردن اخبار با استفاده از کش منقضی شده
        if not ignore_cache_expiry:
            logger.warning("Trying to get Canadian news using expired cache")
            return get_canadian_crypto_news(max_items, True, True)
        return []

def get_news_by_category(category, max_items=5, use_cache=True, ignore_cache_expiry=False):
    """
    دریافت اخبار بر اساس دسته‌بندی

    Args:
        category (str): دسته‌بندی اخبار
        max_items (int): حداکثر تعداد اخبار
        use_cache (bool): استفاده از کش
        ignore_cache_expiry (bool): نادیده گرفتن زمان انقضای کش در صورت خطا

    Returns:
        list: لیست اخبار
    """
    try:
        # ابتدا سعی کنید با استفاده از API خبری جدید، اخبار دسته‌بندی شده را دریافت کنید
        if HAS_NEWS_API:
            try:
                logger.info(f"Getting {category} crypto news from the new API")
                api_news = get_news_by_category_from_api(category, max_items, 
                                                       use_cache=use_cache, 
                                                       ignore_cache_expiry=ignore_cache_expiry)
                if api_news:
                    logger.info(f"Received {len(api_news)} {category} crypto news items from API")
                    return api_news
                else:
                    logger.warning(f"No {category} crypto news received from API, falling back to web scraping")
            except Exception as api_err:
                logger.error(f"Error getting {category} news from API: {str(api_err)}")
                # ادامه به روش قدیمی در صورت خطا
        
        # دریافت اخبار ترکیبی
        combined_news = get_combined_news(max_items * 3, use_cache, ignore_cache_expiry)
        
        # تعریف کلیدواژه‌های هر دسته
        categories = {
            "bitcoin": ["bitcoin", "btc", "satoshi", "nakamoto", "halving"],
            "ethereum": ["ethereum", "eth", "vitalik", "buterin", "dapps", "smart contracts"],
            "defi": ["defi", "decentralized finance", "yield farming", "liquidity", "staking", "lending"],
            "nft": ["nft", "non-fungible token", "collectible", "digital art", "metaverse"],
            "regulation": ["regulation", "sec", "law", "compliance", "government", "regulatory", "legal"],
            "trading": ["trading", "price", "market", "bull", "bear", "chart", "technical analysis"],
            "mining": ["mining", "miner", "hash rate", "asic", "proof of work", "energy", "electricity"]
        }
        
        # اگر دسته مشخص شده وجود ندارد، اخبار عمومی برگردان
        if category.lower() not in categories:
            return combined_news[:max_items]
        
        # فیلتر کردن اخبار مربوط به دسته
        category_keywords = categories[category.lower()]
        filtered_news = []
        
        for news in combined_news:
            title = news.get("title", "").lower()
            summary = news.get("summary", "").lower()
            
            for keyword in category_keywords:
                if keyword.lower() in title or keyword.lower() in summary:
                    filtered_news.append(news)
                    break
        
        # اگر اخبار کمتر از حد انتظار یافت شد، از اخبار عمومی استفاده کن
        if len(filtered_news) < max_items:
            remaining = max_items - len(filtered_news)
            general_news = [n for n in combined_news if n not in filtered_news]
            filtered_news.extend(general_news[:remaining])
        
        return filtered_news[:max_items]
    
    except Exception as e:
        logger.error(f"Error in get_news_by_category: {str(e)}")
        # در صورت خطا، تلاش برای بدست آوردن اخبار با استفاده از کش منقضی شده
        if not ignore_cache_expiry:
            logger.warning(f"Trying to get {category} news using expired cache")
            return get_news_by_category(category, max_items, True, True)
        return []

def get_news_summary(url):
    """
    دریافت و خلاصه‌سازی متن کامل خبر

    Args:
        url (str): آدرس خبر

    Returns:
        dict: خلاصه خبر
    """
    try:
        # دریافت متن کامل خبر با تایم‌اوت و مدیریت خطا
        try:
            downloaded = trafilatura.fetch_url(url, timeout=15)  # افزایش تایم‌اوت
            if not downloaded:
                logger.warning(f"Failed to download content from {url}")
                return {"summary": "Could not download the article content."}
                
            text = trafilatura.extract(downloaded)
        except Exception as fetch_error:
            logger.error(f"Error fetching article from {url}: {str(fetch_error)}")
            return {"summary": "Error downloading the article content."}
        
        if not text or len(text) < 50:
            logger.warning(f"Insufficient text extracted from {url}")
            return {"summary": "No meaningful content could be extracted from this article."}
        
        # برش متن طولانی
        max_length = 5000
        if len(text) > max_length:
            logger.info(f"Truncating long article text from {url} ({len(text)} chars)")
            text = text[:max_length] + "..."
        
        # تولید خلاصه با روش ساده
        try:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            # استفاده از بین ۳ تا ۵ جمله اول به عنوان خلاصه، بسته به طول جمله‌ها
            if not sentences:
                return {"summary": "The article could not be split into sentences."}
                
            # انتخاب تعداد جمله‌ها: کمتر اگر جمله‌ها طولانی هستند
            avg_sentence_length = sum(len(s) for s in sentences[:5]) / min(5, len(sentences))
            num_sentences = 5 if avg_sentence_length < 100 else (4 if avg_sentence_length < 150 else 3)
            
            summary_sentences = sentences[:int(num_sentences)]  
            summary = ' '.join(summary_sentences)
        except Exception as summary_error:
            logger.error(f"Error creating summary from {url}: {str(summary_error)}")
            # استفاده از روش ساده‌تر در صورت خطا
            summary = text[:250] + "..."
        
        # برش خلاصه بلند
        if len(summary) > 250:
            summary = summary[:247] + "..."
            
        return {"summary": summary, "full_text_length": len(text)}
    
    except Exception as e:
        logger.error(f"Error getting news summary: {str(e)}")
        return {"summary": "Error processing article content."}