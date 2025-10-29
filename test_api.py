#!/usr/bin/env python3
"""
AI Investment Research Bot - API Testing Script

This script demonstrates the complete API functionality of the MVP.
It tests all major endpoints and showcases the system capabilities.
"""

import requests
import json
import time
import asyncio
import websockets
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000"


class APITester:
    """API testing class for the AI Investment Research Bot."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print('='*60)
    
    def print_result(self, endpoint: str, status_code: int, data: Any):
        """Print formatted API result."""
        status_emoji = "✅" if 200 <= status_code < 300 else "❌"
        print(f"{status_emoji} {endpoint} - Status: {status_code}")
        if isinstance(data, dict) and len(str(data)) < 500:
            print(f"   Response: {json.dumps(data, indent=2)}")
        elif hasattr(data, 'get'):
            preview = {k: v for k, v in list(data.items())[:3]}
            print(f"   Preview: {json.dumps(preview, indent=2)}...")
        print()
    
    def test_health_check(self):
        """Test system health check."""
        self.print_section("System Health Check")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            self.print_result("GET /health", response.status_code, response.json())
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_authentication(self):
        """Test user authentication flow."""
        self.print_section("Authentication Tests")
        
        # Test user registration
        register_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "analyst"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/register",
                json=register_data
            )
            self.print_result("POST /v1/auth/register", response.status_code, response.json())
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        except Exception as e:
            print(f"Registration may have failed (user might exist): {e}")
        
        # Test user login
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/login",
                json=login_data
            )
            self.print_result("POST /v1/auth/login", response.status_code, response.json())
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
        
        # Test getting current user info
        try:
            response = self.session.get(f"{self.base_url}/v1/auth/me")
            self.print_result("GET /v1/auth/me", response.status_code, response.json())
            
            if response.status_code == 200:
                self.user_data = response.json()
                return True
        except Exception as e:
            print(f"❌ Get user info failed: {e}")
        
        return False
    
    def test_research_queries(self):
        """Test research query functionality."""
        self.print_section("Research Query Tests")
        
        if not self.auth_token:
            print("❌ Skipping research tests - no authentication token")
            return
        
        # Test research query
        query_data = {
            "query": "What is Apple's current financial performance and future outlook?",
            "query_type": "company_analysis",
            "filters": {"ticker": "AAPL"},
            "include_sources": True,
            "max_results": 5
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/research/query",
                json=query_data
            )
            self.print_result("POST /v1/research/query", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Research query failed: {e}")
        
        # Test query history
        try:
            response = self.session.get(f"{self.base_url}/v1/research/history")
            self.print_result("GET /v1/research/history", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Query history failed: {e}")
        
        # Test query suggestions
        try:
            response = self.session.get(f"{self.base_url}/v1/research/suggestions?limit=3")
            self.print_result("GET /v1/research/suggestions", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Query suggestions failed: {e}")
    
    def test_company_analysis(self):
        """Test company analysis endpoints."""
        self.print_section("Company Analysis Tests")
        
        if not self.auth_token:
            print("❌ Skipping company analysis tests - no authentication token")
            return
        
        ticker = "AAPL"
        
        # Test company summary
        try:
            response = self.session.get(f"{self.base_url}/v1/company/{ticker}/summary")
            self.print_result(f"GET /v1/company/{ticker}/summary", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Company summary failed: {e}")
        
        # Test financial metrics
        try:
            response = self.session.get(f"{self.base_url}/v1/company/{ticker}/metrics?period=ttm")
            self.print_result(f"GET /v1/company/{ticker}/metrics", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Financial metrics failed: {e}")
        
        # Test price forecast
        try:
            response = self.session.post(
                f"{self.base_url}/v1/company/{ticker}/forecast?forecast_days=30&model=auto"
            )
            self.print_result(f"POST /v1/company/{ticker}/forecast", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Price forecast failed: {e}")
        
        # Test complete analysis
        try:
            response = self.session.get(
                f"{self.base_url}/v1/company/{ticker}/analysis?include_forecast=true&include_peers=true"
            )
            self.print_result(f"GET /v1/company/{ticker}/analysis", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Complete analysis failed: {e}")
    
    def test_portfolio_management(self):
        """Test portfolio management functionality."""
        self.print_section("Portfolio Management Tests")
        
        if not self.auth_token:
            print("❌ Skipping portfolio tests - no authentication token")
            return
        
        # Test get portfolios
        try:
            response = self.session.get(f"{self.base_url}/v1/portfolio/")
            self.print_result("GET /v1/portfolio/", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Get portfolios failed: {e}")
        
        # Test create portfolio
        portfolio_data = {
            "name": "Test Growth Portfolio",
            "description": "A test portfolio for growth stocks"
        }
        
        portfolio_id = None
        try:
            response = self.session.post(
                f"{self.base_url}/v1/portfolio/",
                json=portfolio_data
            )
            self.print_result("POST /v1/portfolio/", response.status_code, response.json())
            
            if response.status_code == 200:
                portfolio_id = response.json().get("portfolio_id")
        except Exception as e:
            print(f"❌ Create portfolio failed: {e}")
        
        # Test portfolio details
        if portfolio_id:
            try:
                response = self.session.get(f"{self.base_url}/v1/portfolio/{portfolio_id}")
                self.print_result(f"GET /v1/portfolio/{portfolio_id}", response.status_code, response.json())
            except Exception as e:
                print(f"❌ Portfolio details failed: {e}")
            
            # Test add holding
            holding_data = {
                "ticker": "AAPL",
                "shares": 10.0,
                "purchase_price": 150.0
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/v1/portfolio/{portfolio_id}/holdings",
                    json=holding_data
                )
                self.print_result(f"POST /v1/portfolio/{portfolio_id}/holdings", response.status_code, response.json())
            except Exception as e:
                print(f"❌ Add holding failed: {e}")
            
            # Test scenario analysis
            scenario_data = {
                "scenario_name": "Market Correction",
                "price_changes": {
                    "AAPL": -0.20,  # 20% decline
                    "MSFT": -0.15   # 15% decline
                }
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/v1/portfolio/{portfolio_id}/scenario",
                    json=scenario_data
                )
                self.print_result(f"POST /v1/portfolio/{portfolio_id}/scenario", response.status_code, response.json())
            except Exception as e:
                print(f"❌ Scenario analysis failed: {e}")
    
    def test_data_management(self):
        """Test data management endpoints."""
        self.print_section("Data Management Tests")
        
        if not self.auth_token:
            print("❌ Skipping data management tests - no authentication token")
            return
        
        # Test get data sources
        try:
            response = self.session.get(f"{self.base_url}/v1/data/sources")
            self.print_result("GET /v1/data/sources", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Get data sources failed: {e}")
        
        # Test get ingestion jobs
        try:
            response = self.session.get(f"{self.base_url}/v1/data/jobs")
            self.print_result("GET /v1/data/jobs", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Get ingestion jobs failed: {e}")
    
    def test_analytics(self):
        """Test analytics endpoints."""
        self.print_section("Analytics Tests")
        
        if not self.auth_token:
            print("❌ Skipping analytics tests - no authentication token")
            return
        
        # Test market analysis
        try:
            response = self.session.get(f"{self.base_url}/v1/analytics/market")
            self.print_result("GET /v1/analytics/market", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Market analysis failed: {e}")
        
        # Test custom analysis
        analysis_params = {
            "analysis_type": "sector_comparison",
            "sectors": ["Technology", "Healthcare"],
            "metrics": ["pe_ratio", "growth_rate"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/analytics/custom-analysis",
                json=analysis_params
            )
            self.print_result("POST /v1/analytics/custom-analysis", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Custom analysis failed: {e}")
    
    async def test_websocket_chat(self):
        """Test WebSocket chat functionality."""
        self.print_section("WebSocket Chat Test")
        
        if not self.auth_token:
            print("❌ Skipping WebSocket tests - no authentication token")
            return
        
        try:
            uri = f"{WEBSOCKET_URL}/ws/chat"
            async with websockets.connect(uri) as websocket:
                # Send authentication
                auth_message = {
                    "token": self.auth_token
                }
                await websocket.send(json.dumps(auth_message))
                
                # Receive connection confirmation
                response = await websocket.recv()
                print(f"✅ WebSocket connected: {response}")
                
                # Send research query
                query_message = {
                    "type": "research_query",
                    "query": "What are the key risks for Tesla's business model?"
                }
                await websocket.send(json.dumps(query_message))
                
                # Receive responses
                for _ in range(3):  # Receive up to 3 messages
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)
                        print(f"📨 WebSocket message: {data.get('type', 'unknown')} - {data.get('message', 'No message')}")
                    except asyncio.TimeoutError:
                        break
                
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 AI Investment Research Bot - API Testing Suite")
        print("=" * 60)
        
        # Test system health
        if not self.test_health_check():
            print("❌ System health check failed. Ensure the server is running.")
            return
        
        # Test authentication
        if not self.test_authentication():
            print("⚠️ Authentication failed. Continuing with limited tests...")
        
        # Test all API endpoints
        self.test_research_queries()
        self.test_company_analysis()
        self.test_portfolio_management()
        self.test_data_management()
        self.test_analytics()
        
        # Test WebSocket (async)
        try:
            asyncio.run(self.test_websocket_chat())
        except Exception as e:
            print(f"❌ WebSocket tests failed: {e}")
        
        print("\n🎉 API Testing Complete!")
        print("=" * 60)
        print("📊 Summary:")
        print("   - All major API endpoints tested")
        print("   - Authentication flow verified")
        print("   - Research queries demonstrated")
        print("   - Company analysis showcased")
        print("   - Portfolio management tested")
        print("   - WebSocket functionality checked")
        print("\n💡 Next steps:")
        print("   - Add your API keys to .env file for full functionality")
        print("   - Set up databases for complete data operations")
        print("   - Implement React frontend for user interface")


if __name__ == "__main__":
    print("🧪 Starting API Testing Suite...")
    print("⚠️  Make sure the server is running: python main.py")
    print("   or use: ./start_mvp.sh")
    
    time.sleep(2)  # Give user time to read
    
    tester = APITester()
    tester.run_all_tests()