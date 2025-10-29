"""
Data Processing Pipeline

This module combines and processes data from SEC EDGAR and Yahoo Finance
to create unified datasets for the dashboard and API endpoints.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from pathlib import Path

from sec_edgar_fetcher import SECEdgarFetcher
from yahoo_finance_fetcher import YahooFinanceFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Main data processing pipeline that combines SEC and Yahoo Finance data
    """
    
    def __init__(self, cache_dir: str = "data_cache"):
        """
        Initialize the data processor
        
        Args:
            cache_dir: Directory to store cached data
        """
        self.sec_fetcher = SECEdgarFetcher()
        self.yahoo_fetcher = YahooFinanceFetcher()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_comprehensive_company_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive company data combining SEC and Yahoo Finance sources
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with comprehensive company data
        """
        try:
            logger.info(f"Fetching comprehensive data for {ticker}")
            
            # Get Yahoo Finance data (faster, real-time)
            yahoo_data = self.yahoo_fetcher.get_stock_info(ticker)
            real_time_price = self.yahoo_fetcher.get_real_time_price(ticker)
            
            # Get SEC data (official filings)
            sec_company = self.sec_fetcher.search_company_by_ticker(ticker)
            sec_metrics = {}
            if sec_company:
                sec_metrics = self.sec_fetcher.get_financial_metrics(sec_company['cik'])
            
            # Combine data sources
            combined_data = {
                'basic_info': {
                    'ticker': ticker.upper(),
                    'company_name': yahoo_data.get('company_name', ''),
                    'sector': yahoo_data.get('sector', ''),
                    'industry': yahoo_data.get('industry', ''),
                    'business_summary': yahoo_data.get('business_summary', ''),
                    'employees': yahoo_data.get('employees', 0),
                    'website': yahoo_data.get('website', ''),
                    'cik': sec_company.get('cik', '') if sec_company else ''
                },
                'market_data': {
                    'current_price': real_time_price.get('price', yahoo_data.get('current_price', 0)),
                    'change': real_time_price.get('change', 0),
                    'change_percent': real_time_price.get('change_percent', 0),
                    'market_cap': yahoo_data.get('market_cap', 0),
                    'volume': real_time_price.get('volume', yahoo_data.get('volume', 0)),
                    'day_high': real_time_price.get('high', yahoo_data.get('day_high', 0)),
                    'day_low': real_time_price.get('low', yahoo_data.get('day_low', 0)),
                    'fifty_two_week_high': yahoo_data.get('fifty_two_week_high', 0),
                    'fifty_two_week_low': yahoo_data.get('fifty_two_week_low', 0),
                    'beta': yahoo_data.get('beta', 0)
                },
                'valuation_metrics': {
                    'pe_ratio': yahoo_data.get('pe_ratio', 0),
                    'forward_pe': yahoo_data.get('forward_pe', 0),
                    'price_to_book': yahoo_data.get('price_to_book', 0),
                    'dividend_yield': yahoo_data.get('dividend_yield', 0),
                    'eps': yahoo_data.get('eps', 0),
                    'target_price': yahoo_data.get('target_price', 0),
                    'recommendation': yahoo_data.get('recommendation', '')
                },
                'financial_metrics': {
                    # Yahoo Finance data (more recent)
                    'revenue_yf': yahoo_data.get('revenue', 0),
                    'gross_profit': yahoo_data.get('gross_profit', 0),
                    'net_income_yf': yahoo_data.get('net_income', 0),
                    'total_cash': yahoo_data.get('total_cash', 0),
                    'total_debt': yahoo_data.get('total_debt', 0),
                    'return_on_equity': yahoo_data.get('return_on_equity', 0),
                    'return_on_assets': yahoo_data.get('return_on_assets', 0),
                    'operating_margin': yahoo_data.get('operating_margin', 0),
                    'profit_margin': yahoo_data.get('profit_margin', 0),
                    
                    # SEC data (official filings)
                    'revenue_sec': sec_metrics.get('revenue', {}).get('value', 0),
                    'net_income_sec': sec_metrics.get('net_income', {}).get('value', 0),
                    'total_assets_sec': sec_metrics.get('total_assets', {}).get('value', 0),
                    'stockholders_equity_sec': sec_metrics.get('stockholders_equity', {}).get('value', 0)
                },
                'data_sources': {
                    'yahoo_finance': bool(yahoo_data),
                    'sec_edgar': bool(sec_metrics),
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            # Cache the data
            self._cache_data(ticker, combined_data)
            
            logger.info(f"Successfully processed comprehensive data for {ticker}")
            return combined_data
            
        except Exception as e:
            logger.error(f"Error processing comprehensive data for {ticker}: {e}")
            return {}
    
    def get_portfolio_data(self, portfolio: Dict[str, float]) -> Dict[str, Any]:
        """
        Process portfolio data with comprehensive metrics
        
        Args:
            portfolio: Dictionary mapping tickers to quantities
            
        Returns:
            Dictionary with portfolio analysis
        """
        try:
            logger.info(f"Processing portfolio with {len(portfolio)} positions")
            
            portfolio_data = {
                'positions': {},
                'summary': {
                    'total_value': 0,
                    'total_gain_loss': 0,
                    'total_gain_loss_percent': 0,
                    'positions_count': len(portfolio),
                    'sectors': {},
                    'top_performers': [],
                    'worst_performers': []
                },
                'risk_metrics': {},
                'last_updated': datetime.now().isoformat()
            }
            
            # Process each position
            position_performances = []
            
            for ticker, quantity in portfolio.items():
                try:
                    # Get comprehensive data for each stock
                    stock_data = self.get_comprehensive_company_data(ticker)
                    
                    if stock_data:
                        current_price = stock_data['market_data']['current_price']
                        change_percent = stock_data['market_data']['change_percent']
                        sector = stock_data['basic_info']['sector']
                        
                        position_value = current_price * quantity
                        portfolio_data['summary']['total_value'] += position_value
                        
                        # Track sectors
                        if sector:
                            portfolio_data['summary']['sectors'][sector] = \
                                portfolio_data['summary']['sectors'].get(sector, 0) + position_value
                        
                        # Store position data
                        portfolio_data['positions'][ticker] = {
                            'quantity': quantity,
                            'current_price': current_price,
                            'position_value': position_value,
                            'change_percent': change_percent,
                            'company_name': stock_data['basic_info']['company_name'],
                            'sector': sector
                        }
                        
                        # Track performance for rankings
                        position_performances.append({
                            'ticker': ticker,
                            'change_percent': change_percent,
                            'position_value': position_value
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing position {ticker}: {e}")
            
            # Calculate summary metrics
            if position_performances:
                # Sort by performance
                position_performances.sort(key=lambda x: x['change_percent'], reverse=True)
                
                # Top and worst performers
                portfolio_data['summary']['top_performers'] = position_performances[:3]
                portfolio_data['summary']['worst_performers'] = position_performances[-3:]
                
                # Calculate weighted average performance
                total_value = portfolio_data['summary']['total_value']
                if total_value > 0:
                    weighted_return = sum(
                        (pos['change_percent'] * pos['position_value']) 
                        for pos in position_performances
                    ) / total_value
                    portfolio_data['summary']['total_gain_loss_percent'] = weighted_return
            
            logger.info(f"Portfolio processing complete. Total value: ${portfolio_data['summary']['total_value']:,.2f}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error processing portfolio data: {e}")
            return {}
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive market overview data
        
        Returns:
            Dictionary with market overview data
        """
        try:
            logger.info("Fetching market overview data")
            
            # Get market indices
            market_summary = self.yahoo_fetcher.get_market_summary()
            
            # Get sector performance (using sector ETFs as proxies)
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financials': 'XLF',
                'Energy': 'XLE',
                'Consumer Discretionary': 'XLY',
                'Industrials': 'XLI',
                'Consumer Staples': 'XLP',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE',
                'Materials': 'XLB',
                'Communication Services': 'XLC'
            }
            
            sector_performance = {}
            for sector, etf in sector_etfs.items():
                try:
                    price_data = self.yahoo_fetcher.get_real_time_price(etf)
                    if price_data:
                        sector_performance[sector] = {
                            'change_percent': price_data.get('change_percent', 0),
                            'price': price_data.get('price', 0)
                        }
                except Exception as e:
                    logger.error(f"Error fetching sector data for {sector}: {e}")
            
            # Get some popular stocks for trending
            trending_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V']
            trending_quotes = self.yahoo_fetcher.get_multiple_quotes(trending_tickers)
            
            market_overview = {
                'indices': market_summary,
                'sectors': sector_performance,
                'trending_stocks': trending_quotes,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info("Market overview data retrieved successfully")
            return market_overview
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {}
    
    def get_historical_analysis(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """
        Get comprehensive historical analysis for a stock
        
        Args:
            ticker: Stock ticker symbol
            period: Analysis period
            
        Returns:
            Dictionary with historical analysis
        """
        try:
            logger.info(f"Performing historical analysis for {ticker}")
            
            # Get historical data
            hist_data = self.yahoo_fetcher.get_historical_data(ticker, period=period)
            
            if hist_data.empty:
                return {}
            
            # Calculate analysis metrics
            analysis = {
                'ticker': ticker.upper(),
                'period': period,
                'data_points': len(hist_data),
                'price_analysis': {
                    'current_price': float(hist_data['Close'].iloc[-1]),
                    'period_start_price': float(hist_data['Close'].iloc[0]),
                    'period_high': float(hist_data['High'].max()),
                    'period_low': float(hist_data['Low'].min()),
                    'total_return': float(((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[0]) - 1) * 100),
                    'volatility': float(hist_data['daily_return'].std() * np.sqrt(252) * 100),  # Annualized volatility
                    'average_volume': int(hist_data['Volume'].mean())
                },
                'technical_indicators': {
                    'sma_20': float(hist_data['sma_20'].iloc[-1]) if not pd.isna(hist_data['sma_20'].iloc[-1]) else 0,
                    'sma_50': float(hist_data['sma_50'].iloc[-1]) if not pd.isna(hist_data['sma_50'].iloc[-1]) else 0,
                    'rsi': float(hist_data['rsi'].iloc[-1]) if not pd.isna(hist_data['rsi'].iloc[-1]) else 0
                },
                'trend_analysis': {
                    'trend_direction': 'up' if hist_data['Close'].iloc[-1] > hist_data['Close'].iloc[0] else 'down',
                    'above_sma_20': hist_data['Close'].iloc[-1] > hist_data['sma_20'].iloc[-1] if not pd.isna(hist_data['sma_20'].iloc[-1]) else False,
                    'above_sma_50': hist_data['Close'].iloc[-1] > hist_data['sma_50'].iloc[-1] if not pd.isna(hist_data['sma_50'].iloc[-1]) else False
                }
            }
            
            logger.info(f"Historical analysis complete for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error performing historical analysis for {ticker}: {e}")
            return {}
    
    def _cache_data(self, key: str, data: Dict[str, Any], expiry_hours: int = 1):
        """
        Cache data to disk with expiry
        
        Args:
            key: Cache key
            data: Data to cache
            expiry_hours: Hours until cache expires
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            cache_data = {
                'data': data,
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=expiry_hours)).isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error caching data for {key}: {e}")
    
    def _get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data if not expired
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if expired/not found
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            if not cache_file.exists():
                return None
                
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            if datetime.now() > expires_at:
                return None
                
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cached data for {key}: {e}")
            return None

def test_data_processor():
    """
    Test function to demonstrate the data processing pipeline
    """
    processor = DataProcessor()
    
    print("Testing Data Processing Pipeline...")
    
    # Test comprehensive company data
    print("\n1. Testing comprehensive company data...")
    ticker = 'AAPL'
    company_data = processor.get_comprehensive_company_data(ticker)
    if company_data:
        print(f"Company: {company_data['basic_info']['company_name']}")
        print(f"Current Price: ${company_data['market_data']['current_price']:.2f}")
        print(f"Market Cap: ${company_data['market_data']['market_cap']:,}")
        print(f"SEC Data Available: {company_data['data_sources']['sec_edgar']}")
    
    # Test portfolio data
    print("\n2. Testing portfolio data...")
    sample_portfolio = {
        'AAPL': 10,
        'MSFT': 5,
        'GOOGL': 3
    }
    portfolio_data = processor.get_portfolio_data(sample_portfolio)
    if portfolio_data:
        print(f"Portfolio Value: ${portfolio_data['summary']['total_value']:,.2f}")
        print(f"Positions: {portfolio_data['summary']['positions_count']}")
    
    # Test market overview
    print("\n3. Testing market overview...")
    market_data = processor.get_market_overview()
    if market_data:
        print("Market indices retrieved:", len(market_data.get('indices', {})))
        print("Sector data retrieved:", len(market_data.get('sectors', {})))
    
    # Test historical analysis
    print("\n4. Testing historical analysis...")
    analysis = processor.get_historical_analysis(ticker, period="6mo")
    if analysis:
        print(f"Total Return: {analysis['price_analysis']['total_return']:.2f}%")
        print(f"Volatility: {analysis['price_analysis']['volatility']:.2f}%")

if __name__ == "__main__":
    test_data_processor()