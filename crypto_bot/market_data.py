"""
Functions for fetching market data from cryptocurrency exchanges
"""

import os
import logging
import ccxt
from datetime import datetime, timedelta
import pandas as pd
import random
import time

from crypto_bot.config import (
    BINANCE_API_KEY, BINANCE_API_SECRET, 
    KUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE,
    COINEX_API_KEY, COINEX_API_SECRET
)

logger = logging.getLogger(__name__)

# List of exchanges to try in order of preference
EXCHANGE_LIST = ['kucoin', 'coinex', 'binance', 'kraken', 'okx']

def get_exchange(exchange_id=None):
    """
    Initialize and return the exchange API client
    
    Args:
        exchange_id (str, optional): Specific exchange to use. If None, tries multiple exchanges
        
    Returns:
        ccxt.Exchange: Initialized exchange client
    """
    if exchange_id is not None:
        # Try to initialize the specific exchange
        return _initialize_exchange(exchange_id)
    
    # Try exchanges in order of preference
    for exchange_id in EXCHANGE_LIST:
        try:
            exchange = _initialize_exchange(exchange_id)
            logger.info(f"Successfully initialized {exchange_id} exchange")
            return exchange
        except Exception as e:
            logger.warning(f"Failed to initialize {exchange_id}: {str(e)}, trying next exchange")
    
    # If all exchanges fail, fallback to a public-only client
    logger.error("All exchanges failed to initialize, using public-only client")
    return ccxt.kucoin({'enableRateLimit': True})

def _initialize_exchange(exchange_id):
    """
    Initialize a specific exchange
    
    Args:
        exchange_id (str): Exchange ID to initialize
        
    Returns:
        ccxt.Exchange: Initialized exchange client
    """
    config = {'enableRateLimit': True}
    
    if exchange_id == 'binance':
        if BINANCE_API_KEY and BINANCE_API_SECRET:
            config.update({
                'apiKey': BINANCE_API_KEY,
                'secret': BINANCE_API_SECRET,
            })
    elif exchange_id == 'kucoin':
        if KUCOIN_API_KEY and KUCOIN_API_SECRET and KUCOIN_API_PASSPHRASE:
            config.update({
                'apiKey': KUCOIN_API_KEY,
                'secret': KUCOIN_API_SECRET,
                'password': KUCOIN_API_PASSPHRASE,
            })
    elif exchange_id == 'coinex':
        if COINEX_API_KEY and COINEX_API_SECRET:
            config.update({
                'apiKey': COINEX_API_KEY,
                'secret': COINEX_API_SECRET,
            })
            
    # Get the exchange class
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class(config)
    
    # Test the connection
    exchange.load_markets()
    return exchange

def get_current_prices(symbols):
    """
    Get current prices for a list of cryptocurrency symbols
    
    Args:
        symbols (list): List of symbols like ['BTC/USDT', 'ETH/USDT']
        
    Returns:
        dict: Dictionary of current prices for each symbol
    """
    result = {}
    success = False
    
    # Try each exchange until we get data
    for exchange_id in EXCHANGE_LIST:
        try:
            logger.info(f"Trying to fetch prices from {exchange_id}")
            exchange = _initialize_exchange(exchange_id)
            
            # Check if exchange supports all symbols
            unsupported_symbols = []
            for symbol in symbols:
                if not exchange.has['fetchTicker']:
                    logger.warning(f"{exchange_id} does not support fetchTicker")
                    raise Exception(f"{exchange_id} does not support fetchTicker")
                
                try:
                    # Check if the symbol is available on this exchange
                    exchange.markets[symbol]
                except (KeyError, ValueError):
                    unsupported_symbols.append(symbol)
            
            if unsupported_symbols:
                logger.warning(f"{exchange_id} does not support symbols: {', '.join(unsupported_symbols)}")
                continue
            
            # Fetch tickers for all symbols
            for symbol in symbols:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    result[symbol] = {
                        'price': ticker['last'],
                        'change_24h': ticker['percentage'] if 'percentage' in ticker else None,
                        'high_24h': ticker['high'] if 'high' in ticker else None,
                        'low_24h': ticker['low'] if 'low' in ticker else None,
                        'volume_24h': ticker['quoteVolume'] if 'quoteVolume' in ticker else None,
                        'timestamp': datetime.now().isoformat(),
                        'source': exchange_id
                    }
                except Exception as e:
                    logger.warning(f"Failed to fetch ticker for {symbol} on {exchange_id}: {str(e)}")
            
            # If we got data for all symbols, we're done
            if len(result) == len(symbols):
                success = True
                break
                
        except Exception as e:
            logger.warning(f"Error fetching prices from {exchange_id}: {str(e)}")
    
    # If we couldn't get data from any exchange, try CoinGecko as final fallback
    if not success:
        logger.warning("All exchanges failed, trying CoinGecko")
        try:
            coingecko_result = get_prices_from_coingecko(symbols)
            
            # Merge results - only add symbols that we don't have yet
            for symbol in symbols:
                if symbol not in result and symbol in coingecko_result:
                    result[symbol] = coingecko_result[symbol]
                    result[symbol]['source'] = 'coingecko'
                    
        except Exception as e:
            logger.error(f"Fallback to CoinGecko also failed: {str(e)}")
    
    # Log missing symbols
    missing_symbols = [s for s in symbols if s not in result]
    if missing_symbols:
        logger.warning(f"Could not fetch data for symbols: {', '.join(missing_symbols)}")
    
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
        pandas.DataFrame: DataFrame with historical data and 'source' column indicating data source
    """
    # Try each exchange until we get data
    for exchange_id in EXCHANGE_LIST:
        try:
            logger.info(f"Trying to fetch historical data from {exchange_id} for {symbol}")
            exchange = _initialize_exchange(exchange_id)
            
            # Check if exchange supports OHLCV
            if not exchange.has['fetchOHLCV']:
                logger.warning(f"{exchange_id} does not support fetchOHLCV")
                continue
                
            # Check if symbol is supported
            try:
                exchange.markets[symbol]
            except (KeyError, ValueError):
                logger.warning(f"{exchange_id} does not support symbol: {symbol}")
                continue
                
            # Check if timeframe is supported
            if timeframe not in exchange.timeframes:
                logger.warning(f"{exchange_id} does not support timeframe: {timeframe}")
                continue
                
            # Fetch OHLCV data
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if ohlcv and len(ohlcv) > 0:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['source'] = exchange_id
                logger.info(f"Successfully fetched {len(df)} candles for {symbol} from {exchange_id}")
                return df
                
        except Exception as e:
            logger.warning(f"Error fetching historical data from {exchange_id} for {symbol}: {str(e)}")
    
    # If all exchanges fail, return empty DataFrame
    logger.error(f"All exchanges failed to provide historical data for {symbol}")
    return pd.DataFrame()  # Return empty DataFrame on error

def get_historical_data_from_alternative_source(symbol, timeframe='1d', limit=100):
    """
    Get historical data from alternative sources like Alpha Vantage or Yahoo Finance
    This is a placeholder for future implementation
    
    Args:
        symbol (str): Symbol like 'BTC/USDT'
        timeframe (str): Timeframe like '1d', '4h', '1h', etc.
        limit (int): Number of candles to fetch
        
    Returns:
        pandas.DataFrame: DataFrame with historical data
    """
    # This is a placeholder for future implementation
    # We can add support for Alpha Vantage, Yahoo Finance, or other data sources
    logger.warning("Alternative data sources not yet implemented")
    return pd.DataFrame()
