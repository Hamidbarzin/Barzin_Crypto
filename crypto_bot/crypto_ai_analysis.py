"""
ماژول تحلیل ارزهای دیجیتال با استفاده از هوش مصنوعی

این ماژول از OpenAI API برای تحلیل تکنیکال و فاندامنتال ارزهای دیجیتال استفاده می‌کند.
"""

import logging
import os
import time
import json
import re
from typing import Dict, Any, List, Optional

import openai
from crypto_bot.market_data import get_crypto_price, get_historical_data
from crypto_bot.crypto_news import get_crypto_news

# Setup logging
logger = logging.getLogger(__name__)

# Initialize OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Cache for analysis to prevent repeated API calls
ANALYSIS_CACHE = {}
CACHE_EXPIRY = 3600  # 1 hour in seconds

def cache_with_expiry(key: str, data: Any, expiry_seconds: int = CACHE_EXPIRY) -> None:
    """
    Cache data with expiry
    
    Args:
        key (str): Cache key
        data (Any): Data to cache
        expiry_seconds (int): Cache expiry time in seconds
    """
    ANALYSIS_CACHE[key] = {
        "data": data,
        "timestamp": time.time(),
        "expiry": expiry_seconds
    }

def get_cached_data(key: str) -> Optional[Any]:
    """
    Get cached data if not expired
    
    Args:
        key (str): Cache key
        
    Returns:
        Optional[Any]: Cached data or None if expired/not found
    """
    if key in ANALYSIS_CACHE:
        cache_entry = ANALYSIS_CACHE[key]
        if time.time() - cache_entry["timestamp"] < cache_entry["expiry"]:
            return cache_entry["data"]
    return None

def get_technical_analysis(symbol: str) -> Dict[str, Any]:
    """
    Get technical analysis for a cryptocurrency
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        
    Returns:
        Dict[str, Any]: Technical analysis data
    """
    # Check cache first
    cache_key = f"technical_{symbol.upper()}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    try:
        # Standardize symbol format
        std_symbol = f"{symbol.upper()}/USDT"
        
        # Get current price data
        price_data = get_crypto_price(std_symbol)
        if not price_data:
            return {
                "success": False,
                "message": f"Could not retrieve price data for {symbol}",
                "analysis": f"Technical analysis for {symbol} is not available at the moment due to data retrieval issues."
            }
        
        # Get historical data for technical indicators
        historical_data = get_historical_data(std_symbol, timeframe="1d", limit=30)
        
        # Prepare prompt for OpenAI
        prompt = f"""
        As a cryptocurrency technical analyst, provide a detailed technical analysis for {symbol} based on the following data:
        
        Current price: ${price_data.get('price', 0):,.2f}
        24h change: {price_data.get('change_24h', 0):+.2f}%
        
        Please include analysis of:
        1. Current price action and trends
        2. Key support and resistance levels
        3. RSI, MACD, and other relevant indicators
        4. Short-term price predictions (next 24-48 hours)
        5. Medium-term outlook (1-2 weeks)
        
        Keep your analysis concise yet comprehensive, focused on actionable insights.
        """
        
        # Call OpenAI API
        if OPENAI_API_KEY:
            response = openai.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency technical analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            analysis = response.choices[0].message.content.strip()
        else:
            analysis = f"Technical analysis for {symbol} is not available at the moment due to API configuration issues."
        
        # Build result object
        result = {
            "success": True,
            "symbol": symbol.upper(),
            "price": price_data.get('price', 0),
            "change_24h": price_data.get('change_24h', 0),
            "analysis": analysis,
            "timestamp": time.time()
        }
        
        # Cache the result
        cache_with_expiry(cache_key, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating technical analysis for {symbol}: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "analysis": f"Technical analysis for {symbol} is not available at the moment due to an internal error."
        }

def get_fundamental_analysis(symbol: str) -> Dict[str, Any]:
    """
    Get fundamental analysis for a cryptocurrency
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        
    Returns:
        Dict[str, Any]: Fundamental analysis data
    """
    # Check cache first
    cache_key = f"fundamental_{symbol.upper()}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    try:
        # Standardize symbol format
        std_symbol = f"{symbol.upper()}/USDT"
        
        # Get current price data
        price_data = get_crypto_price(std_symbol)
        if not price_data:
            return {
                "success": False,
                "message": f"Could not retrieve price data for {symbol}",
                "analysis": f"Fundamental analysis for {symbol} is not available at the moment due to data retrieval issues."
            }
        
        # Get news related to the symbol
        news_data = get_crypto_news(symbol=symbol, count=5)
        news_text = ""
        if news_data and len(news_data) > 0:
            news_text = "Recent news:\n" + "\n".join(
                [f"- {item.get('title', 'Untitled')}: {item.get('summary', 'No summary')[:100]}..." 
                 for item in news_data[:3]]
            )
        
        # Add full cryptocurrency name
        full_name = get_full_name(symbol)
        
        # Prepare prompt for OpenAI
        prompt = f"""
        As a cryptocurrency fundamental analyst, provide a detailed fundamental analysis for {full_name} ({symbol}) based on the following data:
        
        Current price: ${price_data.get('price', 0):,.2f}
        24h change: {price_data.get('change_24h', 0):+.2f}%
        
        {news_text}
        
        Please include analysis of:
        1. Market position and strengths/weaknesses
        2. Tokenomics and economic model
        3. Technology and development activity
        4. Adoption, partnerships, and ecosystem
        5. Market sentiment and long-term potential
        
        Keep your analysis concise yet comprehensive, focused on investment value.
        """
        
        # Call OpenAI API
        if OPENAI_API_KEY:
            response = openai.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency fundamental analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            analysis = response.choices[0].message.content.strip()
        else:
            analysis = f"Fundamental analysis for {symbol} is not available at the moment due to API configuration issues."
        
        # Build result object
        result = {
            "success": True,
            "symbol": symbol.upper(),
            "full_name": full_name,
            "price": price_data.get('price', 0),
            "change_24h": price_data.get('change_24h', 0),
            "analysis": analysis,
            "timestamp": time.time()
        }
        
        # Cache the result
        cache_with_expiry(cache_key, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating fundamental analysis for {symbol}: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "analysis": f"Fundamental analysis for {symbol} is not available at the moment due to an internal error."
        }

def get_crypto_ai_answer(query: str) -> Dict[str, Any]:
    """
    Get AI-powered answer to cryptocurrency questions
    
    Args:
        query (str): User's question about cryptocurrency
        
    Returns:
        Dict[str, Any]: AI-generated answer and metadata
    """
    # Check cache first
    cache_key = f"query_{hash(query)}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    try:
        # Extract potential cryptocurrency symbols
        potential_symbol = extract_crypto_symbol(query)
        
        # Get price data if a symbol is detected
        price_context = ""
        if potential_symbol:
            std_symbol = f"{potential_symbol.upper()}/USDT"
            price_data = get_crypto_price(std_symbol)
            if price_data:
                price_context = f"""
                Current {potential_symbol} price: ${price_data.get('price', 0):,.2f}
                24h change: {price_data.get('change_24h', 0):+.2f}%
                """
        
        # Prepare prompt for OpenAI
        prompt = f"""
        As a cryptocurrency expert analyst, please answer the following question:
        
        {query}
        
        {price_context}
        
        Provide a detailed, accurate, and helpful response based on current market knowledge.
        Include specific data points, trends, or recommendations as appropriate.
        """
        
        # Call OpenAI API
        if OPENAI_API_KEY:
            response = openai.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency analyst and expert. Always provide accurate, up-to-date information and clearly indicate when something is your opinion vs. established fact."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
        else:
            answer = "AI-powered analysis is not available at the moment due to API configuration issues."
        
        # Build result object
        result = {
            "success": True,
            "query": query,
            "detected_symbol": potential_symbol,
            "answer": answer,
            "timestamp": time.time()
        }
        
        # Cache the result
        cache_with_expiry(cache_key, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating AI answer for query '{query}': {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "answer": "Unable to process your question at this time due to an internal error."
        }

def get_full_name(symbol: str) -> str:
    """
    Get full name of cryptocurrency from symbol
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        
    Returns:
        str: Full name of cryptocurrency
    """
    symbol_map = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "SOL": "Solana",
        "XRP": "Ripple",
        "ADA": "Cardano",
        "DOGE": "Dogecoin",
        "SHIB": "Shiba Inu",
        "BNB": "Binance Coin",
        "DOT": "Polkadot",
        "AVAX": "Avalanche",
        "MATIC": "Polygon",
        "LINK": "Chainlink",
        "LTC": "Litecoin",
        "XLM": "Stellar",
        "ALGO": "Algorand",
        "UNI": "Uniswap",
        "ATOM": "Cosmos",
        "FIL": "Filecoin",
        "VET": "VeChain",
        "HBAR": "Hedera",
        "NEAR": "NEAR Protocol",
        "XTZ": "Tezos",
        "EGLD": "MultiversX",
        "EOS": "EOS",
        "ZEC": "Zcash",
        "DASH": "Dash",
        "XMR": "Monero",
        "ICP": "Internet Computer",
        "FTM": "Fantom",
        "SAND": "The Sandbox",
        "MANA": "Decentraland",
        "AXS": "Axie Infinity",
        "CAKE": "PancakeSwap",
        "GRT": "The Graph",
        "CHZ": "Chiliz",
        "ENJ": "Enjin Coin",
        "ONE": "Harmony",
        "HOT": "Holo",
        "ZIL": "Zilliqa",
        "BAT": "Basic Attention Token",
        "RVN": "Ravencoin",
        "SC": "Siacoin",
        "ANKR": "Ankr",
        "STORJ": "Storj",
        "KAVA": "Kava",
        "BNT": "Bancor",
        "CELO": "Celo",
        "WIF": "Dogwifhat",
        "PEPE": "Pepe",
        "JTO": "Jito",
        "JUP": "Jupiter",
        "BONK": "Bonk",
        "FLOKI": "Floki Inu",
        "MEME": "Meme Coin",
        "JASMY": "JasmyCoin",
        "INJ": "Injective",
        "IMX": "Immutable X",
        "OP": "Optimism",
        "ARB": "Arbitrum",
        "CRO": "Cronos",
        "TIA": "Celestia",
    }
    
    upper_symbol = symbol.upper()
    return symbol_map.get(upper_symbol, f"{upper_symbol} Coin")

def extract_crypto_symbol(text: str) -> Optional[str]:
    """
    Extract cryptocurrency symbol from text
    
    Args:
        text (str): Text that might contain cryptocurrency symbol
        
    Returns:
        Optional[str]: Extracted cryptocurrency symbol or None
    """
    # Common cryptocurrency symbols
    common_symbols = [
        "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "SHIB", "BNB", 
        "DOT", "AVAX", "MATIC", "LINK", "LTC", "XLM", "ALGO", "UNI",
        "ATOM", "FIL", "VET", "HBAR", "NEAR", "XTZ", "EGLD", "EOS", 
        "ZEC", "DASH", "XMR", "ICP", "FTM", "SAND", "MANA", "AXS",
        "CAKE", "GRT", "CHZ", "ENJ", "ONE", "HOT", "ZIL", "BAT",
        "RVN", "SC", "ANKR", "STORJ", "KAVA", "BNT", "CELO", "WIF",
        "PEPE", "JTO", "JUP", "BONK", "FLOKI", "MEME", "JASMY", "INJ",
        "IMX", "OP", "ARB", "CRO", "TIA"
    ]
    
    # Pattern to find crypto symbols
    pattern = r'\b(' + '|'.join(common_symbols) + r')\b'
    
    # Find all matches
    matches = re.findall(pattern, text.upper())
    
    if matches:
        return matches[0]
    
    # Look for symbol/USDT pattern
    usdt_pattern = r'([A-Z]+)(?:/|-|/)USDT'
    usdt_matches = re.findall(usdt_pattern, text.upper())
    
    if usdt_matches:
        return usdt_matches[0]
    
    # Look for full cryptocurrency names
    full_name_map = {
        "BITCOIN": "BTC",
        "ETHEREUM": "ETH",
        "SOLANA": "SOL",
        "RIPPLE": "XRP",
        "CARDANO": "ADA",
        "DOGECOIN": "DOGE"
    }
    
    for name, symbol in full_name_map.items():
        if name in text.upper():
            return symbol
    
    return None

def test_analysis():
    """Test the analysis functions"""
    # Test technical analysis
    btc_technical = get_technical_analysis("BTC")
    print("BTC Technical Analysis:")
    print(json.dumps(btc_technical, indent=2))
    
    # Test fundamental analysis
    eth_fundamental = get_fundamental_analysis("ETH")
    print("\nETH Fundamental Analysis:")
    print(json.dumps(eth_fundamental, indent=2))
    
    # Test AI Q&A
    query_result = get_crypto_ai_answer("What is the long-term outlook for Bitcoin considering the recent halving?")
    print("\nBTC Question Answer:")
    print(json.dumps(query_result, indent=2))

if __name__ == "__main__":
    if OPENAI_API_KEY:
        test_analysis()
    else:
        print("OPENAI_API_KEY environment variable is not set. Cannot run tests.")