"""
Fundamental Analysis Engine for Stock Market Analysis

This module provides comprehensive fundamental analysis using SEC EDGAR filings and financial data including:
- Financial Ratios (P/E, P/B, P/S, Debt-to-Equity)
- Profitability Metrics (ROE, ROA, Profit Margins)
- Growth Analysis (Revenue Growth, Earnings Growth)
- Financial Health Indicators
- Valuation Analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import yfinance as yf
from datetime import datetime, timedelta
import requests
import json

class FundamentalAnalyzer:
    """Main class for performing fundamental analysis on stocks"""
    
    def __init__(self, symbol: str):
        """
        Initialize the Fundamental Analyzer
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
        """
        self.symbol = symbol.upper()
        self.ticker_data = None
        self.financial_data = {}
        self.ratios = {}
        self._fetch_data()
    
    def _fetch_data(self) -> None:
        """Fetch financial data from multiple sources"""
        try:
            # Get data from Yahoo Finance
            ticker = yf.Ticker(self.symbol)
            self.ticker_data = ticker
            
            # Get financial statements
            self.financial_data = {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
                'info': ticker.info
            }
            
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            self.financial_data = {}
    
    def get_basic_info(self) -> Dict[str, Any]:
        """
        Get basic company information
        
        Returns:
            Dictionary with basic company data
        """
        if not self.financial_data.get('info'):
            return {}
        
        info = self.financial_data['info']
        
        return {
            'company_name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'enterprise_value': info.get('enterpriseValue', 0),
            'employees': info.get('fullTimeEmployees', 0),
            'website': info.get('website', 'N/A'),
            'business_summary': info.get('longBusinessSummary', 'N/A')[:500] + '...' if info.get('longBusinessSummary') else 'N/A'
        }
    
    def calculate_valuation_ratios(self) -> Dict[str, float]:
        """
        Calculate key valuation ratios
        
        Returns:
            Dictionary with valuation ratios
        """
        if not self.financial_data.get('info'):
            return {}
        
        info = self.financial_data['info']
        ratios = {}
        
        # Price-to-Earnings Ratio
        ratios['pe_ratio'] = info.get('trailingPE', None)
        ratios['forward_pe'] = info.get('forwardPE', None)
        
        # Price-to-Book Ratio
        ratios['pb_ratio'] = info.get('priceToBook', None)
        
        # Price-to-Sales Ratio
        ratios['ps_ratio'] = info.get('priceToSalesTrailing12Months', None)
        
        # Enterprise Value ratios
        ratios['ev_revenue'] = info.get('enterpriseToRevenue', None)
        ratios['ev_ebitda'] = info.get('enterpriseToEbitda', None)
        
        # PEG Ratio
        ratios['peg_ratio'] = info.get('pegRatio', None)
        
        self.ratios['valuation'] = ratios
        return ratios
    
    def calculate_profitability_ratios(self) -> Dict[str, float]:
        """
        Calculate profitability ratios
        
        Returns:
            Dictionary with profitability ratios
        """
        if not self.financial_data.get('info'):
            return {}
        
        info = self.financial_data['info']
        ratios = {}
        
        # Return on Equity
        ratios['roe'] = info.get('returnOnEquity', None)
        
        # Return on Assets
        ratios['roa'] = info.get('returnOnAssets', None)
        
        # Profit Margins
        ratios['gross_margin'] = info.get('grossMargins', None)
        ratios['operating_margin'] = info.get('operatingMargins', None)
        ratios['profit_margin'] = info.get('profitMargins', None)
        
        # EBITDA Margin
        if info.get('ebitda') and info.get('totalRevenue'):
            ratios['ebitda_margin'] = info.get('ebitda') / info.get('totalRevenue')
        else:
            ratios['ebitda_margin'] = None
        
        self.ratios['profitability'] = ratios
        return ratios
    
    def calculate_financial_health_ratios(self) -> Dict[str, float]:
        """
        Calculate financial health and leverage ratios
        
        Returns:
            Dictionary with financial health ratios
        """
        ratios = {}
        
        try:
            balance_sheet = self.financial_data.get('balance_sheet')
            info = self.financial_data.get('info', {})
            
            if balance_sheet is not None and not balance_sheet.empty:
                latest_data = balance_sheet.iloc[:, 0]  # Most recent quarter
                
                # Debt-to-Equity Ratio
                total_debt = latest_data.get('Total Debt', 0)
                total_equity = latest_data.get('Stockholders Equity', latest_data.get('Total Stockholder Equity', 0))
                
                if total_equity and total_equity != 0:
                    ratios['debt_to_equity'] = total_debt / total_equity if total_debt else 0
                else:
                    ratios['debt_to_equity'] = None
                
                # Current Ratio
                current_assets = latest_data.get('Current Assets', 0)
                current_liabilities = latest_data.get('Current Liabilities', 0)
                
                if current_liabilities and current_liabilities != 0:
                    ratios['current_ratio'] = current_assets / current_liabilities if current_assets else 0
                else:
                    ratios['current_ratio'] = None
                
                # Quick Ratio
                cash = latest_data.get('Cash And Cash Equivalents', 0)
                short_term_investments = latest_data.get('Short Term Investments', 0)
                receivables = latest_data.get('Accounts Receivable', 0)
                
                quick_assets = cash + short_term_investments + receivables
                if current_liabilities and current_liabilities != 0:
                    ratios['quick_ratio'] = quick_assets / current_liabilities
                else:
                    ratios['quick_ratio'] = None
            
            # From Yahoo Finance info
            ratios['debt_to_equity_yf'] = info.get('debtToEquity', None)
            
        except Exception as e:
            print(f"Error calculating financial health ratios: {e}")
        
        self.ratios['financial_health'] = ratios
        return ratios
    
    def calculate_growth_metrics(self) -> Dict[str, float]:
        """
        Calculate growth metrics
        
        Returns:
            Dictionary with growth metrics
        """
        if not self.financial_data.get('info'):
            return {}
        
        info = self.financial_data['info']
        metrics = {}
        
        # Revenue Growth
        metrics['revenue_growth'] = info.get('revenueGrowth', None)
        
        # Earnings Growth
        metrics['earnings_growth'] = info.get('earningsGrowth', None)
        
        # Quarterly Revenue Growth
        metrics['quarterly_revenue_growth'] = info.get('revenueQuarterlyGrowth', None)
        
        # Quarterly Earnings Growth
        metrics['quarterly_earnings_growth'] = info.get('earningsQuarterlyGrowth', None)
        
        # Book Value Growth (if available)
        try:
            balance_sheet = self.financial_data.get('balance_sheet')
            if balance_sheet is not None and not balance_sheet.empty and balance_sheet.shape[1] >= 2:
                current_book_value = balance_sheet.iloc[:, 0].get('Stockholders Equity', 0)
                previous_book_value = balance_sheet.iloc[:, 1].get('Stockholders Equity', 0)
                
                if previous_book_value and previous_book_value != 0:
                    metrics['book_value_growth'] = (current_book_value - previous_book_value) / previous_book_value
                else:
                    metrics['book_value_growth'] = None
            else:
                metrics['book_value_growth'] = None
        except:
            metrics['book_value_growth'] = None
        
        self.ratios['growth'] = metrics
        return metrics
    
    def calculate_dividend_metrics(self) -> Dict[str, float]:
        """
        Calculate dividend-related metrics
        
        Returns:
            Dictionary with dividend metrics
        """
        if not self.financial_data.get('info'):
            return {}
        
        info = self.financial_data['info']
        metrics = {}
        
        # Dividend Yield
        metrics['dividend_yield'] = info.get('dividendYield', None)
        
        # Dividend Rate
        metrics['dividend_rate'] = info.get('dividendRate', None)
        
        # Payout Ratio
        metrics['payout_ratio'] = info.get('payoutRatio', None)
        
        # Five Year Average Dividend Yield
        metrics['five_year_avg_dividend_yield'] = info.get('fiveYearAvgDividendYield', None)
        
        self.ratios['dividend'] = metrics
        return metrics
    
    def analyze_financial_statements(self) -> Dict[str, Any]:
        """
        Analyze financial statements for trends and insights
        
        Returns:
            Dictionary with financial statement analysis
        """
        analysis = {}
        
        try:
            # Income Statement Analysis
            income_statement = self.financial_data.get('income_statement')
            if income_statement is not None and not income_statement.empty:
                analysis['income_trends'] = self._analyze_income_trends(income_statement)
            
            # Balance Sheet Analysis
            balance_sheet = self.financial_data.get('balance_sheet')
            if balance_sheet is not None and not balance_sheet.empty:
                analysis['balance_sheet_trends'] = self._analyze_balance_sheet_trends(balance_sheet)
            
            # Cash Flow Analysis
            cash_flow = self.financial_data.get('cash_flow')
            if cash_flow is not None and not cash_flow.empty:
                analysis['cash_flow_trends'] = self._analyze_cash_flow_trends(cash_flow)
        
        except Exception as e:
            print(f"Error analyzing financial statements: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_income_trends(self, income_statement: pd.DataFrame) -> Dict[str, Any]:
        """Analyze income statement trends over time"""
        trends = {}
        
        try:
            if income_statement.shape[1] >= 2:
                # Revenue trend
                revenue_latest = income_statement.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income_statement.index else 0
                revenue_previous = income_statement.loc['Total Revenue'].iloc[1] if 'Total Revenue' in income_statement.index else 0
                
                if revenue_previous != 0:
                    trends['revenue_growth_rate'] = (revenue_latest - revenue_previous) / revenue_previous
                
                # Net Income trend
                net_income_latest = income_statement.loc['Net Income'].iloc[0] if 'Net Income' in income_statement.index else 0
                net_income_previous = income_statement.loc['Net Income'].iloc[1] if 'Net Income' in income_statement.index else 0
                
                if net_income_previous != 0:
                    trends['net_income_growth_rate'] = (net_income_latest - net_income_previous) / net_income_previous
        
        except Exception as e:
            trends['error'] = str(e)
        
        return trends
    
    def _analyze_balance_sheet_trends(self, balance_sheet: pd.DataFrame) -> Dict[str, Any]:
        """Analyze balance sheet trends over time"""
        trends = {}
        
        try:
            if balance_sheet.shape[1] >= 2:
                # Total Assets trend
                assets_latest = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else 0
                assets_previous = balance_sheet.loc['Total Assets'].iloc[1] if 'Total Assets' in balance_sheet.index else 0
                
                if assets_previous != 0:
                    trends['total_assets_growth'] = (assets_latest - assets_previous) / assets_previous
                
                # Total Debt trend
                debt_latest = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index else 0
                debt_previous = balance_sheet.loc['Total Debt'].iloc[1] if 'Total Debt' in balance_sheet.index else 0
                
                if debt_previous != 0:
                    trends['total_debt_growth'] = (debt_latest - debt_previous) / debt_previous
        
        except Exception as e:
            trends['error'] = str(e)
        
        return trends
    
    def _analyze_cash_flow_trends(self, cash_flow: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cash flow trends over time"""
        trends = {}
        
        try:
            if cash_flow.shape[1] >= 2:
                # Operating Cash Flow trend
                ocf_latest = cash_flow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cash_flow.index else 0
                ocf_previous = cash_flow.loc['Operating Cash Flow'].iloc[1] if 'Operating Cash Flow' in cash_flow.index else 0
                
                if ocf_previous != 0:
                    trends['operating_cash_flow_growth'] = (ocf_latest - ocf_previous) / ocf_previous
                
                # Free Cash Flow (Operating Cash Flow - Capital Expenditures)
                capex_latest = cash_flow.loc['Capital Expenditures'].iloc[0] if 'Capital Expenditures' in cash_flow.index else 0
                capex_previous = cash_flow.loc['Capital Expenditures'].iloc[1] if 'Capital Expenditures' in cash_flow.index else 0
                
                fcf_latest = ocf_latest - abs(capex_latest)  # CapEx is usually negative
                fcf_previous = ocf_previous - abs(capex_previous)
                
                if fcf_previous != 0:
                    trends['free_cash_flow_growth'] = (fcf_latest - fcf_previous) / fcf_previous
        
        except Exception as e:
            trends['error'] = str(e)
        
        return trends
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive fundamental analysis
        
        Returns:
            Dictionary with complete fundamental analysis
        """
        if not self.financial_data:
            return {"error": "No financial data available"}
        
        analysis = {
            'symbol': self.symbol,
            'analysis_date': datetime.now().isoformat(),
            'basic_info': self.get_basic_info(),
            'valuation_ratios': self.calculate_valuation_ratios(),
            'profitability_ratios': self.calculate_profitability_ratios(),
            'financial_health_ratios': self.calculate_financial_health_ratios(),
            'growth_metrics': self.calculate_growth_metrics(),
            'dividend_metrics': self.calculate_dividend_metrics(),
            'financial_statement_analysis': self.analyze_financial_statements(),
            'investment_score': self._calculate_investment_score()
        }
        
        return analysis
    
    def _calculate_investment_score(self) -> Dict[str, Any]:
        """
        Calculate an overall investment score based on fundamental metrics
        
        Returns:
            Dictionary with investment score and reasoning
        """
        score = 0
        max_score = 100
        factors = []
        
        try:
            info = self.financial_data.get('info', {})
            
            # Valuation Score (20 points)
            pe_ratio = info.get('trailingPE')
            if pe_ratio:
                if pe_ratio < 15:
                    score += 20
                    factors.append("Excellent P/E ratio")
                elif pe_ratio < 25:
                    score += 15
                    factors.append("Good P/E ratio")
                elif pe_ratio < 35:
                    score += 10
                    factors.append("Fair P/E ratio")
                else:
                    factors.append("High P/E ratio")
            
            # Profitability Score (25 points)
            roe = info.get('returnOnEquity')
            if roe:
                if roe > 0.20:
                    score += 25
                    factors.append("Excellent ROE")
                elif roe > 0.15:
                    score += 20
                    factors.append("Good ROE")
                elif roe > 0.10:
                    score += 15
                    factors.append("Fair ROE")
                else:
                    factors.append("Low ROE")
            
            # Growth Score (25 points)
            revenue_growth = info.get('revenueGrowth')
            if revenue_growth:
                if revenue_growth > 0.20:
                    score += 25
                    factors.append("Excellent revenue growth")
                elif revenue_growth > 0.10:
                    score += 20
                    factors.append("Good revenue growth")
                elif revenue_growth > 0.05:
                    score += 15
                    factors.append("Moderate revenue growth")
                else:
                    factors.append("Low revenue growth")
            
            # Financial Health Score (20 points)
            debt_to_equity = info.get('debtToEquity')
            if debt_to_equity is not None:
                if debt_to_equity < 0.3:
                    score += 20
                    factors.append("Low debt levels")
                elif debt_to_equity < 0.6:
                    score += 15
                    factors.append("Moderate debt levels")
                elif debt_to_equity < 1.0:
                    score += 10
                    factors.append("High debt levels")
                else:
                    factors.append("Very high debt levels")
            
            # Dividend Score (10 points)
            dividend_yield = info.get('dividendYield')
            if dividend_yield:
                if dividend_yield > 0.03:
                    score += 10
                    factors.append("Pays dividends")
                elif dividend_yield > 0.01:
                    score += 5
                    factors.append("Low dividend yield")
            
            # Determine rating
            if score >= 80:
                rating = "STRONG BUY"
            elif score >= 65:
                rating = "BUY"
            elif score >= 50:
                rating = "HOLD"
            elif score >= 35:
                rating = "WEAK HOLD"
            else:
                rating = "SELL"
        
        except Exception as e:
            score = 0
            rating = "UNABLE TO RATE"
            factors = [f"Error calculating score: {str(e)}"]
        
        return {
            'score': score,
            'max_score': max_score,
            'rating': rating,
            'factors': factors
        }

def analyze_multiple_fundamentals(symbols: List[str]) -> Dict[str, Dict]:
    """
    Analyze multiple stocks for fundamental metrics
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        Dictionary with fundamental analysis for each stock
    """
    results = {}
    
    for symbol in symbols:
        try:
            analyzer = FundamentalAnalyzer(symbol)
            results[symbol] = analyzer.get_comprehensive_analysis()
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    # Example usage
    analyzer = FundamentalAnalyzer("AAPL")
    analysis = analyzer.get_comprehensive_analysis()
    
    print(f"Fundamental Analysis for {analysis['symbol']}")
    print(f"Company: {analysis['basic_info']['company_name']}")
    print(f"P/E Ratio: {analysis['valuation_ratios'].get('pe_ratio', 'N/A')}")
    print(f"ROE: {analysis['profitability_ratios'].get('roe', 'N/A')}")
    print(f"Investment Score: {analysis['investment_score']['score']}/100")
    print(f"Rating: {analysis['investment_score']['rating']}")