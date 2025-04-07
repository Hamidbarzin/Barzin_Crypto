"""
ماژول هوش مصنوعی برای تحلیل بازار ارزهای دیجیتال با استفاده از OpenAI
"""
import os
import json
import logging
from datetime import datetime
from openai import OpenAI

# تنظیم لاگر
logger = logging.getLogger(__name__)

# دریافت کلید API از متغیرهای محیطی
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ایجاد کلاینت OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_market_condition(market_data, news_data=None):
    """
    تحلیل شرایط بازار با استفاده از هوش مصنوعی
    
    Args:
        market_data (dict): داده‌های بازار شامل قیمت‌ها و شاخص‌های تکنیکال
        news_data (list, optional): داده‌های اخبار بازار
        
    Returns:
        dict: تحلیل بازار
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("کلید API هوش مصنوعی تنظیم نشده است")
            return {"error": "کلید API هوش مصنوعی تنظیم نشده است"}
        
        # تبدیل داده‌ها به متن
        market_context = f"داده‌های بازار ارزهای دیجیتال در تاریخ {datetime.now().strftime('%Y-%m-%d %H:%M')}: \n"
        
        for symbol, data in market_data.items():
            market_context += f"{symbol}: قیمت {data['price']} دلار, "
            if 'change_percent' in data and data['change_percent'] != 0:
                market_context += f"تغییرات {data['change_percent']}%, "
            market_context += "\n"
        
        if news_data:
            market_context += "\nاخبار مهم اخیر بازار:\n"
            for idx, news in enumerate(news_data[:5]):
                market_context += f"{idx+1}. {news['title']}\n"
        
        prompt = f"""
        با توجه به داده‌های بازار زیر، یک تحلیل کوتاه و مفید ارائه دهید. لطفاً شامل این موارد باشد:
        1. ارزیابی کلی از وضعیت بازار (صعودی، نزولی یا خنثی)
        2. ارزهایی که فرصت خرید یا فروش مناسبی دارند
        3. پیش‌بینی کوتاه‌مدت برای بیت‌کوین و اتریوم
        4. توصیه‌های سرمایه‌گذاری با توجه به ریسک متوسط
        
        داده‌های بازار:
        {market_context}
        
        پاسخ را به فارسی و در قالب یک تحلیل کاربردی و موجز ارائه دهید. پاسخ شما باید برای یک سرمایه‌گذار غیرحرفه‌ای قابل فهم باشد.
        """
        
        # # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        
        analysis = response.choices[0].message.content
        
        # بازگرداندن نتیجه
        return {
            "analysis": analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_used": {
                "market_data": market_data,
                "news_count": len(news_data) if news_data else 0
            }
        }
    
    except Exception as e:
        logger.error(f"خطا در تحلیل بازار با هوش مصنوعی: {str(e)}")
        return {"error": f"خطا در تحلیل بازار: {str(e)}"}


def get_smart_trading_suggestion(symbol, market_data, technical_data):
    """
    دریافت پیشنهاد معاملاتی هوشمند برای یک ارز خاص
    
    Args:
        symbol (str): نماد ارز
        market_data (dict): داده‌های بازار
        technical_data (dict): داده‌های تحلیل تکنیکال
        
    Returns:
        dict: پیشنهاد معاملاتی
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("کلید API هوش مصنوعی تنظیم نشده است")
            return {"error": "کلید API هوش مصنوعی تنظیم نشده است"}
        
        # تهیه متن برای پرامپت
        if symbol in market_data:
            price_data = market_data[symbol]
        else:
            price_data = {"price": "نامشخص", "change_percent": "نامشخص"}
        
        prompt = f"""
        با توجه به اطلاعات زیر برای ارز {symbol}، یک پیشنهاد معاملاتی دقیق و توضیح آن را ارائه دهید:
        
        قیمت فعلی: {price_data['price']} دلار
        تغییرات قیمت (24 ساعته): {price_data.get('change_percent', 'نامشخص')}%
        
        داده‌های تحلیل تکنیکال:
        RSI: {technical_data.get('rsi', 'نامشخص')}
        MACD: {technical_data.get('macd', 'نامشخص')}
        میانگین متحرک 20 روزه: {technical_data.get('ma20', 'نامشخص')}
        میانگین متحرک 50 روزه: {technical_data.get('ma50', 'نامشخص')}
        
        سیگنال‌های تکنیکال:
        {technical_data.get('signals', 'اطلاعات کافی نیست')}
        
        پاسخ را به فارسی در قالب این موارد ارائه دهید:
        1. وضعیت فعلی: (توضیح مختصر)
        2. پیشنهاد معاملاتی: (خرید/فروش/نگهداری)
        3. نقاط ورود پیشنهادی: (در صورت توصیه به خرید)
        4. حد ضرر پیشنهادی: (در صورت توصیه به خرید)
        5. هدف قیمتی: (در صورت توصیه به خرید یا نگهداری)
        6. دلیل این پیشنهاد: (توضیح مختصر)
        
        پاسخ باید مفید، کاربردی و برای یک معامله‌گر با دانش متوسط قابل فهم باشد.
        """
        
        # # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        
        suggestion = response.choices[0].message.content
        
        # بازگرداندن نتیجه
        return {
            "symbol": symbol,
            "suggestion": suggestion,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    except Exception as e:
        logger.error(f"خطا در دریافت پیشنهاد معاملاتی برای {symbol}: {str(e)}")
        return {"error": f"خطا در دریافت پیشنهاد معاملاتی: {str(e)}"}


def analyze_news_impact(news_items, top_coins=None):
    """
    تحلیل تأثیر اخبار بر بازار ارزهای دیجیتال
    
    Args:
        news_items (list): لیست اخبار
        top_coins (list): لیست ارزهای برتر برای بررسی تأثیر
        
    Returns:
        dict: تحلیل تأثیر اخبار
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("کلید API هوش مصنوعی تنظیم نشده است")
            return {"error": "کلید API هوش مصنوعی تنظیم نشده است"}
        
        if not top_coins:
            top_coins = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE"]
        
        # تهیه متن اخبار
        news_text = "اخبار اخیر مرتبط با ارزهای دیجیتال:\n\n"
        
        for idx, news in enumerate(news_items[:10]):
            news_text += f"{idx+1}. {news['title']}\n"
            if 'summary' in news and news['summary']:
                news_text += f"   خلاصه: {news['summary']}\n"
            news_text += f"   منبع: {news.get('source', 'نامشخص')} - تاریخ: {news.get('date', 'نامشخص')}\n\n"
        
        prompt = f"""
        با توجه به اخبار زیر در مورد ارزهای دیجیتال، تحلیل کنید که این اخبار چه تأثیری بر بازار و به ویژه ارزهای {', '.join(top_coins)} خواهند داشت:
        
        {news_text}
        
        لطفاً تحلیل خود را به فارسی و در این قالب ارائه دهید:
        
        1. خلاصه کلی تأثیر اخبار بر بازار
        2. تأثیرات احتمالی بر هر یک از ارزهای ذکر شده
        3. فرصت‌های سرمایه‌گذاری که ممکن است در نتیجه این اخبار ایجاد شوند
        4. ریسک‌های احتمالی که سرمایه‌گذاران باید آگاه باشند
        
        پاسخ را به صورت مختصر و کاربردی ارائه دهید.
        """
        
        # # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        
        analysis = response.choices[0].message.content
        
        # بازگرداندن نتیجه
        return {
            "news_impact_analysis": analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analyzed_news_count": len(news_items[:10]),
            "coins_analyzed": top_coins
        }
    
    except Exception as e:
        logger.error(f"خطا در تحلیل تأثیر اخبار: {str(e)}")
        return {"error": f"خطا در تحلیل تأثیر اخبار: {str(e)}"}