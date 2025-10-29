"""
FastAPI dependencies for the AI Investment Research Bot API.

Common dependencies used across multiple endpoints.
"""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from config.settings import Settings
from src.models.database import get_db_session
from src.models.postgresql import User, UserRole
from .auth import get_current_user, get_current_active_user

logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.
    
    Yields:
        Database session
    """
    async with get_db_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


async def get_rag_system(request: Request):
    """Get RAG system from application state."""
    if not hasattr(request.app.state, 'rag_system'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    return request.app.state.rag_system


async def get_metrics_engine(request: Request):
    """Get financial metrics engine from application state."""
    if not hasattr(request.app.state, 'metrics_engine'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics engine not initialized"
        )
    return request.app.state.metrics_engine


async def get_forecaster(request: Request):
    """Get time series forecaster from application state."""
    if not hasattr(request.app.state, 'forecaster'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Forecaster not initialized"
        )
    return request.app.state.forecaster


def require_analyst_role():
    """Dependency that requires analyst role or higher."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role.value < UserRole.ANALYST.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Analyst role required"
            )
        return current_user
    return role_checker


def require_admin_role():
    """Dependency that requires admin role."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required"
            )
        return current_user
    return role_checker


class PaginationParams:
    """Pagination parameters."""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be positive"
            )
        
        if page_size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be positive"
            )
        
        if page_size > max_page_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page size cannot exceed {max_page_size}"
            )
        
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.limit = page_size


def get_pagination_params(
    page: int = 1,
    page_size: int = 20
) -> PaginationParams:
    """Get pagination parameters dependency."""
    return PaginationParams(page=page, page_size=page_size)


class FilterParams:
    """Common filter parameters for queries."""
    
    def __init__(
        self,
        ticker: Optional[str] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        market_cap_min: Optional[float] = None,
        market_cap_max: Optional[float] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ):
        self.ticker = ticker
        self.sector = sector
        self.industry = industry
        self.market_cap_min = market_cap_min
        self.market_cap_max = market_cap_max
        self.date_from = date_from
        self.date_to = date_to


def get_filter_params(
    ticker: Optional[str] = None,
    sector: Optional[str] = None,
    industry: Optional[str] = None,
    market_cap_min: Optional[float] = None,
    market_cap_max: Optional[float] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> FilterParams:
    """Get filter parameters dependency."""
    return FilterParams(
        ticker=ticker,
        sector=sector,
        industry=industry,
        market_cap_min=market_cap_min,
        market_cap_max=market_cap_max,
        date_from=date_from,
        date_to=date_to
    )


async def validate_ticker(ticker: str, db: AsyncSession = Depends(get_db)) -> str:
    """
    Validate that a ticker exists in the database.
    
    Args:
        ticker: Stock ticker symbol
        db: Database session
        
    Returns:
        Validated ticker
        
    Raises:
        HTTPException: If ticker is not found
    """
    from src.models.postgresql import Company
    
    try:
        company = await db.query(Company).filter(Company.ticker == ticker.upper()).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ticker '{ticker}' not found"
            )
        
        return ticker.upper()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ticker validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate ticker"
        )


async def get_request_context(request: Request) -> dict:
    """
    Get request context information.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request context dictionary
    """
    return {
        "request_id": getattr(request.state, 'request_id', None),
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent"),
        "timestamp": request.state.start_time if hasattr(request.state, 'start_time') else None
    }


class QueryLimits:
    """Query execution limits."""
    
    def __init__(
        self,
        max_results: int = 1000,
        timeout_seconds: int = 30
    ):
        self.max_results = max_results
        self.timeout_seconds = timeout_seconds


def get_query_limits(
    max_results: int = 1000,
    timeout_seconds: int = 30
) -> QueryLimits:
    """Get query limits dependency."""
    if max_results > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum results limit is 10,000"
        )
    
    if timeout_seconds > 300:  # 5 minutes max
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum timeout is 300 seconds"
        )
    
    return QueryLimits(max_results=max_results, timeout_seconds=timeout_seconds)