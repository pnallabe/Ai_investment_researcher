"""
Company analysis API routes for the AI Investment Research Bot.

Handles company-specific analysis and financial metrics.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import logging
from datetime import datetime, date

from src.models.postgresql import User
from src.analytics.financial_metrics import FinancialMetricsEngine
from src.analytics.forecasting import TimeSeriesForecaster
from ..auth import get_current_active_user
from ..dependencies import (
    get_metrics_engine, 
    get_forecaster, 
    validate_ticker,
    PaginationParams, 
    get_pagination_params
)

logger = logging.getLogger(__name__)

company_router = APIRouter()


class CompanySummary(BaseModel):
    """Company summary model."""
    ticker: str
    name: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    description: Optional[str] = None
    employees: Optional[int] = None
    founded: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None


class FinancialMetrics(BaseModel):
    """Financial metrics model."""
    ticker: str
    period: str
    metrics: Dict[str, float]
    ratios: Dict[str, float]
    growth_rates: Dict[str, float]
    calculated_at: datetime


class PriceData(BaseModel):
    """Stock price data model."""
    ticker: str
    date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    adjusted_close: Optional[float] = None


class PriceForecast(BaseModel):
    """Price forecast model."""
    ticker: str
    forecast_dates: List[date]
    forecast_prices: List[float]
    confidence_intervals: List[Dict[str, float]]
    model_used: str
    accuracy_metrics: Dict[str, float]
    forecast_generated_at: datetime


class CompanyAnalysis(BaseModel):
    """Complete company analysis model."""
    summary: CompanySummary
    financial_metrics: FinancialMetrics
    price_forecast: Optional[PriceForecast] = None
    recent_prices: List[PriceData]
    peer_comparison: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    analyst_notes: Optional[str] = None


@company_router.get("/{ticker}/summary", response_model=CompanySummary)
async def get_company_summary(
    ticker: str = Depends(validate_ticker),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get company summary and basic information.
    
    Args:
        ticker: Stock ticker symbol
        current_user: Current authenticated user
        
    Returns:
        Company summary information
    """
    try:
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        return CompanySummary(
            ticker=ticker,
            name=f"{ticker} Corporation",
            sector="Technology",
            industry="Software",
            market_cap=500000000000.0,  # $500B
            description=f"Leading technology company trading as {ticker}",
            employees=150000,
            founded=1995,
            headquarters="Cupertino, CA",
            website=f"https://www.{ticker.lower()}.com"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company summary for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company summary"
        )


@company_router.get("/{ticker}/metrics", response_model=FinancialMetrics)
async def get_financial_metrics(
    ticker: str = Depends(validate_ticker),
    period: str = Query(default="ttm", regex="^(annual|quarterly|ttm)$"),
    current_user: User = Depends(get_current_active_user),
    metrics_engine: FinancialMetricsEngine = Depends(get_metrics_engine)
):
    """
    Get financial metrics and ratios for a company.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (annual, quarterly, ttm)
        current_user: Current authenticated user
        metrics_engine: Financial metrics engine
        
    Returns:
        Financial metrics and ratios
    """
    try:
        # In a real implementation, this would fetch actual financial data
        # Mock financial data
        mock_financial_data = {
            "revenue": 365000000000,  # $365B
            "net_income": 90000000000,  # $90B
            "total_assets": 350000000000,  # $350B
            "total_liabilities": 200000000000,  # $200B
            "shareholders_equity": 150000000000,  # $150B
            "cash_and_equivalents": 50000000000,  # $50B
            "total_debt": 100000000000,  # $100B
            "shares_outstanding": 16000000000,  # 16B shares
            "current_assets": 120000000000,  # $120B
            "current_liabilities": 80000000000,  # $80B
        }
        
        # Calculate metrics using the engine
        calculated_metrics = metrics_engine.compute_metrics(mock_financial_data)
        
        return FinancialMetrics(
            ticker=ticker,
            period=period,
            metrics=calculated_metrics.get("metrics", {}),
            ratios=calculated_metrics.get("ratios", {}),
            growth_rates=calculated_metrics.get("growth_rates", {}),
            calculated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get financial metrics for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve financial metrics"
        )


@company_router.get("/{ticker}/prices", response_model=List[PriceData])
async def get_price_history(
    ticker: str = Depends(validate_ticker),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get historical price data for a company.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date for price history
        end_date: End date for price history
        current_user: Current authenticated user
        pagination: Pagination parameters
        
    Returns:
        Historical price data
    """
    try:
        # In a real implementation, this would query the database or external API
        # Mock price data
        mock_prices = [
            PriceData(
                ticker=ticker,
                date=date(2024, 1, 1),
                open_price=150.0,
                high_price=155.0,
                low_price=148.0,
                close_price=152.0,
                volume=50000000,
                adjusted_close=152.0
            ),
            PriceData(
                ticker=ticker,
                date=date(2024, 1, 2),
                open_price=152.0,
                high_price=158.0,
                low_price=151.0,
                close_price=157.0,
                volume=45000000,
                adjusted_close=157.0
            )
        ]
        
        # Apply date filtering if provided
        if start_date:
            mock_prices = [p for p in mock_prices if p.date >= start_date]
        if end_date:
            mock_prices = [p for p in mock_prices if p.date <= end_date]
        
        # Apply pagination
        start_idx = pagination.offset
        end_idx = start_idx + pagination.limit
        
        return mock_prices[start_idx:end_idx]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get price history for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve price history"
        )


@company_router.post("/{ticker}/forecast", response_model=PriceForecast)
async def generate_price_forecast(
    ticker: str = Depends(validate_ticker),
    forecast_days: int = Query(default=30, ge=1, le=365),
    model: str = Query(default="auto", regex="^(auto|sma|exponential|linear)$"),
    current_user: User = Depends(get_current_active_user),
    forecaster: TimeSeriesForecaster = Depends(get_forecaster)
):
    """
    Generate price forecast for a company.
    
    Args:
        ticker: Stock ticker symbol
        forecast_days: Number of days to forecast
        model: Forecasting model to use
        current_user: Current authenticated user
        forecaster: Time series forecaster
        
    Returns:
        Price forecast
    """
    try:
        # In a real implementation, this would fetch historical price data
        # Mock historical prices for forecasting
        import numpy as np
        
        mock_prices = np.array([150.0, 152.0, 148.0, 155.0, 160.0, 158.0, 162.0])
        mock_dates = [date.today().replace(day=i+1) for i in range(len(mock_prices))]
        
        # Generate forecast using the forecaster
        if model == "auto":
            forecast_prices, confidence_intervals = forecaster.forecast_sma(
                mock_prices, forecast_days, window=5
            )
            model_used = "Simple Moving Average"
        elif model == "sma":
            forecast_prices, confidence_intervals = forecaster.forecast_sma(
                mock_prices, forecast_days, window=5
            )
            model_used = "Simple Moving Average"
        elif model == "exponential":
            forecast_prices, confidence_intervals = forecaster.forecast_exponential_smoothing(
                mock_prices, forecast_days
            )
            model_used = "Exponential Smoothing"
        elif model == "linear":
            forecast_prices, confidence_intervals = forecaster.forecast_linear_regression(
                mock_prices, forecast_days
            )
            model_used = "Linear Regression"
        
        # Generate forecast dates
        from datetime import timedelta
        base_date = date.today()
        forecast_dates = [base_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        return PriceForecast(
            ticker=ticker,
            forecast_dates=forecast_dates,
            forecast_prices=forecast_prices.tolist(),
            confidence_intervals=[
                {"lower": float(ci[0]), "upper": float(ci[1])} 
                for ci in confidence_intervals
            ],
            model_used=model_used,
            accuracy_metrics={
                "mae": 2.5,  # Mock accuracy metrics
                "rmse": 3.2,
                "mape": 0.025
            },
            forecast_generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate forecast for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate price forecast"
        )


@company_router.get("/{ticker}/analysis", response_model=CompanyAnalysis)
async def get_complete_analysis(
    ticker: str = Depends(validate_ticker),
    include_forecast: bool = Query(default=True),
    include_peers: bool = Query(default=True),
    current_user: User = Depends(get_current_active_user),
    metrics_engine: FinancialMetricsEngine = Depends(get_metrics_engine),
    forecaster: TimeSeriesForecaster = Depends(get_forecaster)
):
    """
    Get complete company analysis including all available data.
    
    Args:
        ticker: Stock ticker symbol
        include_forecast: Include price forecast
        include_peers: Include peer comparison
        current_user: Current authenticated user
        metrics_engine: Financial metrics engine
        forecaster: Time series forecaster
        
    Returns:
        Complete company analysis
    """
    try:
        # Get all components (would call actual functions in real implementation)
        summary = CompanySummary(
            ticker=ticker,
            name=f"{ticker} Corporation",
            sector="Technology",
            industry="Software",
            market_cap=500000000000.0,
            description=f"Leading technology company trading as {ticker}",
            employees=150000,
            founded=1995,
            headquarters="Cupertino, CA",
            website=f"https://www.{ticker.lower()}.com"
        )
        
        # Mock financial metrics
        financial_metrics = FinancialMetrics(
            ticker=ticker,
            period="ttm",
            metrics={"revenue": 365000000000, "net_income": 90000000000},
            ratios={"pe_ratio": 25.5, "debt_to_equity": 0.67},
            growth_rates={"revenue_growth": 0.15, "earnings_growth": 0.12},
            calculated_at=datetime.utcnow()
        )
        
        # Mock recent prices
        recent_prices = [
            PriceData(
                ticker=ticker,
                date=date.today(),
                open_price=150.0,
                high_price=155.0,
                low_price=148.0,
                close_price=152.0,
                volume=50000000,
                adjusted_close=152.0
            )
        ]
        
        # Optional components
        price_forecast = None
        if include_forecast:
            price_forecast = PriceForecast(
                ticker=ticker,
                forecast_dates=[date.today()],
                forecast_prices=[155.0],
                confidence_intervals=[{"lower": 150.0, "upper": 160.0}],
                model_used="Simple Moving Average",
                accuracy_metrics={"mae": 2.5, "rmse": 3.2},
                forecast_generated_at=datetime.utcnow()
            )
        
        peer_comparison = None
        if include_peers:
            peer_comparison = {
                "peers": ["MSFT", "GOOGL", "META"],
                "metrics_comparison": {
                    "pe_ratio": {"AAPL": 25.5, "MSFT": 28.2, "GOOGL": 22.1},
                    "market_cap": {"AAPL": 500e9, "MSFT": 450e9, "GOOGL": 400e9}
                }
            }
        
        return CompanyAnalysis(
            summary=summary,
            financial_metrics=financial_metrics,
            price_forecast=price_forecast,
            recent_prices=recent_prices,
            peer_comparison=peer_comparison,
            risk_assessment={
                "overall_risk": "Medium",
                "volatility": 0.25,
                "beta": 1.2,
                "key_risks": ["Market competition", "Regulatory changes"]
            },
            analyst_notes=f"Comprehensive analysis for {ticker} shows strong fundamentals with moderate growth prospects."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get complete analysis for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company analysis"
        )


@company_router.get("/{ticker}/peers")
async def get_peer_companies(
    ticker: str = Depends(validate_ticker),
    current_user: User = Depends(get_current_active_user)
):
    """Get peer companies for comparison."""
    try:
        # Mock peer data
        return {
            "ticker": ticker,
            "peers": [
                {"ticker": "MSFT", "name": "Microsoft Corporation", "similarity_score": 0.92},
                {"ticker": "GOOGL", "name": "Alphabet Inc.", "similarity_score": 0.87},
                {"ticker": "META", "name": "Meta Platforms Inc.", "similarity_score": 0.82}
            ],
            "comparison_metrics": ["market_cap", "pe_ratio", "revenue_growth", "profit_margin"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get peers for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve peer companies"
        )