"""
Financial market data ingester (prices, volumes, etc.)
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
import yfinance as yf
import pandas as pd

from .base import BaseIngester, IngestionResult, RateLimiter, RetryMixin
from config.settings import settings

logger = logging.getLogger(__name__)


class MarketDataIngester(BaseIngester, RetryMixin):
    """Ingester for market price data"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rate_limiter = RateLimiter(calls_per_second=2.0)  # Conservative rate limit
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
    
    async def fetch_yahoo_finance_data(self, tickers: List[str], 
                                     start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Fetch price data from Yahoo Finance"""
        all_data = []
        
        for ticker in tickers:
            try:
                await self.rate_limiter.wait()
                
                # Download data
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty:
                    logger.warning(f"No data found for ticker {ticker}")
                    continue
                
                # Convert to records
                hist.reset_index(inplace=True)
                
                for _, row in hist.iterrows():
                    record = {
                        'ticker': ticker,
                        'date': row['Date'].date(),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume']),
                        'adj_close': float(row['Close'])  # Yahoo Finance adjusted close
                    }
                    all_data.append(record)
                
                logger.info(f"Fetched {len(hist)} records for {ticker}")
                
            except Exception as e:
                logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
        
        return all_data
    
    async def fetch_alpha_vantage_data(self, ticker: str, 
                                     function: str = "TIME_SERIES_DAILY") -> List[Dict[str, Any]]:
        """Fetch data from Alpha Vantage API"""
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured")
            return []
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': function,
            'symbol': ticker,
            'apikey': self.alpha_vantage_key,
            'outputsize': 'full'
        }
        
        await self.rate_limiter.wait()
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return []
                
                data = await response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    logger.error(f"Alpha Vantage error: {data['Error Message']}")
                    return []
                
                if 'Note' in data:
                    logger.warning(f"Alpha Vantage note: {data['Note']}")
                    return []
                
                # Parse time series data
                time_series_key = None
                for key in data.keys():
                    if 'Time Series' in key:
                        time_series_key = key
                        break
                
                if not time_series_key:
                    logger.error("No time series data found in Alpha Vantage response")
                    return []
                
                time_series = data[time_series_key]
                records = []
                
                for date_str, values in time_series.items():
                    record = {
                        'ticker': ticker,
                        'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume']),
                        'adj_close': float(values['4. close'])
                    }
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {ticker}: {str(e)}")
            return []
    
    async def fetch_company_info(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch company information for tickers"""
        company_info = {}
        
        for ticker in tickers:
            try:
                await self.rate_limiter.wait()
                
                stock = yf.Ticker(ticker)
                info = stock.info
                
                company_info[ticker] = {
                    'company_name': info.get('longName', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap'),
                    'enterprise_value': info.get('enterpriseValue'),
                    'employees': info.get('fullTimeEmployees'),
                    'description': info.get('longBusinessSummary', ''),
                    'website': info.get('website', ''),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', 'USD')
                }
                
            except Exception as e:
                logger.error(f"Failed to fetch company info for {ticker}: {str(e)}")
                company_info[ticker] = {}
        
        return company_info
    
    async def fetch_data(self, tickers: List[str] = None, 
                        start_date: date = None, end_date: date = None,
                        data_source: str = "yahoo") -> List[Dict[str, Any]]:
        """Fetch market data"""
        if not tickers:
            # Default tickers for demo
            tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        
        if not start_date:
            start_date = date.today() - timedelta(days=365)  # 1 year ago
        
        if not end_date:
            end_date = date.today()
        
        logger.info(f"Fetching market data for {len(tickers)} tickers from {start_date} to {end_date}")
        
        if data_source == "yahoo":
            return await self.fetch_yahoo_finance_data(tickers, start_date, end_date)
        elif data_source == "alpha_vantage":
            all_data = []
            for ticker in tickers:
                data = await self.fetch_alpha_vantage_data(ticker)
                # Filter by date range
                filtered_data = [
                    record for record in data
                    if start_date <= record['date'] <= end_date
                ]
                all_data.extend(filtered_data)
            return all_data
        else:
            raise ValueError(f"Unsupported data source: {data_source}")
    
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform market data"""
        # Get unique tickers to fetch company info
        tickers = list(set(record['ticker'] for record in raw_data))
        company_info = await self.fetch_company_info(tickers)
        
        transformed = []
        
        for record in raw_data:
            ticker = record['ticker']
            info = company_info.get(ticker, {})
            
            # Calculate additional metrics
            try:
                daily_return = ((record['close'] - record['open']) / record['open']) * 100 if record['open'] > 0 else 0
                price_range = record['high'] - record['low']
                price_range_pct = (price_range / record['open']) * 100 if record['open'] > 0 else 0
            except (ZeroDivisionError, TypeError):
                daily_return = 0
                price_range = 0
                price_range_pct = 0
            
            transformed_record = {
                **record,
                'company_name': info.get('company_name', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('market_cap'),
                'daily_return': daily_return,
                'price_range': price_range,
                'price_range_pct': price_range_pct,
                'ingested_at': datetime.utcnow()
            }
            
            transformed.append(transformed_record)
        
        return transformed
    
    async def load_data(self, transformed_data: List[Dict[str, Any]]) -> IngestionResult:
        """Load market data into database"""
        try:
            # TODO: Implement actual database loading
            # - Insert into daily_prices table
            # - Update/insert companies table
            # - Handle duplicates (upsert based on ticker + date)
            
            # Group by ticker for reporting
            tickers = set(record['ticker'] for record in transformed_data)
            
            return IngestionResult(
                success=True,
                records_processed=len(transformed_data),
                errors=[],
                metadata={
                    'source': 'Market Data',
                    'tickers': list(tickers),
                    'date_range': {
                        'start': min(record['date'] for record in transformed_data).isoformat(),
                        'end': max(record['date'] for record in transformed_data).isoformat()
                    }
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to load market data: {str(e)}")
            return IngestionResult(
                success=False,
                records_processed=0,
                errors=[str(e)],
                metadata={},
                timestamp=datetime.utcnow()
            )