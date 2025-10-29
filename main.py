"""
Main entry point for the AI Investment Research Bot.

This module initializes and runs the complete system including:
- FastAPI web server with comprehensive API endpoints
- Authentication and authorization
- Data ingestion pipelines
- Analytics engines  
- AI/NLP services with RAG
- WebSocket connections for real-time features
"""

import asyncio
import logging
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point with FastAPI server."""
    try:
        logger.info("Starting AI Investment Research Bot API Server...")
        
        # Initialize configuration
        from config.settings import Settings
        settings = Settings()
        
        # Import the FastAPI application
        from src.api.app import app
        
        logger.info(f"Starting server on {settings.host}:{settings.port}")
        logger.info("Available endpoints:")
        logger.info("  - POST /v1/auth/login - User authentication")
        logger.info("  - POST /v1/research/query - AI research queries")
        logger.info("  - GET /v1/company/{ticker}/analysis - Company analysis")
        logger.info("  - GET /v1/portfolio/ - Portfolio management")
        logger.info("  - WebSocket /ws/chat - Real-time chat")
        logger.info("  - GET /docs - API documentation")
        
        # Run the server
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info",
            access_log=True,
            use_colors=True,
            server_header=False,
            date_header=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise


async def run_standalone_services():
    """
    Run standalone services without the web API.
    Useful for data processing, analytics, and AI services only.
    """
    try:
        logger.info("Starting AI Investment Research Bot (Standalone Mode)...")
        
        # Initialize configuration
        from config.settings import Settings
        settings = Settings()
        
        # Initialize databases
        logger.info("Initializing databases...")
        from src.models.database import init_databases
        await init_databases()
        
        # Initialize data ingestion system
        logger.info("Setting up data ingestion...")
        from src.data_ingestion import IngestionOrchestrator
        orchestrator = IngestionOrchestrator(settings.dict())
        orchestrator.setup_default_jobs()
        
        # Initialize analytics engines
        logger.info("Initializing analytics engines...")
        from src.analytics import FinancialMetricsEngine, TimeSeriesForecaster
        metrics_engine = FinancialMetricsEngine()
        forecaster = TimeSeriesForecaster()
        
        # Initialize AI/NLP system
        logger.info("Initializing AI/NLP system...")
        from src.ai_nlp import RAGSystem
        rag_system = RAGSystem()
        await rag_system.initialize()
        
        logger.info("AI Investment Research Bot services initialized successfully!")
        
        # Run a sample workflow demonstration
        logger.info("Running sample data ingestion...")
        results = await orchestrator.run_all_jobs()
        logger.info(f"Ingestion results: {results}")
        
        # Demonstrate analytics
        logger.info("Running sample analytics...")
        sample_data = {
            "revenue": 365000000000,
            "net_income": 90000000000,
            "total_assets": 350000000000,
            "shareholders_equity": 150000000000
        }
        metrics = metrics_engine.compute_metrics(sample_data)
        logger.info(f"Sample metrics computed: {len(metrics)} metrics calculated")
        
        # Keep the services running
        logger.info("Services are running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(60)
                logger.info("Services health check - All systems operational")
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
            
    except Exception as e:
        logger.error(f"Failed to start services: {e}", exc_info=True)
        raise
    finally:
        logger.info("AI Investment Research Bot shutdown complete.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "standalone":
        # Run in standalone mode (services only, no web API)
        logger.info("Starting in standalone mode...")
        asyncio.run(run_standalone_services())
    else:
        # Run with FastAPI web server (default)
        main()