"""
ماژول سرویس OpenAI برای تحلیل هوشمند بازار ارزهای دیجیتال
"""

import os
import json
import logging
from openai import OpenAI

# تنظیم لاگر
logger = logging.getLogger(__name__)

# بارگذاری کلید API از متغیرهای محیطی
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# مقداردهی اولیه کلاینت OpenAI
openai_client = None

def initialize_openai():
    """
    راه‌اندازی کلاینت OpenAI
    """
    global openai_client
    
    try:
        if OPENAI_API_KEY:
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("سرویس OpenAI با موفقیت راه‌اندازی شد")
            return True
        else:
            logger.warning("کلید API برای OpenAI یافت نشد")
            return False
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی سرویس OpenAI: {str(e)}")
        return False


def analyze_market_data(symbol, price_data, news_data=None, timeframe="24h"):
    """
    تحلیل داده‌های بازار با استفاده از هوش مصنوعی OpenAI
    
    Args:
        symbol (str): نماد ارز دیجیتال
        price_data (dict): داده‌های قیمت
        news_data (list): اخبار مرتبط
        timeframe (str): بازه زمانی
        
    Returns:
        dict: تحلیل هوشمند بازار
    """
    global openai_client
    
    if openai_client is None:
        if not initialize_openai():
            logger.warning("سرویس OpenAI در دسترس نیست. از داده‌های نمونه استفاده می‌شود")
            return _get_sample_analysis(symbol, timeframe)
    
    try:
        # آماده‌سازی داده‌ها برای ارسال به OpenAI
        prompt = f"""
        لطفاً تحلیل دقیقی از وضعیت فعلی ارز {symbol} ارائه دهید.
        
        داده‌های قیمت:
        {json.dumps(price_data, ensure_ascii=False, indent=2)}
        """
        
        if news_data:
            prompt += f"""
            اخبار مرتبط:
            {json.dumps(news_data, ensure_ascii=False, indent=2)}
            """
            
        prompt += """
        لطفاً پاسخ را در قالب JSON با ساختار زیر برگردانید:
        {
            "summary": "خلاصه کلی وضعیت",
            "trend": "روند (صعودی، نزولی، خنثی)",
            "strength": "قدرت روند (0 تا 1)",
            "key_factors": ["عامل 1", "عامل 2", "عامل 3"],
            "forecast": "پیش‌بینی کوتاه‌مدت",
            "risk_level": "سطح ریسک (کم، متوسط، زیاد)"
        }
        """
        
        # ارسال درخواست به OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # استفاده از مدل پیشرفته OpenAI - نسخه جدید است، تغییر ندهید
            messages=[
                {"role": "system", "content": "شما یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال هستید. لطفاً تحلیل‌های دقیق و عمیق ارائه دهید."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # پردازش پاسخ دریافتی
        result = json.loads(response.choices[0].message.content)
        result["symbol"] = symbol
        result["timeframe"] = timeframe
        result["is_ai_analysis"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"خطا در تحلیل با OpenAI: {str(e)}")
        return _get_sample_analysis(symbol, timeframe)


def analyze_news_sentiment(news_items):
    """
    تحلیل احساسات اخبار با استفاده از هوش مصنوعی OpenAI
    
    Args:
        news_items (list): لیست اخبار
        
    Returns:
        dict: تحلیل احساسات اخبار
    """
    global openai_client
    
    if openai_client is None:
        if not initialize_openai():
            logger.warning("سرویس OpenAI در دسترس نیست. از داده‌های نمونه استفاده می‌شود")
            return _get_sample_sentiment()
    
    try:
        # محدود کردن تعداد اخبار برای کاهش حجم درخواست
        limited_news = news_items[:5]
        
        # آماده‌سازی داده‌ها برای ارسال به OpenAI
        prompt = f"""
        لطفاً احساسات اخبار زیر را تحلیل کنید و تأثیر آن‌ها بر بازار ارزهای دیجیتال را بررسی نمایید:
        
        {json.dumps(limited_news, ensure_ascii=False, indent=2)}
        
        لطفاً پاسخ را در قالب JSON با ساختار زیر برگردانید:
        {
            "overall_sentiment": "نمره کلی احساسات (-1 تا 1)",
            "sentiment_label": "برچسب احساسات (منفی، خنثی، مثبت)",
            "sentiment_description": "توضیح مختصر وضعیت",
            "news_analysis": [
                {
                    "title": "عنوان خبر",
                    "sentiment": "احساسات (منفی، خنثی، مثبت)",
                    "impact": "تأثیر بر بازار (کم، متوسط، زیاد)",
                    "key_points": ["نکته کلیدی 1", "نکته کلیدی 2"]
                }
            ],
            "keywords": ["کلمه کلیدی 1", "کلمه کلیدی 2", "کلمه کلیدی 3"]
        }
        """
        
        # ارسال درخواست به OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # استفاده از مدل پیشرفته OpenAI - نسخه جدید است، تغییر ندهید
            messages=[
                {"role": "system", "content": "شما یک تحلیلگر احساسات اخبار ارزهای دیجیتال هستید. لطفاً تحلیل‌های دقیق و موجز ارائه دهید."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # پردازش پاسخ دریافتی
        result = json.loads(response.choices[0].message.content)
        result["is_ai_analysis"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"خطا در تحلیل احساسات با OpenAI: {str(e)}")
        return _get_sample_sentiment()


def suggest_trading_strategy(symbol, price_data, technical_indicators, risk_level="متوسط"):
    """
    پیشنهاد استراتژی معاملاتی با استفاده از هوش مصنوعی OpenAI
    
    Args:
        symbol (str): نماد ارز دیجیتال
        price_data (dict): داده‌های قیمت
        technical_indicators (dict): شاخص‌های تکنیکال
        risk_level (str): سطح ریسک
        
    Returns:
        dict: استراتژی پیشنهادی
    """
    global openai_client
    
    if openai_client is None:
        if not initialize_openai():
            logger.warning("سرویس OpenAI در دسترس نیست. از داده‌های نمونه استفاده می‌شود")
            return _get_sample_strategy(symbol, risk_level)
    
    try:
        # آماده‌سازی داده‌ها برای ارسال به OpenAI
        prompt = f"""
        لطفاً با توجه به داده‌های زیر، یک استراتژی معاملاتی برای ارز {symbol} با سطح ریسک {risk_level} پیشنهاد دهید:
        
        داده‌های قیمت:
        {json.dumps(price_data, ensure_ascii=False, indent=2)}
        
        شاخص‌های تکنیکال:
        {json.dumps(technical_indicators, ensure_ascii=False, indent=2)}
        
        لطفاً پاسخ را در قالب JSON با ساختار زیر برگردانید:
        {
            "strategy_name": "نام استراتژی",
            "strategy_type": "نوع استراتژی (روند، نوسانی، معکوس و...)",
            "timeframe": "بازه زمانی پیشنهادی",
            "entry_points": ["نقطه ورود 1", "نقطه ورود 2"],
            "exit_points": ["نقطه خروج 1", "نقطه خروج 2"],
            "stop_loss": "پیشنهاد حد ضرر",
            "take_profit": "پیشنهاد حد سود",
            "risk_reward_ratio": "نسبت ریسک به پاداش",
            "key_indicators": ["شاخص کلیدی 1", "شاخص کلیدی 2"],
            "strategy_description": "توضیح مختصر استراتژی",
            "confidence": "میزان اطمینان استراتژی (0 تا 1)"
        }
        """
        
        # ارسال درخواست به OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # استفاده از مدل پیشرفته OpenAI - نسخه جدید است، تغییر ندهید
            messages=[
                {"role": "system", "content": "شما یک استراتژیست معاملاتی حرفه‌ای در بازار ارزهای دیجیتال هستید. لطفاً استراتژی‌های دقیق و کاربردی ارائه دهید."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # پردازش پاسخ دریافتی
        result = json.loads(response.choices[0].message.content)
        result["symbol"] = symbol
        result["risk_level"] = risk_level
        result["is_ai_strategy"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"خطا در پیشنهاد استراتژی با OpenAI: {str(e)}")
        return _get_sample_strategy(symbol, risk_level)


def detect_price_patterns(symbol, price_data, timeframe="1d"):
    """
    شناسایی الگوهای قیمت با استفاده از هوش مصنوعی OpenAI
    
    Args:
        symbol (str): نماد ارز دیجیتال
        price_data (dict): داده‌های قیمت
        timeframe (str): بازه زمانی
        
    Returns:
        dict: الگوهای شناسایی شده
    """
    global openai_client
    
    if openai_client is None:
        if not initialize_openai():
            logger.warning("سرویس OpenAI در دسترس نیست. از داده‌های نمونه استفاده می‌شود")
            return _get_sample_patterns(symbol, timeframe)
    
    try:
        # آماده‌سازی داده‌ها برای ارسال به OpenAI
        prompt = f"""
        لطفاً الگوهای قیمت موجود در داده‌های زیر برای ارز {symbol} در بازه زمانی {timeframe} را شناسایی کنید:
        
        داده‌های قیمت:
        {json.dumps(price_data, ensure_ascii=False, indent=2)}
        
        لطفاً پاسخ را در قالب JSON با ساختار زیر برگردانید:
        {
            "patterns_found": true/false,
            "pattern_count": "تعداد الگوهای شناسایی شده",
            "identified_patterns": [
                {
                    "pattern_name": "نام الگو",
                    "completion_percentage": "درصد تکمیل الگو",
                    "signal": "سیگنال (خرید، فروش، خنثی)",
                    "confidence": "میزان اطمینان (0 تا 1)",
                    "description": "توضیح مختصر الگو"
                }
            ],
            "chart_areas": ["ناحیه مهم 1", "ناحیه مهم 2"]
        }
        """
        
        # ارسال درخواست به OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # استفاده از مدل پیشرفته OpenAI - نسخه جدید است، تغییر ندهید
            messages=[
                {"role": "system", "content": "شما یک متخصص تحلیل تکنیکال و شناسایی الگوهای قیمت در بازار ارزهای دیجیتال هستید. لطفاً الگوهای قیمت را با دقت شناسایی کنید."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # پردازش پاسخ دریافتی
        result = json.loads(response.choices[0].message.content)
        result["symbol"] = symbol
        result["timeframe"] = timeframe
        result["is_ai_analysis"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"خطا در شناسایی الگوها با OpenAI: {str(e)}")
        return _get_sample_patterns(symbol, timeframe)


def _get_sample_analysis(symbol, timeframe):
    """
    تولید داده‌های نمونه برای تحلیل بازار
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        
    Returns:
        dict: تحلیل نمونه
    """
    import random
    import datetime
    
    # تعیین روند بر اساس نماد به صورت تصادفی
    trends = ["صعودی", "نزولی", "خنثی"]
    trend_weights = [0.5, 0.3, 0.2]  # احتمال هر روند
    trend = random.choices(trends, weights=trend_weights, k=1)[0]
    
    # تنظیم سایر پارامترها بر اساس روند
    if trend == "صعودی":
        strength = round(random.uniform(0.6, 0.9), 2)
        risk_level = random.choice(["متوسط", "کم"])
        forecast = "رشد قیمت در کوتاه‌مدت"
        key_factors = [
            "افزایش تقاضا در بازار",
            "خبرهای مثبت",
            "روند صعودی بازار کلی",
            "شکست مقاومت‌های کلیدی"
        ]
    elif trend == "نزولی":
        strength = round(random.uniform(0.6, 0.9), 2)
        risk_level = random.choice(["متوسط", "زیاد"])
        forecast = "کاهش قیمت در کوتاه‌مدت"
        key_factors = [
            "کاهش تقاضا در بازار",
            "خبرهای منفی",
            "روند نزولی بازار کلی",
            "شکست حمایت‌های کلیدی"
        ]
    else:  # خنثی
        strength = round(random.uniform(0.3, 0.6), 2)
        risk_level = "متوسط"
        forecast = "نوسان در محدوده فعلی"
        key_factors = [
            "تعادل عرضه و تقاضا",
            "عدم قطعیت در بازار",
            "منتظر شکست محدوده",
            "حجم معاملات پایین"
        ]
    
    # انتخاب تصادفی عوامل کلیدی
    selected_factors = random.sample(key_factors, k=min(3, len(key_factors)))
    
    return {
        "symbol": symbol,
        "summary": f"ارز {symbol} در حال حاضر در روند {trend} با قدرت {strength} قرار دارد.",
        "trend": trend,
        "strength": strength,
        "key_factors": selected_factors,
        "forecast": forecast,
        "risk_level": risk_level,
        "timeframe": timeframe,
        "is_sample_data": True,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _get_sample_sentiment():
    """
    تولید داده‌های نمونه برای تحلیل احساسات
    
    Returns:
        dict: تحلیل احساسات نمونه
    """
    import random
    import datetime
    
    # انتخاب برچسب احساسات
    sentiment_options = ["منفی", "خنثی", "مثبت"]
    sentiment_weights = [0.3, 0.3, 0.4]  # احتمال هر برچسب
    sentiment_label = random.choices(sentiment_options, weights=sentiment_weights, k=1)[0]
    
    # تنظیم نمره احساسات بر اساس برچسب
    if sentiment_label == "مثبت":
        overall_sentiment = round(random.uniform(0.3, 0.8), 2)
        sentiment_description = "احساسات بازار به طور کلی مثبت است، با خوش‌بینی نسبت به رشد آینده"
    elif sentiment_label == "منفی":
        overall_sentiment = round(random.uniform(-0.8, -0.3), 2)
        sentiment_description = "احساسات بازار به طور کلی منفی است، با نگرانی نسبت به کاهش قیمت‌ها"
    else:  # خنثی
        overall_sentiment = round(random.uniform(-0.3, 0.3), 2)
        sentiment_description = "احساسات بازار متعادل است، با انتظار برای مشخص شدن روند"
    
    # کلمات کلیدی بر اساس احساسات
    if sentiment_label == "مثبت":
        keywords = ["رشد", "سرمایه‌گذاری", "روند صعودی", "خرید", "پذیرش", "آینده روشن"]
    elif sentiment_label == "منفی":
        keywords = ["کاهش", "ریسک", "روند نزولی", "فروش", "محدودیت", "نگرانی"]
    else:  # خنثی
        keywords = ["نوسان", "انتظار", "تحلیل", "احتیاط", "استراتژی", "صبر"]
    
    # انتخاب تصادفی کلمات کلیدی
    selected_keywords = random.sample(keywords, k=min(4, len(keywords)))
    
    # ساخت مثال‌های تحلیل اخبار
    news_analysis = [
        {
            "title": "اخبار توسعه تکنولوژی بلاکچین",
            "sentiment": random.choice(sentiment_options),
            "impact": random.choice(["کم", "متوسط", "زیاد"]),
            "key_points": ["پیشرفت فنی", "افزایش کاربران"]
        },
        {
            "title": "تغییرات قانونی در بازار ارزهای دیجیتال",
            "sentiment": random.choice(sentiment_options),
            "impact": random.choice(["کم", "متوسط", "زیاد"]),
            "key_points": ["قوانین جدید", "تأثیر بر معاملات"]
        }
    ]
    
    return {
        "overall_sentiment": overall_sentiment,
        "sentiment_label": sentiment_label,
        "sentiment_description": sentiment_description,
        "news_analysis": news_analysis,
        "keywords": selected_keywords,
        "is_sample_data": True,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _get_sample_strategy(symbol, risk_level):
    """
    تولید داده‌های نمونه برای استراتژی معاملاتی
    
    Args:
        symbol (str): نماد ارز
        risk_level (str): سطح ریسک
        
    Returns:
        dict: استراتژی نمونه
    """
    import random
    import datetime
    
    # استراتژی‌های ممکن بر اساس سطح ریسک
    if risk_level == "کم":
        strategy_options = [
            {
                "name": "میانگین متحرک متقاطع",
                "type": "روند",
                "timeframe": "روزانه",
                "description": "استفاده از تقاطع میانگین‌های متحرک 50 و 200 روزه برای تشخیص روند"
            },
            {
                "name": "معامله حمایت و مقاومت",
                "type": "محدوده",
                "timeframe": "4 ساعته",
                "description": "خرید در نزدیکی حمایت‌ها و فروش در نزدیکی مقاومت‌ها با حد ضرر نزدیک"
            }
        ]
    elif risk_level == "متوسط":
        strategy_options = [
            {
                "name": "شکست محدوده",
                "type": "شکست",
                "timeframe": "4 ساعته",
                "description": "ورود پس از شکست محدوده‌های مهم با حجم بالا"
            },
            {
                "name": "RSI واگرایی",
                "type": "معکوس",
                "timeframe": "روزانه",
                "description": "شناسایی واگرایی‌های مثبت و منفی در اندیکاتور RSI"
            }
        ]
    else:  # ریسک زیاد
        strategy_options = [
            {
                "name": "اسکالپینگ با Bollinger Bands",
                "type": "نوسانی",
                "timeframe": "15 دقیقه",
                "description": "معاملات سریع بر اساس برگشت قیمت از باندهای بولینگر"
            },
            {
                "name": "فیبوناچی اکستنشن",
                "type": "روند",
                "timeframe": "ساعتی",
                "description": "هدف‌گذاری سود با استفاده از سطوح فیبوناچی اکستنشن در روندهای قوی"
            }
        ]
    
    # انتخاب یک استراتژی تصادفی
    strategy = random.choice(strategy_options)
    
    # تعیین نقاط ورود و خروج
    entry_points = [
        f"ورود در شکست سطح مقاومت {random.randint(5, 15)}%",
        f"ورود در تقاطع میانگین متحرک {random.choice(['50', '20', '100'])} روزه",
        f"ورود در برگشت از حمایت اصلی"
    ]
    
    exit_points = [
        f"خروج در رسیدن به هدف قیمتی {random.randint(10, 30)}%",
        f"خروج در شکست روند",
        f"خروج با سیگنال واگرایی"
    ]
    
    # تعیین حد ضرر و حد سود
    if risk_level == "کم":
        stop_loss = f"{random.randint(3, 8)}% زیر قیمت ورود"
        take_profit = f"{random.randint(10, 20)}% بالای قیمت ورود"
        risk_reward = f"1:{random.choice(['2.5', '3', '3.5'])}"
    elif risk_level == "متوسط":
        stop_loss = f"{random.randint(8, 15)}% زیر قیمت ورود"
        take_profit = f"{random.randint(20, 40)}% بالای قیمت ورود"
        risk_reward = f"1:{random.choice(['2', '2.5', '3'])}"
    else:  # ریسک زیاد
        stop_loss = f"{random.randint(15, 25)}% زیر قیمت ورود"
        take_profit = f"{random.randint(40, 75)}% بالای قیمت ورود"
        risk_reward = f"1:{random.choice(['1.5', '2', '2.5'])}"
    
    # شاخص‌های کلیدی
    key_indicators = [
        "RSI",
        "میانگین متحرک",
        "MACD",
        "حجم معاملات",
        "Bollinger Bands",
        "فیبوناچی"
    ]
    selected_indicators = random.sample(key_indicators, k=3)
    
    return {
        "symbol": symbol,
        "strategy_name": strategy["name"],
        "strategy_type": strategy["type"],
        "timeframe": strategy["timeframe"],
        "entry_points": random.sample(entry_points, k=2),
        "exit_points": random.sample(exit_points, k=2),
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_reward_ratio": risk_reward,
        "key_indicators": selected_indicators,
        "strategy_description": strategy["description"],
        "confidence": round(random.uniform(0.6, 0.9), 2),
        "risk_level": risk_level,
        "is_sample_data": True,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _get_sample_patterns(symbol, timeframe):
    """
    تولید داده‌های نمونه برای الگوهای قیمت
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        
    Returns:
        dict: الگوهای نمونه
    """
    import random
    import datetime
    
    # لیست الگوهای ممکن
    patterns = [
        {
            "name": "سر و شانه",
            "signal": "فروش",
            "description": "این الگو نشان‌دهنده پایان روند صعودی و احتمال شروع روند نزولی است"
        },
        {
            "name": "سر و شانه معکوس",
            "signal": "خرید",
            "description": "این الگو نشان‌دهنده پایان روند نزولی و احتمال شروع روند صعودی است"
        },
        {
            "name": "مثلث صعودی",
            "signal": "خرید",
            "description": "الگوی ادامه‌دهنده روند صعودی با همگرایی قیمت"
        },
        {
            "name": "مثلث نزولی",
            "signal": "فروش",
            "description": "الگوی ادامه‌دهنده روند نزولی با همگرایی قیمت"
        },
        {
            "name": "کف دوگانه",
            "signal": "خرید",
            "description": "الگوی برگشتی که نشان‌دهنده پایان روند نزولی است"
        },
        {
            "name": "سقف دوگانه",
            "signal": "فروش",
            "description": "الگوی برگشتی که نشان‌دهنده پایان روند صعودی است"
        },
        {
            "name": "پرچم",
            "signal": "ادامه روند",
            "description": "الگوی ادامه‌دهنده روند پس از یک حرکت قوی"
        },
        {
            "name": "گوه صعودی",
            "signal": "خرید",
            "description": "الگوی برگشتی در روند نزولی"
        },
        {
            "name": "الگوی هارمونیک گارتلی",
            "signal": "خرید",
            "description": "الگوی پیشرفته برای تشخیص نقاط برگشت"
        }
    ]
    
    # تصمیم‌گیری برای شناسایی الگو یا عدم شناسایی
    patterns_found = random.choice([True, True, True, False])  # احتمال 75% برای یافتن الگو
    
    if patterns_found:
        # تعیین تعداد الگوهای شناسایی شده
        pattern_count = random.randint(1, 2)
        
        # انتخاب الگوهای تصادفی
        selected_patterns = random.sample(patterns, k=pattern_count)
        
        identified_patterns = []
        for pattern in selected_patterns:
            completion = round(random.uniform(60, 98), 1)
            confidence = round(random.uniform(0.6, 0.9), 2)
            
            identified_patterns.append({
                "pattern_name": pattern["name"],
                "completion_percentage": completion,
                "signal": pattern["signal"],
                "confidence": confidence,
                "description": pattern["description"]
            })
            
        # ناحیه‌های مهم نمودار
        chart_areas = [
            f"حمایت اصلی در محدوده {random.randint(-10, -5)}% زیر قیمت فعلی",
            f"مقاومت کلیدی در محدوده {random.randint(5, 15)}% بالای قیمت فعلی"
        ]
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "patterns_found": True,
            "pattern_count": pattern_count,
            "identified_patterns": identified_patterns,
            "chart_areas": chart_areas,
            "is_sample_data": True,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "patterns_found": False,
            "pattern_count": 0,
            "identified_patterns": [],
            "chart_areas": [
                f"حمایت اصلی در محدوده {random.randint(-10, -5)}% زیر قیمت فعلی",
                f"مقاومت کلیدی در محدوده {random.randint(5, 15)}% بالای قیمت فعلی"
            ],
            "is_sample_data": True,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }