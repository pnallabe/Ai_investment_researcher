"""
Main FastAPI application factory and configuration.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from config.settings import Settings
from .auth import auth_router
from .routes import (
    research_router,
    company_router,
    portfolio_router,
    data_router,
    analytics_router
)
from .websocket import websocket_router
from .middleware import RateLimitMiddleware, LoggingMiddleware
from src.models.database import init_databases, close_databases

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    try:
        # Startup
        logger.info("Starting AI Investment Research Bot API...")
        
        # Initialize databases
        await init_databases()
        logger.info("Databases initialized successfully")
        
        # Initialize AI/NLP systems
        from src.ai_nlp import RAGSystem
        app.state.rag_system = RAGSystem()
        await app.state.rag_system.initialize()
        logger.info("RAG system initialized successfully")
        
        # Initialize analytics engine
        from src.analytics import FinancialMetricsEngine, TimeSeriesForecaster
        app.state.metrics_engine = FinancialMetricsEngine()
        app.state.forecaster = TimeSeriesForecaster()
        logger.info("Analytics engines initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AI Investment Research Bot API...")
        await close_databases()
        logger.info("Application shutdown complete")


def create_app(settings: Settings = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        settings: Application settings instance
        
    Returns:
        Configured FastAPI application
    """
    if settings is None:
        settings = Settings()
    
    app = FastAPI(
        title="AI Investment Research Bot API",
        description="Comprehensive AI-powered investment research platform",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Store settings in app state
    app.state.settings = settings
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for security
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit)
    
    # Include routers
    app.include_router(
        auth_router,
        prefix="/v1/auth",
        tags=["Authentication"]
    )
    
    app.include_router(
        research_router,
        prefix="/v1/research",
        tags=["Research Queries"]
    )
    
    app.include_router(
        company_router,
        prefix="/v1/company",
        tags=["Company Analysis"]
    )
    
    app.include_router(
        portfolio_router,
        prefix="/v1/portfolio",
        tags=["Portfolio Management"]
    )
    
    app.include_router(
        data_router,
        prefix="/v1/data",
        tags=["Data Management"]
    )
    
    app.include_router(
        analytics_router,
        prefix="/v1/analytics",
        tags=["Analytics & Forecasting"]
    )
    
    app.include_router(
        websocket_router,
        prefix="/ws",
        tags=["WebSocket"]
    )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "services": {
                "api": "running",
                "database": "connected",
                "rag_system": "initialized"
            }
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler for unhandled errors."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    # Custom HTTP exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """Custom HTTP exception handler."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    from config.settings import Settings
    
    settings = Settings()
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )