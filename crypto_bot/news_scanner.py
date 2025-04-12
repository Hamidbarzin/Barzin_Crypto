"""
اسکنر اخبار ارزهای دیجیتال

این ماژول اخبار ارزهای دیجیتال را از منابع مختلف جمع‌آوری می‌کند،
آنها را خلاصه می‌کند و نتایج را برای استفاده در ربات تلگرام و وب‌سایت ذخیره می‌کند.
"""
import os
import time
import logging
import requests
from bs4 import BeautifulSoup
import trafilatura
from crypto_bot.cache_manager import news_cache

# تنظیم لاگر
logger = logging.getLogger(__name__)

# منابع اخبار - API‌ها و وب‌سایت‌های معتبر اخبار ارزهای دیجیتال 
NEWS_SOURCES = [
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/feed",
        "type": "rss",
        "country": "global"
    },
    {
        "name": "Decrypt",
        "url": "https://decrypt.co/feed",
        "type": "rss",
        "country": "global"
    },
    {
        "name": "CryptoSlate",
        "url": "https://cryptoslate.com/feed/",
        "type": "rss",
        "country": "global"
    },
    {
        "name": "CoinTelegraph",
        "url": "https://cointelegraph.com/rss",
        "type": "rss",
        "country": "global"
    },
    # منابع کانادایی
    {
        "name": "The Globe and Mail - Crypto",
        "url": "https://www.theglobeandmail.com/investing/",
        "type": "web",
        "country": "canada",
        "category": "Cryptocurrency",
        "selector": ".c-card"
    }
]

# زمان انقضای کش (2 ساعت)
NEWS_CACHE_TTL = 2 * 60 * 60

def get_combined_news(max_items=10, use_cache=True):
    """
    دریافت اخبار ترکیبی از تمامی منابع

    Args:
        max_items (int): حداکثر تعداد اخبار برای هر منبع
        use_cache (bool): استفاده از کش

    Returns:
        list: لیست اخبار ترکیبی
    """
    cache_key = f"combined_news_{max_items}"
    
    # بررسی کش
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("Combined news retrieved from cache")
            return cached_data

    all_news = []
    
    # دریافت اخبار از منابع مختلف
    for source in NEWS_SOURCES:
        try:
            if source["type"] == "rss":
                news_items = fetch_rss_news(source, max_items)
            elif source["type"] == "web":
                news_items = fetch_web_news(source, max_items)
            else:
                continue
                
            all_news.extend(news_items)
            
        except Exception as e:
            logger.error(f"Error fetching news from {source['name']}: {str(e)}")
    
    # مرتب‌سازی بر اساس زمان (جدیدترین اخبار ابتدا نمایش داده شوند)
    all_news.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    
    # محدود کردن تعداد کل اخبار
    all_news = all_news[:max_items*3]
    
    # ذخیره در کش
    if all_news:
        news_cache.set(cache_key, all_news, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(all_news)} combined news items to cache")
    
    return all_news

def fetch_rss_news(source, max_items=5):
    """
    دریافت اخبار از فید RSS

    Args:
        source (dict): اطلاعات منبع خبری
        max_items (int): حداکثر تعداد اخبار

    Returns:
        list: لیست اخبار
    """
    news_items = []
    
    try:
        response = requests.get(source["url"], timeout=10)
        if response.status_code != 200:
            logger.error(f"Error fetching RSS feed from {source['name']}: {response.status_code}")
            return news_items
            
        # پردازش XML با BeautifulSoup
        soup = BeautifulSoup(response.text, "xml")
        
        # یافتن آیتم‌های خبر
        items = soup.find_all("item")
        
        for item in items[:max_items]:
            try:
                # استخراج عنوان، لینک و تاریخ
                title_elem = item.find("title")
                title = title_elem.text if title_elem else "No Title"
                
                link_elem = item.find("link")
                link = link_elem.text if link_elem else "#"
                
                # استخراج تاریخ
                date_elem = item.find("pubDate")
                date = date_elem.text if date_elem else "Unknown Date"
                
                # استخراج توضیحات
                desc_elem = item.find("description")
                description = desc_elem.text if desc_elem else ""
                
                # استخراج تصویر
                image_url = ""
                
                # ابتدا تلاش برای یافتن تگ تصویر
                media_content = item.find("media:content") or item.find("enclosure")
                if media_content and "url" in media_content.attrs:
                    image_url = media_content.get("url", "")
                    
                # اگر تصویر در توضیحات وجود داشته باشد
                if not image_url and desc_elem:
                    desc_soup = BeautifulSoup(description, "html.parser")
                    img_tag = desc_soup.find("img")
                    if img_tag and "src" in img_tag.attrs:
                        image_url = img_tag["src"]
                
                # ساخت آیتم خبر
                news_item = {
                    "title": title,
                    "title_fa": "",  # می‌توانیم بعدا با API ترجمه پر کنیم
                    "url": link,
                    "published_date": date,
                    "summary": description[:150] + "..." if len(description) > 150 else description,
                    "imageurl": image_url,
                    "source": source["name"],
                    "country": source.get("country", "global"),
                    "is_sample_data": False
                }
                
                news_items.append(news_item)
                
            except Exception as e:
                logger.error(f"Error parsing RSS item from {source['name']}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching RSS feed from {source['name']}: {str(e)}")
    
    return news_items

def fetch_web_news(source, max_items=5):
    """
    دریافت اخبار از وب‌سایت

    Args:
        source (dict): اطلاعات منبع خبری
        max_items (int): حداکثر تعداد اخبار

    Returns:
        list: لیست اخبار
    """
    news_items = []
    
    try:
        # دریافت صفحه وب
        downloaded = trafilatura.fetch_url(source["url"])
        if not downloaded:
            logger.error(f"Error downloading page from {source['name']}")
            return news_items
            
        # پردازش HTML با BeautifulSoup
        soup = BeautifulSoup(downloaded, "html.parser")
        
        # یافتن آیتم‌های خبر بر اساس سلکتور CSS
        selector = source.get("selector", "article")
        articles = soup.select(selector)
        
        for article in articles[:max_items]:
            try:
                # استخراج عنوان و لینک
                title_elem = article.find(["h1", "h2", "h3", "h4"]) or article.select_one(".title, .headline")
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
                # استخراج لینک
                link_elem = title_elem.find("a") or article.find("a")
                link = "#"
                if link_elem and "href" in link_elem.attrs:
                    link = link_elem["href"]
                    # اگر لینک نسبی باشد، دامنه را اضافه کنیم
                    if link.startswith("/"):
                        base_url = "/".join(source["url"].split("/")[:3])
                        link = f"{base_url}{link}"
                
                # استخراج تاریخ
                date_elem = article.find(["time"]) or article.select_one(".date, .time, .published")
                date = date_elem.text.strip() if date_elem else "Unknown Date"
                
                # استخراج خلاصه
                summary_elem = article.find(["p"]) or article.select_one(".summary, .excerpt, .description")
                summary = summary_elem.text.strip() if summary_elem else ""
                
                # استخراج تصویر
                image_elem = article.find("img")
                image_url = ""
                if image_elem and "src" in image_elem.attrs:
                    image_url = image_elem["src"]
                    # اگر آدرس تصویر نسبی باشد، دامنه را اضافه کنیم
                    if image_url.startswith("/"):
                        base_url = "/".join(source["url"].split("/")[:3])
                        image_url = f"{base_url}{image_url}"
                
                # بررسی کنیم که آیا خبر مربوط به ارزهای دیجیتال است
                is_crypto_related = False
                category = source.get("category", "").lower()
                
                if category == "cryptocurrency":
                    is_crypto_related = True
                else:
                    # بررسی کلمات کلیدی در عنوان و خلاصه
                    crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", 
                                       "cryptocurrency", "digital currency", "token", "coin", 
                                       "defi", "nft", "altcoin", "binance", "coinbase"]
                    
                    title_lower = title.lower()
                    summary_lower = summary.lower()
                    
                    for keyword in crypto_keywords:
                        if keyword in title_lower or keyword in summary_lower:
                            is_crypto_related = True
                            break
                
                # اگر خبر مربوط به ارزهای دیجیتال نباشد، آن را نادیده بگیریم
                if not is_crypto_related:
                    continue
                
                # ساخت آیتم خبر
                news_item = {
                    "title": title,
                    "title_fa": "",  # می‌توانیم بعدا با API ترجمه پر کنیم
                    "url": link,
                    "published_date": date,
                    "summary": summary[:150] + "..." if len(summary) > 150 else summary,
                    "imageurl": image_url,
                    "source": source["name"],
                    "country": source.get("country", "global"),
                    "is_sample_data": False
                }
                
                news_items.append(news_item)
                
            except Exception as e:
                logger.error(f"Error parsing web article from {source['name']}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching web news from {source['name']}: {str(e)}")
    
    return news_items

def get_canadian_crypto_news(max_items=5, use_cache=True):
    """
    دریافت اخبار ارزهای دیجیتال مربوط به کانادا

    Args:
        max_items (int): حداکثر تعداد اخبار
        use_cache (bool): استفاده از کش

    Returns:
        list: لیست اخبار کانادایی
    """
    cache_key = f"canadian_crypto_news_{max_items}"
    
    # بررسی کش
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("Canadian crypto news retrieved from cache")
            return cached_data
    
    all_news = get_combined_news(max_items * 2, use_cache=use_cache)
    
    # فیلتر کردن فقط اخبار کانادایی
    canadian_news = [news for news in all_news if news.get("country") == "canada"]
    
    # اگر اخبار کانادایی کافی نبود، نمونه‌هایی از اخبار معتبر جهانی را اضافه کنیم
    if len(canadian_news) < max_items:
        global_news = [news for news in all_news if news.get("country") == "global"]
        canadian_news.extend(global_news[:max_items - len(canadian_news)])
    
    # محدود کردن به تعداد مورد نظر
    canadian_news = canadian_news[:max_items]
    
    # ذخیره در کش
    if canadian_news:
        news_cache.set(cache_key, canadian_news, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(canadian_news)} Canadian crypto news items to cache")
    
    return canadian_news

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
    # برای مثال می‌توانیم دسته‌بندی‌هایی مانند "bitcoin", "ethereum", "defi", "nft" و غیره داشته باشیم
    cache_key = f"news_by_category_{category}_{max_items}"
    
    # بررسی کش
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"News for category {category} retrieved from cache")
            return cached_data
    
    all_news = get_combined_news(max_items * 3, use_cache=use_cache)
    
    # فیلتر کردن اخبار بر اساس دسته‌بندی
    keywords = []
    
    if category.lower() == "bitcoin":
        keywords = ["bitcoin", "btc"]
    elif category.lower() == "ethereum":
        keywords = ["ethereum", "eth"]
    elif category.lower() == "defi":
        keywords = ["defi", "decentralized finance", "yield farming", "liquidity"]
    elif category.lower() == "nft":
        keywords = ["nft", "non-fungible token", "digital art"]
    
    category_news = []
    
    for news in all_news:
        title = news.get("title", "").lower()
        summary = news.get("summary", "").lower()
        
        for keyword in keywords:
            if keyword in title or keyword in summary:
                category_news.append(news)
                break
    
    # محدود کردن به تعداد مورد نظر
    category_news = category_news[:max_items]
    
    # ذخیره در کش
    if category_news:
        news_cache.set(cache_key, category_news, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(category_news)} news items for category {category} to cache")
    
    return category_news

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
        if not downloaded:
            logger.error(f"Error downloading article from {url}")
            return {"summary": "Could not download the article."}
            
        # استخراج متن اصلی
        text = trafilatura.extract(downloaded)
        
        if not text or len(text) < 100:
            logger.error(f"Could not extract meaningful text from {url}")
            return {"summary": "Could not extract the article content."}
        
        # ساخت خلاصه (اینجا می‌توانیم از الگوریتم‌های خلاصه‌سازی پیشرفته‌تر استفاده کنیم)
        summary = text[:500] + "..." if len(text) > 500 else text
        
        return {
            "summary": summary,
            "full_text": text,
            "word_count": len(text.split()),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error summarizing article from {url}: {str(e)}")
        return {
            "summary": "Error generating summary.",
            "success": False,
            "error": str(e)
        }

# تابع اصلی برای آزمایش
if __name__ == "__main__":
    # تنظیم لاگر
    logging.basicConfig(level=logging.INFO)
    
    # آزمایش دریافت اخبار
    news = get_combined_news(max_items=3, use_cache=False)
    print(f"Retrieved {len(news)} news items.")
    
    for item in news[:3]:
        print(f"Title: {item['title']}")
        print(f"Source: {item['source']}")
        print(f"Date: {item['published_date']}")
        print(f"URL: {item['url']}")
        print("-" * 50)