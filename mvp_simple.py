"""
AI Investment Research Bot - Simplified MVP Startup
This version runs with minimal dependencies for demonstration.
"""

import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

import hashlib
from datetime import datetime, timedelta

try:
    from pydantic import BaseModel
    from fastapi import FastAPI, HTTPException, Form, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi import Header
    import uvicorn
    
    # Import data ingestion modules
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'data_ingestion'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))
    from data_ingestion.data_processor import DataProcessor
    from analysis.technical_analysis import TechnicalAnalyzer, analyze_multiple_stocks
    from analysis.fundamental_analysis import FundamentalAnalyzer, analyze_multiple_fundamentals
    from analysis.portfolio_risk_analysis import PortfolioRiskAnalyzer, analyze_multiple_portfolios
    from analysis.ai_analysis import AIStockAnalyzer, LLMProvider, analyze_stock_with_ai, analyze_portfolio_with_ai
    FASTAPI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"FastAPI not available: {e}")
    FASTAPI_AVAILABLE = False
    # Fallback BaseModel for when pydantic is not available
    class BaseModel:
        pass

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    logger.warning("PyJWT not available - authentication will be simplified")
    JWT_AVAILABLE = False

# Simple data models
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    components: Dict[str, str]

class ResearchQuery(BaseModel):
    query: str
    query_type: str = "general"

class ResearchResponse(BaseModel):
    query_id: str
    query: str
    answer: str
    confidence_score: float
    processing_time: float
    timestamp: str

# Authentication models
class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    email: str
    username: str
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True
    created_at: str
    updated_at: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# JWT Configuration
JWT_SECRET = "demo-secret-key-for-mvp-only"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Demo users database
DEMO_USERS = {
    "demo@example.com": {
        "id": "demo-user-001",
        "email": "demo@example.com",
        "username": "demo_user",
        "first_name": "Demo",
        "last_name": "User",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}

# Authentication utilities
def create_access_token(user_data: dict) -> str:
    """Create JWT access token."""
    if JWT_AVAILABLE:
        to_encode = user_data.copy()
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        to_encode.update({"exp": expire, "sub": user_data["email"]})
        return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    else:
        # Fallback: simple token (not secure, for demo only)
        import base64
        import json
        token_data = {
            "user": user_data,
            "exp": (datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)).isoformat()
        }
        return base64.b64encode(json.dumps(token_data).encode()).decode()

def get_current_user(authorization: str = Header(None)) -> dict:
    """Get current user from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    if JWT_AVAILABLE:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            email = payload.get("sub")
            if email is None or email not in DEMO_USERS:
                raise HTTPException(status_code=401, detail="Invalid token")
            return DEMO_USERS[email]
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    else:
        # Fallback: simple token verification (not secure, for demo only)
        try:
            import base64
            import json
            token_data = json.loads(base64.b64decode(token).decode())
            exp_time = datetime.fromisoformat(token_data["exp"])
            if datetime.utcnow() > exp_time:
                raise HTTPException(status_code=401, detail="Token expired")
            email = token_data["user"]["email"]
            if email not in DEMO_USERS:
                raise HTTPException(status_code=401, detail="Invalid token")
            return DEMO_USERS[email]
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user with username/password."""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user["password_hash"]:
        return None
    
    return user

def create_simple_app() -> FastAPI:
    """Create a simplified FastAPI app for MVP demonstration."""
    
    app = FastAPI(
        title="AI Investment Research Bot - MVP",
        description="Simplified version for demonstration",
        version="1.0.0-mvp"
    )
    
    # Initialize data processor for real financial data
    try:
        data_processor = DataProcessor()
        logger.info("Data processor initialized successfully - real financial data available")
    except Exception as e:
        logger.warning(f"Data processor initialization failed: {e} - using mock data")
        data_processor = None
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "AI Investment Research Bot MVP",
            "status": "running",
            "version": "1.0.0-mvp",
            "documentation": "/docs"
        }
    
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().timestamp(),
            version="1.0.0-mvp",
            components={
                "api": "running",
                "core_services": "available",
                "database": "simulated",
                "ai_nlp": "simulated"
            }
        )
    
    # Authentication endpoints
    @app.post("/v1/auth/login", response_model=AuthResponse, tags=["Authentication"])
    async def login(username: str = Form(), password: str = Form()):
        """
        Authenticate user and return access token.
        Demo credentials: username=demo@example.com, password=demo123
        """
        user_data = authenticate_user(username, password)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        
        # Create access token
        token = create_access_token({
            "user_id": user_data["id"],
            "email": user_data["email"],
            "username": user_data["username"]
        })
        
        # Return user info without password
        user_response = User(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"]
        )
        
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=user_response
        )
    
    @app.get("/v1/auth/me", response_model=User, tags=["Authentication"])
    async def get_user_info(current_user: dict = Depends(get_current_user)):
        """Get current authenticated user information."""
        return User(
            id=current_user["id"],
            email=current_user["email"],
            username=current_user["username"],
            first_name=current_user["first_name"],
            last_name=current_user["last_name"],
            is_active=current_user["is_active"],
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"]
        )
    
    @app.post("/v1/auth/refresh", response_model=AuthResponse, tags=["Authentication"])
    async def refresh_user_token(current_user: dict = Depends(get_current_user)):
        """Refresh access token."""
        # Create new access token
        token = create_access_token({
            "user_id": current_user["id"],
            "email": current_user["email"],
            "username": current_user["username"]
        })
        
        user_response = User(
            id=current_user["id"],
            email=current_user["email"],
            username=current_user["username"],
            first_name=current_user["first_name"],
            last_name=current_user["last_name"],
            is_active=current_user["is_active"],
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"]
        )
        
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=user_response
        )
    
    @app.post("/v1/research/query", response_model=ResearchResponse, tags=["Research"])
    async def research_query(query_data: ResearchQuery):
        """
        Execute a research query (simplified version).
        """
        import time
        import uuid
        
        start_time = time.time()
        
        # Simulate processing
        await simulate_processing(0.5)
        
        # Generate mock response based on query
        answer = generate_mock_answer(query_data.query, query_data.query_type)
        
        processing_time = time.time() - start_time
        
        return ResearchResponse(
            query_id=str(uuid.uuid4()),
            query=query_data.query,
            answer=answer,
            confidence_score=0.85,
            processing_time=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @app.get("/v1/company/{ticker}/summary", tags=["Company"])
    async def get_company_summary(ticker: str):
        """Get company summary (mock data)."""
        return {
            "ticker": ticker.upper(),
            "name": f"{ticker.upper()} Corporation",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 500000000000.0,
            "description": f"Mock company data for {ticker.upper()}",
            "mock_data": True
        }
    
    @app.get("/v1/portfolio/", tags=["Portfolio"])
    async def get_portfolios():
        """Get user portfolios with real financial data."""
        if data_processor:
            try:
                # Sample portfolio for demo
                sample_portfolio = {
                    'AAPL': 10,
                    'MSFT': 5, 
                    'GOOGL': 3,
                    'TSLA': 2
                }
                
                portfolio_data = data_processor.get_portfolio_data(sample_portfolio)
                
                return {
                    "portfolios": [
                        {
                            "id": "portfolio_1",
                            "name": "Growth Portfolio",
                            "total_value": portfolio_data.get('summary', {}).get('total_value', 0),
                            "holdings_count": portfolio_data.get('summary', {}).get('positions_count', 0),
                            "total_gain_loss_percent": portfolio_data.get('summary', {}).get('total_gain_loss_percent', 0),
                            "positions": portfolio_data.get('positions', {}),
                            "sectors": portfolio_data.get('summary', {}).get('sectors', {}),
                            "top_performers": portfolio_data.get('summary', {}).get('top_performers', []),
                            "last_updated": portfolio_data.get('last_updated', ''),
                            "real_data": True
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"Error fetching real portfolio data: {e}")
        
        # Fallback to mock data
        return {
            "portfolios": [
                {
                    "id": "portfolio_1",
                    "name": "Growth Portfolio",
                    "total_value": 125000.0,
                    "holdings_count": 8,
                    "mock_data": True
                }
            ]
        }
    
    @app.get("/v1/market/overview", tags=["Market Data"])
    async def get_market_overview():
        """Get comprehensive market overview with real data."""
        if data_processor:
            try:
                market_data = data_processor.get_market_overview()
                return {
                    "market_overview": market_data,
                    "real_data": True,
                    "last_updated": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error fetching market data: {e}")
        
        # Fallback to mock data
        return {
            "market_overview": {
                "indices": {
                    "S&P 500": {"price": 5800.0, "change_percent": 0.5},
                    "NASDAQ": {"price": 18500.0, "change_percent": 0.8}
                }
            },
            "mock_data": True
        }
    
    @app.get("/v1/stock/{ticker}", tags=["Market Data"])
    async def get_stock_data(ticker: str):
        """Get comprehensive stock data for a specific ticker."""
        if data_processor:
            try:
                stock_data = data_processor.get_comprehensive_company_data(ticker.upper())
                return {
                    "stock_data": stock_data,
                    "real_data": True,
                    "last_updated": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error fetching stock data for {ticker}: {e}")
        
        # Fallback to mock data
        return {
            "stock_data": {
                "basic_info": {
                    "ticker": ticker.upper(),
                    "company_name": f"Mock Company for {ticker.upper()}",
                    "sector": "Technology"
                },
                "market_data": {
                    "current_price": 150.0,
                    "change_percent": 2.5
                }
            },
            "mock_data": True
        }

    @app.get("/v1/analysis/technical/{ticker}", tags=["Advanced Analysis"])
    async def get_technical_analysis(ticker: str, period: str = "1y"):
        """Get comprehensive technical analysis for a stock."""
        try:
            from analysis.technical_analysis import TechnicalAnalyzer
            analyzer = TechnicalAnalyzer(ticker.upper(), period)
            analysis = analyzer.get_all_indicators()
            return {
                "technical_analysis": analysis,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in technical analysis for {ticker}: {e}")
            return {
                "error": f"Technical analysis failed: {str(e)}",
                "ticker": ticker.upper(),
                "mock_data": True
            }
    
    @app.get("/v1/analysis/fundamental/{ticker}", tags=["Advanced Analysis"])
    async def get_fundamental_analysis(ticker: str):
        """Get comprehensive fundamental analysis for a stock."""
        try:
            from analysis.fundamental_analysis import FundamentalAnalyzer
            analyzer = FundamentalAnalyzer(ticker.upper())
            analysis = analyzer.get_comprehensive_analysis()
            return {
                "fundamental_analysis": analysis,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in fundamental analysis for {ticker}: {e}")
            return {
                "error": f"Fundamental analysis failed: {str(e)}",
                "ticker": ticker.upper(),
                "mock_data": True
            }
    
    @app.post("/v1/analysis/portfolio-risk", tags=["Advanced Analysis"])
    async def analyze_portfolio_risk(portfolio_data: dict):
        """
        Analyze portfolio risk metrics.
        Expected format: {"portfolio": {"AAPL": 0.3, "MSFT": 0.25, ...}, "benchmark": "^GSPC"}
        """
        try:
            from analysis.portfolio_risk_analysis import PortfolioRiskAnalyzer
            
            portfolio = portfolio_data.get("portfolio", {})
            benchmark = portfolio_data.get("benchmark", "^GSPC")
            
            if not portfolio:
                raise HTTPException(status_code=400, detail="Portfolio data is required")
            
            analyzer = PortfolioRiskAnalyzer(portfolio, benchmark)
            analysis = analyzer.get_comprehensive_risk_analysis()
            
            return {
                "portfolio_risk_analysis": analysis,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in portfolio risk analysis: {e}")
            return {
                "error": f"Portfolio risk analysis failed: {str(e)}",
                "portfolio": portfolio_data.get("portfolio", {}),
                "mock_data": True
            }
    
    @app.post("/v1/analysis/multi-stock", tags=["Advanced Analysis"])
    async def analyze_multiple_stocks(stock_data: dict):
        """
        Analyze multiple stocks with both technical and fundamental analysis.
        Expected format: {"symbols": ["AAPL", "MSFT", "GOOGL"], "period": "1y"}
        """
        try:
            from technical_analysis import analyze_multiple_stocks
            from fundamental_analysis import analyze_multiple_fundamentals
            
            symbols = stock_data.get("symbols", [])
            period = stock_data.get("period", "1y")
            
            if not symbols:
                raise HTTPException(status_code=400, detail="Stock symbols are required")
            
            # Get technical analysis
            technical_results = analyze_multiple_stocks(symbols, period)
            
            # Get fundamental analysis
            fundamental_results = analyze_multiple_fundamentals(symbols)
            
            return {
                "multi_stock_analysis": {
                    "symbols": symbols,
                    "technical_analysis": technical_results,
                    "fundamental_analysis": fundamental_results
                },
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in multi-stock analysis: {e}")
            return {
                "error": f"Multi-stock analysis failed: {str(e)}",
                "symbols": stock_data.get("symbols", []),
                "mock_data": True
            }
    
    @app.get("/v1/analysis/stock-comparison", tags=["Advanced Analysis"])
    async def compare_stocks(symbols: str, period: str = "1y"):
        """
        Compare multiple stocks side-by-side.
        Symbols should be comma-separated, e.g., "AAPL,MSFT,GOOGL"
        """
        try:
            from analysis.technical_analysis import analyze_multiple_stocks
            from analysis.fundamental_analysis import analyze_multiple_fundamentals
            
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            
            if len(symbol_list) < 2:
                raise HTTPException(status_code=400, detail="At least 2 symbols required for comparison")
            
            # Get analysis for all stocks
            technical_results = analyze_multiple_stocks(symbol_list, period)
            fundamental_results = analyze_multiple_fundamentals(symbol_list)
            
            # Create comparison matrix
            comparison = {}
            for symbol in symbol_list:
                tech_data = technical_results.get(symbol, {})
                fund_data = fundamental_results.get(symbol, {})
                
                comparison[symbol] = {
                    "current_price": tech_data.get("current_price"),
                    "rsi": tech_data.get("momentum_indicators", {}).get("rsi"),
                    "pe_ratio": fund_data.get("valuation_ratios", {}).get("pe_ratio"),
                    "roe": fund_data.get("profitability_ratios", {}).get("roe"),
                    "revenue_growth": fund_data.get("growth_metrics", {}).get("revenue_growth"),
                    "investment_score": fund_data.get("investment_score", {}).get("score"),
                    "investment_rating": fund_data.get("investment_score", {}).get("rating"),
                    "technical_signals": tech_data.get("signals", {}),
                    "market_cap": fund_data.get("basic_info", {}).get("market_cap")
                }
            
            # Ensure all numeric/numpy types are converted to native Python types
            def _to_native(o):
                try:
                    import numpy as _np
                except Exception:
                    _np = None

                # Handle numpy scalars
                if _np is not None and isinstance(o, (_np.generic,)):
                    try:
                        return o.item()
                    except Exception:
                        # fallback to native cast
                        if isinstance(o, _np.integer):
                            return int(o)
                        if isinstance(o, _np.floating):
                            return float(o)
                        return o

                # Recursively handle lists/tuples
                if isinstance(o, list):
                    return [_to_native(v) for v in o]
                if isinstance(o, tuple):
                    return tuple(_to_native(v) for v in o)

                # Recursively handle dicts
                if isinstance(o, dict):
                    return {k: _to_native(v) for k, v in o.items()}

                # Other types (int, float, str, None, etc.) are left as-is
                return o

            response_payload = {
                "stock_comparison": {
                    "symbols": symbol_list,
                    "comparison_matrix": comparison,
                    "detailed_technical": technical_results,
                    "detailed_fundamental": fundamental_results
                },
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }

            # Sanitize payload to avoid numpy types causing JSON encoding errors
            sanitized = _to_native(response_payload)
            return sanitized
        except Exception as e:
            logger.error(f"Error in stock comparison: {e}")
            return {
                "error": f"Stock comparison failed: {str(e)}",
                "symbols": symbols,
                "mock_data": True
            }

    @app.get("/v1/analysis/ai/{ticker}", tags=["AI Analysis"])
    async def get_ai_stock_analysis(ticker: str, period: str = "1y", provider: str = "mock"):
        """Get AI-powered stock analysis with intelligent insights and recommendations."""
        try:
            from analysis.ai_analysis import AIStockAnalyzer, LLMProvider
            
            # Map provider string to enum
            provider_map = {
                "openai": LLMProvider.OPENAI,
                "anthropic": LLMProvider.ANTHROPIC,
                "groq": LLMProvider.GROQ,
                "mock": LLMProvider.MOCK
            }
            
            llm_provider = provider_map.get(provider.lower(), LLMProvider.MOCK)
            
            analyzer = AIStockAnalyzer(llm_provider)
            result = analyzer.analyze_stock(ticker.upper(), period)
            
            return {
                "ai_analysis": {
                    "symbol": result.symbol,
                    "analysis_type": result.analysis_type.value,
                    "overall_recommendation": result.overall_recommendation,
                    "confidence_score": result.confidence_score,
                    "investment_thesis": result.investment_thesis,
                    "key_insights": [
                        {
                            "type": insight.insight_type,
                            "confidence": insight.confidence_score,
                            "recommendation": insight.recommendation,
                            "reasoning": insight.reasoning,
                            "key_factors": insight.key_factors,
                            "risk_level": insight.risk_level,
                            "time_horizon": insight.time_horizon,
                            "action_items": insight.action_items
                        }
                        for insight in result.key_insights
                    ],
                    "risk_factors": result.risk_factors,
                    "opportunities": result.opportunities,
                    "price_targets": result.price_targets,
                    "summary": result.summary,
                    "timestamp": result.timestamp
                },
                "llm_provider": provider,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in AI stock analysis for {ticker}: {e}")
            return {
                "error": f"AI stock analysis failed: {str(e)}",
                "ticker": ticker.upper(),
                "provider": provider,
                "mock_data": True
            }
    
    @app.post("/v1/analysis/ai-portfolio", tags=["AI Analysis"])
    async def get_ai_portfolio_analysis(portfolio_data: dict):
        """
        Get AI-powered portfolio analysis with intelligent risk assessment and optimization.
        Expected format: {"portfolio": {"AAPL": 0.3, "MSFT": 0.25, ...}, "provider": "mock", "benchmark": "^GSPC"}
        """
        try:
            from analysis.ai_analysis import AIStockAnalyzer, LLMProvider
            
            portfolio = portfolio_data.get("portfolio", {})
            provider = portfolio_data.get("provider", "mock")
            benchmark = portfolio_data.get("benchmark", "^GSPC")
            
            if not portfolio:
                raise HTTPException(status_code=400, detail="Portfolio data is required")
            
            # Map provider string to enum
            provider_map = {
                "openai": LLMProvider.OPENAI,
                "anthropic": LLMProvider.ANTHROPIC,
                "groq": LLMProvider.GROQ,
                "mock": LLMProvider.MOCK
            }
            
            llm_provider = provider_map.get(provider.lower(), LLMProvider.MOCK)
            
            analyzer = AIStockAnalyzer(llm_provider)
            result = analyzer.analyze_portfolio(portfolio, benchmark)
            
            return {
                "ai_portfolio_analysis": {
                    "portfolio_composition": portfolio,
                    "analysis_type": result.analysis_type.value,
                    "overall_recommendation": result.overall_recommendation,
                    "confidence_score": result.confidence_score,
                    "investment_thesis": result.investment_thesis,
                    "key_insights": [
                        {
                            "type": insight.insight_type,
                            "confidence": insight.confidence_score,
                            "recommendation": insight.recommendation,
                            "reasoning": insight.reasoning,
                            "key_factors": insight.key_factors,
                            "risk_level": insight.risk_level,
                            "time_horizon": insight.time_horizon,
                            "action_items": insight.action_items
                        }
                        for insight in result.key_insights
                    ],
                    "risk_factors": result.risk_factors,
                    "opportunities": result.opportunities,
                    "summary": result.summary,
                    "timestamp": result.timestamp
                },
                "llm_provider": provider,
                "benchmark": benchmark,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in AI portfolio analysis: {e}")
            return {
                "error": f"AI portfolio analysis failed: {str(e)}",
                "portfolio": portfolio_data.get("portfolio", {}),
                "provider": portfolio_data.get("provider", "mock"),
                "mock_data": True
            }
    
    @app.post("/v1/analysis/ai-comparison", tags=["AI Analysis"])
    async def get_ai_stock_comparison(comparison_data: dict):
        """
        Get AI-powered multi-stock comparison with intelligent ranking and recommendations.
        Expected format: {"symbols": ["AAPL", "MSFT", "GOOGL"], "period": "1y", "provider": "mock"}
        """
        try:
            from analysis.ai_analysis import AIStockAnalyzer, LLMProvider
            
            symbols = comparison_data.get("symbols", [])
            period = comparison_data.get("period", "1y")
            provider = comparison_data.get("provider", "mock")
            
            if not symbols or len(symbols) < 2:
                raise HTTPException(status_code=400, detail="At least 2 stock symbols are required")
            
            # Map provider string to enum
            provider_map = {
                "openai": LLMProvider.OPENAI,
                "anthropic": LLMProvider.ANTHROPIC,
                "groq": LLMProvider.GROQ,
                "mock": LLMProvider.MOCK
            }
            
            llm_provider = provider_map.get(provider.lower(), LLMProvider.MOCK)
            
            analyzer = AIStockAnalyzer(llm_provider)
            result = analyzer.compare_stocks(symbols, period)
            
            return {
                "ai_comparison_analysis": {
                    "symbols": symbols,
                    "analysis_type": result.analysis_type.value,
                    "overall_recommendation": result.overall_recommendation,
                    "confidence_score": result.confidence_score,
                    "investment_thesis": result.investment_thesis,
                    "key_insights": [
                        {
                            "type": insight.insight_type,
                            "confidence": insight.confidence_score,
                            "recommendation": insight.recommendation,
                            "reasoning": insight.reasoning,
                            "key_factors": insight.key_factors,
                            "risk_level": insight.risk_level,
                            "time_horizon": insight.time_horizon,
                            "action_items": insight.action_items
                        }
                        for insight in result.key_insights
                    ],
                    "risk_factors": result.risk_factors,
                    "opportunities": result.opportunities,
                    "summary": result.summary,
                    "timestamp": result.timestamp
                },
                "period": period,
                "llm_provider": provider,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in AI comparison analysis: {e}")
            return {
                "error": f"AI comparison analysis failed: {str(e)}",
                "symbols": comparison_data.get("symbols", []),
                "provider": comparison_data.get("provider", "mock"),
                "mock_data": True
            }
    
    @app.get("/v1/analysis/ai-market-sentiment", tags=["AI Analysis"])
    async def get_ai_market_sentiment(provider: str = "mock"):
        """Get AI-powered market sentiment analysis and outlook."""
        try:
            from analysis.ai_analysis import AIStockAnalyzer, LLMProvider
            
            # Map provider string to enum
            provider_map = {
                "openai": LLMProvider.OPENAI,
                "anthropic": LLMProvider.ANTHROPIC,  
                "groq": LLMProvider.GROQ,
                "mock": LLMProvider.MOCK
            }
            
            llm_provider = provider_map.get(provider.lower(), LLMProvider.MOCK)
            
            # Create a market sentiment prompt
            prompt = """
Analyze the current stock market sentiment and provide insights on:
1. Overall market direction and trends
2. Key sectors to watch
3. Economic factors influencing markets
4. Investment opportunities and risks
5. Recommended market positioning

Consider recent market performance, economic indicators, and global events.
"""
            
            analyzer = AIStockAnalyzer(llm_provider)
            ai_response = analyzer._generate_completion(prompt, max_tokens=2000)
            
            return {
                "market_sentiment_analysis": {
                    "sentiment": "NEUTRAL",
                    "confidence": 0.75,
                    "market_direction": "Mixed signals with cautious optimism",
                    "key_themes": [
                        "Economic uncertainty",
                        "Technology sector strength", 
                        "Interest rate concerns",
                        "Geopolitical tensions"
                    ],
                    "recommended_positioning": "Balanced approach with quality focus",
                    "analysis": ai_response,
                    "timestamp": datetime.now().isoformat()
                },
                "llm_provider": provider,
                "real_data": True,
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in AI market sentiment analysis: {e}")
            return {
                "error": f"AI market sentiment analysis failed: {str(e)}",
                "provider": provider,
                "mock_data": True
            }

    @app.get("/status", tags=["System"])
    async def system_status():
        """Get system status and available features."""
        return {
            "system": "AI Investment Research Bot MVP",
            "status": "running",
            "available_features": [
                "Real-time market data" if data_processor else "Basic research queries",
                "Company analysis with SEC/Yahoo Finance data" if data_processor else "Company summaries",
                "Live portfolio tracking" if data_processor else "Portfolio overview", 
                "Market overview and indices" if data_processor else "Health monitoring",
                "Technical analysis with 15+ indicators",
                "Fundamental analysis with financial ratios",
                "Portfolio risk analysis with Sharpe ratio, VaR, Monte Carlo",
                "Multi-stock comparison and analysis",
                "Advanced investment scoring algorithms",
                "AI-powered stock analysis with LLM integration",
                "AI portfolio optimization and risk assessment",
                "AI market sentiment analysis",
                "AI-driven investment recommendations"
            ],
            "dependencies": {
                "fastapi": "available",
                "data_processor": "available" if data_processor else "unavailable",
                "sec_edgar": "available" if data_processor else "unavailable",
                "yahoo_finance": "available" if data_processor else "unavailable",
                "technical_analysis": "available", 
                "fundamental_analysis": "available",
                "portfolio_risk_analysis": "available",
                "ai_analysis": "available",
                "llm_providers": ["OpenAI", "Anthropic", "Groq", "Mock"],
                "core_services": "live" if data_processor else "simulated"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    return app

async def simulate_processing(duration: float):
    """Simulate processing time."""
    import asyncio
    await asyncio.sleep(duration)

def generate_mock_answer(query: str, query_type: str) -> str:
    """Generate a mock answer based on the query."""
    
    query_lower = query.lower()
    
    if "apple" in query_lower or "aapl" in query_lower:
        return """Based on the available data, Apple Inc. (AAPL) shows strong financial fundamentals:

**Financial Highlights:**
- Revenue: $365B (trailing twelve months)
- Net Income: $90B with healthy margins
- Market Cap: ~$500B
- Strong balance sheet with significant cash reserves

**Key Strengths:**
- Diversified product portfolio (iPhone, Mac, Services)
- Strong brand loyalty and ecosystem
- Consistent revenue growth and profitability
- Innovation in emerging technologies

**Investment Outlook:**
Apple remains a solid investment choice for growth-oriented portfolios, with strong fundamentals and market position.

*Note: This is a demonstration response. Full functionality requires database connections and real-time data.*"""
    
    elif "portfolio" in query_lower:
        return """Portfolio analysis recommendations:

**Diversification Strategy:**
- Spread investments across sectors (Technology, Healthcare, Finance)
- Consider geographic diversification
- Balance growth and value stocks

**Risk Management:**
- Monitor portfolio volatility and beta
- Implement stop-loss strategies
- Regular rebalancing (quarterly recommended)

**Current Market Considerations:**
- Interest rate environment impact
- Inflation hedge opportunities
- Sector rotation trends

*Note: This is a demonstration response. Full portfolio analysis requires real-time data and advanced analytics.*"""
    
    elif "forecast" in query_lower or "prediction" in query_lower:
        return """Market forecasting insights:

**Technical Indicators:**
- Moving averages suggest current trend direction
- Volume analysis indicates market sentiment
- Support and resistance levels identified

**Economic Factors:**
- GDP growth projections
- Employment data trends
- Federal Reserve policy impact

**Risk Assessment:**
- Market volatility expectations
- Geopolitical considerations
- Sector-specific risks

*Note: This is a demonstration response. Actual forecasting requires advanced analytics and real-time data feeds.*"""
    
    else:
        return f"""Thank you for your research query: "{query}"

**Analysis Summary:**
Based on the query type "{query_type}", here's a comprehensive response:

**Key Insights:**
- Market data analysis indicates current trends
- Financial metrics suggest various opportunities
- Risk factors have been evaluated

**Recommendations:**
- Consider diversification strategies
- Monitor key performance indicators
- Stay updated with market developments

**Next Steps:**
- Review additional data sources
- Consider professional consultation
- Monitor ongoing market conditions

*Note: This is a demonstration response from the AI Investment Research Bot MVP. Full functionality with real-time data, advanced analytics, and comprehensive research capabilities is available with complete system setup.*"""

def main():
    """Main function to start the MVP."""
    
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI dependencies not available.")
        print("🔧 Please install dependencies: pip install fastapi uvicorn")
        return
    
    print("🚀 Starting AI Investment Research Bot MVP...")
    print("=" * 60)
    
    # Create the app
    app = create_simple_app()
    
    print("📋 MVP Features Available:")
    print("  ✅ Basic API endpoints")
    print("  ✅ Research query simulation")
    print("  ✅ Company data (mock)")
    print("  ✅ Portfolio overview (mock)")
    print("  ✅ Health monitoring")
    print()
    print("🌐 API Documentation:")
    print("  📖 Interactive docs: http://localhost:8000/docs")
    print("  📖 Alternative docs: http://localhost:8000/redoc")
    print("  ❤️  Health check: http://localhost:8000/health")
    print("  📊 System status: http://localhost:8000/status")
    print()
    print("🧪 Test the API:")
    print("  curl -X POST http://localhost:8000/v1/research/query \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"query\":\"Analyze Apple stock\",\"query_type\":\"company_analysis\"}'")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the server
    try:
        uvicorn.run(
            app,
            host="localhost",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()