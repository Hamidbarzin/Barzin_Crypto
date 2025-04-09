"""
ماژول دریافت و پردازش اخبار ارزهای دیجیتال

این ماژول برای دریافت اخبار مهم ارزهای دیجیتال از منابع معتبر استفاده می‌شود
و قابلیت دسته‌بندی، ترجمه و تحلیل احساسات اخبار را نیز فراهم می‌کند.
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

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیمات API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CRYPTOCOMPARE_API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY")

# تنظیم منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')


def get_cryptocompare_news(limit: int = 10, lang: str = "EN") -> List[Dict[str, Any]]:
    """
    دریافت اخبار از CryptoCompare API
    
    Args:
        limit (int): تعداد اخبار مورد نیاز
        lang (str): زبان اخبار
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار دریافت شده
    """
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/news/?lang={lang}&api_key={CRYPTOCOMPARE_API_KEY}&limit={limit}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "Success" or data.get("Type") == 100:
                return data.get("Data", [])
            else:
                logger.warning(f"خطا در پاسخ CryptoCompare: {data.get('Message')}")
                return []
        else:
            logger.warning(f"خطا در درخواست CryptoCompare: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"خطا در دریافت اخبار از CryptoCompare: {str(e)}")
        return []


def get_coindesk_news(limit: int = 5) -> List[Dict[str, Any]]:
    """
    دریافت اخبار از وب‌سایت CoinDesk
    
    Args:
        limit (int): تعداد اخبار مورد نیاز
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار دریافت شده
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
                        
                        # دریافت تصویر اگر موجود باشد
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
                    logger.error(f"خطا در پردازش مقاله CoinDesk: {str(e)}")
                    continue
            
            return articles
        else:
            logger.warning(f"خطا در درخواست CoinDesk: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"خطا در دریافت اخبار از CoinDesk: {str(e)}")
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
        logger.error(f"خطا در ترجمه اخبار: {str(e)}")
        # اگر ترجمه با خطا مواجه شود، اخبار اصلی را برمی‌گردانیم
        for item in news_items:
            item['title_fa'] = item['title']
        return news_items


def get_crypto_news(limit: int = 10, translate: bool = True) -> List[Dict[str, Any]]:
    """
    دریافت و ترکیب اخبار از منابع مختلف
    
    Args:
        limit (int): تعداد کل اخبار مورد نیاز
        translate (bool): آیا اخبار ترجمه شوند
        
    Returns:
        List[Dict[str, Any]]: لیست اخبار ترکیب شده
    """
    # تعیین تعداد اخبار از هر منبع
    per_source = limit // 3 + 1
    
    # دریافت اخبار از منابع مختلف
    cryptocompare_news = get_cryptocompare_news(limit=per_source)
    coindesk_news = get_coindesk_news(limit=per_source)
    cointelegraph_news = get_cointelegraph_news(limit=per_source)
    
    # ترکیب اخبار
    all_news = []
    all_news.extend(cryptocompare_news)
    all_news.extend(coindesk_news)
    all_news.extend(cointelegraph_news)
    
    # مرتب‌سازی بر اساس زمان انتشار (جدیدترین اخبار ابتدا)
    all_news.sort(key=lambda x: x.get('published_on', 0), reverse=True)
    
    # محدود کردن تعداد اخبار
    all_news = all_news[:limit]
    
    # ترجمه عناوین اخبار به فارسی
    if translate and OPENAI_API_KEY:
        all_news = translate_news(all_news)
    else:
        # اگر ترجمه نیاز نیست یا امکان آن وجود ندارد
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
        
        return result
    except Exception as e:
        logger.error(f"خطا در تحلیل احساسات بازار: {str(e)}")
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
    دریافت شاخص ترس و طمع بازار
    
    Returns:
        Dict[str, Any]: شاخص ترس و طمع
    """
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("metadata", {}).get("error") is None:
                fng_data = data.get("data", [{}])[0]
                
                # تبدیل تاریخ به منطقه زمانی تورنتو
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
        
        # اگر داده در دسترس نباشد یا با خطا مواجه شویم
        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": int(time.time()),
            "date": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M'),
            "data_available": False
        }
    except Exception as e:
        logger.error(f"خطا در دریافت شاخص ترس و طمع: {str(e)}")
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
    دریافت بینش‌ها و تحلیل‌های بازار ارزهای دیجیتال
    
    Returns:
        Dict[str, Any]: بینش‌ها و تحلیل‌های بازار
    """
    # دریافت داده‌های مختلف
    news = get_crypto_news(limit=8, translate=True)
    sentiment = get_crypto_sentiment_analysis()
    fear_greed = get_fear_greed_index()
    
    # ترکیب و برگرداندن داده‌ها
    return {
        "news": news,
        "sentiment": sentiment,
        "fear_greed_index": fear_greed,
        "updated_at": datetime.now(toronto_tz).strftime('%Y-%m-%d %H:%M')
    }


def format_market_insights_for_telegram(insights: Dict[str, Any]) -> str:
    """
    قالب‌بندی بینش‌های بازار برای ارسال به تلگرام
    
    Args:
        insights (Dict[str, Any]): بینش‌های بازار
        
    Returns:
        str: متن قالب‌بندی شده برای تلگرام
    """
    news = insights.get('news', [])
    sentiment = insights.get('sentiment', {})
    fear_greed = insights.get('fear_greed_index', {})
    
    # تنظیم ایموجی بر اساس احساسات بازار
    sentiment_emoji = "😐"  # neutral by default
    if sentiment.get('overall_sentiment') == 'bullish':
        sentiment_emoji = "🚀"
    elif sentiment.get('overall_sentiment') == 'bearish':
        sentiment_emoji = "🐻"
    
    # تنظیم ایموجی برای شاخص ترس و طمع
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
    
    # ساخت متن اصلی با استفاده از روش جایگزین برای اجتناب از مشکلات f-string با حروف فارسی
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
    
    # اضافه کردن اخبار
    for i, item in enumerate(news[:5], 1):
        # استفاده از نسخه فارسی عنوان اگر موجود باشد
        title = item.get('title_fa', item.get('title', ''))
        url = item.get('url', '')
        source = item.get('source', '')
        published_date = item.get('published_date', '')
        
        message += f"\n{i}. [{title}]({url})"
        message += f"\n   منبع: {source} | {published_date}"
    
    # اضافه کردن تحلیل
    if sentiment.get('short_analysis'):
        message += f"\n\n🔍 *تحلیل کوتاه:*\n{sentiment.get('short_analysis')}"
    
    return message


def get_crypto_news_formatted_for_telegram() -> str:
    """
    دریافت اخبار ارزهای دیجیتال با قالب‌بندی مناسب برای تلگرام
    
    Returns:
        str: متن قالب‌بندی شده برای تلگرام
    """
    insights = get_market_insights()
    return format_market_insights_for_telegram(insights)


if __name__ == "__main__":
    # تست ماژول
    print("دریافت اخبار ارزهای دیجیتال...")
    news = get_crypto_news(limit=5, translate=True)
    for item in news:
        print(f"عنوان: {item.get('title')}")
        print(f"ترجمه: {item.get('title_fa', '')}")
        print(f"منبع: {item.get('source')}")
        print(f"تاریخ: {item.get('published_date', '')}")
        print(f"لینک: {item.get('url')}")
        print("-" * 50)
    
    print("\nتحلیل احساسات بازار:")
    sentiment = get_crypto_sentiment_analysis()
    print(json.dumps(sentiment, indent=2, ensure_ascii=False))
    
    print("\nشاخص ترس و طمع:")
    fear_greed = get_fear_greed_index()
    print(json.dumps(fear_greed, indent=2, ensure_ascii=False))
    
    print("\nگزارش تلگرام:")
    telegram_message = get_crypto_news_formatted_for_telegram()
    print(telegram_message)