"""
Cryptocurrency News Retrieval and Processing Module

This module is used to retrieve important cryptocurrency news from reliable sources
and provides functionality for categorizing, translating, and sentiment analysis of news.
"""

import os
import logging
import requests
import json
import time
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import trafilatura
from openai import OpenAI
from typing import List, Dict, Any, Optional

# Add access to the new cryptocurrency news API
try:
    from crypto_bot.crypto_news_api import (
        get_crypto_news_from_api,
        get_canadian_crypto_news_from_api
    )
    HAS_NEWS_API = True
    logging.info("Cryptocurrency News API module loaded successfully")
except ImportError:
    HAS_NEWS_API = False
    logging.warning("Cryptocurrency News API module not found, using legacy sources")

# CMC Markets Canada news module
try:
    from crypto_bot.cmc_canada_news import (
        get_cmc_canada_news, 
        get_cmc_canada_crypto_analysis, 
        get_combined_cmc_canada_content,
        get_ndax_blog_news,
        get_bitbuy_blog_news,
        get_newton_learn_articles,
        get_all_canadian_crypto_news
    )
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("CMC Markets Canada news module not found. This news source will not be available.")
    
    def get_cmc_canada_news(max_items=5, use_cache=True):
        return []
    
    def get_cmc_canada_crypto_analysis(max_items=3, use_cache=True):
        return []
    
    def get_combined_cmc_canada_content(max_news=5, max_analysis=3, use_cache=True):
        return []
    
    def get_ndax_blog_news(max_items=5, use_cache=True):
        return []
    
    def get_bitbuy_blog_news(max_items=5, use_cache=True):
        return []
    
    def get_newton_learn_articles(max_items=5, use_cache=True):
        return []
    
    def get_all_canadian_crypto_news(max_per_source=3, use_cache=True):
        return []

# Setup logger
logger = logging.getLogger(__name__)

# API settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CRYPTOCOMPARE_API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY")

# Set Toronto timezone
toronto_tz = pytz.timezone('America/Toronto')


def get_cryptocompare_news(limit: int = 10, lang: str = "EN") -> List[Dict[str, Any]]:
    """
    Get news from CryptoCompare API
    
    Args:
        limit (int): Number of news items needed
        lang (str): News language
        
    Returns:
        List[Dict[str, Any]]: List of retrieved news items
    """
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/news/?lang={lang}&api_key={CRYPTOCOMPARE_API_KEY}&limit={limit}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "Success" or data.get("Type") == 100:
                return data.get("Data", [])
            else:
                logger.warning(f"Error in CryptoCompare response: {data.get('Message')}")
                return []
        else:
            logger.warning(f"Error in CryptoCompare request: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting news from CryptoCompare: {str(e)}")
        return []


def get_coindesk_news(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get news from CoinDesk website
    
    Args:
        limit (int): Number of news items needed
        
    Returns:
        List[Dict[str, Any]]: List of retrieved news items
    """
    try:
        url = "https://www.coindesk.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            for article in soup.select('article')[:limit]:
                try:
                    title_elem = article.select_one('h6') or article.select_one('h5') or article.select_one('h4')
                    link_elem = article.select_one('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get('href', '')
                        if not link.startswith('http'):
                            link = f"https://www.coindesk.com{link}"
                        
                        # Get image if available
                        img_elem = article.select_one('img')
                        image_url = img_elem.get('src', '') if img_elem else ''
                        
                        articles.append({
                            "title": title,
                            "url": link,
                            "imageurl": image_url,
                            "source": "CoinDesk",
                            "published_on": int(time.time())
                        })
                except Exception as e:
                    logger.error(f"Error processing CoinDesk article: {str(e)}")
                    continue
            
            return articles
        else:
            logger.warning(f"Error in CoinDesk request: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting news from CoinDesk: {str(e)}")
        return []


def get_cointelegraph_news(limit: int = 5) -> List[Dict[str, Any]]:
    """
    دریافت اخبار از وب‌سایت CoinTelegraph
    
    Args:
        limit (int): تعداد اخبار مورد نیاز
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار دریافت شده
    """
    try:
        url = "https://cointelegraph.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # مقالات اصلی
            for article in soup.select('.post-card')[:limit]:
                try:
                    title_elem = article.select_one('.post-card__title')
                    link_elem = article.select_one('a.post-card__link')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get('href', '')
                        if not link.startswith('http'):
                            link = f"https://cointelegraph.com{link}"
                        
                        # دریافت تصویر اگر موجود باشد
                        img_elem = article.select_one('img')
                        image_url = img_elem.get('src', '') if img_elem else ''
                        
                        articles.append({
                            "title": title,
                            "url": link,
                            "imageurl": image_url,
                            "source": "CoinTelegraph",
                            "published_on": int(time.time())
                        })
                except Exception as e:
                    logger.error(f"خطا در پردازش مقاله CoinTelegraph: {str(e)}")
                    continue
            
            return articles
        else:
            logger.warning(f"خطا در درخواست CoinTelegraph: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"خطا در دریافت اخبار از CoinTelegraph: {str(e)}")
        return []


def extract_article_content(url: str) -> str:
    """
    استخراج محتوای مقاله از URL
    
    Args:
        url (str): آدرس مقاله
        
    Returns:
        str: محتوای استخراج شده مقاله
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return text
        
        # اگر trafilatura نتواند محتوا را استخراج کند، روش جایگزین
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # حذف المان‌های غیرضروری
            for elem in soup(['script', 'style', 'nav', 'footer', 'header']):
                elem.decompose()
            
            # گرفتن محتوای اصلی
            article_content = soup.select_one('article') or soup.select_one('.article-content') or soup.select_one('.content')
            if article_content:
                return article_content.get_text(separator='\n').strip()
            
            # اگر محتوای اصلی پیدا نشد، از متن کل صفحه استفاده می‌کنیم
            return soup.get_text(separator='\n').strip()
        
        return ""
    except Exception as e:
        logger.error(f"خطا در استخراج محتوای مقاله: {str(e)}")
        return ""


def translate_news(news_items: List[Dict[str, Any]], target_language: str = "fa") -> List[Dict[str, Any]]:
    """
    ترجمه عناوین اخبار با استفاده از OpenAI API
    
    Args:
        news_items (List[Dict[str, Any]]): لیست اخبار
        target_language (str): زبان مقصد (fa برای فارسی)
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار با عناوین ترجمه شده
    """
    if not OPENAI_API_KEY or not news_items:
        return news_items
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        translated_items = []
        
        # ترجمه هر ۴ خبر در یک درخواست
        for i in range(0, len(news_items), 4):
            batch = news_items[i:i+4]
            titles = [item['title'] for item in batch]
            
            # ساخت پرامپت به صورت دستی و با استفاده از + برای چسباندن رشته‌ها به جای f-string
            titles_formatted = "\n".join([f"{idx+1}. {title}" for idx, title in enumerate(titles)])
            prompt = "ترجمه عناوین زیر از انگلیسی به فارسی به صورت طبیعی و روان:\n\n" + titles_formatted + "\n\nپاسخ را فقط به صورت عناوین ترجمه شده با شماره بدهید، بدون هیچ توضیح یا مقدمه."
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            
            translation_text = response.choices[0].message.content.strip()
            
            # پردازش ترجمه‌ها
            translations = []
            for line in translation_text.split('\n'):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, 10)):
                    # حذف شماره از ابتدای خط
                    translations.append(line.split('.', 1)[1].strip())
            
            # اعمال ترجمه به اخبار
            for j, item in enumerate(batch):
                if j < len(translations):
                    translated_title = translations[j]
                    item['title_fa'] = translated_title
                else:
                    item['title_fa'] = item['title']  # اگر ترجمه موفق نبود، از عنوان اصلی استفاده می‌کنیم
                
                translated_items.append(item)
        
        return translated_items
    except Exception as e:
        logger.error(f"Error translating news: {str(e)}")
        # If translation fails, return the original news
        for item in news_items:
            item['title_fa'] = item['title']
        return news_items


def get_crypto_news(limit: int = 10, translate: bool = True, include_canada: bool = True) -> List[Dict[str, Any]]:
    """
    دریافت و ترکیب اخبار از منابع مختلف
    
    Args:
        limit (int): تعداد کل اخبار مورد نیاز
        translate (bool): آیا اخبار ترجمه شوند
        include_canada (bool): آیا اخبار بازار کانادا شامل شود
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار ترکیب شده
    """
    # اول سعی کنیم از API جدید استفاده کنیم
    if HAS_NEWS_API:
        try:
            logger.info("Attempting to get news from specialized API...")
            api_news = get_crypto_news_from_api(items_per_page=limit)
            
            if api_news:
                logger.info(f"{len(api_news)} news items received from specialized API")
                
                # Add Canadian news if needed
                if include_canada:
                    canada_news = get_canadian_crypto_news_from_api(items_per_page=limit // 2)
                    if canada_news:
                        logger.info(f"{len(canada_news)} Canadian news items received from specialized API")
                        # ادغام اخبار با اطمینان از عدم تکرار
                        seen_urls = {item['url'] for item in api_news}
                        for item in canada_news:
                            if item['url'] not in seen_urls:
                                api_news.append(item)
                                seen_urls.add(item['url'])
                
                # ترجمه عناوین اخبار به فارسی اگر لازم است
                if translate and OPENAI_API_KEY:
                    try:
                        api_news = translate_news(api_news)
                    except Exception as e:
                        logger.error(f"Error translating news: {str(e)}")
                        # If translation fails, fill the Persian title field with the English title
                        for item in api_news:
                            if 'title_fa' not in item:
                                item['title_fa'] = item['title']
                else:
                    # اگر ترجمه نیاز نیست، عنوان انگلیسی را کپی می‌کنیم
                    for item in api_news:
                        item['title_fa'] = item['title']
                
                # تبدیل timestamp به تاریخ و زمان خوانا
                for item in api_news:
                    if 'published_at' in item and not item.get('published_date'):
                        try:
                            # تبدیل ISO format به datetime
                            dt = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                            dt_toronto = dt.astimezone(toronto_tz)
                            item['published_date'] = dt_toronto.strftime('%Y-%m-%d %H:%M')
                            # اضافه کردن published_on برای سازگاری با فرمت قدیمی
                            if 'published_on' not in item:
                                item['published_on'] = int(dt.timestamp())
                        except Exception as dt_error:
                            logger.error(f"خطا در تبدیل تاریخ: {str(dt_error)}")
                            item['published_date'] = datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M')
                            item['published_on'] = int(time.time())
                
                # مرتب‌سازی بر اساس زمان انتشار
                api_news.sort(key=lambda x: x.get('published_on', 0), reverse=True)
                
                # محدود کردن تعداد اخبار
                return api_news[:limit]
        except Exception as api_err:
            logger.error(f"خطا در دریافت اخبار از API تخصصی: {str(api_err)}")
            # ادامه با روش قدیمی در صورت خطا
    
    # اگر API جدید در دسترس نباشد یا خطا داشته باشد، از روش قدیمی استفاده می‌کنیم
    logger.warning("Using old sources to retrieve news")
    
    # تعیین تعداد اخبار از هر منبع
    source_count = 4 if include_canada else 3
    per_source = limit // source_count + 1
    
    # دریافت اخبار از منابع مختلف
    cryptocompare_news = get_cryptocompare_news(limit=per_source)
    coindesk_news = get_coindesk_news(limit=per_source)
    cointelegraph_news = get_cointelegraph_news(limit=per_source)
    
    # ترکیب اخبار
    all_news = []
    all_news.extend(cryptocompare_news)
    all_news.extend(coindesk_news)
    all_news.extend(cointelegraph_news)
    
    # اضافه کردن اخبار CMC Markets Canada
    if include_canada:
        try:
            # دریافت اخبار و تحلیل‌های CMC Markets Canada
            cmc_canada_content = get_combined_cmc_canada_content(max_news=per_source, max_analysis=2)
            
            # تبدیل فرمت اخبار CMC Markets Canada به فرمت استاندارد
            for item in cmc_canada_content:
                # اضافه کردن فیلدهای ضروری
                if 'published_on' not in item:
                    item['published_on'] = int(time.time())
                
                # افزودن منبع اگر وجود ندارد
                if 'source' not in item:
                    item['source'] = 'CMC Markets Canada'
                
                # تبدیل URL تصویر
                if 'image_url' in item and 'imageurl' not in item:
                    item['imageurl'] = item['image_url']
                
                # افزودن برچسب‌های اضافی
                if 'tags' not in item:
                    item['tags'] = ['canada', 'market']
                elif 'canada' not in item['tags']:
                    item['tags'].append('canada')
                
                # اضافه کردن به لیست کل
                all_news.append(item)
            
            logger.info(f"Added {len(cmc_canada_content)} news items from CMC Markets Canada")
        except Exception as e:
            logger.error(f"Error fetching CMC Markets Canada content: {str(e)}")
    
    # مرتب‌سازی بر اساس زمان انتشار (جدیدترین اخبار ابتدا)
    all_news.sort(key=lambda x: x.get('published_on', 0), reverse=True)
    
    # محدود کردن تعداد اخبار
    all_news = all_news[:limit]
    
    # ترجمه عناوین اخبار به فارسی
    try:
        if translate and OPENAI_API_KEY:
            # برای جلوگیری از خطای محدودیت API، تعداد اخبار برای ترجمه را محدود می‌کنیم
            max_translate_items = min(5, len(all_news))
            news_to_translate = all_news[:max_translate_items]
            
            logger.info(f"Translating {max_translate_items} news items out of {len(all_news)} total")
            translated_news = translate_news(news_to_translate)
            
            # اخباری که ترجمه نشدند را اضافه می‌کنیم
            for i in range(max_translate_items, len(all_news)):
                all_news[i]['title_fa'] = all_news[i]['title']
                
            # جایگزینی اخبار ترجمه شده
            all_news[:max_translate_items] = translated_news
        else:
            # اگر ترجمه نیاز نیست یا امکان آن وجود ندارد
            for item in all_news:
                item['title_fa'] = item['title']
    except Exception as e:
        logger.error(f"Error in news translation in main function: {str(e)}")
        # In case of any error, all titles will be displayed in English
        for item in all_news:
            item['title_fa'] = item['title']
    
    # تبدیل timestamp به تاریخ و زمان خوانا بر اساس منطقه زمانی تورنتو
    for item in all_news:
        if 'published_on' in item:
            dt_utc = datetime.utcfromtimestamp(item['published_on'])
            dt_toronto = dt_utc.replace(tzinfo=pytz.utc).astimezone(toronto_tz)
            item['published_date'] = dt_toronto.strftime('%Y-%m-%d %H:%M')
    
    return all_news


def get_crypto_sentiment_analysis() -> Dict[str, Any]:
    """
    دریافت تحلیل احساسات بازار ارزهای دیجیتال
    
    Returns:
        Dict[str, Any]: تحلیل احساسات بازار
    """
    # اگر Open AI API در دسترس نباشد، داده ساده برمی‌گردانیم
    if not OPENAI_API_KEY:
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 50,
            "bitcoin_sentiment": "neutral",
            "ethereum_sentiment": "neutral",
            "updated_at": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M'),
            "data_available": False
        }
    
    # اول سعی می‌کنیم نتایج قبلی را برگردانیم اگر خیلی قدیمی نباشند
    # در اینجا استفاده از یک حافظه نهان ساده برای محدود کردن فراخوانی‌های API
    cached_sentiment_file = os.path.join(os.path.dirname(__file__), "cached_sentiment.json")
    try:
        if os.path.exists(cached_sentiment_file):
            with open(cached_sentiment_file, 'r') as f:
                cached_data = json.load(f)
                
            # بررسی اعتبار داده‌های حافظه نهان (کمتر از 30 دقیقه)
            cached_time = cached_data.get("cached_at", 0)
            if time.time() - cached_time < 1800:  # 30 دقیقه
                logger.info("Using cached sentiment analysis (less than 30 minutes old)")
                return cached_data
            else:
                logger.info("Cached sentiment analysis has expired (more than 30 minutes old)")
    except Exception as cache_err:
        logger.error(f"Error reading cached sentiment analysis: {str(cache_err)}")
    
    try:
        # دریافت چند خبر برای تحلیل
        news = get_crypto_news(limit=5, translate=False)
        
        # اگر خبری دریافت نشد
        if not news:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 50,
                "bitcoin_sentiment": "neutral",
                "ethereum_sentiment": "neutral",
                "updated_at": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M'),
                "data_available": False
            }
        
        # آماده‌سازی محتوا برای تحلیل
        news_titles = "\n".join([f"- {item['title']}" for item in news])
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # ساخت پرامپت به صورت دستی بدون استفاده از f-string با حروف فارسی
        prompt_first_part = "با توجه به عناوین اخبار زیر، تحلیل احساسات بازار رمزارزها را انجام دهید:\n\n"
        prompt_second_part = """

لطفاً نتایج را به صورت یک JSON با این ساختار برگردانید:
{
  "overall_sentiment": "bullish/neutral/bearish",
  "sentiment_score": <عدد بین 0 تا 100. 0 کاملاً bearish، 50 neutral، 100 کاملاً bullish>,
  "bitcoin_sentiment": "bullish/neutral/bearish",
  "ethereum_sentiment": "bullish/neutral/bearish",
  "short_analysis": "<یک یا دو جمله تحلیل کلی به فارسی>"
}
"""
        prompt = prompt_first_part + news_titles + prompt_second_part
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # اضافه کردن زمان به‌روزرسانی
        result["updated_at"] = datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M')
        result["data_available"] = True
        
        # ذخیره نتیجه در حافظه نهان
        try:
            result["cached_at"] = time.time()
            with open(cached_sentiment_file, 'w') as f:
                json.dump(result, f)
            logger.info("Sentiment analysis saved in cache")
        except Exception as cache_err:
            logger.error(f"Error saving sentiment analysis in cache: {str(cache_err)}")
        
        return result
    except Exception as e:
        logger.error(f"Error in market sentiment analysis: {str(e)}")
        
        # If there was an error, try to use the cached data even if it's expired
        try:
            if os.path.exists(cached_sentiment_file):
                with open(cached_sentiment_file, 'r') as f:
                    cached_data = json.load(f)
                logger.info("Using expired cached sentiment analysis due to error")
                return cached_data
        except Exception as cache_err:
            logger.error(f"Error reading expired cached sentiment analysis: {str(cache_err)}")
        
        # If the cache also had a problem, we return default data
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 50,
            "bitcoin_sentiment": "neutral",
            "ethereum_sentiment": "neutral",
            "updated_at": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M'),
            "data_available": False,
            "error": str(e)
        }


def get_fear_greed_index() -> Dict[str, Any]:
    """
    Get Fear and Greed index of the market
    
    Returns:
        Dict[str, Any]: Fear and Greed index data
    """
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("metadata", {}).get("error") is None:
                fng_data = data.get("data", [{}])[0]
                
                # Convert date to Toronto timezone
                time_until_update = fng_data.get("time_until_update", "")
                timestamp = int(fng_data.get("timestamp", "0"))
                dt_utc = datetime.utcfromtimestamp(timestamp)
                dt_toronto = dt_utc.replace(tzinfo=pytz.utc).astimezone(toronto_tz)
                
                return {
                    "value": int(fng_data.get("value", 50)),
                    "value_classification": fng_data.get("value_classification", "Neutral"),
                    "timestamp": timestamp,
                    "date": dt_toronto.strftime('%Y-%m-%d %H:%M'),
                    "time_until_update": time_until_update,
                    "data_available": True
                }
        
        # If data is not available or we encounter an error
        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": int(time.time()),
            "date": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M'),
            "data_available": False
        }
    except Exception as e:
        logger.error(f"Error retrieving fear and greed index: {str(e)}")
        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": int(time.time()),
            "date": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M'),
            "data_available": False,
            "error": str(e)
        }


def get_market_insights() -> Dict[str, Any]:
    """
    Get market insights and analysis for cryptocurrencies
    
    Returns:
        Dict[str, Any]: Market insights and analysis data
    """
    # Get various data
    news = get_crypto_news(limit=8, translate=True, include_canada=True)
    sentiment = get_crypto_sentiment_analysis()
    fear_greed = get_fear_greed_index()
    
    # Get CMC Markets Canada news separately
    cmc_canada_content = []
    try:
        cmc_canada_content = get_combined_cmc_canada_content(max_news=3, max_analysis=2)
        logger.info(f"Retrieved {len(cmc_canada_content)} items from CMC Markets Canada")
    except Exception as e:
        logger.error(f"Error getting CMC Markets Canada content: {str(e)}")
    
    # Combine and return the data
    return {
        "news": news,
        "sentiment": sentiment,
        "fear_greed_index": fear_greed,
        "cmc_canada": cmc_canada_content,
        "updated_at": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M')
    }


def format_market_insights_for_telegram(insights: Dict[str, Any]) -> str:
    """
    Format market insights for sending to Telegram
    
    Args:
        insights (Dict[str, Any]): Market insights data
        
    Returns:
        str: Formatted text for Telegram
    """
    news = insights.get('news', [])
    sentiment = insights.get('sentiment', {})
    fear_greed = insights.get('fear_greed_index', {})
    cmc_canada = insights.get('cmc_canada', [])
    
    # Set emoji based on market sentiment
    sentiment_emoji = "😐"  # neutral by default
    if sentiment.get('overall_sentiment') == 'bullish':
        sentiment_emoji = "🚀"
    elif sentiment.get('overall_sentiment') == 'bearish':
        sentiment_emoji = "🐻"
    
    # Set emoji for fear and greed index
    fng_value = fear_greed.get('value', 50)
    fng_emoji = "😐"  # neutral by default
    if fng_value >= 75:
        fng_emoji = "😈"  # extreme greed
    elif fng_value >= 55:
        fng_emoji = "😀"  # greed
    elif fng_value <= 25:
        fng_emoji = "😱"  # extreme fear
    elif fng_value <= 45:
        fng_emoji = "😨"  # fear
    
    # Build the main text using an alternative method to avoid f-string issues with non-English characters
    message_parts = [
        "🌐 *گزارش روزانه بازار ارزهای دیجیتال* 🌐",
        f"تاریخ: {insights.get('updated_at')}",
        "",
        f"{sentiment_emoji} *تحلیل احساسات بازار:*",
        f"• وضعیت کلی: {sentiment.get('overall_sentiment', 'نامشخص')}",
        f"• امتیاز: {sentiment.get('sentiment_score', 50)}",
        f"• بیت‌کوین: {sentiment.get('bitcoin_sentiment', 'نامشخص')}",
        f"• اتریوم: {sentiment.get('ethereum_sentiment', 'نامشخص')}",
        "",
        f"{fng_emoji} *شاخص ترس و طمع:*",
        f"• عدد: {fear_greed.get('value', 'نامشخص')}",
        f"• وضعیت: {fear_greed.get('value_classification', 'نامشخص')}",
        "",
        "📰 *آخرین اخبار:*"
    ]
    message = "\n".join(message_parts)
    
    # Add news
    news_count = 0
    for i, item in enumerate(news[:4], 1):
        # Use the English title if available
        title = item.get('title_fa', item.get('title', ''))
        url = item.get('url', '')
        source = item.get('source', '')
        published_date = item.get('published_date', '')
        
        message += f"\n{i}. [{title}]({url})"
        message += f"\n   منبع: {source} | {published_date}"
        news_count += 1
    
    # Add CMC Markets Canada news
    if cmc_canada:
        # If news was already added, create a line break
        if news_count > 0:
            message += "\n"
        
        message += "\n🇨🇦 *تحلیل بازار کانادا:*"
        
        for i, item in enumerate(cmc_canada[:2], news_count + 1):
            title = item.get('title_fa', item.get('title', ''))
            url = item.get('url', '')
            source = "CMC Markets Canada"
            content_type = item.get('content_type', 'news')
            
            # Select appropriate emoji for content type
            emoji = "📊" if content_type == 'analysis' else "📰"
            
            message += f"\n{i}. {emoji} [{title}]({url})"
            message += f"\n   منبع: {source}"
    
    # Add short analysis
    if sentiment.get('short_analysis'):
        message += f"\n\n🔍 *تحلیل کوتاه:*\n{sentiment.get('short_analysis')}"
    
    return message


def get_crypto_news_formatted_for_telegram() -> str:
    """
    Get cryptocurrency news formatted for Telegram
    
    Returns:
        str: Formatted text for Telegram
    """
    insights = get_market_insights()
    return format_market_insights_for_telegram(insights)


if __name__ == "__main__":
    # Module test
    print("Getting cryptocurrency news...")
    news = get_crypto_news(limit=5, translate=True)
    for item in news:
        print(f"Title: {item.get('title')}")
        print(f"Translation: {item.get('title_fa', '')}")
        print(f"Source: {item.get('source')}")
        print(f"Date: {item.get('published_date', '')}")
        print(f"Link: {item.get('url')}")
        print("-" * 50)
    
    print("\nMarket Sentiment Analysis:")
    sentiment = get_crypto_sentiment_analysis()
    print(json.dumps(sentiment, indent=2, ensure_ascii=False))
    
    print("\nFear and Greed Index:")
    fear_greed = get_fear_greed_index()
    print(json.dumps(fear_greed, indent=2, ensure_ascii=False))
    
    print("\nTelegram Report:")
    telegram_message = get_crypto_news_formatted_for_telegram()
    print(telegram_message)