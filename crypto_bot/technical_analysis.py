"""
Technical analysis functions for cryptocurrency market data
"""

import logging
import pandas as pd
import numpy as np
import ta

from crypto_bot.market_data import get_historical_data
from crypto_bot.config import TA_SETTINGS

logger = logging.getLogger(__name__)

def add_moving_averages(df):
    """
    Add Simple Moving Averages (SMA) indicators to DataFrame
    """
    try:
        df['sma_short'] = ta.trend.sma_indicator(df['close'], window=TA_SETTINGS['short_sma'])
        df['sma_medium'] = ta.trend.sma_indicator(df['close'], window=TA_SETTINGS['medium_sma'])
        df['sma_long'] = ta.trend.sma_indicator(df['close'], window=TA_SETTINGS['long_sma'])
        return df
    except Exception as e:
        logger.error(f"Error calculating moving averages: {str(e)}")
        return df

def add_rsi(df):
    """
    Add Relative Strength Index (RSI) indicator to DataFrame
    """
    try:
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=TA_SETTINGS['rsi_period']
        ).rsi()
        return df
    except Exception as e:
        logger.error(f"Error calculating RSI: {str(e)}")
        return df

def add_macd(df):
    """
    Add Moving Average Convergence Divergence (MACD) indicator to DataFrame
    """
    try:
        macd = ta.trend.MACD(
            close=df['close'],
            window_fast=TA_SETTINGS['macd_fast'],
            window_slow=TA_SETTINGS['macd_slow'],
            window_sign=TA_SETTINGS['macd_signal']
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        return df
    except Exception as e:
        logger.error(f"Error calculating MACD: {str(e)}")
        return df

def add_bollinger_bands(df):
    """
    Add Bollinger Bands indicator to DataFrame
    """
    try:
        bollinger = ta.volatility.BollingerBands(
            close=df['close'],
            window=20,
            window_dev=2
        )
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_lower'] = bollinger.bollinger_lband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        return df
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {str(e)}")
        return df

def get_technical_indicators(symbol, timeframe='1d'):
    """
    Calculate technical indicators for a specific cryptocurrency
    
    Args:
        symbol (str): Symbol like 'BTC/USDT'
        timeframe (str): Timeframe like '1d', '4h', '1h', etc.
        
    Returns:
        dict: Dictionary of technical indicators and their values
    """
    try:
        # Get historical data
        df = get_historical_data(symbol, timeframe, limit=100)
        
        if df.empty:
            logger.warning(f"No historical data available for {symbol} on {timeframe} timeframe")
            return {}
        
        # Add technical indicators
        df = add_moving_averages(df)
        df = add_rsi(df)
        df = add_macd(df)
        df = add_bollinger_bands(df)
        
        # Get the most recent values
        latest = df.iloc[-1]
        
        # Analyze trend based on moving averages
        trend = "Neutral"
        if latest['sma_short'] > latest['sma_medium'] > latest['sma_long']:
            trend = "Strong Bullish"
        elif latest['sma_short'] > latest['sma_medium']:
            trend = "Bullish"
        elif latest['sma_short'] < latest['sma_medium'] < latest['sma_long']:
            trend = "Strong Bearish"
        elif latest['sma_short'] < latest['sma_medium']:
            trend = "Bearish"
            
        # RSI condition
        rsi_condition = "Neutral"
        if latest['rsi'] > TA_SETTINGS['rsi_overbought']:
            rsi_condition = "Overbought"
        elif latest['rsi'] < TA_SETTINGS['rsi_oversold']:
            rsi_condition = "Oversold"
            
        # MACD condition
        macd_condition = "Neutral"
        if latest['macd'] > latest['macd_signal'] and latest['macd_diff'] > 0:
            macd_condition = "Bullish"
        elif latest['macd'] < latest['macd_signal'] and latest['macd_diff'] < 0:
            macd_condition = "Bearish"
            
        # Determine if price is near Bollinger Bands
        bb_condition = "Neutral"
        if latest['close'] > latest['bb_upper']:
            bb_condition = "Overbought"
        elif latest['close'] < latest['bb_lower']:
            bb_condition = "Oversold"
            
        # Calculate simple price momentum (current close vs average of last 5 closes)
        momentum = (latest['close'] / df['close'].iloc[-6:-1].mean() - 1) * 100
        
        # Prepare the result
        result = {
            'price': latest['close'],
            'trend': trend,
            'rsi': {
                'value': latest['rsi'],
                'condition': rsi_condition
            },
            'macd': {
                'value': latest['macd'],
                'signal': latest['macd_signal'],
                'diff': latest['macd_diff'],
                'condition': macd_condition
            },
            'bollinger_bands': {
                'upper': latest['bb_upper'],
                'middle': latest['bb_middle'],
                'lower': latest['bb_lower'],
                'condition': bb_condition
            },
            'momentum': momentum,
            'moving_averages': {
                'short': latest['sma_short'],
                'medium': latest['sma_medium'],
                'long': latest['sma_long']
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
        return {'error': str(e)}
