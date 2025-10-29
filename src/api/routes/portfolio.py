"""
Portfolio management API routes for the AI Investment Research Bot.

Handles portfolio tracking, analysis, and scenario modeling.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import logging
from datetime import datetime, date
from decimal import Decimal

from src.models.postgresql import User
from ..auth import get_current_active_user
from ..dependencies import PaginationParams, get_pagination_params

logger = logging.getLogger(__name__)

portfolio_router = APIRouter()


class PortfolioHolding(BaseModel):
    """Portfolio holding model."""
    ticker: str
    shares: float = Field(..., gt=0)
    average_cost: float = Field(..., gt=0)
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_gain_loss: Optional[float] = None
    unrealized_gain_loss_percent: Optional[float] = None
    weight: Optional[float] = None
    added_date: datetime


class Portfolio(BaseModel):
    """Portfolio model."""
    portfolio_id: str
    name: str
    description: Optional[str] = None
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float
    holdings: List[PortfolioHolding]
    created_at: datetime
    updated_at: datetime


class PortfolioSummary(BaseModel):
    """Portfolio summary model."""
    portfolio_id: str
    name: str
    total_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    holdings_count: int
    updated_at: datetime


class PortfolioCreate(BaseModel):
    """Portfolio creation model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class HoldingCreate(BaseModel):
    """Holding creation model."""
    ticker: str = Field(..., min_length=1, max_length=10)
    shares: float = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)
    purchase_date: Optional[date] = None


class HoldingUpdate(BaseModel):
    """Holding update model."""
    ticker: str
    shares: Optional[float] = Field(None, gt=0)
    average_cost: Optional[float] = Field(None, gt=0)


class ScenarioAnalysis(BaseModel):
    """Scenario analysis model."""
    scenario_name: str
    price_changes: Dict[str, float]  # ticker -> percentage change
    portfolio_impact: Dict[str, Any]
    total_impact: float
    total_impact_percent: float
    risk_metrics: Dict[str, float]


@portfolio_router.get("/", response_model=List[PortfolioSummary])
async def get_user_portfolios(
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get all portfolios for the current user.
    
    Args:
        current_user: Current authenticated user
        pagination: Pagination parameters
        
    Returns:
        List of user portfolios
    """
    try:
        # Mock portfolios (would query database in real implementation)
        mock_portfolios = [
            PortfolioSummary(
                portfolio_id="portfolio_1",
                name="Growth Portfolio",
                total_value=125000.0,
                total_gain_loss=25000.0,
                total_gain_loss_percent=0.25,
                holdings_count=8,
                updated_at=datetime.utcnow()
            ),
            PortfolioSummary(
                portfolio_id="portfolio_2", 
                name="Dividend Portfolio",
                total_value=75000.0,
                total_gain_loss=5000.0,
                total_gain_loss_percent=0.07,
                holdings_count=12,
                updated_at=datetime.utcnow()
            )
        ]
        
        # Apply pagination
        start_idx = pagination.offset
        end_idx = start_idx + pagination.limit
        
        return mock_portfolios[start_idx:end_idx]
        
    except Exception as e:
        logger.error(f"Failed to get user portfolios: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolios"
        )


@portfolio_router.post("/", response_model=Portfolio)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new portfolio.
    
    Args:
        portfolio_data: Portfolio creation data
        current_user: Current authenticated user
        
    Returns:
        Created portfolio
    """
    try:
        # Create new portfolio (would save to database in real implementation)
        new_portfolio = Portfolio(
            portfolio_id=f"portfolio_{datetime.utcnow().timestamp()}",
            name=portfolio_data.name,
            description=portfolio_data.description,
            total_value=0.0,
            total_cost=0.0,
            total_gain_loss=0.0,
            total_gain_loss_percent=0.0,
            holdings=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        logger.info(
            f"Created new portfolio",
            extra={
                "user_id": str(current_user.id),
                "portfolio_id": new_portfolio.portfolio_id,
                "portfolio_name": new_portfolio.name
            }
        )
        
        return new_portfolio
        
    except Exception as e:
        logger.error(f"Failed to create portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portfolio"
        )


@portfolio_router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio_details(
    portfolio_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed portfolio information.
    
    Args:
        portfolio_id: Portfolio identifier
        current_user: Current authenticated user
        
    Returns:
        Detailed portfolio information
    """
    try:
        # Mock portfolio details (would query database in real implementation)
        mock_holdings = [
            PortfolioHolding(
                ticker="AAPL",
                shares=100.0,
                average_cost=150.0,
                current_price=160.0,
                market_value=16000.0,
                unrealized_gain_loss=1000.0,
                unrealized_gain_loss_percent=0.067,
                weight=0.32,
                added_date=datetime.utcnow()
            ),
            PortfolioHolding(
                ticker="MSFT",
                shares=50.0,
                average_cost=300.0,
                current_price=320.0,
                market_value=16000.0,
                unrealized_gain_loss=1000.0,
                unrealized_gain_loss_percent=0.067,
                weight=0.32,
                added_date=datetime.utcnow()
            )
        ]
        
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            name="Growth Portfolio",
            description="Long-term growth focused portfolio",
            total_value=50000.0,
            total_cost=45000.0,
            total_gain_loss=5000.0,
            total_gain_loss_percent=0.11,
            holdings=mock_holdings,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return portfolio
        
    except Exception as e:
        logger.error(f"Failed to get portfolio details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio details"
        )


@portfolio_router.post("/{portfolio_id}/holdings", response_model=PortfolioHolding)
async def add_holding(
    portfolio_id: str,
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a new holding to a portfolio.
    
    Args:
        portfolio_id: Portfolio identifier
        holding_data: Holding data
        current_user: Current authenticated user
        
    Returns:
        Created holding
    """
    try:
        # Create new holding (would save to database in real implementation)
        new_holding = PortfolioHolding(
            ticker=holding_data.ticker.upper(),
            shares=holding_data.shares,
            average_cost=holding_data.purchase_price,
            current_price=holding_data.purchase_price,  # Initial price
            market_value=holding_data.shares * holding_data.purchase_price,
            unrealized_gain_loss=0.0,
            unrealized_gain_loss_percent=0.0,
            weight=None,  # Will be calculated when portfolio is updated
            added_date=datetime.utcnow()
        )
        
        logger.info(
            f"Added holding to portfolio",
            extra={
                "user_id": str(current_user.id),
                "portfolio_id": portfolio_id,
                "ticker": holding_data.ticker,
                "shares": holding_data.shares
            }
        )
        
        return new_holding
        
    except Exception as e:
        logger.error(f"Failed to add holding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add holding"
        )


@portfolio_router.put("/{portfolio_id}/holdings/{ticker}")
async def update_holding(
    portfolio_id: str,
    ticker: str,
    holding_update: HoldingUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing holding in a portfolio.
    
    Args:
        portfolio_id: Portfolio identifier
        ticker: Stock ticker symbol
        holding_update: Updated holding data
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Update holding (would update database in real implementation)
        logger.info(
            f"Updated holding in portfolio",
            extra={
                "user_id": str(current_user.id),
                "portfolio_id": portfolio_id,
                "ticker": ticker,
                "update_data": holding_update.dict(exclude_none=True)
            }
        )
        
        return {"message": f"Holding {ticker} updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update holding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update holding"
        )


@portfolio_router.delete("/{portfolio_id}/holdings/{ticker}")
async def remove_holding(
    portfolio_id: str,
    ticker: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a holding from a portfolio.
    
    Args:
        portfolio_id: Portfolio identifier
        ticker: Stock ticker symbol
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Remove holding (would delete from database in real implementation)
        logger.info(
            f"Removed holding from portfolio",
            extra={
                "user_id": str(current_user.id),
                "portfolio_id": portfolio_id,
                "ticker": ticker
            }
        )
        
        return {"message": f"Holding {ticker} removed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to remove holding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove holding"
        )


@portfolio_router.post("/{portfolio_id}/scenario", response_model=ScenarioAnalysis)
async def analyze_scenario(
    portfolio_id: str,
    scenario_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform scenario analysis on a portfolio.
    
    Args:
        portfolio_id: Portfolio identifier
        scenario_data: Scenario parameters (price changes, etc.)
        current_user: Current authenticated user
        
    Returns:
        Scenario analysis results
    """
    try:
        scenario_name = scenario_data.get("scenario_name", "Custom Scenario")
        price_changes = scenario_data.get("price_changes", {})
        
        # Perform scenario analysis (mock implementation)
        portfolio_impact = {}
        total_impact = 0.0
        
        # Mock calculations
        for ticker, change_percent in price_changes.items():
            holding_impact = 1000.0 * change_percent  # Mock calculation
            portfolio_impact[ticker] = {
                "price_change_percent": change_percent,
                "value_impact": holding_impact,
                "new_value": 16000.0 * (1 + change_percent)
            }
            total_impact += holding_impact
        
        total_portfolio_value = 50000.0  # Mock current value
        total_impact_percent = total_impact / total_portfolio_value
        
        scenario_analysis = ScenarioAnalysis(
            scenario_name=scenario_name,
            price_changes=price_changes,
            portfolio_impact=portfolio_impact,
            total_impact=total_impact,
            total_impact_percent=total_impact_percent,
            risk_metrics={
                "value_at_risk": abs(total_impact) if total_impact < 0 else 0,
                "volatility": 0.15,
                "max_drawdown": -0.08
            }
        )
        
        logger.info(
            f"Performed scenario analysis",
            extra={
                "user_id": str(current_user.id),
                "portfolio_id": portfolio_id,
                "scenario_name": scenario_name,
                "total_impact": total_impact
            }
        )
        
        return scenario_analysis
        
    except Exception as e:
        logger.error(f"Failed to analyze scenario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform scenario analysis"
        )


@portfolio_router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(
    portfolio_id: str,
    period: str = Query(default="1y", regex="^(1d|1w|1m|3m|6m|1y|2y|5y|max)$"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get portfolio performance metrics over time.
    
    Args:
        portfolio_id: Portfolio identifier
        period: Time period for performance analysis
        current_user: Current authenticated user
        
    Returns:
        Portfolio performance data
    """
    try:
        # Mock performance data
        performance_data = {
            "portfolio_id": portfolio_id,
            "period": period,
            "total_return": 0.15,
            "annualized_return": 0.12,
            "volatility": 0.18,
            "sharpe_ratio": 0.85,
            "max_drawdown": -0.08,
            "beta": 1.1,
            "alpha": 0.03,
            "performance_chart": [
                {"date": "2024-01-01", "value": 45000.0},
                {"date": "2024-06-01", "value": 47500.0},
                {"date": "2024-12-01", "value": 50000.0}
            ],
            "benchmark_comparison": {
                "benchmark": "S&P 500",
                "portfolio_return": 0.15,
                "benchmark_return": 0.12,
                "outperformance": 0.03
            }
        }
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Failed to get portfolio performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio performance"
        )


@portfolio_router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a portfolio.
    
    Args:
        portfolio_id: Portfolio identifier
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Delete portfolio (would delete from database in real implementation)
        logger.info(
            f"Deleted portfolio",
            extra={
                "user_id": str(current_user.id),
                "portfolio_id": portfolio_id
            }
        )
        
        return {"message": "Portfolio deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete portfolio"
        )