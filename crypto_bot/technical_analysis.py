"""
ماژول تحلیل تکنیکال برای ارزهای دیجیتال

این ماژول تحلیل تکنیکال را با استفاده از کتابخانه TA انجام می‌دهد.
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import talib - Not currently available in the environment

from typing import Dict, List, Any, Union, Optional
from datetime import datetime, timedelta

from crypto_bot.market_data import get_historical_data

logger = logging.getLogger(__name__)

def calculate_technical_indicators(historical_data: Union[pd.DataFrame, list], symbol: str) -> Dict[str, Any]:
    """
    محاسبه اندیکاتورهای تکنیکال برای یک ارز

    Args:
        historical_data: داده‌های تاریخی با ستون‌های OHLC (DataFrame یا list)
        symbol: نماد ارز

    Returns:
        Dict[str, Any]: اندیکاتورهای تکنیکال
    """
    # Check if historical_data is None or empty
    if historical_data is None:
        logger.warning(f"داده‌های تاریخی برای {symbol} در دسترس نیست")
        return {}
        
    # Convert list to DataFrame if it's a list
    if isinstance(historical_data, list):
        if not historical_data:  # Check if list is empty
            logger.warning(f"داده‌های تاریخی خالی برای {symbol}")
            return {}
        try:
            historical_data = pd.DataFrame(historical_data)
        except Exception as e:
            logger.error(f"خطا در تبدیل داده‌های تاریخی به DataFrame برای {symbol}: {str(e)}")
            return {}
    
    # Check if DataFrame is empty
    if isinstance(historical_data, pd.DataFrame) and historical_data.empty:
        logger.warning(f"داده‌های تاریخی برای {symbol} خالی است")
        return {}

    try:
        # مطمئن شویم که داده‌ها تمیز هستند
        df = historical_data.copy()
        
        # نام ستون‌ها را چک کنیم
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for column in required_columns:
            if column not in df.columns:
                logger.warning(f"ستون {column} در داده‌های تاریخی یافت نشد")
                return {}

        # تبدیل به نوع عددی
        for column in required_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')

        # حذف ردیف‌های با مقادیر گم شده
        df = df.dropna(subset=required_columns)

        if len(df) < 14:
            logger.warning(f"داده‌های تاریخی برای {symbol} کافی نیست (نیاز به حداقل 14 روز)")
            return {}

        # محاسبه اندیکاتورها
        indicators = {}

        # به دلیل عدم دسترسی به talib، از محاسبات ساده برای اندیکاتورها استفاده می‌کنیم
        
        # RSI (محاسبه ساده)
        close_diff = df['close'].diff().dropna()
        gains = close_diff.mask(close_diff < 0, 0)
        losses = -close_diff.mask(close_diff > 0, 0)
        avg_gain = gains.rolling(window=14).mean().iloc[-1]
        avg_loss = losses.rolling(window=14).mean().iloc[-1]
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        indicators['rsi'] = 100 - (100 / (1 + rs))

        # میانگین‌های متحرک
        indicators['ma20'] = df['close'].rolling(window=20).mean().iloc[-1]
        indicators['ma50'] = df['close'].rolling(window=50).mean().iloc[-1]
        indicators['ma200'] = df['close'].rolling(window=200).mean().iloc[-1]

        # MACD (محاسبه ساده)
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        indicators['macd'] = macd_line.iloc[-1]
        indicators['macd_signal'] = signal_line.iloc[-1]
        indicators['macd_histogram'] = macd_line.iloc[-1] - signal_line.iloc[-1]

        # باندهای بولینگر
        ma20 = df['close'].rolling(window=20).mean()
        std20 = df['close'].rolling(window=20).std()
        
        upper_band = ma20 + (std20 * 2)
        lower_band = ma20 - (std20 * 2)
        
        indicators['bb_upper'] = upper_band.iloc[-1]
        indicators['bb_middle'] = ma20.iloc[-1]
        indicators['bb_lower'] = lower_band.iloc[-1]
        indicators['bb_width'] = (upper_band.iloc[-1] - lower_band.iloc[-1]) / ma20.iloc[-1]

        # استوکاستیک (محاسبه ساده)
        low_min = df['low'].rolling(window=14).min()
        high_max = df['high'].rolling(window=14).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        k_3 = k.rolling(window=3).mean()
        d_3 = k_3.rolling(window=3).mean()
        
        indicators['stoch_k'] = k_3.iloc[-1]
        indicators['stoch_d'] = d_3.iloc[-1]

        # حجم میانگین معاملات
        indicators['volume_ema'] = df['volume'].ewm(span=20, adjust=False).mean().iloc[-1]
        
        # روند قیمت
        price_change = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10] * 100
        indicators['price_trend_10d'] = price_change
        
        return indicators
    
    except Exception as e:
        logger.error(f"خطا در محاسبه اندیکاتورهای تکنیکال برای {symbol}: {str(e)}")
        return {}

def get_technical_analysis(symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
    """
    تحلیل تکنیکال یک ارز

    Args:
        symbol: نماد ارز
        timeframe: بازه زمانی

    Returns:
        Dict[str, Any]: نتایج تحلیل تکنیکال
    """
    try:
        # دریافت داده‌های تاریخی
        historical_data = get_historical_data(symbol, timeframe=timeframe, limit=100)
        
        # آماده‌سازی نتیجه
        analysis = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Get current price if possible
        current_price = None
        if isinstance(historical_data, pd.DataFrame) and not historical_data.empty and 'close' in historical_data.columns:
            current_price = historical_data['close'].iloc[-1]
        elif isinstance(historical_data, list) and historical_data and 'close' in historical_data[-1]:
            current_price = historical_data[-1]['close']
        
        # If we have a current price, add it to the analysis
        if current_price is not None:
            analysis['current_price'] = current_price
        
        # محاسبه اندیکاتورها
        indicators = calculate_technical_indicators(historical_data, symbol)
        
        # ترکیب با اندیکاتورها
        analysis.update(indicators)
        
        # محاسبه سیگنال
        signal = "خنثی"
        signal_strength = 0
        
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi < 30:
                signal = "خرید"
                signal_strength += 2
            elif rsi > 70:
                signal = "فروش"
                signal_strength -= 2
                
        if 'macd' in indicators and 'macd_signal' in indicators:
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            if macd > macd_signal:
                if signal != "فروش":
                    signal = "خرید"
                signal_strength += 1
            elif macd < macd_signal:
                if signal != "خرید":
                    signal = "فروش"
                signal_strength -= 1
                
        if 'ma20' in indicators and 'ma50' in indicators and 'ma200' in indicators:
            ma20 = indicators['ma20']
            ma50 = indicators['ma50']
            ma200 = indicators['ma200']
            
            # Use safely retrieved current_price or indicators['current_price'] if it exists
            if current_price is not None:
                if current_price > ma20 > ma50 > ma200:
                    if signal != "فروش":
                        signal = "خرید"
                    signal_strength += 2
                elif current_price < ma20 < ma50 < ma200:
                    if signal != "خرید":
                        signal = "فروش"
                    signal_strength -= 2
        
        # تعیین قدرت سیگنال
        if signal_strength >= 3:
            final_signal = "خرید قوی"
        elif signal_strength > 0:
            final_signal = "خرید"
        elif signal_strength <= -3:
            final_signal = "فروش قوی"
        elif signal_strength < 0:
            final_signal = "فروش"
        else:
            final_signal = "خنثی"
            
        analysis['signal'] = final_signal
        analysis['signal_strength'] = abs(signal_strength)
            
        return analysis
    
    except Exception as e:
        logger.error(f"خطا در تحلیل تکنیکال {symbol}: {str(e)}")
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }

def analyze_symbol(symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
    """
    تابع تحلیل نماد با استفاده از ماژول تحلیل تکنیکال
    
    Args:
        symbol: نماد ارز
        timeframe: بازه زمانی
    
    Returns:
        Dict[str, Any]: نتایج تحلیل تکنیکال
    """
    return get_technical_analysis(symbol, timeframe)


def get_technical_indicators(symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
    """
    دریافت اندیکاتورهای تکنیکال برای یک ارز
    
    این تابع برای استفاده در ماژول market_detector اضافه شده است
    و همان تابع calculate_technical_indicators را فراخوانی می‌کند.
    
    Args:
        symbol: نماد ارز
        timeframe: بازه زمانی
    
    Returns:
        Dict[str, Any]: اندیکاتورهای تکنیکال
    """
    try:
        # دریافت داده‌های تاریخی
        historical_data = get_historical_data(symbol, timeframe=timeframe, limit=100)
        
        # محاسبه اندیکاتورها
        indicators = calculate_technical_indicators(historical_data, symbol)
        
        return indicators
    
    except Exception as e:
        logger.error(f"خطا در دریافت اندیکاتورهای تکنیکال برای {symbol}: {str(e)}")
        return {}