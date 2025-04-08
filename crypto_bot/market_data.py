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
# Binance removed due to Canada IP restrictions
EXCHANGE_LIST = ['kucoin', 'coinex', 'kraken', 'okx']

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

def get_current_prices(symbols, timeout=3):
    """
    Get current prices for a list of cryptocurrency symbols
    
    Args:
        symbols (list): List of symbols like ['BTC/USDT', 'ETH/USDT']
        timeout (int): Maximum time to wait for API responses in seconds
        
    Returns:
        dict: Dictionary of current prices for each symbol
    """
    # Always use CoinGecko as the primary source for live data
    logger.info(f"Fetching real-time prices from CoinGecko for {symbols}")
    result = {}
    
    try:
        # First try to get data from CoinGecko
        coingecko_result = get_prices_from_coingecko(symbols, timeout)
        
        # Add results
        for symbol in symbols:
            if symbol in coingecko_result:
                result[symbol] = coingecko_result[symbol]
                # Mark the data as real (not sample)
                result[symbol]['is_sample_data'] = False
                
        # Log success or missing symbols
        if len(result) == len(symbols):
            logger.info(f"Successfully fetched all prices from CoinGecko")
        else:
            missing_symbols = [s for s in symbols if s not in result]
            logger.warning(f"CoinGecko could not provide data for: {', '.join(missing_symbols)}")
            
    except Exception as e:
        logger.error(f"Error fetching prices from CoinGecko: {str(e)}")
    
    # If CoinGecko failed, fallback to exchanges
    if len(result) < len(symbols):
        logger.info("CoinGecko didn't provide all data, trying exchanges")
        
        missing_symbols = [s for s in symbols if s not in result]
        start_time = time.time()
        
        # Try each exchange until we get data for missing symbols
        for exchange_id in EXCHANGE_LIST:
            # Check if we've exceeded our overall timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Overall timeout of {timeout} seconds exceeded")
                break
                
            try:
                logger.info(f"Trying to fetch prices from {exchange_id}")
                exchange = _initialize_exchange(exchange_id)
                
                # Set a timeout for the exchange API requests
                exchange.timeout = timeout * 1000  # ccxt uses milliseconds
                
                # Check if exchange supports all symbols
                unsupported_symbols = []
                for symbol in missing_symbols:
                    if not exchange.has['fetchTicker']:
                        logger.warning(f"{exchange_id} does not support fetchTicker")
                        raise Exception(f"{exchange_id} does not support fetchTicker")
                    
                    try:
                        # Check if the symbol is available on this exchange
                        exchange.markets[symbol]
                    except (KeyError, ValueError):
                        unsupported_symbols.append(symbol)
                
                if len(unsupported_symbols) == len(missing_symbols):
                    logger.warning(f"{exchange_id} does not support any of the missing symbols")
                    continue
                
                # Fetch tickers for missing symbols that are supported
                for symbol in [s for s in missing_symbols if s not in unsupported_symbols]:
                    # Check if we've exceeded our timeout
                    if time.time() - start_time > timeout:
                        logger.warning(f"Timeout of {timeout} seconds exceeded during ticker fetching")
                        break
                        
                    try:
                        # Use a shorter timeout for each individual request
                        ticker = exchange.fetch_ticker(symbol)
                        result[symbol] = {
                            'price': ticker['last'],
                            'change_24h': ticker['percentage'] if 'percentage' in ticker else None,
                            'high_24h': ticker['high'] if 'high' in ticker else None,
                            'low_24h': ticker['low'] if 'low' in ticker else None,
                            'volume_24h': ticker['quoteVolume'] if 'quoteVolume' in ticker else None,
                            'timestamp': datetime.now().isoformat(),
                            'source': exchange_id,
                            'is_sample_data': False
                        }
                    except Exception as e:
                        logger.warning(f"Failed to fetch ticker for {symbol} on {exchange_id}: {str(e)}")
                
                # Update missing symbols list
                missing_symbols = [s for s in symbols if s not in result]
                if not missing_symbols:
                    logger.info("All symbols fetched successfully")
                    break
                    
            except Exception as e:
                logger.warning(f"Error fetching prices from {exchange_id}: {str(e)}")
    
    # Final check - if we still have missing symbols, log it
    missing_symbols = [s for s in symbols if s not in result]
    if missing_symbols:
        logger.warning(f"Could not fetch data for symbols: {', '.join(missing_symbols)}")
    
    return result

def get_prices_from_coingecko(symbols, timeout=3):
    """
    Fallback function to get prices from CoinGecko if the primary exchange fails
    
    Args:
        symbols (list): List of symbols like ['BTC/USDT', 'ETH/USDT']
        timeout (int): Maximum time to wait for API response in seconds
        
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
        'LUNA/USDT': 'terra-luna-2',
        # Add BTC-USDT format mapping
        'BTC-USDT': 'bitcoin',
        'ETH-USDT': 'ethereum',
        'XRP-USDT': 'ripple',
        'BNB-USDT': 'binancecoin',
        'ADA-USDT': 'cardano',
        'SOL-USDT': 'solana',
        'DOT-USDT': 'polkadot',
        'DOGE-USDT': 'dogecoin',
        'AVAX-USDT': 'avalanche-2',
        'LUNA-USDT': 'terra-luna-2'
    }
    
    # Check which symbols we have mappings for
    valid_symbols = [s for s in symbols if s in coin_map]
    if not valid_symbols:
        logger.warning(f"No CoinGecko mappings found for symbols: {symbols}")
        return {}
        
    coin_ids = [coin_map[symbol] for symbol in valid_symbols]
    coin_ids_str = ','.join(coin_ids)
    
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_ids_str}&order=market_cap_desc&sparkline=false&price_change_percentage=24h"
    
    try:
        # Add timeout to the request
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            for coin in data:
                # Find all corresponding symbols that map to this coin
                matching_symbols = [s for s, cid in coin_map.items() if cid == coin['id'] and s in symbols]
                
                for symbol in matching_symbols:
                    result[symbol] = {
                        'price': coin['current_price'],
                        'change_24h': coin['price_change_percentage_24h'],
                        'high_24h': coin['high_24h'],
                        'low_24h': coin['low_24h'],
                        'volume_24h': coin['total_volume'],
                        'timestamp': datetime.now().isoformat(),
                        'source': 'coingecko'
                    }
        else:
            logger.warning(f"CoinGecko API returned status code {response.status_code}")
            
    except requests.exceptions.Timeout:
        logger.warning(f"CoinGecko API request timed out after {timeout} seconds")
    except requests.exceptions.RequestException as e:
        logger.warning(f"CoinGecko API request failed: {str(e)}")
    
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
