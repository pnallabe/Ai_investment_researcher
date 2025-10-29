"""
SEC EDGAR Data Ingestion Module

This module provides functions to fetch company filings, financial statements,
and other data from the SEC EDGAR database using the official SEC API.
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECEdgarFetcher:
    """
    A class to fetch data from SEC EDGAR database
    """
    
    def __init__(self, user_agent: str = "AI Investment Research Bot 1.0"):
        """
        Initialize the SEC EDGAR fetcher
        
        Args:
            user_agent: User agent string for SEC API requests (required by SEC)
        """
        self.base_url = "https://data.sec.gov"
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """
        Make a request to SEC API with proper rate limiting
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        try:
            # SEC requires 10 requests per second max
            time.sleep(0.1)
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            raise
    
    def get_company_tickers(self) -> pd.DataFrame:
        """
        Get all company tickers and CIK numbers from SEC
        
        Returns:
            DataFrame with company information
        """
        # Try multiple possible endpoints
        possible_urls = [
            f"{self.base_url}/files/company_tickers.json",
            f"{self.base_url}/files/company_tickers_exchange.json",
            "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
        ]
        
        for url in possible_urls:
            try:
                if url.endswith('.txt'):
                    # Handle text format
                    response = self.session.get(url)
                    response.raise_for_status()
                    
                    companies = []
                    for line in response.text.split('\n'):
                        if ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                company_name = parts[0].strip()
                                cik = parts[1].strip()
                                companies.append({
                                    'cik': cik,
                                    'ticker': '',  # Not available in this format
                                    'title': company_name
                                })
                    
                    df = pd.DataFrame(companies)
                    logger.info(f"Retrieved {len(df)} companies from SEC (text format)")
                    return df
                else:
                    # Handle JSON format
                    data = self._make_request(url)
                    
                    # Convert to DataFrame
                    companies = []
                    if isinstance(data, dict):
                        for key, company_info in data.items():
                            if isinstance(company_info, dict):
                                companies.append({
                                    'cik': str(company_info.get('cik_str', company_info.get('cik', ''))),
                                    'ticker': company_info.get('ticker', ''),
                                    'title': company_info.get('title', company_info.get('name', ''))
                                })
                    
                    df = pd.DataFrame(companies)
                    logger.info(f"Retrieved {len(df)} company tickers from SEC")
                    return df
                    
            except Exception as e:
                logger.warning(f"Failed to fetch from {url}: {e}")
                continue
        
        # If all endpoints fail, return empty DataFrame
        logger.error("All SEC ticker endpoints failed")
        return pd.DataFrame()
    
    def get_company_facts(self, cik: str) -> Dict:
        """
        Get company facts (financial data) for a specific company
        
        Args:
            cik: Company CIK number (as string)
            
        Returns:
            Dictionary containing company financial facts
        """
        # Ensure CIK is 10 digits with leading zeros
        cik = str(cik).zfill(10)
        url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik}.json"
        
        try:
            data = self._make_request(url)
            logger.info(f"Retrieved company facts for CIK {cik}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching company facts for CIK {cik}: {e}")
            raise
    
    def get_company_filings(self, cik: str, form_type: str = None, 
                           limit: int = 10) -> pd.DataFrame:
        """
        Get recent filings for a company
        
        Args:
            cik: Company CIK number
            form_type: Type of form (e.g., '10-K', '10-Q', '8-K')
            limit: Maximum number of filings to retrieve
            
        Returns:
            DataFrame with filing information
        """
        # Ensure CIK is 10 digits with leading zeros
        cik = str(cik).zfill(10)
        url = f"{self.base_url}/api/xbrl/submissions/CIK{cik}.json"
        
        try:
            data = self._make_request(url)
            
            # Extract recent filings
            filings = data.get('filings', {}).get('recent', {})
            
            if not filings:
                logger.warning(f"No recent filings found for CIK {cik}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(filings)
            
            # Filter by form type if specified
            if form_type:
                df = df[df['form'] == form_type]
            
            # Limit results
            df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} filings for CIK {cik}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching filings for CIK {cik}: {e}")
            raise
    
    def get_financial_metrics(self, cik: str) -> Dict[str, Any]:
        """
        Extract key financial metrics from company facts
        
        Args:
            cik: Company CIK number
            
        Returns:
            Dictionary with key financial metrics
        """
        try:
            facts = self.get_company_facts(cik)
            
            metrics = {}
            
            # Extract US GAAP data
            us_gaap = facts.get('facts', {}).get('us-gaap', {})
            
            # Common financial metrics to extract
            metric_mappings = {
                'revenue': ['Revenues', 'Revenue', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
                'net_income': ['NetIncomeLoss', 'NetIncome'],
                'total_assets': ['Assets', 'AssetsCurrent'],
                'total_liabilities': ['Liabilities', 'LiabilitiesCurrent'],
                'stockholders_equity': ['StockholdersEquity', 'ShareholdersEquity'],
                'cash': ['Cash', 'CashAndCashEquivalentsAtCarryingValue'],
                'debt': ['LongTermDebt', 'DebtCurrent']
            }
            
            for metric_name, possible_keys in metric_mappings.items():
                for key in possible_keys:
                    if key in us_gaap:
                        # Get the most recent annual value
                        units = us_gaap[key].get('units', {})
                        if 'USD' in units:
                            usd_values = units['USD']
                            # Filter for annual values (form 10-K)
                            annual_values = [
                                v for v in usd_values 
                                if v.get('form') == '10-K' and v.get('val')
                            ]
                            if annual_values:
                                # Get most recent value
                                latest = max(annual_values, key=lambda x: x.get('end', ''))
                                metrics[metric_name] = {
                                    'value': latest['val'],
                                    'end_date': latest['end'],
                                    'form': latest['form']
                                }
                                break
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting financial metrics for CIK {cik}: {e}")
            return {}
    
    def search_company_by_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Find company information by ticker symbol
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with company information or None if not found
        """
        # Known CIK mappings for major companies (fallback approach)
        known_ciks = {
            'AAPL': {'cik': '0000320193', 'title': 'Apple Inc.'},
            'MSFT': {'cik': '0000789019', 'title': 'Microsoft Corporation'},
            'GOOGL': {'cik': '0001652044', 'title': 'Alphabet Inc.'},
            'AMZN': {'cik': '0001018724', 'title': 'Amazon.com Inc.'},
            'TSLA': {'cik': '0001318605', 'title': 'Tesla Inc.'},
            'META': {'cik': '0001326801', 'title': 'Meta Platforms Inc.'},
            'NVDA': {'cik': '0001045810', 'title': 'NVIDIA Corporation'},
            'JPM': {'cik': '0000019617', 'title': 'JPMorgan Chase & Co.'},
            'JNJ': {'cik': '0000200406', 'title': 'Johnson & Johnson'},
            'V': {'cik': '0001403161', 'title': 'Visa Inc.'}
        }
        
        ticker_upper = ticker.upper()
        
        # Try known mappings first
        if ticker_upper in known_ciks:
            return {
                'cik': known_ciks[ticker_upper]['cik'],
                'ticker': ticker_upper,
                'title': known_ciks[ticker_upper]['title']
            }
        
        # Try to search in SEC data
        try:
            companies_df = self.get_company_tickers()
            
            if not companies_df.empty and 'ticker' in companies_df.columns:
                # Search for ticker (case insensitive)
                matching_company = companies_df[
                    companies_df['ticker'].str.upper() == ticker_upper
                ]
                
                if not matching_company.empty:
                    return matching_company.iloc[0].to_dict()
            
            logger.warning(f"No company found for ticker {ticker}")
            return None
                
        except Exception as e:
            logger.error(f"Error searching for ticker {ticker}: {e}")
            # Return known mapping if available
            if ticker_upper in known_ciks:
                return {
                    'cik': known_ciks[ticker_upper]['cik'],
                    'ticker': ticker_upper,
                    'title': known_ciks[ticker_upper]['title']
                }
            return None

def test_sec_fetcher():
    """
    Test function to demonstrate SEC EDGAR data fetching
    """
    fetcher = SECEdgarFetcher()
    
    # Test with Apple Inc.
    print("Testing SEC EDGAR data fetching...")
    
    # Find Apple by ticker
    apple_info = fetcher.search_company_by_ticker('AAPL')
    if apple_info:
        print(f"Found Apple: {apple_info}")
        
        # Get financial metrics
        metrics = fetcher.get_financial_metrics(apple_info['cik'])
        print(f"Financial metrics: {json.dumps(metrics, indent=2)}")
        
        # Get recent filings (skip if endpoint not available)
        try:
            filings = fetcher.get_company_filings(apple_info['cik'], form_type='10-K', limit=3)
            if not filings.empty:
                print(f"Recent 10-K filings:\n{filings[['form', 'filingDate', 'reportDate']].head()}")
            else:
                print("No recent filings data available")
        except Exception as e:
            print(f"Filings endpoint not available: {e}")

if __name__ == "__main__":
    test_sec_fetcher()