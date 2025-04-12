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

import requests
import trafilatura
from bs4 import BeautifulSoup

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

def get_combined_news(max_items=10, use_cache=True):
    """
    دریافت اخبار ترکیبی از تمامی منابع

    Args:
        max_items (int): حداکثر تعداد اخبار برای هر منبع
        use_cache (bool): استفاده از کش

    Returns:
        list: لیست اخبار ترکیبی
    """
    try:
        # بررسی داده‌های کش شده
        if use_cache and os.path.exists(CACHE_FILE):
            cache_age = time.time() - os.path.getmtime(CACHE_FILE)
            if cache_age < CACHE_EXPIRY:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cached_news = json.load(f)
                    logger.info(f"Loaded {len(cached_news)} news items from cache")
                    return cached_news

        # جمع‌آوری اخبار از همه منابع
        combined_news = []
        
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
                logger.error(f"Error fetching news from {source['name']}: {str(e)}")
        
        # مرتب‌سازی براساس زمان (جدیدترین اخبار اول)
        combined_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        
        # محدود کردن به تعداد مشخص
        combined_news = combined_news[:max_items]
        
        # ذخیره در کش
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(combined_news, f, ensure_ascii=False, indent=2)
        
        return combined_news
    
    except Exception as e:
        logger.error(f"Error in get_combined_news: {str(e)}")
        # در صورت خطا، داده تستی برای جلوگیری از خالی‌ماندن صفحه
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
        response = requests.get(source["url"], headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {source['name']}: {response.status_code}")
            return []
        
        # استخراج اخبار
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.select(source["selector"])
        
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
                    domain = re.match(r"https?://[^/]+", source["url"]).group(0)
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
                        domain = re.match(r"https?://[^/]+", source["url"]).group(0)
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

def get_canadian_crypto_news(max_items=5, use_cache=True):
    """
    دریافت اخبار ارزهای دیجیتال مربوط به کانادا

    Args:
        max_items (int): حداکثر تعداد اخبار
        use_cache (bool): استفاده از کش

    Returns:
        list: لیست اخبار کانادایی
    """
    try:
        # دریافت اخبار ترکیبی
        combined_news = get_combined_news(max_items * 3, use_cache)
        
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
        
        # اگر اخبار کانادایی کمتر از حد انتظار یافت شد، از اخبار عمومی استفاده کن
        if len(canadian_news) < max_items:
            remaining = max_items - len(canadian_news)
            general_news = [n for n in combined_news if n not in canadian_news]
            canadian_news.extend(general_news[:remaining])
        
        return canadian_news[:max_items]
    
    except Exception as e:
        logger.error(f"Error in get_canadian_crypto_news: {str(e)}")
        return []

def get_news_by_category(category, max_items=5, use_cache=True):
    """
    دریافت اخبار بر اساس دسته‌بندی

    Args:
        category (str): دسته‌بندی اخبار
        max_items (int): حداکثر تعداد اخبار
        use_cache (bool): استفاده از کش

    Returns:
        list: لیست اخبار
    """
    try:
        # دریافت اخبار ترکیبی
        combined_news = get_combined_news(max_items * 3, use_cache)
        
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
        # دریافت متن کامل خبر
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        
        if not text or len(text) < 50:
            return {"summary": "No content could be extracted from this article."}
        
        # برش متن طولانی
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # تولید خلاصه با روش ساده
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary_sentences = sentences[:3]  # استفاده از ۳ جمله اول به عنوان خلاصه
        summary = ' '.join(summary_sentences)
        
        # برش خلاصه بلند
        if len(summary) > 250:
            summary = summary[:247] + "..."
            
        return {"summary": summary}
    
    except Exception as e:
        logger.error(f"Error getting news summary: {str(e)}")
        return {"summary": "Error retrieving article content."}