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
        'volatility': 0,  # New factor for volatility
        'swing_trade': 0,  # New factor specifically for swing trading
        'news': 0
    }
    
    # Current price
    current_price = price_data.get('price', 0)
    
    # 1. Evaluate trend
    if ta_data.get('trend') == "Strong Bullish":
        signal_factors['trend'] = 1.0
    elif ta_data.get('trend') == "Bullish":
        signal_factors['trend'] = 0.5
    elif ta_data.get('trend') == "Bearish":
        signal_factors['trend'] = -0.5
    elif ta_data.get('trend') == "Strong Bearish":
        signal_factors['trend'] = -1.0
        
    # 2. Evaluate RSI - enhanced for swing trading
    rsi_value = ta_data.get('rsi', {}).get('value', 50)
    if rsi_value < 30:  # Oversold - bullish signal
        signal_factors['rsi'] = (30 - rsi_value) / 30  # Stronger as it approaches 0
        
        # Even stronger if deeply oversold (good for swing trading)
        if rsi_value < 20:
            signal_factors['rsi'] = min(1.0, signal_factors['rsi'] * 1.5)
            
    elif rsi_value > 70:  # Overbought - bearish signal
        signal_factors['rsi'] = -1 * (rsi_value - 70) / 30  # Stronger as it approaches 100
        
        # Even stronger if deeply overbought (good for swing trading)
        if rsi_value > 80:
            signal_factors['rsi'] = max(-1.0, signal_factors['rsi'] * 1.5)
    
    # RSI for swing trading - look for RSI reversals
    # When RSI starts to turn upward from oversold territory
    if 30 < rsi_value < 40 and signal_factors['trend'] >= 0:
        signal_factors['swing_trade'] += 0.5  # Good time to enter a long position
    # When RSI starts to turn downward from overbought territory
    elif 60 < rsi_value < 70 and signal_factors['trend'] <= 0:
        signal_factors['swing_trade'] -= 0.5  # Good time to enter a short position
        
    # 3. Evaluate MACD - enhanced for swing trading signals
    macd = ta_data.get('macd', {})
    macd_value = macd.get('value', 0)
    macd_signal = macd.get('signal', 0)
    macd_diff = macd.get('diff', 0)
    
    if macd.get('condition') == "Bullish":
        signal_factors['macd'] = 0.7
        
        # Check for MACD crossover (stronger signal for swing trading)
        if 0 < macd_diff < 0.05:  # Recent bullish crossover
            signal_factors['swing_trade'] += 0.7
            
    elif macd.get('condition') == "Bearish":
        signal_factors['macd'] = -0.7
        
        # Check for MACD crossover (stronger signal for swing trading)
        if -0.05 < macd_diff < 0:  # Recent bearish crossover
            signal_factors['swing_trade'] -= 0.7
        
    # 4. Evaluate Bollinger Bands - enhanced for volatility and swing trading
    bb = ta_data.get('bollinger_bands', {})
    bb_upper = bb.get('upper', 0)
    bb_lower = bb.get('lower', 0)
    bb_middle = bb.get('middle', 0)
    
    # Calculate bandwidth as a volatility indicator
    if bb_middle > 0:
        bandwidth = (bb_upper - bb_lower) / bb_middle
        
        # High bandwidth indicates high volatility (good for swing trading)
        if bandwidth > 0.05:  # 5% bandwidth
            signal_factors['volatility'] = 0.8
        elif bandwidth > 0.03:  # 3% bandwidth
            signal_factors['volatility'] = 0.5
    
    if bb.get('condition') == "Oversold":
        signal_factors['bollinger'] = 0.8
        
        # Price touching lower band is a strong bounce signal for swing trading
        if current_price <= bb_lower * 1.02:  # Within 2% of lower band
            signal_factors['swing_trade'] += 0.8
            
    elif bb.get('condition') == "Overbought":
        signal_factors['bollinger'] = -0.8
        
        # Price touching upper band is a strong reversal signal for swing trading
        if current_price >= bb_upper * 0.98:  # Within 2% of upper band
            signal_factors['swing_trade'] -= 0.8
        
    # 5. Evaluate price momentum - enhanced for swing trading
    momentum = ta_data.get('momentum', 0)
    if momentum > 5:  # Strong positive momentum
        signal_factors['momentum'] = 0.6
    elif momentum < -5:  # Strong negative momentum
        signal_factors['momentum'] = -0.6
    elif momentum > 2:  # Moderate positive momentum
        signal_factors['momentum'] = 0.3
    elif momentum < -2:  # Moderate negative momentum
        signal_factors['momentum'] = -0.3
    
    # For swing trading, we look for momentum divergence
    # (when price makes new high but momentum doesn't, or vice versa)
    if momentum < 0 and signal_factors['trend'] > 0:
        # Bearish divergence (price up, momentum down)
        signal_factors['swing_trade'] -= 0.6
    elif momentum > 0 and signal_factors['trend'] < 0:
        # Bullish divergence (price down, momentum up)
        signal_factors['swing_trade'] += 0.6
        
    # 6. Evaluate news sentiment
    # Filter news related to this cryptocurrency
    coin_news = [n for n in news if coin in n['title'].lower() or coin in n.get('source', '').lower()]
    if coin_news:
        # Calculate average sentiment score for news related to this coin
        avg_sentiment = sum(n['sentiment']['score'] for n in coin_news) / len(coin_news)
        signal_factors['news'] = avg_sentiment
        
        # For swing trading, recent strong sentiment change is more important
        if len(coin_news) >= 2:
            recent_sentiment = sum(n['sentiment']['score'] for n in coin_news[:2]) / 2
            if recent_sentiment > 0.5:
                signal_factors['swing_trade'] += 0.4
            elif recent_sentiment < -0.5:
                signal_factors['swing_trade'] -= 0.4
    
    # Calculate overall signal strength (-1.0 to 1.0)
    # Different weights for each factor (swing trade signals and volatility are important for swing trading)
    weights = {
        'trend': 0.15,
        'rsi': 0.15,
        'macd': 0.15,
        'bollinger': 0.15,
        'momentum': 0.10,
        'volatility': 0.10,
        'swing_trade': 0.15,
        'news': 0.05
    }
    
    strength = sum(factor * weights[key] for key, factor in signal_factors.items())
    
    # Determine signal based on strength
    signal = "Neutral"
    farsi_signal = "خنثی"
    
    if strength > SIGNAL_THRESHOLDS['strong_buy']:
        signal = "Strong Buy"
        farsi_signal = "خرید قوی"
    elif strength > SIGNAL_THRESHOLDS['buy']:
        signal = "Buy"
        farsi_signal = "خرید"
    elif strength < SIGNAL_THRESHOLDS['strong_sell']:
        signal = "Strong Sell"
        farsi_signal = "فروش قوی"
    elif strength < SIGNAL_THRESHOLDS['sell']:
        signal = "Sell"
        farsi_signal = "فروش"
    
    # Add swing trading recommendation
    swing_recommendation = ""
    farsi_swing_recommendation = ""
    
    if signal_factors['swing_trade'] > 0.5:
        swing_recommendation = "Good swing entry for long position"
        farsi_swing_recommendation = "نقطه ورود مناسب برای معامله نوسانی صعودی"
    elif signal_factors['swing_trade'] < -0.5:
        swing_recommendation = "Good swing entry for short position"
        farsi_swing_recommendation = "نقطه ورود مناسب برای معامله نوسانی نزولی"
    elif 0.2 < signal_factors['swing_trade'] < 0.5:
        swing_recommendation = "Consider swing trade (long)"
        farsi_swing_recommendation = "پیشنهاد معامله نوسانی (صعودی)"
    elif -0.5 < signal_factors['swing_trade'] < -0.2:
        swing_recommendation = "Consider swing trade (short)"
        farsi_swing_recommendation = "پیشنهاد معامله نوسانی (نزولی)"
    
    return {
        'symbol': symbol,
        'price': price_data['price'],
        'signal': signal,
        'farsi_signal': farsi_signal,
        'strength': strength,
        'factors': signal_factors,
        'swing_recommendation': swing_recommendation,
        'farsi_swing_recommendation': farsi_swing_recommendation,
        'volatility': signal_factors['volatility'],
        'timestamp': datetime.now().isoformat()
    }
