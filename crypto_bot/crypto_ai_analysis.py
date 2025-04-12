"""
ماژول تحلیل ارزهای دیجیتال با استفاده از هوش مصنوعی

این ماژول از OpenAI API برای تحلیل تکنیکال و فاندامنتال ارزهای دیجیتال استفاده می‌کند.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from openai import OpenAI
from crypto_bot.market_data import get_price_data, get_historical_data
from crypto_bot.crypto_news import get_crypto_news
from crypto_bot.cache_manager import cache_with_expiry

# Setup logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
GPT_MODEL = "gpt-4o"

# Cache expiration times
CACHE_EXPIRY_TECHNICAL = 900  # 15 minutes
CACHE_EXPIRY_FUNDAMENTAL = 3600  # 1 hour
CACHE_EXPIRY_GENERAL = 7200  # 2 hours

@cache_with_expiry(expiry_seconds=CACHE_EXPIRY_TECHNICAL)
def get_technical_analysis(symbol: str) -> Dict[str, Any]:
    """
    Get technical analysis for a cryptocurrency
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        
    Returns:
        Dict[str, Any]: Technical analysis data
    """
    try:
        # Standardize symbol format
        if "/" not in symbol and "-" not in symbol:
            symbol = f"{symbol}/USDT"
        
        # Get current price data
        price_data = get_price_data(symbol)
        
        # Get historical data for technical indicators
        timeframes = ["1d", "4h", "1h"]
        historical_data = {}
        
        for timeframe in timeframes:
            try:
                data = get_historical_data(symbol, timeframe)
                if data and len(data) > 0:
                    historical_data[timeframe] = data
            except Exception as e:
                logger.warning(f"Error getting {timeframe} historical data for {symbol}: {str(e)}")
        
        # Prepare the prompt for OpenAI
        historical_summary = ""
        for timeframe, data in historical_data.items():
            if data and len(data) >= 5:
                last_candles = data[-5:]  # Get last 5 candles
                candle_summary = "\n".join([
                    f"- {candle['timestamp'].strftime('%Y-%m-%d %H:%M')}: Open ${candle['open']:.2f}, "
                    f"High ${candle['high']:.2f}, Low ${candle['low']:.2f}, Close ${candle['close']:.2f}, "
                    f"Volume {candle['volume']:.2f}"
                    for candle in last_candles
                ])
                historical_summary += f"\n\n{timeframe.upper()} Timeframe:\n{candle_summary}"
        
        # Create analysis prompt
        analysis_prompt = f"""
        You are a professional cryptocurrency technical analyst. 
        Provide a detailed technical analysis for {symbol}.
        
        Current Data:
        - Price: ${price_data.get('price', 'Unknown')}
        - 24h Change: {price_data.get('change_24h', 'Unknown')}%
        
        Recent Price Action: {historical_summary}
        
        Please analyze the following:
        1. Current trend direction (bullish, bearish, or neutral)
        2. Key support and resistance levels
        3. RSI, MACD and moving averages analysis (estimate these based on the price action)
        4. Volume analysis
        5. Chart patterns if any are visible
        6. Trading recommendation (buy, sell, or hold) with confidence level
        
        Format your response as a detailed analysis a trader could use to make decisions.
        Include numerical values for support/resistance levels and indicators where possible.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional cryptocurrency technical analyst expert."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.4,  # Lower temperature for more factual responses
            max_tokens=1000
        )
        
        # Extract the analysis text
        analysis_text = response.choices[0].message.content
        
        return {
            "success": True,
            "symbol": symbol,
            "price": price_data.get('price', None),
            "change_24h": price_data.get('change_24h', None),
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis_text,
            "timeframes_analyzed": list(historical_data.keys())
        }
    
    except Exception as e:
        logger.error(f"Error in technical analysis for {symbol}: {str(e)}")
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@cache_with_expiry(expiry_seconds=CACHE_EXPIRY_FUNDAMENTAL)
def get_fundamental_analysis(symbol: str) -> Dict[str, Any]:
    """
    Get fundamental analysis for a cryptocurrency
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        
    Returns:
        Dict[str, Any]: Fundamental analysis data
    """
    try:
        # Normalize symbol
        normalized_symbol = symbol.upper().replace("/USDT", "").replace("-USDT", "")
        
        # Get current price data
        if "/" not in symbol and "-" not in symbol:
            price_symbol = f"{symbol}/USDT"
        else:
            price_symbol = symbol
            
        price_data = get_price_data(price_symbol)
        
        # Get latest news (without translation)
        news_data = get_crypto_news(translate=False, limit=5)
        
        # Filter news relevant to this cryptocurrency if possible
        relevant_news = []
        keywords = [
            normalized_symbol, 
            get_full_name(normalized_symbol),
            f"${normalized_symbol}"
        ]
        
        for news in news_data:
            title = news.get('title', '').lower()
            if any(keyword.lower() in title for keyword in keywords):
                relevant_news.append(news)
        
        # If we couldn't find specific news for this crypto, include general market news
        if len(relevant_news) < 2:
            relevant_news = news_data[:5]  # Just take the 5 most recent news
        
        # Format news for the prompt
        news_summary = "\n".join([
            f"- {news.get('title', 'Unknown')}: {news.get('summary', '')[:100]}... (Source: {news.get('source', 'Unknown')})"
            for news in relevant_news
        ])
        
        # Create analysis prompt
        analysis_prompt = f"""
        You are a cryptocurrency fundamental analyst. 
        Provide a detailed fundamental analysis for {normalized_symbol} ({get_full_name(normalized_symbol)}).
        
        Current Data:
        - Price: ${price_data.get('price', 'Unknown')}
        - 24h Change: {price_data.get('change_24h', 'Unknown')}%
        
        Recent News:
        {news_summary}
        
        Please analyze the following aspects:
        1. Market position and market cap analysis
        2. Recent developments and news impact
        3. Team and development activity
        4. Tokenomics and use case
        5. Competitive positioning
        6. Future outlook and potential catalysts
        7. Investment thesis (pros and cons)
        
        Format your response as a comprehensive fundamental analysis that investors could use to make long-term decisions.
        If you don't have specific information about certain aspects of this cryptocurrency, provide general analysis and mention where data is limited.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a cryptocurrency fundamental analyst and expert."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.4,  # Lower temperature for more factual responses
            max_tokens=1200
        )
        
        # Extract the analysis text
        analysis_text = response.choices[0].message.content
        
        return {
            "success": True,
            "symbol": normalized_symbol,
            "full_name": get_full_name(normalized_symbol),
            "price": price_data.get('price', None),
            "change_24h": price_data.get('change_24h', None),
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis_text,
            "news_count": len(relevant_news)
        }
    
    except Exception as e:
        logger.error(f"Error in fundamental analysis for {symbol}: {str(e)}")
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@cache_with_expiry(expiry_seconds=CACHE_EXPIRY_GENERAL)
def get_crypto_ai_answer(query: str) -> Dict[str, Any]:
    """
    Get AI-powered answer to cryptocurrency questions
    
    Args:
        query (str): User's question about cryptocurrency
        
    Returns:
        Dict[str, Any]: AI-generated answer and metadata
    """
    try:
        # Extract symbol if the query is about a specific cryptocurrency
        symbol = extract_crypto_symbol(query)
        
        # Get some context data if we have a specific cryptocurrency
        context_data = ""
        if symbol:
            try:
                price_symbol = f"{symbol}/USDT"
                price_data = get_price_data(price_symbol)
                context_data += f"\nCurrent {symbol} data:\n"
                context_data += f"- Price: ${price_data.get('price', 'Unknown')}\n"
                context_data += f"- 24h Change: {price_data.get('change_24h', 'Unknown')}%\n"
            except Exception as e:
                logger.warning(f"Could not get price data for {symbol}: {str(e)}")
        
        # Create analysis prompt
        analysis_prompt = f"""
        You are a cryptocurrency expert advisor who can analyze markets and provide detailed information.
        
        User Query: {query}
        
        {context_data}
        
        Please provide a comprehensive, accurate answer to the query. Include:
        - Relevant facts and data
        - Technical and fundamental considerations if applicable
        - Historical context if relevant
        - Future outlook based on current trends and known information
        
        If the query is too vague, still provide helpful information about the general topic.
        If the query concerns price predictions, explain factors that could affect price rather than giving specific price targets.
        
        Today's date is {datetime.now().strftime('%Y-%m-%d')}.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a cryptocurrency expert advisor with detailed knowledge of blockchain technology, trading, and markets."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        # Extract the analysis text
        answer_text = response.choices[0].message.content
        
        return {
            "success": True,
            "query": query,
            "detected_symbol": symbol,
            "answer": answer_text,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in AI answer generation for query '{query}': {str(e)}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def get_full_name(symbol: str) -> str:
    """
    Get full name of cryptocurrency from symbol
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        
    Returns:
        str: Full name of cryptocurrency
    """
    crypto_names = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "SOL": "Solana",
        "XRP": "XRP (Ripple)",
        "ADA": "Cardano",
        "DOGE": "Dogecoin",
        "DOT": "Polkadot",
        "SHIB": "Shiba Inu",
        "AVAX": "Avalanche",
        "MATIC": "Polygon",
        "LTC": "Litecoin",
        "UNI": "Uniswap",
        "LINK": "Chainlink",
        "XLM": "Stellar",
        "ATOM": "Cosmos",
        "NEAR": "NEAR Protocol",
        "ALGO": "Algorand",
        "BCH": "Bitcoin Cash",
        "ICP": "Internet Computer",
        "FIL": "Filecoin",
        "VET": "VeChain",
        "SAND": "The Sandbox",
        "MANA": "Decentraland",
        "AXS": "Axie Infinity",
        "HBAR": "Hedera",
        "EGLD": "MultiversX (Elrond)",
        "EOS": "EOS",
        "XTZ": "Tezos",
        "PEPE": "Pepe",
        "WIF": "Dogwifhat",
        "FLOKI": "Floki Inu",
        "XDC": "XDC Network",
        "GALA": "Gala",
        "JASMY": "JasmyCoin",
        "MEME": "MemeAI"
    }
    
    return crypto_names.get(symbol.upper(), symbol)

def extract_crypto_symbol(text: str) -> Optional[str]:
    """
    Extract cryptocurrency symbol from text
    
    Args:
        text (str): Text that might contain cryptocurrency symbol
        
    Returns:
        Optional[str]: Extracted cryptocurrency symbol or None
    """
    common_symbols = [
        "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "SHIB", "AVAX", "MATIC",
        "LTC", "UNI", "LINK", "XLM", "ATOM", "NEAR", "ALGO", "BCH", "ICP", "FIL",
        "VET", "SAND", "MANA", "AXS", "HBAR", "EGLD", "EOS", "XTZ"
    ]
    
    # Also look for common names
    common_names = {
        "BITCOIN": "BTC",
        "ETHEREUM": "ETH",
        "SOLANA": "SOL",
        "RIPPLE": "XRP",
        "CARDANO": "ADA",
        "DOGECOIN": "DOGE",
        "POLKADOT": "DOT",
        "SHIBA": "SHIB",
        "AVALANCHE": "AVAX",
        "POLYGON": "MATIC",
        "LITECOIN": "LTC",
        "UNISWAP": "UNI",
        "CHAINLINK": "LINK",
        "STELLAR": "XLM",
        "COSMOS": "ATOM",
        "NEAR": "NEAR",
        "ALGORAND": "ALGO",
        "BITCOIN CASH": "BCH",
        "INTERNET COMPUTER": "ICP",
        "FILECOIN": "FIL",
        "VECHAIN": "VET",
        "SANDBOX": "SAND",
        "DECENTRALAND": "MANA",
        "AXIE": "AXS",
        "HEDERA": "HBAR",
        "ELROND": "EGLD",
        "TEZOS": "XTZ"
    }
    
    # Check for symbols first
    upper_text = text.upper()
    for symbol in common_symbols:
        # Look for symbol with various delimiters
        for pattern in [f" {symbol} ", f"${symbol}", f"#{symbol}", f" {symbol}/", f" {symbol}-"]:
            if pattern in upper_text:
                return symbol
    
    # Check for names next
    for name, symbol in common_names.items():
        if name in upper_text:
            return symbol
    
    return None

# Testing function
def test_analysis():
    """Test the analysis functions"""
    print("Testing technical analysis...")
    tech_analysis = get_technical_analysis("BTC")
    print(f"Success: {tech_analysis['success']}")
    print(f"Analysis length: {len(tech_analysis.get('analysis', ''))}")
    
    print("\nTesting fundamental analysis...")
    fund_analysis = get_fundamental_analysis("ETH")
    print(f"Success: {fund_analysis['success']}")
    print(f"Analysis length: {len(fund_analysis.get('analysis', ''))}")
    
    print("\nTesting general query...")
    ai_answer = get_crypto_ai_answer("What are the prospects for layer 2 solutions in 2025?")
    print(f"Success: {ai_answer['success']}")
    print(f"Answer length: {len(ai_answer.get('answer', ''))}")

if __name__ == "__main__":
    test_analysis()