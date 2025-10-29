"""
Yahoo Finance Data Ingestion Module

This module provides functions to fetch real-time stock prices, historical data,
company information, and financial metrics from Yahoo Finance using the yfinance library.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceFetcher:
    """
    A class to fetch financial data from Yahoo Finance
    """
    
    def __init__(self):
        """
        Initialize the Yahoo Finance fetcher
        """
        self.session = None  # yfinance handles sessions internally
        
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive stock information for a ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing stock information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Clean and structure the data
            cleaned_info = {
                'symbol': info.get('symbol', ticker),
                'company_name': info.get('longName', info.get('shortName', '')),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'previous_close': info.get('previousClose', 0),
                'day_high': info.get('dayHigh', 0),
                'day_low': info.get('dayLow', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'volume': info.get('volume', 0),
                'average_volume': info.get('averageVolume', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'eps': info.get('trailingEps', 0),
                'revenue': info.get('totalRevenue', 0),
                'gross_profit': info.get('grossProfits', 0),
                'net_income': info.get('netIncomeToCommon', 0),
                'total_cash': info.get('totalCash', 0),
                'total_debt': info.get('totalDebt', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'return_on_assets': info.get('returnOnAssets', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'profit_margin': info.get('profitMargins', 0),
                'recommendation': info.get('recommendationKey', ''),
                'target_price': info.get('targetMeanPrice', 0),
                'business_summary': info.get('businessSummary', ''),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info(f"Retrieved stock info for {ticker}")
            return cleaned_info
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {e}")
            return {}
    
    def get_historical_data(self, ticker: str, period: str = "1y", 
                           interval: str = "1d") -> pd.DataFrame:
        """
        Get historical price data
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with historical price data
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No historical data found for {ticker}")
                return pd.DataFrame()
            
            # Reset index to make Date a column
            hist = hist.reset_index()
            
            # Calculate additional metrics
            hist['daily_return'] = hist['Close'].pct_change()
            hist['volatility'] = hist['daily_return'].rolling(window=20).std()
            hist['sma_20'] = hist['Close'].rolling(window=20).mean()
            hist['sma_50'] = hist['Close'].rolling(window=50).mean()
            hist['rsi'] = self._calculate_rsi(hist['Close'])
            
            logger.info(f"Retrieved {len(hist)} days of historical data for {ticker}")
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_financial_statements(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Get financial statements (income statement, balance sheet, cash flow)
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing financial statements as DataFrames
        """
        try:
            stock = yf.Ticker(ticker)
            
            statements = {
                'income_statement': stock.financials,
                'balance_sheet': stock.balance_sheet,
                'cash_flow': stock.cashflow,
                'quarterly_income': stock.quarterly_financials,
                'quarterly_balance_sheet': stock.quarterly_balance_sheet,
                'quarterly_cash_flow': stock.quarterly_cashflow
            }
            
            # Clean empty DataFrames
            statements = {k: v for k, v in statements.items() if not v.empty}
            
            logger.info(f"Retrieved financial statements for {ticker}")
            return statements
            
        except Exception as e:
            logger.error(f"Error fetching financial statements for {ticker}: {e}")
            return {}
    
    def get_real_time_price(self, ticker: str) -> Dict[str, Any]:
        """
        Get real-time price and trading data
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with real-time trading data
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get current day data
            today_data = stock.history(period="1d", interval="1m")
            
            if today_data.empty:
                # Fallback to info data
                info = stock.info
                return {
                    'symbol': ticker,
                    'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                    'change': info.get('regularMarketChange', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', 0),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get latest data point
            latest = today_data.iloc[-1]
            previous_close = stock.info.get('previousClose', latest['Close'])
            
            change = latest['Close'] - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            return {
                'symbol': ticker,
                'price': float(latest['Close']),
                'change': float(change),
                'change_percent': float(change_percent),
                'volume': int(latest['Volume']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'timestamp': latest.name.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching real-time price for {ticker}: {e}")
            return {}
    
    def get_multiple_quotes(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        Get quotes for multiple tickers efficiently
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary mapping tickers to their quote data
        """
        quotes = {}
        
        try:
            # Download data for all tickers at once
            data = yf.download(tickers, period="1d", interval="1d", group_by='ticker')
            
            for ticker in tickers:
                try:
                    if len(tickers) == 1:
                        ticker_data = data
                    else:
                        ticker_data = data[ticker]
                    
                    if not ticker_data.empty:
                        latest = ticker_data.iloc[-1]
                        quotes[ticker] = {
                            'symbol': ticker,
                            'price': float(latest['Close']),
                            'volume': int(latest['Volume']),
                            'high': float(latest['High']),
                            'low': float(latest['Low']),
                            'timestamp': latest.name.isoformat()
                        }
                    
                except Exception as e:
                    logger.error(f"Error processing quote for {ticker}: {e}")
                    quotes[ticker] = {}
            
            logger.info(f"Retrieved quotes for {len(quotes)} tickers")
            return quotes
            
        except Exception as e:
            logger.error(f"Error fetching multiple quotes: {e}")
            return {}
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get market summary data for major indices
        
        Returns:
            Dictionary with market index data
        """
        indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'Russell 2000': '^RUT',
            'VIX': '^VIX'
        }
        
        summary = {}
        
        for name, symbol in indices.items():
            try:
                quote = self.get_real_time_price(symbol)
                summary[name] = quote
            except Exception as e:
                logger.error(f"Error fetching {name} data: {e}")
                summary[name] = {}
        
        return summary
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of closing prices
            window: Period for RSI calculation
            
        Returns:
            Series with RSI values
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_portfolio_metrics(self, portfolio: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate portfolio performance metrics
        
        Args:
            portfolio: Dictionary mapping tickers to quantities/weights
            
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            tickers = list(portfolio.keys())
            quotes = self.get_multiple_quotes(tickers)
            
            total_value = 0
            portfolio_return = 0
            
            for ticker, quantity in portfolio.items():
                if ticker in quotes and quotes[ticker]:
                    price = quotes[ticker]['price']
                    value = price * quantity
                    total_value += value
            
            # Get historical data for portfolio analysis
            portfolio_data = []
            for ticker in tickers:
                hist = self.get_historical_data(ticker, period="1y")
                if not hist.empty:
                    hist['ticker'] = ticker
                    hist['weight'] = portfolio[ticker] / sum(portfolio.values())
                    portfolio_data.append(hist)
            
            if portfolio_data:
                # Combine data and calculate portfolio returns
                combined_data = pd.concat(portfolio_data)
                # Additional portfolio calculations can be added here
                
            return {
                'total_value': total_value,
                'positions': len(portfolio),
                'last_updated': datetime.now().isoformat(),
                'quotes': quotes
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {}

def test_yahoo_finance():
    """
    Test function to demonstrate Yahoo Finance data fetching
    """
    fetcher = YahooFinanceFetcher()
    
    print("Testing Yahoo Finance data fetching...")
    
    # Test stock info
    ticker = 'AAPL'
    print(f"\nGetting stock info for {ticker}...")
    info = fetcher.get_stock_info(ticker)
    print(f"Company: {info.get('company_name', 'N/A')}")
    print(f"Current Price: ${info.get('current_price', 0):.2f}")
    print(f"Market Cap: ${info.get('market_cap', 0):,}")
    
    # Test real-time price
    print(f"\nGetting real-time price for {ticker}...")
    price_data = fetcher.get_real_time_price(ticker)
    print(f"Price: ${price_data.get('price', 0):.2f}")
    print(f"Change: {price_data.get('change_percent', 0):.2f}%")
    
    # Test historical data
    print(f"\nGetting historical data for {ticker}...")
    hist = fetcher.get_historical_data(ticker, period="1mo")
    print(f"Retrieved {len(hist)} days of data")
    if not hist.empty:
        print(f"Latest close: ${hist['Close'].iloc[-1]:.2f}")
    
    # Test market summary
    print("\nGetting market summary...")
    summary = fetcher.get_market_summary()
    for index, data in summary.items():
        if data:
            print(f"{index}: ${data.get('price', 0):.2f} ({data.get('change_percent', 0):.2f}%)")

if __name__ == "__main__":
    test_yahoo_finance()