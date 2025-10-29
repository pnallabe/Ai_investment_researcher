"""
Ingestion orchestrator and scheduler
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from .base import IngestionResult
from .sec_edgar import SECEdgarIngester
from .market_data import MarketDataIngester
from .news import NewsIngester

logger = logging.getLogger(__name__)


@dataclass
class IngestionJob:
    """Configuration for an ingestion job"""
    name: str
    ingester_class: type
    config: Dict[str, Any]
    schedule: str  # cron-like schedule
    enabled: bool = True
    retry_count: int = 3


class IngestionOrchestrator:
    """Orchestrates data ingestion from multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jobs: Dict[str, IngestionJob] = {}
        self.results_history: List[IngestionResult] = []
    
    def register_job(self, job: IngestionJob):
        """Register an ingestion job"""
        self.jobs[job.name] = job
        logger.info(f"Registered ingestion job: {job.name}")
    
    def setup_default_jobs(self):
        """Setup default ingestion jobs"""
        
        # SEC Edgar filings job
        edgar_job = IngestionJob(
            name="sec_edgar_daily",
            ingester_class=SECEdgarIngester,
            config={
                "cik_list": [
                    "0000320193",  # Apple
                    "0001652044",  # Alphabet
                    "0000789019",  # Microsoft
                    "0001018724",  # Amazon
                    "0001318605",  # Tesla
                ],
                "form_types": ["10-K", "10-Q", "8-K"],
                "lookback_days": 7
            },
            schedule="0 2 * * *",  # Daily at 2 AM
            enabled=True
        )
        
        # Market data job
        market_job = IngestionJob(
            name="market_data_daily",
            ingester_class=MarketDataIngester,
            config={
                "tickers": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"],
                "data_source": "yahoo",
                "lookback_days": 1
            },
            schedule="0 1 * * *",  # Daily at 1 AM
            enabled=True
        )
        
        # News data job
        news_job = IngestionJob(
            name="news_data_hourly",
            ingester_class=NewsIngester,
            config={
                "sources": ["reuters_business", "reuters_markets", "cnbc_markets", "news_api"],
                "company_filter": ["Apple", "Google", "Microsoft", "Amazon", "Tesla"],
                "lookback_hours": 2
            },
            schedule="0 * * * *",  # Hourly
            enabled=True
        )
        
        self.register_job(edgar_job)
        self.register_job(market_job)
        self.register_job(news_job)
    
    async def run_job(self, job_name: str, **kwargs) -> IngestionResult:
        """Run a specific ingestion job"""
        if job_name not in self.jobs:
            raise ValueError(f"Job {job_name} not found")
        
        job = self.jobs[job_name]
        
        if not job.enabled:
            logger.info(f"Job {job_name} is disabled, skipping")
            return IngestionResult(
                success=False,
                records_processed=0,
                errors=["Job is disabled"],
                metadata={"job_name": job_name},
                timestamp=datetime.utcnow()
            )
        
        logger.info(f"Starting ingestion job: {job_name}")
        
        try:
            # Merge job config with runtime kwargs
            job_config = {**job.config, **kwargs}
            
            # Create ingester instance
            async with job.ingester_class(job_config) as ingester:
                
                # Prepare job-specific parameters
                if job_name == "sec_edgar_daily":
                    lookback_days = job_config.get("lookback_days", 7)
                    start_date = date.today() - timedelta(days=lookback_days)
                    
                    result = await ingester.run_etl(
                        cik_list=job_config.get("cik_list"),
                        form_types=job_config.get("form_types"),
                        start_date=start_date,
                        end_date=date.today()
                    )
                
                elif job_name == "market_data_daily":
                    lookback_days = job_config.get("lookback_days", 1)
                    start_date = date.today() - timedelta(days=lookback_days)
                    
                    result = await ingester.run_etl(
                        tickers=job_config.get("tickers"),
                        start_date=start_date,
                        end_date=date.today(),
                        data_source=job_config.get("data_source", "yahoo")
                    )
                
                elif job_name == "news_data_hourly":
                    lookback_hours = job_config.get("lookback_hours", 2)
                    from_date = date.today() - timedelta(hours=lookback_hours)
                    
                    result = await ingester.run_etl(
                        sources=job_config.get("sources"),
                        company_filter=job_config.get("company_filter"),
                        from_date=from_date,
                        to_date=date.today()
                    )
                
                else:
                    # Generic job execution
                    result = await ingester.run_etl(**job_config)
                
                # Store result
                result.metadata["job_name"] = job_name
                self.results_history.append(result)
                
                if result.success:
                    logger.info(f"Job {job_name} completed successfully: {result.records_processed} records")
                else:
                    logger.error(f"Job {job_name} failed: {result.errors}")
                
                return result
        
        except Exception as e:
            logger.error(f"Job {job_name} failed with exception: {str(e)}")
            error_result = IngestionResult(
                success=False,
                records_processed=0,
                errors=[str(e)],
                metadata={"job_name": job_name},
                timestamp=datetime.utcnow()
            )
            self.results_history.append(error_result)
            return error_result
    
    async def run_all_jobs(self, filter_enabled: bool = True) -> Dict[str, IngestionResult]:
        """Run all registered jobs"""
        results = {}
        
        jobs_to_run = [
            (name, job) for name, job in self.jobs.items()
            if not filter_enabled or job.enabled
        ]
        
        logger.info(f"Running {len(jobs_to_run)} ingestion jobs")
        
        # Run jobs in parallel (be careful with rate limits)
        tasks = []
        for job_name, job in jobs_to_run:
            task = asyncio.create_task(self.run_job(job_name))
            tasks.append((job_name, task))
        
        # Wait for all tasks to complete
        for job_name, task in tasks:
            try:
                result = await task
                results[job_name] = result
            except Exception as e:
                logger.error(f"Task for job {job_name} failed: {str(e)}")
                results[job_name] = IngestionResult(
                    success=False,
                    records_processed=0,
                    errors=[str(e)],
                    metadata={"job_name": job_name},
                    timestamp=datetime.utcnow()
                )
        
        return results
    
    def get_job_status(self, job_name: str = None) -> Dict[str, Any]:
        """Get status of jobs"""
        if job_name:
            if job_name not in self.jobs:
                return {"error": f"Job {job_name} not found"}
            
            job = self.jobs[job_name]
            recent_results = [
                r for r in self.results_history 
                if r.metadata.get("job_name") == job_name
            ]
            
            return {
                "job_name": job_name,
                "enabled": job.enabled,
                "schedule": job.schedule,
                "last_run": recent_results[-1].timestamp if recent_results else None,
                "last_success": recent_results[-1].success if recent_results else None,
                "total_runs": len(recent_results)
            }
        
        else:
            # Return status for all jobs
            status = {}
            for name in self.jobs:
                status[name] = self.get_job_status(name)
            return status
    
    def get_ingestion_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get ingestion summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_results = [
            r for r in self.results_history 
            if r.timestamp >= cutoff_time
        ]
        
        total_records = sum(r.records_processed for r in recent_results)
        successful_jobs = sum(1 for r in recent_results if r.success)
        failed_jobs = len(recent_results) - successful_jobs
        
        by_source = {}
        for result in recent_results:
            source = result.metadata.get("source", "Unknown")
            if source not in by_source:
                by_source[source] = {"records": 0, "runs": 0, "failures": 0}
            
            by_source[source]["records"] += result.records_processed
            by_source[source]["runs"] += 1
            if not result.success:
                by_source[source]["failures"] += 1
        
        return {
            "time_period": f"{hours} hours",
            "total_records_ingested": total_records,
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "total_job_runs": len(recent_results),
            "success_rate": successful_jobs / len(recent_results) if recent_results else 0,
            "by_source": by_source
        }