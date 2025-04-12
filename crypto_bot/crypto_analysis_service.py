#!/usr/bin/env python3
"""
سرویس تحلیل ارزهای دیجیتال

این ماژول توابع مربوط به تحلیل و پاسخگویی به سوالات در مورد ارزهای دیجیتال را ارائه می‌دهد.
"""

import logging
import requests
import json
import os
from datetime import datetime
import openai

# تنظیم لاگ
logger = logging.getLogger(__name__)

# تنظیم کلید API OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY", "")

def get_crypto_analysis(crypto_name, question_type="general"):
    """
    دریافت تحلیل برای یک ارز دیجیتال
    
    Args:
        crypto_name (str): نام ارز دیجیتال
        question_type (str): نوع سوال (تحلیل تکنیکال، تحلیل بنیادی، اخبار، و غیره)
    
    Returns:
        dict: نتیجه تحلیل
    """
    try:
        # بررسی نوع سوال
        prompt = create_analysis_prompt(crypto_name, question_type)
        
        # استفاده از OpenAI برای تحلیل - همسازگار با نسخه قدیمی‌تر API
        system_message = "You are a cryptocurrency analysis expert. Provide detailed and accurate information about cryptocurrencies based on technical analysis, fundamental analysis, and market trends."
        
        # استفاده از نسخه قدیمی‌تر OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # استفاده از مدل پایدارتر
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "success": True,
            "crypto": crypto_name,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_crypto_analysis: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "crypto": crypto_name
        }

def create_analysis_prompt(crypto_name, question_type):
    """
    ایجاد پرامپت مناسب برای تحلیل ارز دیجیتال
    
    Args:
        crypto_name (str): نام ارز دیجیتال
        question_type (str): نوع سوال
    
    Returns:
        str: پرامپت
    """
    base_prompt = f"Provide a detailed analysis for the cryptocurrency {crypto_name}. "
    
    if question_type == "technical":
        prompt = base_prompt + "Focus on technical analysis, including price patterns, support/resistance levels, moving averages, RSI, MACD, and other relevant technical indicators. Also mention potential entry and exit points."
    elif question_type == "fundamental":
        prompt = base_prompt + "Focus on fundamental analysis, including the project's technology, team, use cases, tokenomics, partnerships, and competitive advantages or disadvantages in the market."
    elif question_type == "news":
        prompt = base_prompt + "Focus on recent news, developments, and events that might impact the price and future of this cryptocurrency."
    elif question_type == "price_prediction":
        prompt = base_prompt + "Focus on potential price movements in the short term (1-7 days), medium term (1-3 months), and long term (1 year+). Include factors that might influence these predictions."
    elif question_type == "trading_strategy":
        prompt = base_prompt + "Suggest trading strategies for this cryptocurrency, including potential entry and exit points, risk management, and position sizing."
    else:  # general
        prompt = base_prompt + "Include key aspects of both technical and fundamental analysis, recent news, and a general outlook for this cryptocurrency."
    
    return prompt

def get_crypto_market_data(crypto_symbol):
    """
    دریافت داده‌های بازار برای یک ارز دیجیتال
    
    Args:
        crypto_symbol (str): نماد ارز دیجیتال
    
    Returns:
        dict: داده‌های بازار
    """
    try:
        # تلاش برای دریافت داده‌ها از CoinGecko
        api_url = f"https://api.coingecko.com/api/v3/coins/{crypto_symbol.lower()}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            market_data = {
                "success": True,
                "name": data.get("name"),
                "symbol": data.get("symbol", "").upper(),
                "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                "price_change_7d": data.get("market_data", {}).get("price_change_percentage_7d"),
                "price_change_30d": data.get("market_data", {}).get("price_change_percentage_30d"),
                "all_time_high": data.get("market_data", {}).get("ath", {}).get("usd"),
                "all_time_high_date": data.get("market_data", {}).get("ath_date", {}).get("usd"),
                "all_time_low": data.get("market_data", {}).get("atl", {}).get("usd"),
                "all_time_low_date": data.get("market_data", {}).get("atl_date", {}).get("usd"),
                "timestamp": datetime.now().isoformat()
            }
            
            return market_data
        else:
            logger.warning(f"Failed to get data from CoinGecko: {response.status_code}")
            return {
                "success": False,
                "error": f"API request failed with status code {response.status_code}"
            }
    except Exception as e:
        logger.error(f"Error in get_crypto_market_data: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_crypto_news(crypto_name, limit=5):
    """
    دریافت اخبار مرتبط با یک ارز دیجیتال
    
    Args:
        crypto_name (str): نام ارز دیجیتال
        limit (int): تعداد اخبار
    
    Returns:
        dict: اخبار
    """
    try:
        # استفاده از OpenAI برای ایجاد خلاصه‌ای از اخبار اخیر
        prompt = f"What are the most important recent news (last 2-4 weeks) about {crypto_name} cryptocurrency? Please list {limit} news items with dates and a brief description of each."
        
        # استفاده از نسخه قدیمی‌تر OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # استفاده از مدل پایدارتر
            messages=[
                {"role": "system", "content": "You are a cryptocurrency news analyst. Provide the most relevant and recent news about cryptocurrencies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        
        news_content = response.choices[0].message.content
        
        return {
            "success": True,
            "crypto": crypto_name,
            "news": news_content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_crypto_news: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "crypto": crypto_name
        }