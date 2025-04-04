#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تحلیل تکنیکال برای ارزهای دیجیتال

این ماژول شاخص‌های تکنیکال مهم را محاسبه می‌کند و سیگنال‌های معاملاتی تولید می‌کند.
"""

import logging
import numpy as np
import pandas as pd
import ta
from datetime import datetime, timedelta
import traceback

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# در این نسخه ساده از داده‌های نمونه استفاده می‌کنیم
# در نسخه‌های آینده می‌توان از API‌های واقعی استفاده کرد
def get_sample_data(symbol, days=30):
    """
    دریافت داده‌های نمونه برای تست الگوریتم‌های تحلیل تکنیکال
    
    Args:
        symbol (str): نماد ارز دیجیتال
        days (int): تعداد روزهای داده
        
    Returns:
        pd.DataFrame: دیتافریم حاوی داده‌های قیمت
    """
    # ساخت یک سری زمانی نمونه
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # مقادیر قیمت پایه برای ارزهای مختلف
    base_prices = {
        'BTC/USDT': 65000,
        'ETH/USDT': 3200,
        'XRP/USDT': 0.52,
        'BNB/USDT': 550,
        'SOL/USDT': 140,
        'ADA/USDT': 0.45,
        'DOGE/USDT': 0.12,
        'DOT/USDT': 6.5,
        'AVAX/USDT': 35,
        'LUNA/USDT': 0.8
    }
    
    # قیمت پایه ارز انتخاب شده
    base_price = base_prices.get(symbol, 1000)
    
    # ایجاد نوسانات قیمت با استفاده از نویز تصادفی
    np.random.seed(42)  # برای قابلیت تکرار
    
    # ایجاد روند کلی (صعودی، نزولی یا جانبی)
    trend = np.random.choice(['up', 'down', 'sideways'], p=[0.4, 0.3, 0.3])
    
    if trend == 'up':
        trend_factor = np.linspace(0, 0.2, len(dates))
    elif trend == 'down':
        trend_factor = np.linspace(0, -0.2, len(dates))
    else:
        trend_factor = np.zeros(len(dates))
    
    # ایجاد نوسانات روزانه
    daily_changes = np.random.normal(0, 0.03, len(dates)) 
    
    # محاسبه قیمت‌ها با ترکیب روند و نوسانات
    changes = trend_factor + daily_changes
    prices = base_price * (1 + np.cumsum(changes))
    
    # حصول اطمینان از اینکه قیمت‌ها مثبت هستند
    prices = np.maximum(prices, base_price * 0.5)
    
    # ایجاد قیمت‌های OHLC
    high_prices = prices * (1 + np.random.uniform(0, 0.03, len(dates)))
    low_prices = prices * (1 - np.random.uniform(0, 0.03, len(dates)))
    open_prices = np.roll(prices, 1)
    open_prices[0] = prices[0] * (1 + np.random.uniform(-0.02, 0.02))
    
    # محاسبه حجم معاملات
    volumes = base_price * 100 * (1 + np.random.uniform(-0.5, 1.5, len(dates)))
    
    # ایجاد دیتافریم
    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': prices,
        'volume': volumes
    })
    
    df.set_index('date', inplace=True)
    return df

def calculate_indicators(df):
    """
    محاسبه شاخص‌های تکنیکال برای داده‌های قیمت
    
    Args:
        df (pd.DataFrame): دیتافریم حاوی داده‌های OHLCV
        
    Returns:
        pd.DataFrame: دیتافریم با شاخص‌های اضافه شده
    """
    try:
        # افزودن شاخص‌های تکنیکال با استفاده از کتابخانه TA
        
        # شاخص‌های روند
        # میانگین متحرک ساده
        df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        
        # میانگین متحرک نمایی
        df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
        df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
        
        # MACD
        macd = ta.trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # شاخص‌های مومنتوم
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # شاخص‌های نوسان
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_mid'] = bollinger.bollinger_mavg()
        df['bb_low'] = bollinger.bollinger_lband()
        
        # ATR (Average True Range)
        df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
        
        return df
    except Exception as e:
        logger.error(f"خطا در محاسبه شاخص‌های تکنیکال: {str(e)}")
        logger.error(traceback.format_exc())
        return df

def generate_signals(df):
    """
    تولید سیگنال‌های معاملاتی بر اساس شاخص‌های تکنیکال
    
    Args:
        df (pd.DataFrame): دیتافریم با شاخص‌های تکنیکال
        
    Returns:
        pd.DataFrame: دیتافریم با سیگنال‌های معاملاتی
    """
    try:
        # سیگنال‌های میانگین متحرک
        df['sma_signal'] = 0
        df.loc[df['sma_20'] > df['sma_50'], 'sma_signal'] = 1  # سیگنال خرید
        df.loc[df['sma_20'] < df['sma_50'], 'sma_signal'] = -1  # سیگنال فروش
        
        # سیگنال‌های MACD
        df['macd_signal_line'] = 0
        df.loc[df['macd'] > df['macd_signal'], 'macd_signal_line'] = 1  # سیگنال خرید
        df.loc[df['macd'] < df['macd_signal'], 'macd_signal_line'] = -1  # سیگنال فروش
        
        # سیگنال‌های RSI
        df['rsi_signal'] = 0
        df.loc[df['rsi'] < 30, 'rsi_signal'] = 1  # اشباع فروش (سیگنال خرید)
        df.loc[df['rsi'] > 70, 'rsi_signal'] = -1  # اشباع خرید (سیگنال فروش)
        
        # سیگنال‌های Stochastic
        df['stoch_signal'] = 0
        df.loc[(df['stoch_k'] < 20) & (df['stoch_k'] > df['stoch_d']), 'stoch_signal'] = 1  # سیگنال خرید
        df.loc[(df['stoch_k'] > 80) & (df['stoch_k'] < df['stoch_d']), 'stoch_signal'] = -1  # سیگنال فروش
        
        # سیگنال‌های Bollinger Bands
        df['bb_signal'] = 0
        df.loc[df['close'] < df['bb_low'], 'bb_signal'] = 1  # قیمت زیر باند پایین (سیگنال خرید)
        df.loc[df['close'] > df['bb_high'], 'bb_signal'] = -1  # قیمت بالای باند بالا (سیگنال فروش)
        
        # محاسبه سیگنال کلی با ترکیب سیگنال‌های مختلف
        # وزن‌دهی به سیگنال‌های مختلف می‌تواند بر اساس نیاز تنظیم شود
        df['combined_signal'] = (
            0.3 * df['sma_signal'] + 
            0.3 * df['macd_signal_line'] + 
            0.15 * df['rsi_signal'] + 
            0.15 * df['stoch_signal'] + 
            0.1 * df['bb_signal']
        )
        
        return df
    except Exception as e:
        logger.error(f"خطا در تولید سیگنال‌های معاملاتی: {str(e)}")
        logger.error(traceback.format_exc())
        return df

def get_latest_signals(symbol, timeframe='1d'):
    """
    دریافت آخرین سیگنال‌های معاملاتی برای یک ارز
    
    Args:
        symbol (str): نماد ارز دیجیتال
        timeframe (str): بازه زمانی
        
    Returns:
        dict: خلاصه سیگنال‌های معاملاتی
    """
    try:
        # دریافت داده‌های قیمت
        df = get_sample_data(symbol)
        
        # محاسبه شاخص‌ها
        df = calculate_indicators(df)
        
        # تولید سیگنال‌ها
        df = generate_signals(df)
        
        # آخرین داده‌ها برای خلاصه
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # تفسیر سیگنال‌های کلی
        signal_value = latest['combined_signal']
        if signal_value > 0.2:
            signal_text = "خرید قوی"
            signal_color = "green"
            signal_recommendation = "افزایش موقعیت توصیه می‌شود"
        elif signal_value > 0:
            signal_text = "خرید"
            signal_color = "lightgreen"
            signal_recommendation = "خرید با احتیاط"
        elif signal_value < -0.2:
            signal_text = "فروش قوی"
            signal_color = "red"
            signal_recommendation = "کاهش موقعیت توصیه می‌شود"
        elif signal_value < 0:
            signal_text = "فروش"
            signal_color = "lightcoral"
            signal_recommendation = "فروش با احتیاط"
        else:
            signal_text = "خنثی"
            signal_color = "gray"
            signal_recommendation = "حفظ موقعیت فعلی"
        
        # تفسیر روند
        if latest['sma_20'] > latest['sma_50'] and prev['sma_20'] <= prev['sma_50']:
            trend_text = "شروع روند صعودی"
        elif latest['sma_20'] < latest['sma_50'] and prev['sma_20'] >= prev['sma_50']:
            trend_text = "شروع روند نزولی"
        elif latest['sma_20'] > latest['sma_50']:
            trend_text = "روند صعودی"
        elif latest['sma_20'] < latest['sma_50']:
            trend_text = "روند نزولی"
        else:
            trend_text = "روند خنثی"
        
        # خلاصه شاخص‌ها
        indicators_summary = {
            "RSI": {
                "value": round(latest['rsi'], 2),
                "interpretation": "اشباع خرید" if latest['rsi'] > 70 else "اشباع فروش" if latest['rsi'] < 30 else "نرمال"
            },
            "MACD": {
                "value": round(latest['macd'], 4),
                "signal": round(latest['macd_signal'], 4),
                "histogram": round(latest['macd_diff'], 4),
                "interpretation": "صعودی" if latest['macd'] > latest['macd_signal'] else "نزولی"
            },
            "Bollinger Bands": {
                "upper": round(latest['bb_high'], 2),
                "middle": round(latest['bb_mid'], 2),
                "lower": round(latest['bb_low'], 2),
                "width": round((latest['bb_high'] - latest['bb_low']) / latest['bb_mid'], 2),
                "interpretation": "نوسان بالا" if (latest['bb_high'] - latest['bb_low']) / latest['bb_mid'] > 0.05 else "نوسان پایین"
            }
        }
        
        # نقاط حمایت و مقاومت ساده (میانگین کمترین و بیشترین قیمت اخیر)
        resistance_level = round(df['high'][-5:].max(), 2)
        support_level = round(df['low'][-5:].min(), 2)
        
        # خلاصه کلی سیگنال‌ها
        result = {
            "symbol": symbol,
            "last_price": round(latest['close'], 2),
            "signal": signal_text,
            "signal_color": signal_color,
            "signal_strength": abs(round(signal_value * 100, 2)),
            "recommendation": signal_recommendation,
            "trend": trend_text,
            "support_level": support_level,
            "resistance_level": resistance_level,
            "indicators": indicators_summary,
            "timeframe": timeframe,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return result
    except Exception as e:
        logger.error(f"خطا در دریافت سیگنال‌های معاملاتی: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "symbol": symbol,
            "error": f"خطا در تحلیل: {str(e)}",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def get_technical_analysis(symbol, timeframe='1d'):
    """
    دریافت تحلیل تکنیکال کامل برای یک ارز
    
    Args:
        symbol (str): نماد ارز دیجیتال
        timeframe (str): بازه زمانی
        
    Returns:
        dict: تحلیل تکنیکال کامل
    """
    signals = get_latest_signals(symbol, timeframe)
    
    # اضافه کردن جزئیات بیشتر به تحلیل
    if 'error' not in signals:
        df = get_sample_data(symbol)
        df = calculate_indicators(df)
        
        # محاسبه تغییرات قیمت
        signals['daily_change'] = round((df['close'].iloc[-1] / df['close'].iloc[-2] - 1) * 100, 2)
        signals['weekly_change'] = round((df['close'].iloc[-1] / df['close'].iloc[-7] - 1) * 100, 2) if len(df) >= 7 else None
        signals['monthly_change'] = round((df['close'].iloc[-1] / df['close'].iloc[-30] - 1) * 100, 2) if len(df) >= 30 else None
        
        # پیش‌بینی نوسانات
        signals['volatility'] = {
            "daily": round(df['close'].pct_change().rolling(7).std().iloc[-1] * 100, 2),
            "interpretation": "بالا" if df['close'].pct_change().rolling(7).std().iloc[-1] > 0.03 else "متوسط" if df['close'].pct_change().rolling(7).std().iloc[-1] > 0.01 else "پایین"
        }
        
    return signals

def get_multi_timeframe_analysis(symbol):
    """
    دریافت تحلیل در چندین بازه زمانی
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        dict: تحلیل در بازه‌های زمانی مختلف
    """
    return {
        "daily": get_latest_signals(symbol, "1d"),
        "weekly": get_latest_signals(symbol, "1w"),
        "monthly": get_latest_signals(symbol, "1M"),
    }

def get_technical_indicators(symbol, timeframe='1d'):
    """
    تابع میانی برای فراخوانی از سایر ماژول‌ها
    
    Args:
        symbol (str): نماد ارز دیجیتال
        timeframe (str): بازه زمانی
        
    Returns:
        dict: شاخص‌های تکنیکال
    """
    return get_technical_analysis(symbol, timeframe)