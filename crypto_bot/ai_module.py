"""
ماژول هوش مصنوعی و یادگیری ماشین برای تحلیل و پیش‌بینی بازار ارزهای دیجیتال
"""

import datetime
import random
import numpy as np
import logging

from crypto_bot.market_data import get_historical_data
from crypto_bot.news_analyzer import get_latest_news, analyze_sentiment

# راه‌اندازی سیستم ثبت لاگ
logger = logging.getLogger(__name__)

# کلاس مدل پیش‌بینی قیمت
class PricePredictionModel:
    """
    این کلاس الگوریتم‌های یادگیری ماشین را برای پیش‌بینی قیمت ارزهای دیجیتال پیاده‌سازی می‌کند.
    
    در نسخه فعلی، این مدل از داده‌های نمونه استفاده می‌کند، اما در نسخه‌های آینده،
    می‌توان از مدل‌های واقعی یادگیری ماشین مانند LSTM، پرسپترون چندلایه، یا الگوریتم‌های جنگل تصادفی استفاده کرد.
    """
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.model_type = "هوش مصنوعی ترکیبی"
        self.accuracy = round(random.uniform(78, 92), 2)  # دقت مدل (برای نمایش)
        self.confidence = round(random.uniform(0.65, 0.95), 2)  # اطمینان پیش‌بینی
        
    def get_predictions(self, timeframe='24h'):
        """
        پیش‌بینی قیمت برای آینده
        
        Args:
            timeframe (str): بازه زمانی پیش‌بینی ('24h', '7d', '30d')
            
        Returns:
            dict: پیش‌بینی قیمت و اطلاعات مرتبط
        """
        # در نسخه واقعی، اینجا از مدل یادگیری ماشین استفاده می‌شود
        current_price = self._get_current_price()
        
        if not current_price:
            logger.warning(f"قیمت فعلی برای {self.symbol} یافت نشد")
            current_price = 100.0  # مقدار پیش‌فرض برای نمایش
        
        # محاسبه مقادیر پیش‌بینی بر اساس بازه زمانی
        if timeframe == '24h':
            prediction_factor = random.uniform(0.97, 1.05)
            time_horizon = "24 ساعت آینده"
            confidence_modifier = 1.0
        elif timeframe == '7d':
            prediction_factor = random.uniform(0.92, 1.12)
            time_horizon = "7 روز آینده"
            confidence_modifier = 0.9
        elif timeframe == '30d':
            prediction_factor = random.uniform(0.85, 1.25)
            time_horizon = "30 روز آینده"
            confidence_modifier = 0.7
        else:
            prediction_factor = random.uniform(0.97, 1.05)
            time_horizon = "24 ساعت آینده"
            confidence_modifier = 1.0
            
        # تعیین روند و حد بالا و پایین
        predicted_price = current_price * prediction_factor
        upper_bound = predicted_price * (1 + 0.03 * (1/confidence_modifier))
        lower_bound = predicted_price * (1 - 0.03 * (1/confidence_modifier))
        
        # محاسبه احتمال روند صعودی یا نزولی
        if predicted_price > current_price:
            trend = "صعودی"
            trend_probability = round(random.uniform(0.55, 0.95), 2)
        else:
            trend = "نزولی"
            trend_probability = round(random.uniform(0.55, 0.95), 2)
            
        # محاسبه تاریخ پیش‌بینی
        now = datetime.datetime.now()
        if timeframe == '24h':
            prediction_date = now + datetime.timedelta(hours=24)
        elif timeframe == '7d':
            prediction_date = now + datetime.timedelta(days=7)
        elif timeframe == '30d':
            prediction_date = now + datetime.timedelta(days=30)
        else:
            prediction_date = now + datetime.timedelta(hours=24)
            
        prediction_date_str = prediction_date.strftime("%Y-%m-%d %H:%M:%S")
            
        # ایجاد خروجی
        prediction = {
            'symbol': self.symbol,
            'current_price': current_price,
            'predicted_price': round(predicted_price, 2),
            'upper_bound': round(upper_bound, 2),
            'lower_bound': round(lower_bound, 2),
            'time_horizon': time_horizon,
            'trend': trend,
            'trend_probability': trend_probability,
            'model_accuracy': self.accuracy,
            'confidence': round(self.confidence * confidence_modifier, 2),
            'prediction_date': prediction_date_str,
            'prediction_factors': self._get_prediction_factors(),
            'is_sample_data': True,
            'model_type': self.model_type
        }
        
        return prediction
    
    def _get_current_price(self):
        """
        دریافت قیمت فعلی ارز
        """
        try:
            # اینجا می‌توان از توابع موجود برای دریافت قیمت استفاده کرد
            # برای سادگی، فعلاً از مقادیر نمونه استفاده می‌کنیم
            coin = self.symbol.split('/')[0] if '/' in self.symbol else self.symbol.split('-')[0]
            
            if coin.lower() == 'btc':
                return 82500
            elif coin.lower() == 'eth': 
                return 3200
            elif coin.lower() == 'bnb':
                return 560
            elif coin.lower() == 'xrp':
                return 0.52
            elif coin.lower() == 'sol':
                return 145
            elif coin.lower() == 'doge':
                return 0.15
            else:
                return 100.0
        except Exception as e:
            logger.error(f"خطا در دریافت قیمت فعلی: {str(e)}")
            return None
    
    def _get_prediction_factors(self):
        """
        عوامل مؤثر در پیش‌بینی قیمت را برمی‌گرداند
        """
        return {
            'technical_analysis': round(random.uniform(0.2, 0.8), 2),
            'market_sentiment': round(random.uniform(0.2, 0.8), 2),
            'news_impact': round(random.uniform(0.1, 0.6), 2),
            'trading_volume': round(random.uniform(0.2, 0.7), 2),
            'historical_patterns': round(random.uniform(0.3, 0.8), 2)
        }


class MarketSentimentAnalyzer:
    """
    تحلیل احساسات بازار با استفاده از الگوریتم‌های هوش مصنوعی
    """
    
    def __init__(self):
        self.sources = ["اخبار", "شبکه‌های اجتماعی", "فروم‌های تخصصی", "داده‌های بازار"]
    
    def analyze_market_sentiment(self, symbol=None, include_middle_east=True):
        """
        تحلیل احساسات بازار برای یک ارز خاص یا کل بازار
        
        Args:
            symbol (str): نماد ارز دیجیتال
            include_middle_east (bool): آیا منابع خاورمیانه در نظر گرفته شوند
            
        Returns:
            dict: تحلیل احساسات بازار
        """
        try:
            # دریافت اخبار از طریق ماژول موجود
            news = get_latest_news(limit=20, include_middle_east=include_middle_east)
            
            # فیلتر اخبار مرتبط با ارز مورد نظر (اگر مشخص شده باشد)
            if symbol:
                coin = symbol.split('/')[0] if '/' in symbol else symbol.split('-')[0]
                filtered_news = []
                
                for item in news:
                    if coin.lower() in item['title'].lower():
                        filtered_news.append(item)
                
                if filtered_news:
                    news = filtered_news
            
            # محاسبه نمره احساسات کلی
            sentiment_scores = [item['sentiment']['score'] for item in news if 'sentiment' in item]
            
            if sentiment_scores:
                overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            else:
                overall_sentiment = 0
                
            # تعیین برچسب احساسات
            if overall_sentiment > 0.3:
                sentiment_label = "مثبت"
                sentiment_description = "احساسات بازار به طور کلی مثبت است"
            elif overall_sentiment < -0.3:
                sentiment_label = "منفی"
                sentiment_description = "احساسات بازار به طور کلی منفی است"
            else:
                sentiment_label = "خنثی"
                sentiment_description = "احساسات بازار متعادل است"
                
            # ایجاد نمرات احساسات منابع مختلف
            source_sentiments = {}
            for source in self.sources:
                source_sentiments[source] = round(random.uniform(-0.8, 0.8), 2)
                
            # ایجاد کلمات کلیدی مرتبط
            keywords = self._generate_related_keywords(symbol, sentiment_label)
            
            # خروجی تحلیل
            result = {
                'symbol': symbol,
                'overall_sentiment': round(overall_sentiment, 2),
                'sentiment_label': sentiment_label,
                'sentiment_description': sentiment_description,
                'source_sentiments': source_sentiments,
                'related_keywords': keywords,
                'news_count': len(news),
                'is_sample_data': True,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return result
        
        except Exception as e:
            logger.error(f"خطا در تحلیل احساسات بازار: {str(e)}")
            return {
                'symbol': symbol,
                'overall_sentiment': 0,
                'sentiment_label': "نامشخص",
                'error': str(e),
                'is_sample_data': True
            }
    
    def _generate_related_keywords(self, symbol, sentiment_type):
        """
        تولید کلمات کلیدی مرتبط با ارز و نوع احساسات
        """
        positive_keywords = ["افزایش قیمت", "روند صعودی", "خوش‌بینی بازار", "رشد", "سرمایه‌گذاری", "آینده روشن"]
        negative_keywords = ["کاهش قیمت", "روند نزولی", "بدبینی بازار", "ریزش", "فروش", "محدودیت‌های قانونی"]
        neutral_keywords = ["نوسان بازار", "تثبیت قیمت", "معاملات جانبی", "انتظار", "تحلیل تکنیکال"]
        
        if sentiment_type == "مثبت":
            main_keywords = positive_keywords
            secondary_keywords = neutral_keywords
        elif sentiment_type == "منفی":
            main_keywords = negative_keywords
            secondary_keywords = neutral_keywords
        else:
            main_keywords = neutral_keywords
            secondary_keywords = positive_keywords + negative_keywords
            
        # انتخاب تصادفی کلمات کلیدی
        selected_keywords = random.sample(main_keywords, min(3, len(main_keywords)))
        selected_keywords += random.sample(secondary_keywords, min(2, len(secondary_keywords)))
        
        # اضافه کردن نام ارز به کلمات کلیدی
        if symbol:
            coin = symbol.split('/')[0] if '/' in symbol else symbol.split('-')[0]
            selected_keywords.insert(0, coin.upper())
            
        return selected_keywords


class PatternRecognition:
    """
    شناسایی الگوهای قیمت با استفاده از هوش مصنوعی
    """
    
    def __init__(self):
        self.patterns = [
            "سر و شانه", "سر و شانه معکوس", "دوقلو", "سه‌قلو", 
            "مثلث صعودی", "مثلث نزولی", "مثلث متقارن", "کف دوگانه", 
            "سقف دوگانه", "کانال صعودی", "کانال نزولی", "پرچم", 
            "وج صعودی", "وج نزولی", "الگوی هارمونیک"
        ]
    
    def identify_patterns(self, symbol, timeframe='1d'):
        """
        شناسایی الگوهای قیمت برای یک ارز
        
        Args:
            symbol (str): نماد ارز
            timeframe (str): بازه زمانی
            
        Returns:
            dict: الگوهای شناسایی شده
        """
        try:
            # در نسخه واقعی، باید از داده‌های تاریخی برای شناسایی الگوها استفاده کرد
            # فعلاً از الگوهای تصادفی استفاده می‌کنیم
            
            # تعیین تعداد الگوهای شناسایی شده
            pattern_count = random.randint(0, 3)
            
            # انتخاب الگوهای تصادفی
            identified_patterns = []
            if pattern_count > 0:
                selected_patterns = random.sample(self.patterns, pattern_count)
                
                for pattern in selected_patterns:
                    completion = round(random.uniform(60, 100), 1)
                    
                    # تعیین سیگنال بر اساس نوع الگو
                    if pattern in ["سر و شانه معکوس", "مثلث صعودی", "کف دوگانه", "کانال صعودی", "وج صعودی"]:
                        signal = "خرید"
                        confidence = round(random.uniform(0.65, 0.95), 2)
                    elif pattern in ["سر و شانه", "مثلث نزولی", "سقف دوگانه", "کانال نزولی", "وج نزولی"]:
                        signal = "فروش"
                        confidence = round(random.uniform(0.65, 0.95), 2)
                    else:
                        signal = "خنثی"
                        confidence = round(random.uniform(0.55, 0.75), 2)
                    
                    identified_patterns.append({
                        'pattern_name': pattern,
                        'completion_percentage': completion,
                        'signal': signal,
                        'confidence': confidence,
                        'timeframe': timeframe
                    })
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'patterns_found': pattern_count > 0,
                'pattern_count': pattern_count,
                'identified_patterns': identified_patterns,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_sample_data': True
            }
            
            return result
        
        except Exception as e:
            logger.error(f"خطا در شناسایی الگوها: {str(e)}")
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'patterns_found': False,
                'error': str(e),
                'is_sample_data': True
            }


class TradingStrategyRecommender:
    """
    پیشنهاد استراتژی‌های معاملاتی بر اساس هوش مصنوعی
    """
    
    def __init__(self):
        self.strategies = [
            "معامله روند", "معامله نوسانی", "معامله برگشتی", 
            "میانگین متحرک متقاطع", "شکست محدوده", "حمایت و مقاومت",
            "معامله حجم", "اسکالپینگ", "سرمایه‌گذاری بلندمدت"
        ]
    
    def recommend_strategy(self, symbol, risk_level="متوسط", timeframe="کوتاه‌مدت"):
        """
        پیشنهاد استراتژی معاملاتی برای یک ارز خاص
        
        Args:
            symbol (str): نماد ارز
            risk_level (str): سطح ریسک ("کم"، "متوسط"، "زیاد")
            timeframe (str): افق زمانی ("کوتاه‌مدت"، "میان‌مدت"، "بلندمدت")
            
        Returns:
            dict: استراتژی‌های پیشنهادی
        """
        try:
            # انتخاب تعداد استراتژی‌های پیشنهادی
            strategy_count = random.randint(1, 3)
            
            # انتخاب استراتژی‌های مناسب بر اساس سطح ریسک و افق زمانی
            suitable_strategies = []
            
            if risk_level == "کم":
                if timeframe == "کوتاه‌مدت":
                    suitable_strategies = ["معامله نوسانی", "حمایت و مقاومت", "میانگین متحرک متقاطع"]
                elif timeframe == "میان‌مدت":
                    suitable_strategies = ["معامله روند", "شکست محدوده", "حمایت و مقاومت"]
                else:  # بلندمدت
                    suitable_strategies = ["سرمایه‌گذاری بلندمدت", "معامله روند", "میانگین متحرک متقاطع"]
            elif risk_level == "متوسط":
                if timeframe == "کوتاه‌مدت":
                    suitable_strategies = ["اسکالپینگ", "معامله نوسانی", "شکست محدوده"]
                elif timeframe == "میان‌مدت":
                    suitable_strategies = ["معامله روند", "معامله برگشتی", "معامله حجم"]
                else:  # بلندمدت
                    suitable_strategies = ["سرمایه‌گذاری بلندمدت", "معامله روند", "شکست محدوده"]
            else:  # ریسک زیاد
                if timeframe == "کوتاه‌مدت":
                    suitable_strategies = ["اسکالپینگ", "معامله برگشتی", "معامله حجم"]
                elif timeframe == "میان‌مدت":
                    suitable_strategies = ["معامله برگشتی", "شکست محدوده", "معامله حجم"]
                else:  # بلندمدت
                    suitable_strategies = ["معامله روند", "سرمایه‌گذاری بلندمدت", "معامله برگشتی"]
            
            # محدود کردن تعداد استراتژی‌ها به تعداد موجود
            if len(suitable_strategies) > strategy_count:
                selected_strategies = random.sample(suitable_strategies, strategy_count)
            else:
                selected_strategies = suitable_strategies
            
            # ایجاد جزئیات برای هر استراتژی
            recommended_strategies = []
            for strategy in selected_strategies:
                recommended_strategies.append({
                    'strategy_name': strategy,
                    'confidence': round(random.uniform(0.65, 0.95), 2),
                    'expected_profit': f"{round(random.uniform(2, 15), 1)}%",
                    'stop_loss': f"{round(random.uniform(1, 8), 1)}%",
                    'take_profit': f"{round(random.uniform(3, 20), 1)}%",
                    'time_horizon': self._get_time_horizon(strategy, timeframe),
                    'description': self._get_strategy_description(strategy),
                    'key_indicators': self._get_strategy_indicators(strategy)
                })
            
            result = {
                'symbol': symbol,
                'risk_level': risk_level,
                'timeframe': timeframe,
                'strategy_count': len(recommended_strategies),
                'recommended_strategies': recommended_strategies,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_sample_data': True
            }
            
            return result
        
        except Exception as e:
            logger.error(f"خطا در پیشنهاد استراتژی: {str(e)}")
            return {
                'symbol': symbol,
                'risk_level': risk_level,
                'timeframe': timeframe,
                'strategy_count': 0,
                'error': str(e),
                'is_sample_data': True
            }
    
    def _get_time_horizon(self, strategy, timeframe):
        """
        تعیین افق زمانی مناسب برای استراتژی
        """
        if strategy in ["اسکالپینگ", "معامله حجم"]:
            return "چند دقیقه تا چند ساعت"
        elif strategy in ["معامله نوسانی", "معامله برگشتی", "شکست محدوده"]:
            return "چند ساعت تا چند روز"
        elif strategy in ["میانگین متحرک متقاطع", "حمایت و مقاومت"]:
            return "چند روز تا چند هفته"
        elif strategy in ["معامله روند"]:
            return "چند هفته تا چند ماه"
        elif strategy in ["سرمایه‌گذاری بلندمدت"]:
            return "چند ماه تا چند سال"
        else:
            return "نامشخص"
    
    def _get_strategy_description(self, strategy):
        """
        توضیحات استراتژی
        """
        descriptions = {
            "معامله روند": "خرید در روند صعودی و فروش در روند نزولی با هدف سود از تداوم روند",
            "معامله نوسانی": "خرید در کف قیمتی و فروش در سقف قیمتی با هدف سود از نوسانات قیمت",
            "معامله برگشتی": "ورود به معامله در نقاط برگشت احتمالی روند با هدف کسب سود از تغییر جهت قیمت",
            "میانگین متحرک متقاطع": "استفاده از تقاطع میانگین‌های متحرک برای شناسایی تغییرات روند",
            "شکست محدوده": "ورود به معامله پس از شکست سطوح مهم قیمتی",
            "حمایت و مقاومت": "خرید در سطوح حمایت و فروش در سطوح مقاومت",
            "معامله حجم": "استفاده از تغییرات حجم معاملات برای پیش‌بینی حرکات قیمت",
            "اسکالپینگ": "انجام معاملات سریع و کوتاه‌مدت با سود کم اما مکرر",
            "سرمایه‌گذاری بلندمدت": "خرید و نگهداری ارز برای دوره زمانی طولانی با هدف سود از رشد بلندمدت"
        }
        
        return descriptions.get(strategy, "توضیحات موجود نیست")
    
    def _get_strategy_indicators(self, strategy):
        """
        شاخص‌های کلیدی مورد استفاده در استراتژی
        """
        indicators = {
            "معامله روند": ["میانگین متحرک", "MACD", "خط روند"],
            "معامله نوسانی": ["RSI", "استوکاستیک", "باندهای بولینگر"],
            "معامله برگشتی": ["RSI", "واگرایی", "الگوهای شمعی", "فیبوناچی"],
            "میانگین متحرک متقاطع": ["میانگین متحرک سریع", "میانگین متحرک کند"],
            "شکست محدوده": ["سطوح حمایت و مقاومت", "حجم معاملات", "ATR"],
            "حمایت و مقاومت": ["سطوح فیبوناچی", "سطوح روانی", "نقاط پیوت"],
            "معامله حجم": ["حجم معاملات", "شاخص تجمعی/توزیعی", "OBV"],
            "اسکالپینگ": ["نمودار تیک", "کتاب سفارشات", "الگوهای شمعی کوتاه‌مدت"],
            "سرمایه‌گذاری بلندمدت": ["میانگین متحرک بلندمدت", "تحلیل بنیادی", "شاخص‌های اقتصادی"]
        }
        
        return indicators.get(strategy, ["شاخص مشخص نشده"])


# توابع سطح بالا برای استفاده در برنامه اصلی

def get_price_prediction(symbol, timeframe='24h'):
    """
    پیش‌بینی قیمت برای یک ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی ('24h', '7d', '30d')
        
    Returns:
        dict: داده‌های پیش‌بینی
    """
    try:
        model = PricePredictionModel(symbol)
        return model.get_predictions(timeframe)
    except Exception as e:
        logger.error(f"خطا در پیش‌بینی قیمت: {str(e)}")
        return {
            'symbol': symbol,
            'error': str(e),
            'is_sample_data': True
        }


def get_market_sentiment(symbol=None, include_middle_east=True):
    """
    تحلیل احساسات بازار برای یک ارز یا کل بازار
    
    Args:
        symbol (str): نماد ارز (اختیاری)
        include_middle_east (bool): آیا منابع خاورمیانه در نظر گرفته شوند
        
    Returns:
        dict: تحلیل احساسات بازار
    """
    try:
        analyzer = MarketSentimentAnalyzer()
        return analyzer.analyze_market_sentiment(symbol, include_middle_east)
    except Exception as e:
        logger.error(f"خطا در تحلیل احساسات بازار: {str(e)}")
        return {
            'symbol': symbol,
            'error': str(e),
            'is_sample_data': True
        }


def get_price_patterns(symbol, timeframe='1d'):
    """
    شناسایی الگوهای قیمت
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        
    Returns:
        dict: الگوهای شناسایی شده
    """
    try:
        pattern_recognizer = PatternRecognition()
        return pattern_recognizer.identify_patterns(symbol, timeframe)
    except Exception as e:
        logger.error(f"خطا در شناسایی الگوهای قیمت: {str(e)}")
        return {
            'symbol': symbol,
            'error': str(e),
            'is_sample_data': True
        }


def get_trading_strategy(symbol, risk_level="متوسط", timeframe="کوتاه‌مدت"):
    """
    پیشنهاد استراتژی معاملاتی
    
    Args:
        symbol (str): نماد ارز
        risk_level (str): سطح ریسک ("کم"، "متوسط"، "زیاد")
        timeframe (str): افق زمانی ("کوتاه‌مدت"، "میان‌مدت"، "بلندمدت")
        
    Returns:
        dict: استراتژی‌های پیشنهادی
    """
    try:
        strategy_recommender = TradingStrategyRecommender()
        return strategy_recommender.recommend_strategy(symbol, risk_level, timeframe)
    except Exception as e:
        logger.error(f"خطا در پیشنهاد استراتژی معاملاتی: {str(e)}")
        return {
            'symbol': symbol,
            'error': str(e),
            'is_sample_data': True
        }
