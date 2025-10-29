"""
News data ingester for financial news and sentiment analysis
"""
import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
from urllib.parse import urljoin, urlparse
import feedparser
from bs4 import BeautifulSoup

from .base import BaseIngester, IngestionResult, RateLimiter, RetryMixin
from config.settings import settings

logger = logging.getLogger(__name__)


class NewsIngester(BaseIngester, RetryMixin):
    """Ingester for financial news articles"""
    
    # RSS feeds for financial news
    NEWS_FEEDS = {
        'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
        'reuters_markets': 'https://feeds.reuters.com/reuters/marketsNews',
        'bloomberg_markets': 'https://feeds.bloomberg.com/markets/news.rss',
        'cnbc_markets': 'https://www.cnbc.com/id/10000664/device/rss/rss.html',
        'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
        'seeking_alpha': 'https://seekingalpha.com/feed.xml'
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rate_limiter = RateLimiter(calls_per_second=1.0)
        self.news_api_key = settings.NEWS_API_KEY
    
    async def fetch_rss_feed(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from RSS feed"""
        try:
            await self.rate_limiter.wait()
            
            # Use feedparser to parse RSS
            feed = feedparser.parse(feed_url)
            
            articles = []
            
            for entry in feed.entries:
                # Extract publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                # Extract content
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                # Clean HTML from content
                content = self.clean_html(content)
                
                article = {
                    'title': getattr(entry, 'title', ''),
                    'url': getattr(entry, 'link', ''),
                    'content': content,
                    'published_at': pub_date,
                    'source': feed_name,
                    'author': getattr(entry, 'author', ''),
                    'tags': [tag.term for tag in getattr(entry, 'tags', [])]
                }
                
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {feed_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {feed_name}: {str(e)}")
            return []
    
    async def fetch_news_api_data(self, query: str = "stock market", 
                                 from_date: date = None, to_date: date = None) -> List[Dict[str, Any]]:
        """Fetch news from News API"""
        if not self.news_api_key:
            logger.warning("News API key not configured")
            return []
        
        if not from_date:
            from_date = date.today() - timedelta(days=7)
        
        if not to_date:
            to_date = date.today()
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'from': from_date.isoformat(),
            'to': to_date.isoformat(),
            'domains': 'reuters.com,bloomberg.com,cnbc.com,marketwatch.com,yahoo.com',
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': self.news_api_key,
            'pageSize': 100
        }
        
        await self.rate_limiter.wait()
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"News API error: {response.status}")
                    return []
                
                data = await response.json()
                
                if data.get('status') != 'ok':
                    logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                    return []
                
                articles = []
                
                for article_data in data.get('articles', []):
                    # Parse publication date
                    pub_date = None
                    if article_data.get('publishedAt'):
                        pub_date = datetime.fromisoformat(
                            article_data['publishedAt'].replace('Z', '+00:00')
                        )
                    
                    article = {
                        'title': article_data.get('title', ''),
                        'url': article_data.get('url', ''),
                        'content': article_data.get('content', '') or article_data.get('description', ''),
                        'published_at': pub_date,
                        'source': article_data.get('source', {}).get('name', ''),
                        'author': article_data.get('author', ''),
                        'url_to_image': article_data.get('urlToImage', ''),
                        'tags': []
                    }
                    
                    articles.append(article)
                
                logger.info(f"Fetched {len(articles)} articles from News API")
                return articles
                
        except Exception as e:
            logger.error(f"Error fetching News API data: {str(e)}")
            return []
    
    def clean_html(self, html_content: str) -> str:
        """Clean HTML tags from content"""
        if not html_content:
            return ""
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_company_mentions(self, text: str, company_names: List[str] = None) -> List[str]:
        """Extract company mentions from text"""
        if not company_names:
            # Default list of major companies
            company_names = [
                'Apple', 'Microsoft', 'Amazon', 'Google', 'Alphabet', 'Meta', 'Tesla',
                'NVIDIA', 'Berkshire Hathaway', 'JPMorgan', 'Johnson & Johnson',
                'Visa', 'Procter & Gamble', 'Mastercard', 'UnitedHealth'
            ]
        
        mentions = []
        text_lower = text.lower()
        
        for company in company_names:
            if company.lower() in text_lower:
                mentions.append(company)
        
        return mentions
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Simple sentiment analysis (placeholder - use proper sentiment analysis in production)"""
        # This is a very basic implementation
        # In production, use libraries like VADER, TextBlob, or transformer models
        
        positive_words = [
            'growth', 'profit', 'increase', 'gain', 'rise', 'bullish', 'optimistic',
            'positive', 'strong', 'beat', 'exceed', 'outperform', 'success'
        ]
        
        negative_words = [
            'loss', 'decline', 'decrease', 'fall', 'bearish', 'pessimistic',
            'negative', 'weak', 'miss', 'underperform', 'fail', 'drop', 'crash'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        
        # Normalize to [-1, 1] range
        return max(-1.0, min(1.0, sentiment * 10))
    
    async def fetch_data(self, sources: List[str] = None, 
                        company_filter: List[str] = None,
                        from_date: date = None, to_date: date = None) -> List[Dict[str, Any]]:
        """Fetch news data from various sources"""
        if not sources:
            sources = list(self.NEWS_FEEDS.keys()) + ['news_api']
        
        all_articles = []
        
        # Fetch from RSS feeds
        for source in sources:
            if source in self.NEWS_FEEDS:
                articles = await self.retry_on_failure(
                    self.fetch_rss_feed,
                    max_retries=2,
                    delay=1.0,
                    feed_url=self.NEWS_FEEDS[source],
                    feed_name=source
                )
                all_articles.extend(articles)
        
        # Fetch from News API
        if 'news_api' in sources:
            if company_filter:
                query = ' OR '.join(company_filter)
            else:
                query = "stock market finance investment"
            
            news_api_articles = await self.retry_on_failure(
                self.fetch_news_api_data,
                max_retries=2,
                delay=1.0,
                query=query,
                from_date=from_date,
                to_date=to_date
            )
            all_articles.extend(news_api_articles)
        
        return all_articles
    
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform news data"""
        transformed = []
        
        for article in raw_data:
            # Skip articles without content
            if not article.get('content') or not article.get('title'):
                continue
            
            # Extract company mentions
            full_text = f"{article.get('title', '')} {article.get('content', '')}"
            company_mentions = self.extract_company_mentions(full_text)
            
            # Calculate sentiment
            sentiment_score = self.calculate_sentiment_score(full_text)
            
            # Determine sentiment label
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            transformed_article = {
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': article.get('content', ''),
                'published_at': article.get('published_at'),
                'source': article.get('source', ''),
                'author': article.get('author', ''),
                'company_mentions': company_mentions,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'word_count': len(full_text.split()),
                'tags': article.get('tags', []),
                'ingested_at': datetime.utcnow()
            }
            
            transformed.append(transformed_article)
        
        return transformed
    
    async def load_data(self, transformed_data: List[Dict[str, Any]]) -> IngestionResult:
        """Load news data into database"""
        try:
            # TODO: Implement actual database loading
            # - Insert into news_articles table
            # - Create company-article relationships
            # - Store for vector embedding
            
            sources = set(article['source'] for article in transformed_data)
            sentiment_dist = {}
            for article in transformed_data:
                label = article['sentiment_label']
                sentiment_dist[label] = sentiment_dist.get(label, 0) + 1
            
            return IngestionResult(
                success=True,
                records_processed=len(transformed_data),
                errors=[],
                metadata={
                    'source': 'News Data',
                    'news_sources': list(sources),
                    'sentiment_distribution': sentiment_dist,
                    'date_range': {
                        'start': min(
                            article['published_at'] for article in transformed_data 
                            if article['published_at']
                        ).isoformat() if any(article['published_at'] for article in transformed_data) else None,
                        'end': max(
                            article['published_at'] for article in transformed_data 
                            if article['published_at']
                        ).isoformat() if any(article['published_at'] for article in transformed_data) else None
                    }
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to load news data: {str(e)}")
            return IngestionResult(
                success=False,
                records_processed=0,
                errors=[str(e)],
                metadata={},
                timestamp=datetime.utcnow()
            )