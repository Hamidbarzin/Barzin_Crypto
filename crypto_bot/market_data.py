"""
Functions for fetching market data from cryptocurrency exchanges
"""

import os
import logging
import ccxt
from datetime import datetime, timedelta
import pandas as pd

from crypto_bot.config import BINANCE_API_KEY, BINANCE_API_SECRET

logger = logging.getLogger(__name__)

def get_exchange():
    """
    Initialize and return the exchange API client
    """
    try:
        # Initialize with Binance by default, but could be expanded to support multiple exchanges
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
        })
        return exchange
    except Exception as e:
        logger.error(f"Error initializing exchange: {str(e)}")
        # Fallback to using exchange without authentication
        return ccxt.binance({'enableRateLimit': True})

def get_current_prices(symbols):
    """
    Get current prices for a list of cryptocurrency symbols
    
    Args:
        symbols (list): List of symbols like ['BTC/USDT', 'ETH/USDT']
        
    Returns:
        dict: Dictionary of current prices for each symbol
    """
    exchange = get_exchange()
    result = {}
    
    try:
        tickers = exchange.fetch_tickers(symbols)
        for symbol in symbols:
            if symbol in tickers:
                ticker = tickers[symbol]
                result[symbol] = {
                    'price': ticker['last'],
                    'change_24h': ticker['percentage'] if 'percentage' in ticker else None,
                    'high_24h': ticker['high'] if 'high' in ticker else None,
                    'low_24h': ticker['low'] if 'low' in ticker else None,
                    'volume_24h': ticker['quoteVolume'] if 'quoteVolume' in ticker else None,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Symbol {symbol} not found in tickers")
    except Exception as e:
        logger.error(f"Error fetching ticker data: {str(e)}")
        # Handle API error by using CoinGecko as fallback
        try:
            result = get_prices_from_coingecko(symbols)
        except Exception as e2:
            logger.error(f"Fallback to CoinGecko also failed: {str(e2)}")
            
    return result

def get_prices_from_coingecko(symbols):
    """
    Fallback function to get prices from CoinGecko if the primary exchange fails
    
    Args:
        symbols (list): List of symbols like ['BTC/USDT', 'ETH/USDT']
        
    Returns:
        dict: Dictionary of current prices for each symbol
    """
    import requests
    result = {}
    
    # Convert exchange symbols to CoinGecko IDs
    coin_map = {
        'BTC/USDT': 'bitcoin',
        'ETH/USDT': 'ethereum',
        'XRP/USDT': 'ripple',
        'BNB/USDT': 'binancecoin',
        'ADA/USDT': 'cardano',
        'SOL/USDT': 'solana',
        'DOT/USDT': 'polkadot',
        'DOGE/USDT': 'dogecoin',
        'AVAX/USDT': 'avalanche-2',
        'LUNA/USDT': 'terra-luna-2'
    }
    
    coin_ids = [coin_map[symbol] for symbol in symbols if symbol in coin_map]
    coin_ids_str = ','.join(coin_ids)
    
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_ids_str}&order=market_cap_desc&sparkline=false&price_change_percentage=24h"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        for coin in data:
            # Find the corresponding symbol
            for symbol, coin_id in coin_map.items():
                if coin_id == coin['id']:
                    result[symbol] = {
                        'price': coin['current_price'],
                        'change_24h': coin['price_change_percentage_24h'],
                        'high_24h': coin['high_24h'],
                        'low_24h': coin['low_24h'],
                        'volume_24h': coin['total_volume'],
                        'timestamp': datetime.now().isoformat()
                    }
                    break
    
    return result

def get_historical_data(symbol, timeframe='1d', limit=100):
    """
    Get historical OHLCV data for a specific cryptocurrency
    
    Args:
        symbol (str): Symbol like 'BTC/USDT'
        timeframe (str): Timeframe like '1d', '4h', '1h', etc.
        limit (int): Number of candles to fetch
        
    Returns:
        pandas.DataFrame: DataFrame with historical data
    """
    exchange = get_exchange()
    
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error
