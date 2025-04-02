"""
Functions for generating trading signals based on technical analysis and news
"""

import logging
from datetime import datetime

from crypto_bot.market_data import get_current_prices
from crypto_bot.technical_analysis import get_technical_indicators
from crypto_bot.news_analyzer import get_latest_news, analyze_sentiment
from crypto_bot.config import SIGNAL_THRESHOLDS

logger = logging.getLogger(__name__)

def generate_signals(symbols):
    """
    Generate trading signals for a list of cryptocurrency symbols
    
    Args:
        symbols (list): List of symbols like ['BTC/USDT', 'ETH/USDT']
        
    Returns:
        dict: Dictionary of trading signals for each symbol
    """
    signals = {}
    
    try:
        # Get current prices and news
        prices = get_current_prices(symbols)
        news = get_latest_news(limit=10)
        
        # Process each symbol
        for symbol in symbols:
            # Skip if no price data available
            if symbol not in prices:
                logger.warning(f"No price data available for {symbol}")
                continue
                
            # Get technical indicators
            ta_data = get_technical_indicators(symbol)
            
            # Skip if technical analysis failed
            if not ta_data or 'error' in ta_data:
                logger.warning(f"Technical analysis failed for {symbol}")
                continue
                
            # Generate signal based on technical analysis
            signals[symbol] = generate_signal_for_symbol(symbol, prices[symbol], ta_data, news)
            
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        
    return signals

def generate_signal_for_symbol(symbol, price_data, ta_data, news):
    """
    Generate a trading signal for a specific cryptocurrency
    
    Args:
        symbol (str): Symbol like 'BTC/USDT'
        price_data (dict): Current price data
        ta_data (dict): Technical analysis data
        news (list): Recent news articles
        
    Returns:
        dict: Trading signal with recommendation
    """
    # Extract coin name from symbol (e.g., 'BTC' from 'BTC/USDT')
    coin = symbol.split('/')[0].lower()
    
    # Initialize signal strength factors
    signal_factors = {
        'trend': 0,
        'rsi': 0,
        'macd': 0,
        'bollinger': 0,
        'momentum': 0,
        'news': 0
    }
    
    # 1. Evaluate trend
    if ta_data.get('trend') == "Strong Bullish":
        signal_factors['trend'] = 1.0
    elif ta_data.get('trend') == "Bullish":
        signal_factors['trend'] = 0.5
    elif ta_data.get('trend') == "Bearish":
        signal_factors['trend'] = -0.5
    elif ta_data.get('trend') == "Strong Bearish":
        signal_factors['trend'] = -1.0
        
    # 2. Evaluate RSI
    rsi_value = ta_data.get('rsi', {}).get('value', 50)
    if rsi_value < 30:  # Oversold - bullish signal
        signal_factors['rsi'] = (30 - rsi_value) / 30  # Stronger as it approaches 0
    elif rsi_value > 70:  # Overbought - bearish signal
        signal_factors['rsi'] = -1 * (rsi_value - 70) / 30  # Stronger as it approaches 100
        
    # 3. Evaluate MACD
    macd = ta_data.get('macd', {})
    if macd.get('condition') == "Bullish":
        signal_factors['macd'] = 0.7
    elif macd.get('condition') == "Bearish":
        signal_factors['macd'] = -0.7
        
    # 4. Evaluate Bollinger Bands
    bb = ta_data.get('bollinger_bands', {})
    if bb.get('condition') == "Oversold":
        signal_factors['bollinger'] = 0.8
    elif bb.get('condition') == "Overbought":
        signal_factors['bollinger'] = -0.8
        
    # 5. Evaluate price momentum
    momentum = ta_data.get('momentum', 0)
    if momentum > 5:  # Strong positive momentum
        signal_factors['momentum'] = 0.6
    elif momentum < -5:  # Strong negative momentum
        signal_factors['momentum'] = -0.6
    elif momentum > 2:  # Moderate positive momentum
        signal_factors['momentum'] = 0.3
    elif momentum < -2:  # Moderate negative momentum
        signal_factors['momentum'] = -0.3
        
    # 6. Evaluate news sentiment
    # Filter news related to this cryptocurrency
    coin_news = [n for n in news if coin in n['title'].lower() or coin in n.get('source', '').lower()]
    if coin_news:
        # Calculate average sentiment score for news related to this coin
        avg_sentiment = sum(n['sentiment']['score'] for n in coin_news) / len(coin_news)
        signal_factors['news'] = avg_sentiment
        
    # Calculate overall signal strength (-1.0 to 1.0)
    # Different weights for each factor (trend and momentum are most important)
    weights = {
        'trend': 0.25,
        'rsi': 0.15,
        'macd': 0.20,
        'bollinger': 0.15,
        'momentum': 0.15,
        'news': 0.10
    }
    
    strength = sum(factor * weights[key] for key, factor in signal_factors.items())
    
    # Determine signal based on strength
    signal = "Neutral"
    if strength > SIGNAL_THRESHOLDS['strong_buy']:
        signal = "Strong Buy"
    elif strength > SIGNAL_THRESHOLDS['buy']:
        signal = "Buy"
    elif strength < SIGNAL_THRESHOLDS['strong_sell']:
        signal = "Strong Sell"
    elif strength < SIGNAL_THRESHOLDS['sell']:
        signal = "Sell"
        
    return {
        'symbol': symbol,
        'price': price_data['price'],
        'signal': signal,
        'strength': strength,
        'factors': signal_factors,
        'timestamp': datetime.now().isoformat()
    }
