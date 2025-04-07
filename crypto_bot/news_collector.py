"""
ماژول جمع‌آوری اخبار مرتبط با ارزهای دیجیتال
"""
import os
import logging
import requests
from datetime import datetime, timedelta
import json

# تنظیم لاگر
logger = logging.getLogger(__name__)

class NewsCollector:
    """
    کلاس جمع‌آوری اخبار مرتبط با ارزهای دیجیتال از منابع مختلف
    """
    
    def __init__(self):
        # تنظیم کلیدهای API و منابع خبری
        self.news_sources = [
            {"name": "CryptoCompare", "enabled": True},
            {"name": "CoinDesk", "enabled": False},
            {"name": "CoinTelegraph", "enabled": False}
        ]
    
    def get_recent_news(self, limit=10, include_middle_east=True):
        """
        دریافت اخبار اخیر در حوزه ارزهای دیجیتال
        
        Args:
            limit (int): حداکثر تعداد اخبار
            include_middle_east (bool): آیا منابع خاورمیانه در نظر گرفته شوند
            
        Returns:
            list: لیست اخبار
        """
        news_list = []
        
        try:
            # دریافت اخبار از CryptoCompare
            crypto_compare_news = self._get_cryptocompare_news(limit=limit)
            news_list.extend(crypto_compare_news)
            
            # در صورت نیاز، اخبار منابع دیگر را اضافه کنید
            
            # دریافت اخبار خاورمیانه در صورت نیاز
            if include_middle_east:
                middle_east_news = self._get_middle_east_news(limit=3)
                news_list.extend(middle_east_news)
            
            # محدود کردن تعداد اخبار به limit
            return news_list[:limit]
            
        except Exception as e:
            logger.error(f"خطا در دریافت اخبار: {str(e)}")
            return []
    
    def get_news_about_coin(self, coin_symbol, limit=5):
        """
        دریافت اخبار مرتبط با یک ارز دیجیتال خاص
        
        Args:
            coin_symbol (str): نماد ارز دیجیتال
            limit (int): حداکثر تعداد اخبار
            
        Returns:
            list: لیست اخبار
        """
        try:
            # دریافت همه اخبار
            all_news = self.get_recent_news(limit=20)
            
            # فیلتر کردن اخبار مرتبط با ارز مورد نظر
            coin_news = []
            coin_name = self._get_coin_full_name(coin_symbol)
            
            for news in all_news:
                if (coin_symbol.upper() in news['title'].upper() or 
                    (coin_name and coin_name.upper() in news['title'].upper())):
                    coin_news.append(news)
            
            return coin_news[:limit]
            
        except Exception as e:
            logger.error(f"خطا در دریافت اخبار برای {coin_symbol}: {str(e)}")
            return []
    
    def _get_cryptocompare_news(self, limit=10):
        """
        دریافت اخبار از CryptoCompare
        
        Args:
            limit (int): حداکثر تعداد اخبار
            
        Returns:
            list: لیست اخبار
        """
        try:
            # به دلیل مشکلات دسترسی به API، فعلاً داده‌های ثابت برای تست برمی‌گردانیم
            # در نسخه تولید، باید از API واقعی استفاده شود
            url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                for item in data.get('Data', [])[:limit]:
                    news_list.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'source': item.get('source', ''),
                        'date': datetime.fromtimestamp(item.get('published_on', 0)).strftime('%Y-%m-%d %H:%M'),
                        'summary': item.get('body', '')[:150] + '...' if item.get('body') else ''
                    })
                
                return news_list
            else:
                logger.error(f"خطا در دریافت اخبار از CryptoCompare: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"خطا در دریافت اخبار از CryptoCompare: {str(e)}")
            return []
    
    def _get_middle_east_news(self, limit=3):
        """
        دریافت اخبار مرتبط با ارزهای دیجیتال از منابع خاورمیانه
        
        Args:
            limit (int): حداکثر تعداد اخبار
            
        Returns:
            list: لیست اخبار
        """
        # در نسخه واقعی، این تابع باید به منابع خبری فارسی یا عربی متصل شود
        # در حال حاضر، برای نمونه خبرهای ثابتی را برمی‌گرداند
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        news_list = [
            {
                'title': 'اخبار مرتبط با ارزهای دیجیتال در منطقه خاورمیانه',
                'source': 'منابع خبری منطقه',
                'date': current_date,
                'summary': 'این بخش برای نمایش اخبار منطقه خاورمیانه در نظر گرفته شده است.'
            }
        ]
        
        return news_list[:limit]
    
    def _get_coin_full_name(self, symbol):
        """
        تبدیل نماد ارز به نام کامل آن
        
        Args:
            symbol (str): نماد ارز دیجیتال
            
        Returns:
            str: نام کامل ارز
        """
        # نگاشت نمادهای پرکاربرد به نام کامل آنها
        coin_names = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "BNB": "Binance Coin",
            "XRP": "Ripple",
            "ADA": "Cardano",
            "SOL": "Solana",
            "DOT": "Polkadot",
            "DOGE": "Dogecoin",
            "AVAX": "Avalanche",
            "LUNA": "Terra Luna"
        }
        
        # حذف پسوند /USDT یا مشابه آن
        if '/' in symbol:
            symbol = symbol.split('/')[0]
        
        return coin_names.get(symbol.upper(), symbol)

news_collector = NewsCollector()

def get_recent_news(limit=10, include_middle_east=True):
    """
    دریافت اخبار اخیر در حوزه ارزهای دیجیتال
    
    Args:
        limit (int): حداکثر تعداد اخبار
        include_middle_east (bool): آیا منابع خاورمیانه در نظر گرفته شوند
        
    Returns:
        list: لیست اخبار
    """
    return news_collector.get_recent_news(limit, include_middle_east)

def get_news_about_coin(coin_symbol, limit=5):
    """
    دریافت اخبار مرتبط با یک ارز دیجیتال خاص
    
    Args:
        coin_symbol (str): نماد ارز دیجیتال
        limit (int): حداکثر تعداد اخبار
        
    Returns:
        list: لیست اخبار
    """
    return news_collector.get_news_about_coin(coin_symbol, limit)