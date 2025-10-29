"""
Analytics API routes for the AI Investment Research Bot.

Handles advanced analytics, forecasting, and market analysis.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import logging
from datetime import datetime, date

from src.models.postgresql import User
from src.analytics.financial_metrics import FinancialMetricsEngine
from src.analytics.forecasting import TimeSeriesForecaster
from ..auth import get_current_active_user
from ..dependencies import get_metrics_engine, get_forecaster

logger = logging.getLogger(__name__)

analytics_router = APIRouter()


class MarketAnalysis(BaseModel):
    """Market analysis model."""
    analysis_type: str
    market_indicators: Dict[str, float]
    sector_performance: Dict[str, float]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    generated_at: datetime


@analytics_router.get("/market", response_model=MarketAnalysis)
async def get_market_analysis(
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive market analysis."""
    try:
        return MarketAnalysis(
            analysis_type="comprehensive",
            market_indicators={
                "vix": 18.5,
                "pe_ratio_sp500": 22.1,
                "yield_curve_spread": 0.85
            },
            sector_performance={
                "Technology": 0.15,
                "Healthcare": 0.08,
                "Energy": -0.05
            },
            recommendations=[
                "Consider defensive positioning",
                "Monitor inflation indicators",
                "Evaluate growth vs value allocation"
            ],
            risk_assessment={
                "overall_risk": "Medium",
                "volatility_forecast": "Elevated",
                "key_risks": ["Geopolitical", "Monetary policy"]
            },
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get market analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market analysis"
        )


@analytics_router.post("/custom-analysis")
async def run_custom_analysis(
    analysis_params: dict,
    current_user: User = Depends(get_current_active_user),
    metrics_engine: FinancialMetricsEngine = Depends(get_metrics_engine)
):
    """Run custom analytics based on user parameters."""
    try:
        # Mock custom analysis
        return {
            "analysis_id": f"analysis_{datetime.utcnow().timestamp()}",
            "parameters": analysis_params,
            "results": {
                "score": 0.75,
                "insights": ["Sample insight 1", "Sample insight 2"],
                "data_points": {"metric1": 1.5, "metric2": 2.3}
            },
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to run custom analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run custom analysis"
        )