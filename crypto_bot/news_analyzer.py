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

def get_latest_news(limit=10, include_middle_east=True):
    """
    Get the latest cryptocurrency news articles
    
    Args:
        limit (int): Maximum number of news articles to return
        include_middle_east (bool): Whether to include Middle Eastern news sources
        
    Returns:
        list: List of news article dictionaries with title, source, url, date, and sentiment
    """
    try:
        news_articles = []
        
        # Try with NewsAPI if we have an API key
        if NEWS_API_KEY:
            news_articles.extend(get_news_from_newsapi(limit))
        
        # Even if we have NewsAPI, always scrape from global crypto sites to ensure coverage
        news_articles.extend(scrape_crypto_news(limit, include_middle_east))
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        
        for article in news_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # Sort by date (newest first) and limit results
        sorted_articles = sorted(unique_articles, 
                                key=lambda x: x.get('date', ''), 
                                reverse=True)
                                
        return sorted_articles[:limit]
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

def scrape_crypto_news(limit=10, include_middle_east=True):
    """
    Scrape cryptocurrency news from popular websites when API is not available
    
    Args:
        limit (int): Maximum number of news articles to return
        include_middle_east (bool): Whether to include Middle Eastern news sources
        
    Returns:
        list: List of news article dictionaries
    """
    result = []
    
    # List of popular cryptocurrency news sites (global and Middle East)
    # Define which sites are Middle Eastern
    middle_east_domains = ['ramzarz.news', 'arzdigital.com', 'menaherald.com', 'wallex.ir', 'iranfintech.com', 'irbitex.com', 'tejaratnews.com', 'donya-e-eqtesad.com']
    
    # Updated selectors to match current website structures
    news_sites = [
        # سایت‌های خبری انگلیسی
        {
            'url': 'https://cointelegraph.com/',
            'article_selector': 'article',  # Simplified selector
            'title_selector': 'h2',  # More generic title selector
            'link_selector': 'a'
        },
        {
            'url': 'https://www.coindesk.com/',
            'article_selector': 'article',  # Simplified selector
            'title_selector': 'h5,h4,h6',  # Try multiple possible heading tags
            'link_selector': 'a'
        },
        {
            'url': 'https://decrypt.co/',  # Alternative site
            'article_selector': 'article',  # Simplified selector
            'title_selector': 'h3,h2,h4',  # Try multiple possible heading tags
            'link_selector': 'a'
        },
        # سایت‌های خبری فارسی
        {
            'url': 'https://ramzarz.news/',
            'article_selector': 'article,.post-item',  # Simplified selector
            'title_selector': 'h3,h2,h4',  # Try multiple possible heading tags
            'link_selector': 'a'
        },
        {
            'url': 'https://arzdigital.com/breaking/',
            'article_selector': 'article,.post-card',  # Simplified selector
            'title_selector': 'h3,h2,h4',  # Try multiple possible heading tags
            'link_selector': 'a'
        },
        {
            'url': 'https://wallex.ir/blog/',
            'article_selector': 'article,.blog-card,.post',
            'title_selector': 'h3,h2,h4,h5',
            'link_selector': 'a'
        },
        {
            'url': 'https://iranfintech.com/category/رمز-ارزها/',
            'article_selector': 'article,.post-item',
            'title_selector': 'h3,h2,h4,h5',
            'link_selector': 'a'
        },
        {
            'url': 'https://irbitex.com/blog/',
            'article_selector': 'article,.blog-post,.card',
            'title_selector': 'h3,h2,h4,h5',
            'link_selector': 'a'
        },
        {
            'url': 'https://tejaratnews.com/cryptocurrency',
            'article_selector': 'article,.news-item',
            'title_selector': 'h3,h2,h4,h5',
            'link_selector': 'a'
        },
        {
            'url': 'https://donya-e-eqtesad.com/بخش-رمز-ارز-177',
            'article_selector': 'article,.news-item,.news-box',
            'title_selector': 'h3,h2,h4,h5,a.title',
            'link_selector': 'a'
        }
    ]
    
    filtered_sites = []
    for site in news_sites:
        # Skip Middle Eastern sites if not requested
        domain = site['url'].split('//')[1].split('/')[0].replace('www.', '')
        is_middle_east = any(me_domain in domain for me_domain in middle_east_domains)
        
        if is_middle_east and not include_middle_east:
            continue
            
        filtered_sites.append(site)
    
    for site in filtered_sites:
        if len(result) >= limit:
            break
            
        try:
            response = requests.get(site['url'], headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }, timeout=10)  # Added timeout
            
            if response.status_code != 200:
                logger.warning(f"Error fetching from {site['url']}: Status code {response.status_code}")
                continue
            
            # Generate fallback news if web scraping fails
            fallback_news = []
            domain = site['url'].split('//')[1].split('/')[0].replace('www.', '')
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find articles
                articles = soup.select(site['article_selector'])
                
                # If no articles found with specific selector, try simpler approach
                if not articles:
                    logger.info(f"No articles found with selector '{site['article_selector']}' for {site['url']}, trying simpler extraction")
                    
                    # Simple extraction of all article tags or divs that could be articles
                    articles = soup.find_all('article') or soup.find_all('div', class_=['post', 'article', 'news-item', 'card', 'entry'])
                
                for article in articles[:min(5, limit - len(result))]:
                    try:
                        # Try multiple selectors for title
                        title_element = None
                        for selector in site['title_selector'].split(','):
                            title_element = article.select_one(selector)
                            if title_element:
                                break
                        
                        # If still no title, look for any heading
                        if not title_element:
                            for h_tag in ['h2', 'h3', 'h4', 'h5']:
                                title_element = article.find(h_tag)
                                if title_element:
                                    break
                        
                        # Try to find link
                        link_element = article.select_one(site['link_selector'])
                        
                        # If no link found, try to find any link
                        if not link_element:
                            link_element = article.find('a')
                        
                        if not title_element or not link_element:
                            continue
                            
                        title = title_element.get_text().strip()
                        
                        # Handle different element types for links
                        link = None
                        try:
                            # Handle beautifulsoup Tag objects
                            if hasattr(link_element, 'name'):
                                # If it's a bs4.Tag
                                link = link_element.get('href')
                            else:
                                # Try direct access 
                                link = link_element['href']
                        except (TypeError, KeyError, AttributeError):
                            # If all fails, try other approaches or skip this link
                            pass
                        
                        # Make relative URLs absolute
                        if link and isinstance(link, str) and not link.startswith('http'):
                            base_url = site['url'].rstrip('/')
                            if link.startswith('/'):
                                link = base_url + link
                            else:
                                link = base_url + '/' + link
                                
                        if title and link:
                            # Get article content for sentiment analysis
                            article_content = get_article_content(link)
                            sentiment = analyze_sentiment(title + " " + article_content)
                            
                            result.append({
                                'title': title,
                                'source': domain,
                                'url': link,
                                'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),  # Approximate date
                                'sentiment': sentiment
                            })
                    except Exception as e:
                        logger.error(f"Error processing article from {site['url']}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error parsing HTML from {site['url']}: {str(e)}")
                continue
                                
        except Exception as e:
            logger.error(f"Error scraping from {site['url']}: {str(e)}")
    
    # If we couldn't get enough news items, add general cryptocurrency news
    if len(result) < 2:
        logger.warning("Not enough news found from sources, adding general crypto market news")
        general_crypto_news = [
            {
                'title': "Market Analysis: Understanding Latest Cryptocurrency Trends",
                'source': "crypto-analyzer",
                'url': "#",
                'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'sentiment': analyze_sentiment("Market Analysis Understanding Latest Cryptocurrency Trends")
            },
            {
                'title': "Digital Currency Developments in Global Markets",
                'source': "crypto-analyzer",
                'url': "#",
                'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'sentiment': analyze_sentiment("Digital Currency Developments in Global Markets")
            }
        ]
        
        # Add only as many as needed to reach minimum threshold
        result.extend(general_crypto_news[:min(2, 2 - len(result))])
            
    return result[:limit]

def get_article_content(url):
    """
    Extract the main content from a news article using trafilatura
    
    Args:
        url (str): URL of the article
        
    Returns:
        str: Main content of the article
    """
    try:
        # Using trafilatura for effective content extraction
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        
        if not text:
            # Fallback to simple extraction
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try common content container selectors first
                content_selectors = [
                    'article', 'main', '.article-content', '.post-content',
                    '.entry-content', '#article-body', '.story-body', '.content-body',
                    '.article', '.post', '.news-item', '.news-content', '.article-body',
                    '[itemprop="articleBody"]', '[class*="article"]', '[class*="content"]',
                ]
                
                article_content = ""
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        # Extract text from paragraphs
                        paragraphs = content.find_all('p')
                        if paragraphs:
                            article_content = '\n'.join([p.get_text().strip() for p in paragraphs])
                            break
                
                # If we found content from selectors, use it
                if article_content:
                    text = article_content
                else:
                    # Remove unwanted elements
                    for script in soup(["script", "style", "header", "footer", "nav", "aside", "iframe"]):
                        script.extract()
                        
                    # Get all text
                    text = soup.get_text()
                    # Break into lines and remove leading/trailing whitespace
                    lines = (line.strip() for line in text.splitlines())
                    # Join lines into paragraphs, breaking on blank lines
                    text = '\n'.join(line for line in lines if line)
                
        # Remove excess whitespace and normalize
        if text:
            text = ' '.join(text.split())
            # Split into sentences and rejoin with proper spacing
            sentences = text.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n')
            text = sentences
            
        return text or ""
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return ""

def analyze_sentiment(text):
    """
    Enhanced rule-based sentiment analysis for cryptocurrency news.
    Supports both English and Persian text with weighted keyword matching.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Dictionary with sentiment score and label
    """
    if not text:
        return {
            'score': 0,
            'label': "Neutral",
            'positive_count': 0,
            'negative_count': 0
        }
        
    # Convert to lowercase for case-insensitive matching
    # Note: Persian doesn't have uppercase/lowercase but English does
    text = text.lower()
    
    # Detect language (simple check for Persian characters)
    is_persian = any('\u0600' <= c <= '\u06FF' for c in text)
    
    # Weight modifiers - give more importance to certain patterns
    strong_modifiers = {
        # انگلیسی - English modifiers
        'significant': 1.5, 'major': 1.5, 'huge': 1.5, 'massive': 1.5, 'critical': 1.5, 
        'extremely': 1.5, 'substantially': 1.5, 'dramatic': 1.5, 'serious': 1.5,
        # فارسی - Persian modifiers
        'بسیار': 1.5, 'شدید': 1.5, 'قابل توجه': 1.5, 'چشمگیر': 1.5, 'عظیم': 1.5,
        'فوق‌العاده': 1.5, 'قابل ملاحظه': 1.5, 'به‌شدت': 1.5, 'اساسی': 1.5
    }
    
    # Apply weight to sentiment based on presence of modifiers
    weight_multiplier = 1.0
    for modifier, weight in strong_modifiers.items():
        if modifier in text:
            weight_multiplier = max(weight_multiplier, weight)
    
    # Enhanced keyword matching (count and track occurrences)
    positive_matches = []
    negative_matches = []
    
    # Analyze text in chunks to better handle long texts
    chunks = [text[i:i+200] for i in range(0, len(text), 200)]
    
    for chunk in chunks:
        # Count positive and negative keywords with position info
        for keyword in POSITIVE_KEYWORDS:
            if keyword.lower() in chunk:
                positive_matches.append({
                    'keyword': keyword,
                    'weight': 1.0  # base weight
                })
        
        for keyword in NEGATIVE_KEYWORDS:
            if keyword.lower() in chunk:
                negative_matches.append({
                    'keyword': keyword,
                    'weight': 1.0  # base weight
                })
    
    # Calculate weighted counts
    positive_count = sum(match['weight'] for match in positive_matches)
    negative_count = sum(match['weight'] for match in negative_matches)
    
    # Apply weight multiplier from modifiers
    positive_weighted = positive_count * weight_multiplier
    negative_weighted = negative_count * weight_multiplier
    
    # Add title emphasis - keywords in title are more important
    title_end = min(100, len(text))  # Assume first 100 chars might be title
    title_text = text[:title_end]
    
    title_positive = sum(1 for keyword in POSITIVE_KEYWORDS if keyword.lower() in title_text)
    title_negative = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword.lower() in title_text)
    
    # Add title weights (keywords in title count extra)
    positive_weighted += title_positive * 0.5
    negative_weighted += title_negative * 0.5
    
    # Calculate sentiment score (-1 to 1)
    total = positive_weighted + negative_weighted
    if total == 0:
        score = 0  # Neutral if no keywords found
    else:
        score = (positive_weighted - negative_weighted) / total
    
    # Determine sentiment label with more granular categories
    if score > 0.6:
        label = "Very Positive" if not is_persian else "بسیار مثبت"
        display_label = "Very Positive"
    elif score > 0.2:
        label = "Positive" if not is_persian else "مثبت"
        display_label = "Positive"
    elif score < -0.6:
        label = "Very Negative" if not is_persian else "بسیار منفی"
        display_label = "Very Negative"
    elif score < -0.2:
        label = "Negative" if not is_persian else "منفی"
        display_label = "Negative"
    else:
        label = "Neutral" if not is_persian else "خنثی"
        display_label = "Neutral"
    
    # Additional info for debugging and UI display
    keyword_details = {
        'positive': [match['keyword'] for match in positive_matches[:5]],  # Return top 5 matches
        'negative': [match['keyword'] for match in negative_matches[:5]]   # Return top 5 matches
    }
        
    return {
        'score': score,
        'label': display_label,
        'persian_label': label if is_persian else None,
        'is_persian': is_persian,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'keyword_details': keyword_details,
        'strength': abs(score)  # How strong is the sentiment (0-1)
    }
