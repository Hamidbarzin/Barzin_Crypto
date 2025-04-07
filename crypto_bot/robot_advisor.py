"""
ماژول مشاور رباتیک برای تحلیل بازار ارزهای دیجیتال و ارائه پیشنهادات معاملاتی

این ماژول از ترکیب داده‌های قیمت، تحلیل تکنیکال، اخبار و هوش مصنوعی 
برای ارائه پیشنهادات معاملاتی استفاده می‌کند.
"""
import logging
from datetime import datetime
import random

# ماژول‌های داخلی
from crypto_bot.market_api import get_current_price, get_market_prices
from crypto_bot.openai_helper import analyze_market_condition, get_smart_trading_suggestion, analyze_news_impact
from crypto_bot.news_collector import get_recent_news, get_news_about_coin
from crypto_bot import technical_analysis

# تنظیم لاگر
logger = logging.getLogger(__name__)

class RobotAdvisor:
    """
    کلاس مشاور رباتیک برای تحلیل بازار و ارائه پیشنهادات معاملاتی
    
    این کلاس از ترکیب داده‌های مختلف و هوش مصنوعی برای ارائه 
    پیشنهادات معاملاتی هوشمند استفاده می‌کند.
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس
        """
        # لیست ارزهای پیش‌فرض برای تحلیل
        self.default_symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "SOL/USDT"]
        
        # شاخص‌های فنی پیش‌فرض برای محاسبه
        self.default_indicators = ["RSI", "MACD", "MA"]
        
        # بازه‌های زمانی پیش‌فرض برای تحلیل
        self.default_timeframes = ["1h", "1d", "1w"]
    
    def get_market_overview(self):
        """
        دریافت نمای کلی بازار با استفاده از هوش مصنوعی
        
        Returns:
            dict: نمای کلی بازار
        """
        try:
            # دریافت قیمت‌های فعلی بازار
            market_data = get_market_prices(self.default_symbols)
            
            # دریافت اخبار اخیر
            news_data = get_recent_news(limit=5)
            
            # استفاده از هوش مصنوعی برای تحلیل بازار
            analysis = analyze_market_condition(market_data, news_data)
            
            return {
                "overview": analysis,
                "market_data": market_data,
                "news_count": len(news_data),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت نمای کلی بازار: {str(e)}")
            return {"error": f"خطا در دریافت نمای کلی بازار: {str(e)}"}
    
    def get_coin_analysis(self, symbol):
        """
        تحلیل یک ارز خاص با استفاده از هوش مصنوعی
        
        Args:
            symbol (str): نماد ارز دیجیتال (مثال: BTC/USDT)
            
        Returns:
            dict: تحلیل ارز
        """
        try:
            # دریافت قیمت فعلی
            price_data = get_current_price(symbol)
            
            # دریافت داده‌های تحلیل تکنیکال
            tech_data = technical_analysis.analyze_symbol(symbol)
            
            # دریافت اخبار مرتبط با این ارز
            news_data = get_news_about_coin(symbol.split('/')[0], limit=3)
            
            # استفاده از هوش مصنوعی برای ارائه پیشنهاد معاملاتی
            suggestion = get_smart_trading_suggestion(symbol, {symbol: price_data}, tech_data)
            
            # بازگرداندن نتیجه
            return {
                "symbol": symbol,
                "price": price_data,
                "technical_analysis": tech_data,
                "news": news_data,
                "ai_suggestion": suggestion,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"خطا در تحلیل ارز {symbol}: {str(e)}")
            return {"error": f"خطا در تحلیل ارز {symbol}: {str(e)}"}
    
    def get_buying_opportunities(self, limit=3):
        """
        دریافت فرصت‌های خرید مناسب
        
        Args:
            limit (int): حداکثر تعداد فرصت‌ها
            
        Returns:
            list: لیست فرصت‌های خرید
        """
        try:
            # دریافت قیمت‌های فعلی بازار
            market_data = get_market_prices(self.default_symbols)
            
            opportunities = []
            
            for symbol in self.default_symbols:
                if len(opportunities) >= limit:
                    break
                    
                # دریافت داده‌های تحلیل تکنیکال
                tech_data = technical_analysis.analyze_symbol(symbol)
                
                # بررسی شرایط خرید
                if self._check_buy_conditions(tech_data):
                    opportunities.append({
                        "symbol": symbol,
                        "price": market_data[symbol]["price"],
                        "reason": self._get_buy_reason(tech_data),
                        "confidence": random.uniform(0.7, 0.95)  # در نسخه واقعی باید الگوریتم پیشرفته‌تری استفاده شود
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"خطا در دریافت فرصت‌های خرید: {str(e)}")
            return []
    
    def get_selling_opportunities(self, limit=3):
        """
        دریافت فرصت‌های فروش مناسب
        
        Args:
            limit (int): حداکثر تعداد فرصت‌ها
            
        Returns:
            list: لیست فرصت‌های فروش
        """
        try:
            # دریافت قیمت‌های فعلی بازار
            market_data = get_market_prices(self.default_symbols)
            
            opportunities = []
            
            for symbol in self.default_symbols:
                if len(opportunities) >= limit:
                    break
                    
                # دریافت داده‌های تحلیل تکنیکال
                tech_data = technical_analysis.analyze_symbol(symbol)
                
                # بررسی شرایط فروش
                if self._check_sell_conditions(tech_data):
                    opportunities.append({
                        "symbol": symbol,
                        "price": market_data[symbol]["price"],
                        "reason": self._get_sell_reason(tech_data),
                        "confidence": random.uniform(0.7, 0.95)  # در نسخه واقعی باید الگوریتم پیشرفته‌تری استفاده شود
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"خطا در دریافت فرصت‌های فروش: {str(e)}")
            return []
    
    def get_market_news_analysis(self):
        """
        تحلیل تأثیر اخبار بر بازار
        
        Returns:
            dict: تحلیل اخبار
        """
        try:
            # دریافت اخبار اخیر
            news_data = get_recent_news(limit=10)
            
            # استفاده از هوش مصنوعی برای تحلیل تأثیر اخبار
            top_coins = [s.split('/')[0] for s in self.default_symbols[:5]]
            analysis = analyze_news_impact(news_data, top_coins)
            
            return analysis
            
        except Exception as e:
            logger.error(f"خطا در تحلیل اخبار بازار: {str(e)}")
            return {"error": f"خطا در تحلیل اخبار بازار: {str(e)}"}
    
    def _check_buy_conditions(self, tech_data):
        """
        بررسی شرایط خرید بر اساس داده‌های تکنیکال
        
        Args:
            tech_data (dict): داده‌های تحلیل تکنیکال
            
        Returns:
            bool: آیا شرایط خرید برقرار است
        """
        # شرایط ساده برای خرید
        # در نسخه واقعی باید الگوریتم پیشرفته‌تری استفاده شود
        
        # اگر RSI زیر 30 باشد (اشباع فروش)
        if 'rsi' in tech_data and tech_data['rsi'] < 30:
            return True
        
        # اگر MACD سیگنال خرید داده باشد
        if 'macd_signal' in tech_data and tech_data['macd_signal'] == 'buy':
            return True
        
        # اگر قیمت بالای میانگین متحرک 50 روزه و زیر میانگین متحرک 20 روزه باشد
        if ('ma20' in tech_data and 'ma50' in tech_data and 
            tech_data.get('price', 0) > tech_data['ma50'] and 
            tech_data.get('price', 0) < tech_data['ma20']):
            return True
        
        return False
    
    def _check_sell_conditions(self, tech_data):
        """
        بررسی شرایط فروش بر اساس داده‌های تکنیکال
        
        Args:
            tech_data (dict): داده‌های تحلیل تکنیکال
            
        Returns:
            bool: آیا شرایط فروش برقرار است
        """
        # شرایط ساده برای فروش
        # در نسخه واقعی باید الگوریتم پیشرفته‌تری استفاده شود
        
        # اگر RSI بالای 70 باشد (اشباع خرید)
        if 'rsi' in tech_data and tech_data['rsi'] > 70:
            return True
        
        # اگر MACD سیگنال فروش داده باشد
        if 'macd_signal' in tech_data and tech_data['macd_signal'] == 'sell':
            return True
        
        # اگر قیمت زیر میانگین متحرک 50 روزه و بالای میانگین متحرک 20 روزه باشد
        if ('ma20' in tech_data and 'ma50' in tech_data and 
            tech_data.get('price', 0) < tech_data['ma50'] and 
            tech_data.get('price', 0) > tech_data['ma20']):
            return True
        
        return False
    
    def _get_buy_reason(self, tech_data):
        """
        ارائه دلیل پیشنهاد خرید
        
        Args:
            tech_data (dict): داده‌های تحلیل تکنیکال
            
        Returns:
            str: دلیل پیشنهاد خرید
        """
        reasons = []
        
        if 'rsi' in tech_data and tech_data['rsi'] < 30:
            reasons.append("RSI زیر 30 (اشباع فروش)")
        
        if 'macd_signal' in tech_data and tech_data['macd_signal'] == 'buy':
            reasons.append("سیگنال خرید MACD")
        
        if ('ma20' in tech_data and 'ma50' in tech_data and 
            tech_data.get('price', 0) > tech_data['ma50'] and 
            tech_data.get('price', 0) < tech_data['ma20']):
            reasons.append("قیمت بین MA20 و MA50 در روند صعودی")
        
        if not reasons:
            reasons.append("بر اساس ترکیبی از شاخص‌های تکنیکال")
        
        return "، ".join(reasons)
    
    def _get_sell_reason(self, tech_data):
        """
        ارائه دلیل پیشنهاد فروش
        
        Args:
            tech_data (dict): داده‌های تحلیل تکنیکال
            
        Returns:
            str: دلیل پیشنهاد فروش
        """
        reasons = []
        
        if 'rsi' in tech_data and tech_data['rsi'] > 70:
            reasons.append("RSI بالای 70 (اشباع خرید)")
        
        if 'macd_signal' in tech_data and tech_data['macd_signal'] == 'sell':
            reasons.append("سیگنال فروش MACD")
        
        if ('ma20' in tech_data and 'ma50' in tech_data and 
            tech_data.get('price', 0) < tech_data['ma50'] and 
            tech_data.get('price', 0) > tech_data['ma20']):
            reasons.append("قیمت بین MA20 و MA50 در روند نزولی")
        
        if not reasons:
            reasons.append("بر اساس ترکیبی از شاخص‌های تکنیکال")
        
        return "، ".join(reasons)

# ایجاد نمونه از کلاس
robot_advisor = RobotAdvisor()

def get_market_overview():
    """
    دریافت نمای کلی بازار با استفاده از هوش مصنوعی
    
    Returns:
        dict: نمای کلی بازار
    """
    return robot_advisor.get_market_overview()

def get_coin_analysis(symbol):
    """
    تحلیل یک ارز خاص با استفاده از هوش مصنوعی
    
    Args:
        symbol (str): نماد ارز دیجیتال (مثال: BTC/USDT)
        
    Returns:
        dict: تحلیل ارز
    """
    return robot_advisor.get_coin_analysis(symbol)

def get_buying_opportunities(limit=3):
    """
    دریافت فرصت‌های خرید مناسب
    
    Args:
        limit (int): حداکثر تعداد فرصت‌ها
        
    Returns:
        list: لیست فرصت‌های خرید
    """
    return robot_advisor.get_buying_opportunities(limit)

def get_selling_opportunities(limit=3):
    """
    دریافت فرصت‌های فروش مناسب
    
    Args:
        limit (int): حداکثر تعداد فرصت‌ها
        
    Returns:
        list: لیست فرصت‌های فروش
    """
    return robot_advisor.get_selling_opportunities(limit)

def get_market_news_analysis():
    """
    تحلیل تأثیر اخبار بر بازار
    
    Returns:
        dict: تحلیل اخبار
    """
    return robot_advisor.get_market_news_analysis()