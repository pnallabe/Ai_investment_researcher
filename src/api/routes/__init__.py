"""
API routes package for the AI Investment Research Bot.

Contains all API endpoint modules organized by functionality.
"""

from .research import research_router
from .company import company_router
from .portfolio import portfolio_router
from .data import data_router
from .analytics import analytics_router

__all__ = [
    "research_router",
    "company_router", 
    "portfolio_router",
    "data_router",
    "analytics_router"
]