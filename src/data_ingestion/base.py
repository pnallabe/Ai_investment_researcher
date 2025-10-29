"""
Base data ingestion module
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import asyncio
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of data ingestion operation"""
    success: bool
    records_processed: int
    errors: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


class BaseIngester(ABC):
    """Base class for all data ingesters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch raw data from source"""
        pass
    
    @abstractmethod
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform raw data into normalized format"""
        pass
    
    @abstractmethod
    async def load_data(self, transformed_data: List[Dict[str, Any]]) -> IngestionResult:
        """Load transformed data into database"""
        pass
    
    async def run_etl(self, **kwargs) -> IngestionResult:
        """Run the complete ETL pipeline"""
        try:
            logger.info(f"Starting ETL pipeline for {self.__class__.__name__}")
            
            # Extract
            raw_data = await self.fetch_data(**kwargs)
            logger.info(f"Extracted {len(raw_data)} records")
            
            # Transform
            transformed_data = await self.transform_data(raw_data)
            logger.info(f"Transformed {len(transformed_data)} records")
            
            # Load
            result = await self.load_data(transformed_data)
            logger.info(f"ETL completed: {result.records_processed} records processed")
            
            return result
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}")
            return IngestionResult(
                success=False,
                records_processed=0,
                errors=[str(e)],
                metadata={},
                timestamp=datetime.utcnow()
            )


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.calls_per_second = calls_per_second
        self.last_called = 0.0
    
    async def wait(self):
        """Wait if necessary to respect rate limit"""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_called
        min_interval = 1.0 / self.calls_per_second
        
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self.last_called = asyncio.get_event_loop().time()


class RetryMixin:
    """Mixin for retry functionality"""
    
    async def retry_on_failure(self, func, max_retries: int = 3, delay: float = 1.0, *args, **kwargs):
        """Retry function on failure with exponential backoff"""
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s")
                await asyncio.sleep(wait_time)