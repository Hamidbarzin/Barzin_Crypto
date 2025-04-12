"""
ماژول دریافت اخبار و تحلیل‌های بازار از CMC Markets Canada

این ماژول داده‌های اخبار را از CMC Markets Canada دریافت و
پردازش می‌کند تا برای کاربران ایرانی قابل استفاده باشد.
"""
import time
import logging
import requests
from bs4 import BeautifulSoup
from trafilatura import fetch_url, extract
from crypto_bot.cache_manager import news_cache

# تنظیم لاگر
logger = logging.getLogger(__name__)

# آدرس‌های مهم CMC Markets Canada
CMC_CANADA_BASE_URL = "https://www.cmcmarkets.com/en-ca/"
CMC_CANADA_NEWS_URL = f"{CMC_CANADA_BASE_URL}news-and-analysis"
CMC_CANADA_CRYPTO_URL = f"{CMC_CANADA_BASE_URL}cryptocurrency-trading"
CMC_CANADA_MARKET_ANALYSIS_URL = f"{CMC_CANADA_BASE_URL}financial-trading/market-reports-and-analysis"

# زمان نگهداری کش اخبار (2 ساعت)
NEWS_CACHE_TTL = 2 * 60 * 60


def get_cmc_canada_news(max_items=5, use_cache=True):
    """
    دریافت اخبار از CMC Markets Canada
    
    Args:
        max_items (int): حداکثر تعداد خبر برای بازیابی
        use_cache (bool): استفاده از کش برای داده‌های اخبار
        
    Returns:
        list: لیست اخبار با جزییات
    """
    cache_key = f"cmc_canada_news_{max_items}"
    
    # بررسی کش
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("CMC Markets Canada news retrieved from cache")
            return cached_data
    
    news_items = []
    
    try:
        # دریافت صفحه اخبار
        response = requests.get(CMC_CANADA_NEWS_URL, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error fetching CMC Markets Canada news: {response.status_code}")
            return news_items
        
        # پردازش HTML با BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # یافتن آیتم‌های اخبار
        news_container = soup.find('div', class_='news-listing')
        if not news_container:
            logger.warning("Could not find news container in CMC Markets Canada")
            return news_items
        
        news_articles = news_container.find_all('article', class_='news-item')
        
        for article in news_articles[:max_items]:
            try:
                # استخراج عنوان و لینک
                title_elem = article.find('h2', class_='news-item__title')
                if not title_elem or not title_elem.find('a'):
                    continue
                
                title = title_elem.find('a').text.strip()
                link = title_elem.find('a')['href']
                
                # افزودن دامنه به لینک اگر نسبی باشد
                if link.startswith('/'):
                    link = f"{CMC_CANADA_BASE_URL.rstrip('/')}{link}"
                
                # استخراج تاریخ
                date_elem = article.find('time', class_='news-item__date')
                date = date_elem.text.strip() if date_elem else 'Unknown Date'
                
                # استخراج خلاصه خبر
                summary_elem = article.find('div', class_='news-item__summary')
                summary = summary_elem.text.strip() if summary_elem else ''
                
                # استخراج تصویر
                image_elem = article.find('img')
                image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ''
                
                # ساخت آیتم خبر
                news_item = {
                    'title': title,
                    'url': link,
                    'date': date,
                    'summary': summary,
                    'image_url': image_url,
                    'source': 'CMC Markets Canada',
                    'sentiment': {'score': 0, 'label': 'Neutral'},  # پیش‌فرض - باید با تحلیل متن تکمیل شود
                    'tags': ['canada', 'market analysis'],
                    'is_sample_data': False
                }
                
                news_items.append(news_item)
                
            except Exception as e:
                logger.error(f"Error parsing news article from CMC Markets Canada: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching news from CMC Markets Canada: {str(e)}")
    
    # ذخیره در کش
    if news_items:
        news_cache.set(cache_key, news_items, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(news_items)} CMC Markets Canada news items to cache")
    
    return news_items


def get_cmc_canada_crypto_analysis(max_items=3, use_cache=True):
    """
    دریافت تحلیل‌های ارزهای دیجیتال از CMC Markets Canada
    
    Args:
        max_items (int): حداکثر تعداد تحلیل برای بازیابی
        use_cache (bool): استفاده از کش برای داده‌های تحلیل
        
    Returns:
        list: لیست تحلیل‌ها با جزییات
    """
    cache_key = f"cmc_canada_crypto_analysis_{max_items}"
    
    # بررسی کش
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("CMC Markets Canada crypto analysis retrieved from cache")
            return cached_data
    
    analysis_items = []
    
    try:
        # دریافت صفحه تحلیل‌های ارز دیجیتال
        response = requests.get(CMC_CANADA_CRYPTO_URL, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error fetching CMC Markets Canada crypto analysis: {response.status_code}")
            return analysis_items
        
        # پردازش HTML با BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # یافتن بخش تحلیل‌ها
        analysis_section = soup.find('section', class_='crypto-news')
        if not analysis_section:
            analysis_section = soup.find('div', class_='content-block')  # جایگزین احتمالی
        
        if not analysis_section:
            logger.warning("Could not find crypto analysis section in CMC Markets Canada")
            return analysis_items
        
        # یافتن آیتم‌های تحلیل
        articles = analysis_section.find_all('article') or []
        if not articles:
            # جستجوی عمومی‌تر برای مقالات
            articles = analysis_section.find_all('div', class_=['news-item', 'article-item']) or []
        
        for article in articles[:max_items]:
            try:
                # استخراج عنوان و لینک
                title_elem = article.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a') or article.find('a')
                if not link_elem:
                    continue
                
                title = title_elem.text.strip()
                link = link_elem['href']
                
                # افزودن دامنه به لینک اگر نسبی باشد
                if link.startswith('/'):
                    link = f"{CMC_CANADA_BASE_URL.rstrip('/')}{link}"
                
                # استخراج تاریخ
                date_elem = article.find('time') or article.find('span', class_=['date', 'time'])
                date = date_elem.text.strip() if date_elem else 'Unknown Date'
                
                # استخراج خلاصه
                summary_elem = article.find(['p', 'div'], class_=['summary', 'excerpt', 'description'])
                summary = summary_elem.text.strip() if summary_elem else ''
                
                # استخراج تصویر
                image_elem = article.find('img')
                image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ''
                
                # ساخت آیتم تحلیل
                analysis_item = {
                    'title': title,
                    'url': link,
                    'date': date,
                    'summary': summary,
                    'image_url': image_url,
                    'source': 'CMC Markets Canada',
                    'type': 'crypto_analysis',
                    'tags': ['canada', 'crypto', 'analysis'],
                    'is_sample_data': False
                }
                
                analysis_items.append(analysis_item)
                
            except Exception as e:
                logger.error(f"Error parsing crypto analysis from CMC Markets Canada: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching crypto analysis from CMC Markets Canada: {str(e)}")
    
    # ذخیره در کش
    if analysis_items:
        news_cache.set(cache_key, analysis_items, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(analysis_items)} CMC Markets Canada crypto analysis items to cache")
    
    return analysis_items


def get_combined_cmc_canada_content(max_news=5, max_analysis=3, use_cache=True):
    """
    ترکیب اخبار و تحلیل‌های CMC Markets Canada
    
    Args:
        max_news (int): حداکثر تعداد خبر
        max_analysis (int): حداکثر تعداد تحلیل
        use_cache (bool): استفاده از کش
        
    Returns:
        list: لیست ترکیبی از اخبار و تحلیل‌ها
    """
    cache_key = f"cmc_canada_combined_{max_news}_{max_analysis}"
    
    # بررسی کش
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("Combined CMC Markets Canada content retrieved from cache")
            return cached_data
    
    # دریافت اخبار و تحلیل‌ها
    news = get_cmc_canada_news(max_items=max_news, use_cache=use_cache)
    analysis = get_cmc_canada_crypto_analysis(max_items=max_analysis, use_cache=use_cache)
    
    # ترکیب و مرتب‌سازی بر اساس نوع (تحلیل‌ها اول نمایش داده شوند)
    combined_items = []
    
    # اضافه کردن تحلیل‌ها
    for item in analysis:
        item['content_type'] = 'analysis'
        combined_items.append(item)
    
    # اضافه کردن اخبار
    for item in news:
        item['content_type'] = 'news'
        combined_items.append(item)
    
    # ذخیره در کش
    if combined_items:
        news_cache.set(cache_key, combined_items, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(combined_items)} combined CMC Markets Canada items to cache")
    
    return combined_items


def fetch_full_article_content(url):
    """
    دریافت متن کامل مقاله از URL
    
    Args:
        url (str): آدرس کامل مقاله
        
    Returns:
        str: متن استخراج شده از مقاله
    """
    cache_key = f"article_content_{url}"
    
    # بررسی کش
    cached_content = news_cache.get(cache_key)
    if cached_content is not None:
        logger.info(f"Article content for {url} retrieved from cache")
        return cached_content
    
    try:
        # استفاده از trafilatura برای استخراج متن
        downloaded = fetch_url(url)
        if not downloaded:
            logger.error(f"Could not fetch URL: {url}")
            return ""
        
        # استخراج متن اصلی
        text = extract(downloaded)
        if not text:
            logger.warning(f"Could not extract text from {url}")
            return ""
        
        # ذخیره در کش (2 روز)
        news_cache.set(cache_key, text, 2 * 24 * 60 * 60)
        return text
    
    except Exception as e:
        logger.error(f"Error fetching full article content from {url}: {str(e)}")
        return ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # آزمایش دریافت اخبار
    news = get_cmc_canada_news(max_items=3, use_cache=False)
    print(f"Retrieved {len(news)} news items from CMC Markets Canada")
    
    # آزمایش دریافت تحلیل‌ها
    analysis = get_cmc_canada_crypto_analysis(max_items=2, use_cache=False)
    print(f"Retrieved {len(analysis)} analysis items from CMC Markets Canada")
    
    # آزمایش ترکیب
    combined = get_combined_cmc_canada_content(max_news=3, max_analysis=2, use_cache=False)
    print(f"Retrieved {len(combined)} combined items from CMC Markets Canada")