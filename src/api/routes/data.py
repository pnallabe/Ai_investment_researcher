"""
Data management API routes for the AI Investment Research Bot.

Handles data ingestion, status monitoring, and data quality.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
import logging
from datetime import datetime

from src.models.postgresql import User, UserRole
from src.data_ingestion import IngestionOrchestrator
from ..auth import get_current_active_user, require_role
from ..dependencies import PaginationParams, get_pagination_params

logger = logging.getLogger(__name__)

data_router = APIRouter()


class IngestionJob(BaseModel):
    """Data ingestion job model."""
    job_id: str
    job_type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: Optional[int] = None
    error_message: Optional[str] = None


class DataSource(BaseModel):
    """Data source status model."""
    source_name: str
    source_type: str
    status: str
    last_update: Optional[datetime] = None
    records_count: int
    health_score: float


@data_router.get("/sources", response_model=List[DataSource])
async def get_data_sources(
    current_user: User = Depends(get_current_active_user)
):
    """Get status of all data sources."""
    try:
        # Mock data sources
        sources = [
            DataSource(
                source_name="SEC EDGAR",
                source_type="filing",
                status="active",
                last_update=datetime.utcnow(),
                records_count=15000,
                health_score=0.95
            ),
            DataSource(
                source_name="Yahoo Finance",
                source_type="market_data",
                status="active", 
                last_update=datetime.utcnow(),
                records_count=50000,
                health_score=0.98
            )
        ]
        
        return sources
        
    except Exception as e:
        logger.error(f"Failed to get data sources: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data sources"
        )


@data_router.post("/ingest/{source_type}")
async def trigger_ingestion(
    source_type: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(UserRole.ANALYST))
):
    """Trigger data ingestion for a specific source type."""
    try:
        # Create ingestion job
        job_id = f"job_{datetime.utcnow().timestamp()}"
        
        # Add background task
        background_tasks.add_task(run_ingestion_job, source_type, job_id)
        
        return {
            "job_id": job_id,
            "message": f"Ingestion job for {source_type} started",
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger ingestion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger data ingestion"
        )


@data_router.get("/jobs", response_model=List[IngestionJob])
async def get_ingestion_jobs(
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """Get ingestion job history."""
    try:
        # Mock job data
        jobs = [
            IngestionJob(
                job_id="job_1",
                job_type="sec_edgar",
                status="completed",
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                records_processed=1500
            )
        ]
        
        return jobs
        
    except Exception as e:
        logger.error(f"Failed to get ingestion jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ingestion jobs"
        )


async def run_ingestion_job(source_type: str, job_id: str):
    """Run data ingestion job in background."""
    try:
        logger.info(f"Starting ingestion job {job_id} for {source_type}")
        # Would run actual ingestion logic here
        logger.info(f"Completed ingestion job {job_id}")
    except Exception as e:
        logger.error(f"Ingestion job {job_id} failed: {e}", exc_info=True)