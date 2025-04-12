"""
Canadian Crypto Market News and Analysis Module

This module retrieves and processes news data from Canadian crypto markets
including CMC Markets Canada and other Canadian crypto news sources.
"""
import time
import logging
import requests
from bs4 import BeautifulSoup
from trafilatura import fetch_url, extract
from crypto_bot.cache_manager import news_cache

# تنظیم لاگر
logger = logging.getLogger(__name__)

# Important URLs for Canadian crypto sources
CMC_CANADA_BASE_URL = "https://www.cmcmarkets.com/en-ca/"
CMC_CANADA_NEWS_URL = f"{CMC_CANADA_BASE_URL}news-and-analysis"
CMC_CANADA_CRYPTO_URL = f"{CMC_CANADA_BASE_URL}cryptocurrency-trading"
CMC_CANADA_MARKET_ANALYSIS_URL = f"{CMC_CANADA_BASE_URL}financial-trading/market-reports-and-analysis"

# NDAX Canadian Crypto Exchange
NDAX_BASE_URL = "https://ndax.io/"
NDAX_BLOG_URL = "https://ndax.io/blog/"

# Bitbuy Canadian Exchange
BITBUY_BASE_URL = "https://bitbuy.ca/"
BITBUY_BLOG_URL = "https://bitbuy.ca/en/resources/blog/"

# Newton Canadian Exchange
NEWTON_BASE_URL = "https://www.newton.co/"
NEWTON_LEARN_URL = "https://www.newton.co/learn"

# Cache timeout (2 hours)
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


def get_ndax_blog_news(max_items=5, use_cache=True):
    """
    Retrieve news from NDAX.io blog
    
    Args:
        max_items (int): Maximum number of news items to retrieve
        use_cache (bool): Whether to use cache for news data
        
    Returns:
        list: List of news items with details
    """
    cache_key = f"ndax_blog_news_{max_items}"
    
    # Check cache
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("NDAX blog news retrieved from cache")
            return cached_data
    
    news_items = []
    
    try:
        # Get blog page
        response = requests.get(NDAX_BLOG_URL, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error fetching NDAX blog: {response.status_code}")
            return news_items
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find news items - adjust classes based on actual structure
        blog_posts = soup.find_all('article') or soup.find_all('div', class_=['post', 'blog-post', 'entry'])
        
        for post in blog_posts[:max_items]:
            try:
                # Extract title and link
                title_elem = post.find(['h1', 'h2', 'h3', 'h4']) or post.find(class_=['title', 'entry-title'])
                link_elem = title_elem.find('a') if title_elem else post.find('a')
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.text.strip()
                link = link_elem['href']
                
                # Add domain to link if relative
                if link.startswith('/'):
                    link = f"{NDAX_BASE_URL.rstrip('/')}{link}"
                
                # Extract date
                date_elem = post.find('time') or post.find(class_=['date', 'published', 'entry-date'])
                date = date_elem.text.strip() if date_elem else 'Unknown Date'
                
                # Extract summary
                summary_elem = post.find(['p', 'div'], class_=['summary', 'excerpt', 'entry-summary'])
                summary = summary_elem.text.strip() if summary_elem else ''
                
                # Extract image
                image_elem = post.find('img')
                image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ''
                
                # Create news item
                news_item = {
                    'title': title,
                    'url': link,
                    'date': date,
                    'summary': summary,
                    'image_url': image_url,
                    'source': 'NDAX',
                    'sentiment': {'score': 0, 'label': 'Neutral'},
                    'tags': ['canada', 'crypto', 'exchange'],
                    'is_sample_data': False
                }
                
                news_items.append(news_item)
                
            except Exception as e:
                logger.error(f"Error parsing blog post from NDAX: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching news from NDAX blog: {str(e)}")
    
    # Save to cache
    if news_items:
        news_cache.set(cache_key, news_items, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(news_items)} NDAX blog items to cache")
    
    return news_items


def get_bitbuy_blog_news(max_items=5, use_cache=True):
    """
    Retrieve news from Bitbuy blog
    
    Args:
        max_items (int): Maximum number of news items to retrieve
        use_cache (bool): Whether to use cache for news data
        
    Returns:
        list: List of news items with details
    """
    cache_key = f"bitbuy_blog_news_{max_items}"
    
    # Check cache
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("Bitbuy blog news retrieved from cache")
            return cached_data
    
    news_items = []
    
    try:
        # Get blog page
        response = requests.get(BITBUY_BLOG_URL, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error fetching Bitbuy blog: {response.status_code}")
            return news_items
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find news items - adjust classes based on actual structure
        blog_posts = soup.find_all('article') or soup.find_all('div', class_=['post', 'blog-post', 'entry'])
        
        for post in blog_posts[:max_items]:
            try:
                # Extract title and link
                title_elem = post.find(['h1', 'h2', 'h3', 'h4']) or post.find(class_=['title', 'entry-title'])
                link_elem = title_elem.find('a') if title_elem else post.find('a')
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.text.strip()
                link = link_elem['href']
                
                # Add domain to link if relative
                if link.startswith('/'):
                    link = f"{BITBUY_BASE_URL.rstrip('/')}{link}"
                
                # Extract date
                date_elem = post.find('time') or post.find(class_=['date', 'published', 'entry-date'])
                date = date_elem.text.strip() if date_elem else 'Unknown Date'
                
                # Extract summary
                summary_elem = post.find(['p', 'div'], class_=['summary', 'excerpt', 'entry-summary'])
                summary = summary_elem.text.strip() if summary_elem else ''
                
                # Extract image
                image_elem = post.find('img')
                image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ''
                
                # Create news item
                news_item = {
                    'title': title,
                    'url': link,
                    'date': date,
                    'summary': summary,
                    'image_url': image_url,
                    'source': 'Bitbuy',
                    'sentiment': {'score': 0, 'label': 'Neutral'},
                    'tags': ['canada', 'crypto', 'exchange'],
                    'is_sample_data': False
                }
                
                news_items.append(news_item)
                
            except Exception as e:
                logger.error(f"Error parsing blog post from Bitbuy: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching news from Bitbuy blog: {str(e)}")
    
    # Save to cache
    if news_items:
        news_cache.set(cache_key, news_items, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(news_items)} Bitbuy blog items to cache")
    
    return news_items


def get_newton_learn_articles(max_items=5, use_cache=True):
    """
    Retrieve educational articles from Newton.co Learn section
    
    Args:
        max_items (int): Maximum number of articles to retrieve
        use_cache (bool): Whether to use cache for article data
        
    Returns:
        list: List of articles with details
    """
    cache_key = f"newton_learn_articles_{max_items}"
    
    # Check cache
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("Newton learn articles retrieved from cache")
            return cached_data
    
    articles = []
    
    try:
        # Get learn page
        response = requests.get(NEWTON_LEARN_URL, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error fetching Newton learn articles: {response.status_code}")
            return articles
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find article items - adjust classes based on actual structure
        article_elems = soup.find_all('article') or soup.find_all(['div', 'section'], class_=['article', 'post', 'learn-item'])
        
        for article_elem in article_elems[:max_items]:
            try:
                # Extract title and link
                title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4']) or article_elem.find(class_=['title', 'article-title'])
                link_elem = title_elem.find('a') if title_elem else article_elem.find('a')
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.text.strip()
                link = link_elem['href']
                
                # Add domain to link if relative
                if link.startswith('/'):
                    link = f"{NEWTON_BASE_URL.rstrip('/')}{link}"
                
                # Extract date if available
                date_elem = article_elem.find('time') or article_elem.find(class_=['date', 'published'])
                date = date_elem.text.strip() if date_elem else 'Unknown Date'
                
                # Extract summary
                summary_elem = article_elem.find(['p', 'div'], class_=['summary', 'excerpt', 'description'])
                summary = summary_elem.text.strip() if summary_elem else ''
                
                # Extract image
                image_elem = article_elem.find('img')
                image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ''
                
                # Create article item
                article_item = {
                    'title': title,
                    'url': link,
                    'date': date,
                    'summary': summary,
                    'image_url': image_url,
                    'source': 'Newton',
                    'type': 'educational',
                    'tags': ['canada', 'crypto', 'educational'],
                    'is_sample_data': False
                }
                
                articles.append(article_item)
                
            except Exception as e:
                logger.error(f"Error parsing article from Newton: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error fetching articles from Newton: {str(e)}")
    
    # Save to cache
    if articles:
        news_cache.set(cache_key, articles, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(articles)} Newton learn articles to cache")
    
    return articles


def get_all_canadian_crypto_news(max_per_source=3, use_cache=True):
    """
    Combine news from all Canadian crypto sources
    
    Args:
        max_per_source (int): Maximum number of items to retrieve from each source
        use_cache (bool): Whether to use cache for news data
        
    Returns:
        list: Combined list of news items from all sources
    """
    cache_key = f"all_canadian_crypto_news_{max_per_source}"
    
    # Check cache
    if use_cache:
        cached_data = news_cache.get(cache_key)
        if cached_data is not None:
            logger.info("All Canadian crypto news retrieved from cache")
            return cached_data
    
    # Get news from all sources
    cmc_news = get_cmc_canada_news(max_items=max_per_source, use_cache=use_cache)
    ndax_news = get_ndax_blog_news(max_items=max_per_source, use_cache=use_cache)
    bitbuy_news = get_bitbuy_blog_news(max_items=max_per_source, use_cache=use_cache)
    newton_articles = get_newton_learn_articles(max_items=max_per_source, use_cache=use_cache)
    
    # Combine all news
    all_news = []
    all_news.extend(cmc_news)
    all_news.extend(ndax_news)
    all_news.extend(bitbuy_news)
    all_news.extend(newton_articles)
    
    # Sort by date if possible (most recent first)
    # This is challenging due to different date formats, so we will keep the mixed order
    
    # Save to cache
    if all_news:
        news_cache.set(cache_key, all_news, NEWS_CACHE_TTL)
        logger.info(f"Saved {len(all_news)} combined Canadian crypto news items to cache")
    
    return all_news


def fetch_full_article_content(url):
    """
    Retrieve full article content from URL
    
    Args:
        url (str): Full article URL
        
    Returns:
        str: Extracted article text
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
    
    # Test CMC Markets Canada
    news = get_cmc_canada_news(max_items=3, use_cache=False)
    print(f"Retrieved {len(news)} news items from CMC Markets Canada")
    
    analysis = get_cmc_canada_crypto_analysis(max_items=2, use_cache=False)
    print(f"Retrieved {len(analysis)} analysis items from CMC Markets Canada")
    
    combined = get_combined_cmc_canada_content(max_news=3, max_analysis=2, use_cache=False)
    print(f"Retrieved {len(combined)} combined items from CMC Markets Canada")
    
    # Test Canadian crypto news sources
    ndax_news = get_ndax_blog_news(max_items=3, use_cache=False)
    print(f"Retrieved {len(ndax_news)} news items from NDAX")
    
    bitbuy_news = get_bitbuy_blog_news(max_items=3, use_cache=False)
    print(f"Retrieved {len(bitbuy_news)} news items from Bitbuy")
    
    newton_articles = get_newton_learn_articles(max_items=3, use_cache=False)
    print(f"Retrieved {len(newton_articles)} articles from Newton")
    
    # Test combined Canadian crypto news
    all_canadian_news = get_all_canadian_crypto_news(max_per_source=2, use_cache=False)
    print(f"Retrieved {len(all_canadian_news)} total Canadian crypto news items")