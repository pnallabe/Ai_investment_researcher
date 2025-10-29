"""
Data Ingestion Module

This module provides comprehensive data ingestion capabilities for the
AI Investment Research Bot, including:

- SEC EDGAR filings and financial statements
- Yahoo Finance real-time and historical data
- Data processing and transformation pipeline
- Caching and optimization features

Usage:
    from data_ingestion import DataProcessor, SECEdgarFetcher, YahooFinanceFetcher
    
    # Initialize the main processor
    processor = DataProcessor()
    
    # Get comprehensive company data
    company_data = processor.get_comprehensive_company_data('AAPL')
    
    # Process portfolio data
    portfolio = {'AAPL': 10, 'MSFT': 5}
    portfolio_data = processor.get_portfolio_data(portfolio)
"""

from .sec_edgar_fetcher import SECEdgarFetcher
from .yahoo_finance_fetcher import YahooFinanceFetcher
from .data_processor import DataProcessor

__all__ = [
    'SECEdgarFetcher',
    'YahooFinanceFetcher', 
    'DataProcessor'
]

__version__ = "1.0.0"