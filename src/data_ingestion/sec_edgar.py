"""
SEC EDGAR filing ingester
"""
import re
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

from .base import BaseIngester, IngestionResult, RateLimiter, RetryMixin
from config.settings import settings

logger = logging.getLogger(__name__)


class SECEdgarIngester(BaseIngester, RetryMixin):
    """Ingester for SEC EDGAR filings"""
    
    BASE_URL = "https://www.sec.gov/Archives/edgar/"
    FILING_INDEX_URL = "https://www.sec.gov/Archives/edgar/daily-index/"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rate_limiter = RateLimiter(calls_per_second=0.1)  # SEC rate limit
        self.headers = {
            'User-Agent': settings.SEC_EDGAR_USER_AGENT,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    async def fetch_company_filings(self, cik: str, form_types: List[str] = None, 
                                   start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """Fetch filings for a specific company"""
        if form_types is None:
            form_types = ['10-K', '10-Q', '8-K', 'DEF 14A']
        
        url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
        
        await self.rate_limiter.wait()
        
        async with self.session.get(url, headers=self.headers) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch filings for CIK {cik}: {response.status}")
                return []
            
            data = await response.json()
            
        filings = []
        recent_filings = data.get('filings', {}).get('recent', {})
        
        for i in range(len(recent_filings.get('form', []))):
            form_type = recent_filings['form'][i]
            filing_date = datetime.strptime(recent_filings['filingDate'][i], '%Y-%m-%d').date()
            
            # Filter by form type and date range
            if form_types and form_type not in form_types:
                continue
            
            if start_date and filing_date < start_date:
                continue
                
            if end_date and filing_date > end_date:
                continue
            
            filing = {
                'cik': cik,
                'company_name': data.get('name', ''),
                'form_type': form_type,
                'filing_date': filing_date,
                'accession_number': recent_filings['accessionNumber'][i],
                'file_number': recent_filings.get('fileNumber', [''])[i],
                'primary_document': recent_filings.get('primaryDocument', [''])[i],
                'description': recent_filings.get('description', [''])[i],
            }
            
            filings.append(filing)
        
        return filings
    
    async def fetch_filing_content(self, accession_number: str, primary_document: str) -> Optional[str]:
        """Fetch the content of a specific filing"""
        # Remove dashes from accession number for URL
        accession_clean = accession_number.replace('-', '')
        
        url = f"{self.BASE_URL}data/{accession_clean}/{primary_document}"
        
        await self.rate_limiter.wait()
        
        try:
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    content = await response.text()
                    return self.extract_text_from_filing(content)
                else:
                    logger.error(f"Failed to fetch filing content: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching filing content: {str(e)}")
            return None
    
    def extract_text_from_filing(self, content: str) -> str:
        """Extract readable text from SEC filing HTML/XBRL"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', content)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common SEC filing boilerplate
        patterns_to_remove = [
            r'UNITED STATES\s+SECURITIES AND EXCHANGE COMMISSION.*?FORM \d+-[KQ]',
            r'Table of Contents.*?(?=\n\n|\r\n\r\n)',
            r'SIGNATURES.*?$'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        
        return text.strip()
    
    async def fetch_data(self, cik_list: List[str] = None, form_types: List[str] = None, 
                        start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """Fetch filings data"""
        if not cik_list:
            # Default to some major companies for demo
            cik_list = ['0000320193', '0001652044', '0000789019']  # Apple, Alphabet, Microsoft
        
        all_filings = []
        
        for cik in cik_list:
            try:
                filings = await self.retry_on_failure(
                    self.fetch_company_filings,
                    max_retries=3,
                    delay=1.0,
                    cik=cik,
                    form_types=form_types,
                    start_date=start_date,
                    end_date=end_date
                )
                all_filings.extend(filings)
                
            except Exception as e:
                logger.error(f"Failed to fetch filings for CIK {cik}: {str(e)}")
        
        return all_filings
    
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform filing data"""
        transformed = []
        
        for filing in raw_data:
            # Fetch filing content if needed
            content = None
            if filing.get('accession_number') and filing.get('primary_document'):
                content = await self.fetch_filing_content(
                    filing['accession_number'],
                    filing['primary_document']
                )
            
            transformed_filing = {
                'company_cik': filing['cik'],
                'company_name': filing['company_name'],
                'form_type': filing['form_type'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'file_number': filing['file_number'],
                'description': filing['description'],
                'content': content,
                'url': self._build_filing_url(filing['accession_number'], filing['primary_document']),
                'ingested_at': datetime.utcnow()
            }
            
            transformed.append(transformed_filing)
        
        return transformed
    
    def _build_filing_url(self, accession_number: str, primary_document: str) -> str:
        """Build the full URL for a filing"""
        accession_clean = accession_number.replace('-', '')
        return f"{self.BASE_URL}data/{accession_clean}/{primary_document}"
    
    async def load_data(self, transformed_data: List[Dict[str, Any]]) -> IngestionResult:
        """Load filing data into database"""
        # This would typically involve database operations
        # For now, we'll simulate the process
        
        try:
            # TODO: Implement actual database loading
            # - Insert into filings table
            # - Update companies table if needed
            # - Store filing content for vector embedding
            
            return IngestionResult(
                success=True,
                records_processed=len(transformed_data),
                errors=[],
                metadata={
                    'source': 'SEC EDGAR',
                    'filings_types': list(set(f['form_type'] for f in transformed_data))
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to load filing data: {str(e)}")
            return IngestionResult(
                success=False,
                records_processed=0,
                errors=[str(e)],
                metadata={},
                timestamp=datetime.utcnow()
            )