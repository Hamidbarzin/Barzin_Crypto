"""
ماژول آشکارسازی فرصت‌های خرید و فروش و نوسانات بازار
"""

import logging
from datetime import datetime, timedelta
import random  # برای داده‌های نمونه، در نسخه نهایی حذف خواهد شد
import pandas as pd

from crypto_bot.market_data import get_current_prices, get_historical_data
from crypto_bot.technical_analysis import get_technical_indicators
from crypto_bot.news_analyzer import get_latest_news, analyze_sentiment

# تنظیم لاگر
logger = logging.getLogger(__name__)

# آستانه‌های نوسان برای هشدارها
VOLATILITY_THRESHOLDS = {
    "extreme": 10.0,  # تغییر بیش از 10 درصد در یک ساعت
    "high": 5.0,      # تغییر بیش از 5 درصد در یک ساعت
    "medium": 3.0,    # تغییر بیش از 3 درصد در یک ساعت
    "low": 1.0        # تغییر بیش از 1 درصد در یک ساعت
}

# آستانه‌های شاخص‌های فنی
TECHNICAL_THRESHOLDS = {
    "overbought_rsi": 70,    # شاخص RSI بالای 70
    "oversold_rsi": 30,      # شاخص RSI زیر 30
    "strong_macd": 0.5,      # سیگنال قوی MACD
    "bb_squeeze": 0.1,       # فشردگی باندهای بولینگر
    "sma_crossover": 0.02    # تقاطع میانگین‌های متحرک
}

def detect_buy_sell_opportunities(symbols, sensitivity="medium"):
    """
    تشخیص فرصت‌های خرید و فروش بر اساس تحلیل فنی
    
    Args:
        symbols (list): لیست ارزها برای بررسی
        sensitivity (str): حساسیت تشخیص ('کم'، 'متوسط'، 'زیاد')
        
    Returns:
        list: لیست فرصت‌های شناسایی شده
    """
    opportunities = []
    
    # تنظیم ضریب حساسیت
    sensitivity_factor = {
        "low": 0.7,
        "medium": 1.0,
        "high": 1.3
    }.get(sensitivity, 1.0)
    
    try:
        # دریافت قیمت‌های فعلی
        current_prices = get_current_prices(symbols)
        
        # دریافت اخبار اخیر
        news = get_latest_news(limit=10)
        
        for symbol in symbols:
            try:
                # دریافت تحلیل فنی
                technical = get_technical_indicators(symbol)
                
                # تشخیص فرصت‌ها بر اساس شاخص‌های فنی
                price_data = {}
                if symbol in current_prices:
                    if isinstance(current_prices[symbol], dict):
                        price_data = current_prices[symbol]
                    else:
                        # اگر current_prices[symbol] یک عدد یا شیء float64 باشد
                        price_data = {'price': float(current_prices[symbol])}
                
                opportunity = _analyze_technical_indicators(symbol, technical, price_data, sensitivity_factor)
                
                # اضافه کردن تأثیر اخبار به تحلیل
                opportunity = _add_news_impact(opportunity, news, symbol)
                
                if opportunity:
                    opportunities.append(opportunity)
            except Exception as e:
                logger.error(f"خطا در تحلیل {symbol}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"خطا در تشخیص فرصت‌های خرید/فروش: {str(e)}")
    
    return opportunities

def detect_market_volatility(symbols, timeframe="1h", threshold="medium"):
    """
    تشخیص نوسانات قیمت در بازار
    
    Args:
        symbols (list): لیست ارزها برای بررسی
        timeframe (str): بازه زمانی تحلیل ('5m', '15m', '1h', '4h', '1d')
        threshold (str): آستانه نوسان ('کم'، 'متوسط'، 'زیاد'، 'بسیار زیاد')
        
    Returns:
        list: لیست نوسانات شناسایی شده
    """
    volatility_alerts = []
    
    # تنظیم آستانه‌ها بر اساس ورودی
    volatility_threshold = VOLATILITY_THRESHOLDS.get(threshold, VOLATILITY_THRESHOLDS["medium"])
    
    try:
        # دریافت قیمت‌های فعلی
        current_prices = get_current_prices(symbols)
        
        for symbol in symbols:
            try:
                # دریافت داده‌های تاریخچه
                historical_data = get_historical_data(symbol, timeframe=timeframe, limit=24)
                
                # محاسبه تغییرات قیمت
                if historical_data is None:
                    continue
                    
                # اگر لیست است، بررسی کنیم که خالی نباشد
                if isinstance(historical_data, list):
                    if not historical_data:  # اگر لیست خالی است
                        continue
                    # تبدیل لیست به دیتافریم
                    try:
                        historical_data = pd.DataFrame(historical_data)
                    except Exception as e:
                        logger.error(f"خطا در تبدیل داده‌های تاریخی به DataFrame برای {symbol}: {str(e)}")
                        continue
                
                # بررسی کنیم که دیتافریم خالی نباشد و ستون‌های مورد نیاز را داشته باشد
                if isinstance(historical_data, pd.DataFrame) and not historical_data.empty and 'close' in historical_data.columns and symbol in current_prices:
                    # اگر current_prices[symbol] یک دیکشنری باشد
                    if isinstance(current_prices[symbol], dict) and 'price' in current_prices[symbol]:
                        current_price = current_prices[symbol]['price']
                    # اگر current_prices[symbol] یک عدد یا شیء float64 باشد
                    else:
                        try:
                            current_price = float(current_prices[symbol])
                        except (ValueError, TypeError):
                            # اگر نتوانستیم به float تبدیل کنیم، از این حلقه خارج می‌شویم
                            continue
                    
                    # قیمت ابتدای دوره
                    start_price = historical_data.iloc[0]['close']
                    
                    # محاسبه درصد تغییر
                    change_percent = ((current_price - start_price) / start_price) * 100
                    
                    # بررسی آیا تغییر از آستانه بیشتر است
                    if abs(change_percent) >= volatility_threshold:
                        volatility_alerts.append({
                            'symbol': symbol,
                            'price': current_price,
                            'change_percent': change_percent,
                            'timeframe': timeframe,
                            'detected_at': datetime.now().isoformat(),
                            'type': 'rise' if change_percent > 0 else 'fall',
                            'message': f"{'افزایش' if change_percent > 0 else 'کاهش'} {abs(change_percent):.2f}% در قیمت {symbol} در {timeframe} اخیر"
                        })
            except Exception as e:
                logger.error(f"خطا در بررسی نوسان {symbol}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"خطا در تشخیص نوسانات بازار: {str(e)}")
    
    return volatility_alerts

def analyze_market_trend(symbols=None):
    """
    تحلیل روند کلی بازار
    
    Args:
        symbols (list): لیست ارزها برای بررسی (اگر None باشد، ارزهای پیش‌فرض استفاده می‌شود)
        
    Returns:
        dict: اطلاعات روند بازار
    """
    if symbols is None:
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
    
    try:
        # بررسی روند قیمت ارزهای اصلی
        prices = get_current_prices(symbols)
        
        # دریافت اخبار مهم مرتبط با بازار
        news = get_latest_news(limit=15)
        
        # تحلیل احساسات اخبار
        overall_sentiment = 0
        for article in news:
            sentiment_score = article.get('sentiment', {}).get('score', 0)
            overall_sentiment += sentiment_score
        
        if len(news) > 0:
            overall_sentiment /= len(news)
        
        # بررسی وضعیت شاخص‌های فنی BTC به عنوان ارز پیشرو
        btc_technical = get_technical_indicators("BTC/USDT")
        
        # تحلیل روند بر اساس معیارهای فوق
        trend = "neutral"
        # اطمینان از اینکه rsi یک عدد است
        rsi_value = 50
        if isinstance(btc_technical, dict) and 'rsi' in btc_technical:
            if isinstance(btc_technical['rsi'], (int, float)):
                rsi_value = btc_technical['rsi']
            
        if overall_sentiment > 0.3 and rsi_value > 60:
            trend = "bullish"
        elif overall_sentiment < -0.3 and rsi_value < 40:
            trend = "bearish"
        
        # ارزهای تحت تأثیر
        affected_coins = []
        for symbol in symbols:
            if symbol in prices:
                affected_coins.append(symbol.split('/')[0])
        
        # دلیل روند
        if trend == "bullish":
            reason = "روند صعودی با حمایت بنیادی و فنی تأیید شده است"
            if overall_sentiment > 0.5:
                reason += ". اخبار اخیر بسیار مثبت هستند"
        elif trend == "bearish":
            reason = "روند نزولی با فشار فروش و سیگنال‌های فنی تأیید شده است"
            if overall_sentiment < -0.5:
                reason += ". اخبار اخیر منفی هستند"
        else:
            reason = "بازار در وضعیت تثبیت و انتظار قرار دارد"
        
        return {
            'trend': _translate_trend(trend),
            'sentiment_score': overall_sentiment,
            'affected_coins': affected_coins,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"خطا در تحلیل روند بازار: {str(e)}")
        return {
            'trend': 'خنثی',
            'sentiment_score': 0,
            'affected_coins': [],
            'reason': 'خطا در تحلیل داده‌ها',
            'timestamp': datetime.now().isoformat()
        }

def _analyze_technical_indicators(symbol, technical, price_data, sensitivity_factor):
    """
    تحلیل شاخص‌های فنی برای تشخیص فرصت‌های خرید و فروش
    
    Args:
        symbol (str): نماد ارز
        technical (dict): داده‌های تحلیل فنی
        price_data (dict): داده‌های قیمت فعلی
        sensitivity_factor (float): ضریب حساسیت
        
    Returns:
        dict: اطلاعات فرصت شناسایی شده یا None
    """
    # بررسی داده‌های ورودی
    if not technical or not price_data:
        return None
    
    # استخراج شاخص‌های کلیدی
    rsi = technical.get('rsi', 50)
    macd = technical.get('macd', {}).get('histogram', 0)
    current_price = price_data.get('price', 0)
    
    # بررسی وضعیت اشباع خرید/فروش (RSI)
    signal_type = None
    signal_strength = 0
    
    # تحلیل RSI
    if rsi <= TECHNICAL_THRESHOLDS["oversold_rsi"] * sensitivity_factor:
        signal_type = "buy"
        signal_strength += 0.4
    elif rsi >= TECHNICAL_THRESHOLDS["overbought_rsi"] / sensitivity_factor:
        signal_type = "sell"
        signal_strength += 0.4
    
    # تحلیل MACD
    if macd > TECHNICAL_THRESHOLDS["strong_macd"] * sensitivity_factor:
        if signal_type != "sell":  # اگر RSI قبلا سیگنال فروش نداده باشد
            signal_type = "buy"
            signal_strength += 0.3
    elif macd < -TECHNICAL_THRESHOLDS["strong_macd"] * sensitivity_factor:
        if signal_type != "buy":  # اگر RSI قبلا سیگنال خرید نداده باشد
            signal_type = "sell"
            signal_strength += 0.3
    
    # بررسی باندهای بولینگر
    upper_band = technical.get('bollinger_bands', {}).get('upper', current_price * 1.05)
    lower_band = technical.get('bollinger_bands', {}).get('lower', current_price * 0.95)
    
    # نزدیکی به خط پایین باند بولینگر: سیگنال خرید
    if current_price <= lower_band * (1 + 0.01 * sensitivity_factor):
        if signal_type != "sell":  # تقویت سیگنال خرید یا تغییر سیگنال فروش ضعیف
            signal_type = "buy"
            signal_strength += 0.3
    
    # نزدیکی به خط بالای باند بولینگر: سیگنال فروش
    elif current_price >= upper_band * (1 - 0.01 * sensitivity_factor):
        if signal_type != "buy":  # تقویت سیگنال فروش یا تغییر سیگنال خرید ضعیف
            signal_type = "sell"
            signal_strength += 0.3
    
    # اگر قدرت سیگنال کافی نباشد
    if signal_strength < 0.5:
        return None
    
    # ساخت پیام مناسب
    message = ""
    if signal_type == "buy":
        message = f"فرصت خرید {symbol} با قیمت {current_price} بر اساس "
        if rsi <= TECHNICAL_THRESHOLDS["oversold_rsi"] * sensitivity_factor:
            message += f"RSI اشباع فروش ({rsi:.1f}) "
        if macd > TECHNICAL_THRESHOLDS["strong_macd"] * sensitivity_factor:
            message += f"و سیگنال مثبت MACD ({macd:.3f}) "
        if current_price <= lower_band * (1 + 0.01 * sensitivity_factor):
            message += f"و نزدیکی به خط پایین باند بولینگر "
    else:  # sell
        message = f"فرصت فروش {symbol} با قیمت {current_price} بر اساس "
        if rsi >= TECHNICAL_THRESHOLDS["overbought_rsi"] / sensitivity_factor:
            message += f"RSI اشباع خرید ({rsi:.1f}) "
        if macd < -TECHNICAL_THRESHOLDS["strong_macd"] * sensitivity_factor:
            message += f"و سیگنال منفی MACD ({macd:.3f}) "
        if current_price >= upper_band * (1 - 0.01 * sensitivity_factor):
            message += f"و نزدیکی به خط بالای باند بولینگر "
    
    return {
        'symbol': symbol,
        'price': current_price,
        'action': _translate_action(signal_type),
        'english_action': signal_type,
        'strength': signal_strength,
        'detected_at': datetime.now().isoformat(),
        'message': message,
        'technical_factors': {
            'rsi': rsi,
            'macd': macd,
            'bollinger_distance': (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5
        }
    }

def _add_news_impact(opportunity, news, symbol):
    """
    اضافه کردن تأثیر اخبار به تحلیل فرصت‌های خرید و فروش
    
    Args:
        opportunity (dict): فرصت شناسایی شده
        news (list): اخبار مرتبط
        symbol (str): نماد ارز
        
    Returns:
        dict: فرصت به‌روزرسانی شده
    """
    if not opportunity:
        return None
    
    # استخراج نام ارز از نماد
    coin = symbol.split('/')[0]
    
    # جستجوی اخبار مرتبط با این ارز
    relevant_news = []
    for article in news:
        title = article.get('title', '').lower()
        if coin.lower() in title:
            relevant_news.append(article)
    
    # اگر خبر مرتبطی وجود دارد
    if relevant_news:
        # محاسبه میانگین احساسات اخبار
        news_sentiment = 0
        for article in relevant_news:
            sentiment_score = article.get('sentiment', {}).get('score', 0)
            news_sentiment += sentiment_score
        
        if len(relevant_news) > 0:
            news_sentiment /= len(relevant_news)
        
        # اضافه کردن اطلاعات اخبار به فرصت
        opportunity['news_impact'] = news_sentiment
        opportunity['relevant_news_count'] = len(relevant_news)
        
        # تنظیم قدرت سیگنال بر اساس اخبار
        if (opportunity['english_action'] == 'buy' and news_sentiment > 0.3) or \
           (opportunity['english_action'] == 'sell' and news_sentiment < -0.3):
            # تقویت سیگنال اگر اخبار با آن هم‌راستا باشد
            opportunity['strength'] += 0.2
            opportunity['message'] += f"و {len(relevant_news)} خبر مرتبط با احساسات {'مثبت' if news_sentiment > 0 else 'منفی'}"
        elif (opportunity['english_action'] == 'buy' and news_sentiment < -0.3) or \
             (opportunity['english_action'] == 'sell' and news_sentiment > 0.3):
            # تضعیف سیگنال اگر اخبار با آن در تضاد باشد
            opportunity['strength'] -= 0.2
            opportunity['message'] += f"(هشدار: {len(relevant_news)} خبر مرتبط با احساسات {'منفی' if news_sentiment < 0 else 'مثبت'} وجود دارد)"
        
        # حذف فرصت اگر قدرت سیگنال کافی نباشد
        if opportunity['strength'] < 0.5:
            return None
    
    return opportunity

def _translate_action(action):
    """
    ترجمه عملیات به فارسی
    """
    translations = {
        "buy": "خرید",
        "sell": "فروش",
        "hold": "نگهداری"
    }
    return translations.get(action, action)

def _translate_trend(trend):
    """
    ترجمه روند به فارسی
    """
    translations = {
        "bullish": "صعودی",
        "bearish": "نزولی",
        "neutral": "خنثی"
    }
    return translations.get(trend, trend)

# نمونه استفاده
if __name__ == "__main__":
    # تنظیم لاگینگ
    logging.basicConfig(level=logging.INFO)
    
    # تست تشخیص فرصت‌های خرید و فروش
    symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "SOL/USDT"]
    opportunities = detect_buy_sell_opportunities(symbols)
    
    for opportunity in opportunities:
        logger.info(f"فرصت: {opportunity['action']} {opportunity['symbol']} با قیمت {opportunity['price']}")
        logger.info(f"دلیل: {opportunity['message']}")
        
    # تست تشخیص نوسانات
    volatility = detect_market_volatility(symbols, timeframe="1h", threshold="medium")
    
    for alert in volatility:
        logger.info(f"هشدار نوسان: {alert['message']}")
        
    # تست تحلیل روند
    trend = analyze_market_trend(symbols)
    logger.info(f"تحلیل روند: {trend['trend']} - {trend['reason']}")