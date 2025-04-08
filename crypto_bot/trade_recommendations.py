"""
ماژول پیشنهادهای معاملاتی

این ماژول با تحلیل داده‌های بازار، پیشنهادهای خرید و فروش ایجاد می‌کند.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

from crypto_bot.market_data import get_current_prices, get_historical_data
from crypto_bot.technical_analysis import calculate_technical_indicators, get_technical_analysis

logger = logging.getLogger(__name__)

def get_trade_recommendations(top_n: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """
    تولید پیشنهادهای خرید و فروش بر اساس تحلیل فنی

    Args:
        top_n (int): تعداد پیشنهادات برتر
        
    Returns:
        Dict: دیکشنری شامل دو لیست "buy" و "sell" با پیشنهادهای معاملاتی
    """
    try:
        # دریافت قیمت‌های جاری
        current_prices = get_current_prices(symbols=["BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "SOL/USDT", "ADA/USDT"])
        
        # لیست نمادهای قابل بررسی
        symbols = list(current_prices.keys())
        
        # پیشنهادات خرید و فروش
        buy_recommendations = []
        sell_recommendations = []
        
        # بررسی هر نماد
        for symbol in symbols:
            if not isinstance(current_prices[symbol], dict) or "error" in current_prices[symbol]:
                continue
                
            # دریافت داده‌های تاریخی برای محاسبه اندیکاتورها
            historical_data = get_historical_data(symbol, timeframe="1d", limit=30)
            
            # تحلیل فنی
            indicators = calculate_technical_indicators(historical_data, symbol)
            
            # قیمت فعلی
            current_price = current_prices[symbol]['price']
            
            # حجم معاملات 24 ساعته
            volume_24h = current_prices[symbol].get('volume_24h', 0)
            
            # تعداد معاملات (اطلاعات تقریبی بر اساس میانگین مقدار معاملات)
            # در حالت واقعی از API صرافی دریافت می‌شود
            avg_trade_size = random.uniform(500, 5000)  # میانگین اندازه هر معامله (دلار)
            trade_count = int(volume_24h / avg_trade_size) if volume_24h > 0 else 0
            
            # امتیاز سیگنال
            signal_score = 0
            
            # محاسبه امتیاز سیگنال
            # RSI
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:  # اشباع فروش
                    signal_score += 2
                elif rsi > 70:  # اشباع خرید
                    signal_score -= 2
                    
            # MACD
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                if macd > macd_signal:  # MACD بالای خط سیگنال
                    signal_score += 1.5
                else:  # MACD پایین خط سیگنال
                    signal_score -= 1.5
                    
            # میانگین‌های متحرک
            if 'ma20' in indicators and 'ma50' in indicators and 'ma200' in indicators:
                ma20 = indicators['ma20']
                ma50 = indicators['ma50']
                ma200 = indicators['ma200']
                
                if current_price > ma20 > ma50 > ma200:  # روند صعودی قوی
                    signal_score += 2
                elif current_price < ma20 < ma50 < ma200:  # روند نزولی قوی
                    signal_score -= 2
                elif ma20 > current_price > ma50:  # حمایت MA50
                    signal_score += 0.5
                elif ma20 < current_price < ma50:  # مقاومت MA50
                    signal_score -= 0.5
                    
            # باندهای بولینگر
            if 'bb_upper' in indicators and 'bb_lower' in indicators:
                bb_upper = indicators['bb_upper']
                bb_lower = indicators['bb_lower']
                
                if current_price < bb_lower:  # زیر باند پایینی
                    signal_score += 1
                elif current_price > bb_upper:  # بالای باند بالایی
                    signal_score -= 1
            
            # حجم معاملات
            if volume_24h > 1000000:  # حجم معاملات بالا
                signal_score = signal_score * 1.2  # تقویت سیگنال
                
            # دلایل سیگنال
            reasons = []
            
            # تعیین سیگنال نهایی
            recommendation = None
            
            if signal_score >= 2:
                recommendation = {
                    'symbol': symbol,
                    'action': 'buy',
                    'price': current_price,
                    'strength': min(5, int(signal_score)),
                    'volume_24h': volume_24h,
                    'trade_count': trade_count,
                    'confidence': min(0.95, 0.5 + signal_score / 10),
                    'reasons': generate_buy_reasons(indicators, current_price)
                }
                buy_recommendations.append(recommendation)
            
            elif signal_score <= -2:
                recommendation = {
                    'symbol': symbol,
                    'action': 'sell',
                    'price': current_price,
                    'strength': min(5, int(abs(signal_score))),
                    'volume_24h': volume_24h,
                    'trade_count': trade_count,
                    'confidence': min(0.95, 0.5 + abs(signal_score) / 10),
                    'reasons': generate_sell_reasons(indicators, current_price)
                }
                sell_recommendations.append(recommendation)
        
        # مرتب سازی پیشنهادات بر اساس قدرت سیگنال
        buy_recommendations = sorted(buy_recommendations, key=lambda x: x['strength'] * x['confidence'], reverse=True)[:top_n]
        sell_recommendations = sorted(sell_recommendations, key=lambda x: x['strength'] * x['confidence'], reverse=True)[:top_n]
        
        return {
            'buy': buy_recommendations,
            'sell': sell_recommendations
        }
    
    except Exception as e:
        logger.error(f"خطا در تولید پیشنهادهای معاملاتی: {str(e)}")
        return {
            'buy': [],
            'sell': []
        }

def generate_buy_reasons(indicators, current_price):
    """تولید دلایل پیشنهاد خرید"""
    reasons = []
    
    if 'rsi' in indicators and indicators['rsi'] < 30:
        reasons.append("RSI در ناحیه اشباع فروش")
        
    if 'macd' in indicators and 'macd_signal' in indicators:
        if indicators['macd'] > indicators['macd_signal']:
            reasons.append("MACD بالای خط سیگنال")
            
    if 'ma20' in indicators and 'ma50' in indicators:
        ma20 = indicators['ma20']
        ma50 = indicators['ma50']
        if current_price > ma20 > ma50:
            reasons.append("قیمت بالای میانگین‌های متحرک MA20 و MA50")
            
    if 'bb_lower' in indicators and current_price < indicators['bb_lower']:
        reasons.append("قیمت زیر باند پایینی بولینگر")
        
    if not reasons:
        reasons.append("ترکیب مثبت اندیکاتورهای تکنیکال")
        
    return reasons

def generate_sell_reasons(indicators, current_price):
    """تولید دلایل پیشنهاد فروش"""
    reasons = []
    
    if 'rsi' in indicators and indicators['rsi'] > 70:
        reasons.append("RSI در ناحیه اشباع خرید")
        
    if 'macd' in indicators and 'macd_signal' in indicators:
        if indicators['macd'] < indicators['macd_signal']:
            reasons.append("MACD زیر خط سیگنال")
            
    if 'ma20' in indicators and 'ma50' in indicators:
        ma20 = indicators['ma20']
        ma50 = indicators['ma50']
        if current_price < ma20 < ma50:
            reasons.append("قیمت زیر میانگین‌های متحرک MA20 و MA50")
            
    if 'bb_upper' in indicators and current_price > indicators['bb_upper']:
        reasons.append("قیمت بالای باند بالایی بولینگر")
        
    if not reasons:
        reasons.append("ترکیب منفی اندیکاتورهای تکنیکال")
        
    return reasons

def get_recommendation_summary(recommendations):
    """
    تولید خلاصه پیشنهادات معاملاتی برای ارسال در تلگرام
    
    Args:
        recommendations (Dict): دیکشنری پیشنهادات خرید و فروش
        
    Returns:
        str: متن خلاصه پیشنهادات
    """
    summary = "*پیشنهادهای معاملاتی:*\n\n"
    
    # پیشنهادات خرید
    buy_recs = recommendations.get('buy', [])
    if buy_recs:
        summary += "📈 *پیشنهادات خرید:*\n"
        for i, rec in enumerate(buy_recs, 1):
            symbol = rec['symbol']
            price = rec['price']
            strength = "⭐" * rec['strength']
            confidence = f"{rec['confidence'] * 100:.1f}%"
            volume = rec['volume_24h']
            trades = rec['trade_count']
            
            summary += f"{i}. {symbol}: {price:,.2f} USDT {strength}\n"
            summary += f"   اطمینان: {confidence} | حجم: {volume:,.0f} USDT | تعداد معاملات: {trades:,}\n"
            
            # دلایل
            if rec['reasons']:
                reasons = "\n   • ".join(rec['reasons'])
                summary += f"   دلایل: • {reasons}\n"
            
            summary += "\n"
    else:
        summary += "📈 *پیشنهادات خرید:* هیچ پیشنهاد خریدی یافت نشد\n\n"
    
    # پیشنهادات فروش
    sell_recs = recommendations.get('sell', [])
    if sell_recs:
        summary += "📉 *پیشنهادات فروش:*\n"
        for i, rec in enumerate(sell_recs, 1):
            symbol = rec['symbol']
            price = rec['price']
            strength = "⭐" * rec['strength']
            confidence = f"{rec['confidence'] * 100:.1f}%"
            volume = rec['volume_24h']
            trades = rec['trade_count']
            
            summary += f"{i}. {symbol}: {price:,.2f} USDT {strength}\n"
            summary += f"   اطمینان: {confidence} | حجم: {volume:,.0f} USDT | تعداد معاملات: {trades:,}\n"
            
            # دلایل
            if rec['reasons']:
                reasons = "\n   • ".join(rec['reasons'])
                summary += f"   دلایل: • {reasons}\n"
            
            summary += "\n"
    else:
        summary += "📉 *پیشنهادات فروش:* هیچ پیشنهاد فروشی یافت نشد\n\n"
    
    return summary