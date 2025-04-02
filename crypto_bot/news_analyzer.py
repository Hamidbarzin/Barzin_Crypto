"""
Functions for fetching and analyzing cryptocurrency news
"""

import os
import re
import logging
import requests
from datetime import datetime, timedelta
import trafilatura
from bs4 import BeautifulSoup

from crypto_bot.config import NEWS_API_KEY, NEWS_SOURCES, POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS

logger = logging.getLogger(__name__)

def get_latest_news(limit=10):
    """
    Get the latest cryptocurrency news articles
    
    Args:
        limit (int): Maximum number of news articles to return
        
    Returns:
        list: List of news article dictionaries with title, source, url, date, and sentiment
    """
    try:
        # Try with NewsAPI if we have an API key
        if NEWS_API_KEY:
            return get_news_from_newsapi(limit)
        else:
            # If no NEWS_API_KEY, scrape from cryptocurrency news websites
            return scrape_crypto_news(limit)
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return []

def get_news_from_newsapi(limit=10):
    """
    Get cryptocurrency news from NewsAPI
    """
    url = "https://newsapi.org/v2/everything"
    
    # Get news from the last 3 days
    from_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    params = {
        'q': 'cryptocurrency OR bitcoin OR ethereum OR crypto',
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'from': from_date,
        'sortBy': 'publishedAt',
        'pageSize': limit
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        logger.error(f"NewsAPI error: {response.status_code} - {response.text}")
        return []
    
    data = response.json()
    
    if data['status'] != 'ok':
        logger.error(f"NewsAPI error: {data['status']}")
        return []
    
    result = []
    for article in data['articles'][:limit]:
        # Calculate sentiment score
        title = article['title']
        description = article['description'] or ""
        sentiment = analyze_sentiment(title + " " + description)
        
        result.append({
            'title': title,
            'source': article['source']['name'],
            'url': article['url'],
            'date': article['publishedAt'],
            'sentiment': sentiment
        })
    
    return result

def scrape_crypto_news(limit=10):
    """
    Scrape cryptocurrency news from popular websites when API is not available
    """
    result = []
    
    # List of popular cryptocurrency news sites
    news_sites = [
        {
            'url': 'https://cointelegraph.com/',
            'article_selector': 'article.post-card-inline',
            'title_selector': 'span.post-card-inline__title',
            'link_selector': 'a'
        },
        {
            'url': 'https://www.coindesk.com/',
            'article_selector': 'div.article-card',
            'title_selector': 'h6.heading',
            'link_selector': 'a.card-title-link'
        }
    ]
    
    for site in news_sites:
        if len(result) >= limit:
            break
            
        try:
            response = requests.get(site['url'], headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code != 200:
                logger.warning(f"Error fetching from {site['url']}: Status code {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select(site['article_selector'])
            
            for article in articles[:min(5, limit - len(result))]:
                try:
                    title_element = article.select_one(site['title_selector'])
                    link_element = article.select_one(site['link_selector'])
                    
                    if not title_element or not link_element:
                        continue
                        
                    title = title_element.get_text().strip()
                    link = link_element.get('href')
                    
                    # Make relative URLs absolute
                    if link and not link.startswith('http'):
                        link = site['url'].rstrip('/') + '/' + link.lstrip('/')
                        
                    if title and link:
                        # Get article content for sentiment analysis
                        article_content = get_article_content(link)
                        sentiment = analyze_sentiment(title + " " + article_content)
                        
                        result.append({
                            'title': title,
                            'source': site['url'].split('//')[1].split('/')[0].replace('www.', ''),
                            'url': link,
                            'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),  # Approximate date
                            'sentiment': sentiment
                        })
                except Exception as e:
                    logger.error(f"Error processing article from {site['url']}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error scraping from {site['url']}: {str(e)}")
            
    return result[:limit]

def get_article_content(url):
    """
    Extract the main content from a news article
    """
    try:
        # Using trafilatura for effective content extraction
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        
        if not text:
            # Fallback to simple extraction
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                    
                text = soup.get_text()
                # Break into lines and remove leading/trailing whitespace
                lines = (line.strip() for line in text.splitlines())
                # Join lines into paragraphs, breaking on blank lines
                text = '\n'.join(line for line in lines if line)
                
        return text or ""
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return ""

def analyze_sentiment(text):
    """
    Simple rule-based sentiment analysis for cryptocurrency news
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Dictionary with sentiment score and label
    """
    text = text.lower()
    
    # Count positive and negative keywords
    positive_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword.lower() in text)
    negative_count = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword.lower() in text)
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        score = 0  # Neutral if no keywords found
    else:
        score = (positive_count - negative_count) / total
        
    # Determine sentiment label
    if score > 0.3:
        label = "Positive"
    elif score < -0.3:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {
        'score': score,
        'label': label,
        'positive_count': positive_count,
        'negative_count': negative_count
    }
