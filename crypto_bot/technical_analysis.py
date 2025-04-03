"""
Functions for performing technical analysis on cryptocurrency price data
"""

import pandas as pd
import numpy as np
import logging
import random
import datetime

from crypto_bot.market_data import get_historical_data

# Set up logging
logger = logging.getLogger(__name__)


def get_technical_indicators(symbol, timeframe='1d'):
    """
    Calculate technical indicators for a cryptocurrency
    
    Args:
        symbol (str): Symbol like 'BTC/USDT'
        timeframe (str): Timeframe like '1d', '4h', '1h', etc.
        
    Returns:
        dict: Dictionary of technical indicators and their values
    """
    try:
        # Get historical data
        df = get_historical_data(symbol, timeframe, limit=100)
        
        if df is None or len(df) < 20:
            logger.warning(f"Insufficient data for {symbol} on {timeframe} timeframe")
            
            # در صورت عدم وجود دیتا از داده‌های نمونه استفاده می‌کنیم
            logger.info(f"Using sample data for {symbol} on {timeframe} timeframe")
            return _get_sample_indicators(symbol, timeframe)
            
        # Calculate some basic indicators
        results = {}
        results['symbol'] = symbol
        results['timeframe'] = timeframe
        
        # Calculate Moving Averages
        results['ma_20'] = calculate_ma(df, 20)
        results['ma_50'] = calculate_ma(df, 50)
        results['ma_100'] = calculate_ma(df, 100)
        
        # Calculate Exponential Moving Averages
        results['ema_12'] = calculate_ema(df, 12)
        results['ema_26'] = calculate_ema(df, 26)
        
        # Calculate RSI
        results['rsi_14'] = calculate_rsi(df, 14)
        
        # Calculate MACD
        macd_results = calculate_macd(df)
        results['macd'] = macd_results['macd']
        results['macd_signal'] = macd_results['signal']
        results['macd_histogram'] = macd_results['histogram']
        
        # Calculate Bollinger Bands
        bb_results = calculate_bollinger_bands(df, 20)
        results['bb_upper'] = bb_results['upper']
        results['bb_middle'] = bb_results['middle']
        results['bb_lower'] = bb_results['lower']
        
        # Calculate Stochastic Oscillator
        stoch_results = calculate_stochastic(df, 14, 3)
        results['stoch_k'] = stoch_results['k']
        results['stoch_d'] = stoch_results['d']
        
        # Current price
        results['current_price'] = float(df['close'].iloc[-1])
        
        # Get trading signals
        signals = generate_signals(df, results)
        results.update(signals)
        
        return results
    
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        logger.info(f"Falling back to sample data for {symbol} on {timeframe} timeframe")
        return _get_sample_indicators(symbol, timeframe)


def calculate_ma(df, period):
    """Calculate Simple Moving Average"""
    try:
        return float(df['close'].rolling(window=period).mean().iloc[-1])
    except Exception as e:
        logger.error(f"Error calculating MA-{period}: {str(e)}")
        return None


def calculate_ema(df, period):
    """Calculate Exponential Moving Average"""
    try:
        return float(df['close'].ewm(span=period, adjust=False).mean().iloc[-1])
    except Exception as e:
        logger.error(f"Error calculating EMA-{period}: {str(e)}")
        return None


def calculate_rsi(df, period=14):
    """Calculate Relative Strength Index"""
    try:
        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        
        ema_up = up.ewm(com=period-1, adjust=False).mean()
        ema_down = down.ewm(com=period-1, adjust=False).mean()
        
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1])
    except Exception as e:
        logger.error(f"Error calculating RSI: {str(e)}")
        return None


def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    try:
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd - macd_signal
        
        return {
            'macd': float(macd.iloc[-1]),
            'signal': float(macd_signal.iloc[-1]),
            'histogram': float(macd_histogram.iloc[-1])
        }
    except Exception as e:
        logger.error(f"Error calculating MACD: {str(e)}")
        return {'macd': None, 'signal': None, 'histogram': None}


def calculate_bollinger_bands(df, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    try:
        ma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        return {
            'upper': float(upper_band.iloc[-1]),
            'middle': float(ma.iloc[-1]),
            'lower': float(lower_band.iloc[-1])
        }
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {str(e)}")
        return {'upper': None, 'middle': None, 'lower': None}


def calculate_stochastic(df, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator"""
    try:
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        
        return {
            'k': float(k.iloc[-1]),
            'd': float(d.iloc[-1])
        }
    except Exception as e:
        logger.error(f"Error calculating Stochastic: {str(e)}")
        return {'k': None, 'd': None}


def generate_signals(df, indicators):
    """Generate trading signals based on technical indicators"""
    try:
        current_price = indicators['current_price']
        
        # Initialize signals
        signals = {
            'signal': 'خنثی',
            'signal_strength': 0.5,
            'overbought': False,
            'oversold': False
        }
        
        # Check MA crossover
        ma_crossover = False
        if indicators['ma_20'] > indicators['ma_50']:
            ma_trend = 'صعودی'
            ma_crossover = indicators['ma_20'] / indicators['ma_50'] > 1.01  # 1% above
        else:
            ma_trend = 'نزولی'
            ma_crossover = indicators['ma_20'] / indicators['ma_50'] < 0.99  # 1% below
            
        # Check MACD signal
        macd_signal = 'خنثی'
        if indicators['macd'] > indicators['macd_signal']:
            macd_signal = 'خرید'
        elif indicators['macd'] < indicators['macd_signal']:
            macd_signal = 'فروش'
            
        # Check RSI for overbought/oversold
        rsi = indicators['rsi_14']
        if rsi > 70:
            signals['overbought'] = True
        elif rsi < 30:
            signals['oversold'] = True
            
        # Check Bollinger Bands
        bb_signal = 'خنثی'
        if current_price > indicators['bb_upper']:
            bb_signal = 'فروش'
        elif current_price < indicators['bb_lower']:
            bb_signal = 'خرید'
            
        # Combine signals
        buy_signals = 0
        sell_signals = 0
        
        # Add buy signals
        if ma_trend == 'صعودی' and ma_crossover:
            buy_signals += 1
        if macd_signal == 'خرید':
            buy_signals += 1
        if signals['oversold']:
            buy_signals += 1
        if bb_signal == 'خرید':
            buy_signals += 1
            
        # Add sell signals
        if ma_trend == 'نزولی' and ma_crossover:
            sell_signals += 1
        if macd_signal == 'فروش':
            sell_signals += 1
        if signals['overbought']:
            sell_signals += 1
        if bb_signal == 'فروش':
            sell_signals += 1
            
        # Determine overall signal
        total_signals = buy_signals + sell_signals
        if total_signals > 0:
            if buy_signals > sell_signals:
                signals['signal'] = 'خرید'
                signals['signal_strength'] = min(0.9, 0.5 + 0.1 * (buy_signals - sell_signals))
            elif sell_signals > buy_signals:
                signals['signal'] = 'فروش'
                signals['signal_strength'] = min(0.9, 0.5 + 0.1 * (sell_signals - buy_signals))
            else:
                signals['signal'] = 'خنثی'
                signals['signal_strength'] = 0.5
        
        return signals
        
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        return {
            'signal': 'خنثی',
            'signal_strength': 0.5,
            'overbought': False,
            'oversold': False
        }


def _get_sample_indicators(symbol, timeframe):
    """
    تولید شاخص‌های تکنیکال نمونه برای نمایش
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        
    Returns:
        dict: شاخص‌های تکنیکال نمونه
    """
    # تعیین قیمت فعلی بر اساس نماد ارز
    coin = symbol.split('/')[0] if '/' in symbol else symbol.split('-')[0]
    
    if coin.lower() == 'btc':
        current_price = 82500
    elif coin.lower() == 'eth': 
        current_price = 3200
    elif coin.lower() == 'bnb':
        current_price = 560
    elif coin.lower() == 'xrp':
        current_price = 0.52
    elif coin.lower() == 'sol':
        current_price = 145
    elif coin.lower() == 'doge':
        current_price = 0.15
    elif coin.lower() == 'ada':
        current_price = 0.45
    elif coin.lower() == 'dot':
        current_price = 7.8
    elif coin.lower() == 'avax':
        current_price = 35.6
    elif coin.lower() == 'luna':
        current_price = 0.85
    else:
        current_price = 100.0
        
    # تولید شاخص‌های تکنیکال نمونه
    ma_20 = current_price * (1 + random.uniform(-0.03, 0.03))
    ma_50 = current_price * (1 + random.uniform(-0.06, 0.06))
    ma_100 = current_price * (1 + random.uniform(-0.1, 0.1))
    
    ema_12 = current_price * (1 + random.uniform(-0.02, 0.02))
    ema_26 = current_price * (1 + random.uniform(-0.04, 0.04))
    
    rsi_14 = random.uniform(30, 70)
    
    macd = random.uniform(-10, 10) * (current_price * 0.01)
    macd_signal = macd * (1 + random.uniform(-0.2, 0.2))
    macd_histogram = macd - macd_signal
    
    bb_middle = ma_20
    bb_upper = bb_middle * (1 + random.uniform(0.01, 0.03))
    bb_lower = bb_middle * (1 - random.uniform(0.01, 0.03))
    
    stoch_k = random.uniform(20, 80)
    stoch_d = stoch_k * (1 + random.uniform(-0.15, 0.15))
    
    # تعیین سیگنال‌های معاملاتی
    signals = {}
    
    # شرایط خرید
    if (ma_20 > ma_50 and rsi_14 < 40 and current_price < bb_lower) or (macd > macd_signal and rsi_14 < 50):
        signals['signal'] = 'خرید'
        signals['signal_strength'] = random.uniform(0.6, 0.9)
    # شرایط فروش
    elif (ma_20 < ma_50 and rsi_14 > 60 and current_price > bb_upper) or (macd < macd_signal and rsi_14 > 50):
        signals['signal'] = 'فروش'
        signals['signal_strength'] = random.uniform(0.6, 0.9)
    # شرایط خنثی
    else:
        signals['signal'] = 'خنثی'
        signals['signal_strength'] = random.uniform(0.4, 0.6)
        
    results = {
        'symbol': symbol,
        'timeframe': timeframe,
        'current_price': current_price,
        'ma_20': round(ma_20, 2),
        'ma_50': round(ma_50, 2),
        'ma_100': round(ma_100, 2),
        'ema_12': round(ema_12, 2),
        'ema_26': round(ema_26, 2),
        'rsi_14': round(rsi_14, 2),
        'macd': round(macd, 4),
        'macd_signal': round(macd_signal, 4),
        'macd_histogram': round(macd_histogram, 4),
        'bb_upper': round(bb_upper, 2),
        'bb_middle': round(bb_middle, 2),
        'bb_lower': round(bb_lower, 2),
        'stoch_k': round(stoch_k, 2),
        'stoch_d': round(stoch_d, 2),
        'signal': signals['signal'],
        'signal_strength': round(signals['signal_strength'], 2),
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'is_sample_data': True
    }
    
    # اضافه کردن وضعیت اشباع خرید/فروش بر اساس RSI
    results['overbought'] = rsi_14 > 70
    results['oversold'] = rsi_14 < 30
    
    return results