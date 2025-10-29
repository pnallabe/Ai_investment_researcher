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
    from fastapi import FastAPI, HTTPException, Form, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi import Header
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"FastAPI not available: {e}")
    FASTAPI_AVAILABLE = False

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
        """Get user portfolios (mock data)."""
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
    
    @app.get("/status", tags=["System"])
    async def system_status():
        """Get system status and available features."""
        return {
            "system": "AI Investment Research Bot MVP",
            "status": "running",
            "available_features": [
                "Basic research queries",
                "Company summaries",
                "Portfolio overview",
                "Health monitoring"
            ],
            "simulated_features": [
                "Database connections",
                "AI/NLP processing",
                "Real-time data feeds",
                "Advanced analytics"
            ],
            "next_steps": [
                "Install full dependencies for complete functionality",
                "Set up databases (PostgreSQL, Neo4j, ChromaDB)",
                "Add API keys for external services",
                "Implement React frontend"
            ]
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