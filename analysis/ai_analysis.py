"""
AI-Powered Stock Analysis Engine

This module provides intelligent investment analysis using Large Language Models (LLMs)
to generate insights, recommendations, and explanations based on technical and fundamental data.

Features:
- Multiple LLM provider support (OpenAI, Anthropic, Groq, Local models)
- Context-aware investment analysis
- Risk assessment and portfolio insights
- Market sentiment analysis
- Actionable investment recommendations
- Explanation of analysis reasoning
"""

import json
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import analysis modules
try:
    from technical_analysis import TechnicalAnalyzer
    from fundamental_analysis import FundamentalAnalyzer
    from portfolio_risk_analysis import PortfolioRiskAnalyzer
except ImportError:
    print("Warning: Analysis modules not found. AI engine will use mock data.")

# LLM integrations
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"
    MOCK = "mock"

class AnalysisType(Enum):
    STOCK_ANALYSIS = "stock_analysis"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    MARKET_OUTLOOK = "market_outlook"
    RISK_ASSESSMENT = "risk_assessment"
    COMPARISON_ANALYSIS = "comparison_analysis"

@dataclass
class AIInsight:
    insight_type: str
    confidence_score: float
    recommendation: str
    reasoning: str
    key_factors: List[str]
    risk_level: str
    time_horizon: str
    action_items: List[str]

@dataclass
class AIAnalysisResult:
    symbol: str
    analysis_type: AnalysisType
    timestamp: str
    overall_recommendation: str
    confidence_score: float
    investment_thesis: str
    key_insights: List[AIInsight]
    risk_factors: List[str]
    opportunities: List[str]
    price_targets: Dict[str, float]
    summary: str

class AIStockAnalyzer:
    """Main AI-powered stock analysis engine"""
    
    def __init__(self, provider: Union[LLMProvider, str] = LLMProvider.MOCK, api_key: Optional[str] = None):
        """
        Initialize AI Stock Analyzer
        
        Args:
            provider: LLM provider to use (enum or string)
            api_key: API key for the chosen provider
        """
        # Convert string to enum if needed
        if isinstance(provider, str):
            try:
                self.provider = LLMProvider(provider.lower())
            except ValueError:
                logger.warning(f"Unknown provider '{provider}', falling back to mock")
                self.provider = LLMProvider.MOCK
        else:
            self.provider = provider
            
        self.api_key = api_key or os.getenv(f"{self.provider.value.upper()}_API_KEY")
        self.client = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        try:
            if self.provider == LLMProvider.OPENAI and OPENAI_AVAILABLE:
                if self.api_key:
                    openai.api_key = self.api_key
                    self.client = openai
                    logger.info("OpenAI client initialized")
                else:
                    logger.warning("OpenAI API key not provided")
                    self.provider = LLMProvider.MOCK
            
            elif self.provider == LLMProvider.ANTHROPIC and ANTHROPIC_AVAILABLE:
                if self.api_key:
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                    logger.info("Anthropic client initialized")
                else:
                    logger.warning("Anthropic API key not provided")
                    self.provider = LLMProvider.MOCK
            
            elif self.provider == LLMProvider.GROQ and GROQ_AVAILABLE:
                if self.api_key:
                    self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
                    logger.info("Groq client initialized")
                else:
                    logger.warning("Groq API key not provided")
                    self.provider = LLMProvider.MOCK
            
            else:
                logger.info("Using mock AI analysis")
                self.provider = LLMProvider.MOCK
                
        except Exception as e:
            logger.error(f"Error initializing LLM client: {e}")
            self.provider = LLMProvider.MOCK
    
    def _generate_completion(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate completion using the configured LLM provider"""
        try:
            if self.provider == LLMProvider.OPENAI and self.client:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert financial analyst with deep knowledge of stock markets, technical analysis, and fundamental analysis. Provide detailed, actionable investment insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                return response.choices[0].message.content
            
            elif self.provider == LLMProvider.ANTHROPIC and self.client:
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tokens,
                    temperature=0.3,
                    system="You are an expert financial analyst with deep knowledge of stock markets, technical analysis, and fundamental analysis. Provide detailed, actionable investment insights.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == LLMProvider.GROQ and self.api_key:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "mixtral-8x7b-32768",
                    "messages": [
                        {"role": "system", "content": "You are an expert financial analyst with deep knowledge of stock markets, technical analysis, and fundamental analysis. Provide detailed, actionable investment insights."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                }
                
                response = requests.post(self.groq_endpoint, headers=headers, json=data)
                response.raise_for_status()
                
                return response.json()["choices"][0]["message"]["content"]
            
            else:
                # Mock response for demonstration
                return self._generate_mock_analysis(prompt)
                
        except Exception as e:
            logger.error(f"Error generating LLM completion: {e}")
            return self._generate_mock_analysis(prompt)
    
    def _generate_mock_analysis(self, prompt: str) -> str:
        """Generate mock AI analysis for demonstration"""
        if "AAPL" in prompt:
            return """
**Investment Analysis for Apple Inc. (AAPL)**

**Overall Recommendation: HOLD**
**Confidence: 75%**

**Investment Thesis:**
Apple demonstrates solid fundamental strength with its diversified revenue streams and strong brand moat. However, current valuation metrics suggest the stock is fairly valued to slightly overvalued, warranting a cautious approach.

**Key Technical Insights:**
- RSI at 61.18 indicates neutral momentum with slight bullish bias
- Price trading above key moving averages (SMA 20, SMA 50) confirms uptrend
- MACD showing bullish crossover signals potential continued momentum
- Bollinger Bands suggest stock is trading within normal volatility ranges

**Fundamental Strengths:**
- Strong market position in premium consumer electronics
- Excellent return on equity demonstrating efficient capital utilization
- Robust cash generation and healthy balance sheet
- Diversified revenue streams reducing single-product dependency

**Risk Factors:**
- High P/E ratio of 40.82 suggests premium valuation
- Cyclical nature of consumer electronics market
- Intense competition in smartphone and services markets
- Regulatory pressures in key markets

**Price Targets:**
- Conservative: $245 (support level)
- Fair Value: $265 (current technical resistance)
- Optimistic: $285 (breakout scenario)

**Action Items:**
1. Monitor Q4 earnings for services revenue growth
2. Watch for any supply chain disruption news
3. Track competitor product launches and market share data
4. Consider position sizing based on portfolio allocation limits
"""
        
        elif "portfolio" in prompt.lower():
            return """
**Portfolio Risk Assessment and Recommendations**

**Overall Portfolio Health: MODERATE RISK**
**Diversification Score: 7/10**

**Key Findings:**
Your portfolio demonstrates good diversification across technology leaders but shows concentration risk in the tech sector. The high Sharpe ratio of 4.32 indicates excellent risk-adjusted returns.

**Risk Analysis:**
- Portfolio Beta of 1.34 suggests higher volatility than market
- Maximum drawdown of -4.72% indicates relatively good downside protection
- Effective asset count of 5.9 shows reasonable diversification

**Recommendations:**
1. **Sector Diversification**: Consider adding positions in healthcare, consumer staples, or utilities to reduce tech concentration
2. **Geographic Diversification**: Add international exposure through emerging markets or developed international funds
3. **Risk Management**: Implement stop-loss orders at -15% below current positions
4. **Rebalancing**: Quarterly rebalancing recommended to maintain target allocations

**Optimization Opportunities:**
- Current allocation may benefit from slight reduction in highest-weight positions
- Consider adding defensive positions during market uncertainty
- ESG considerations could enhance long-term sustainability
"""
        
        else:
            return """
**AI-Powered Investment Analysis**

Based on the comprehensive technical and fundamental analysis provided, here are the key insights:

**Market Assessment:**
The current market environment shows mixed signals with technical indicators suggesting cautious optimism while fundamental metrics indicate fair to slightly overvalued conditions.

**Investment Recommendation:**
A balanced approach is recommended, focusing on quality companies with strong fundamentals and favorable technical setups.

**Key Considerations:**
1. Monitor macroeconomic factors affecting market sentiment
2. Focus on companies with strong competitive moats
3. Maintain appropriate risk management through diversification
4. Consider market timing for optimal entry/exit points

**Next Steps:**
Continue monitoring key indicators and adjust positions based on changing market conditions and company-specific developments.
"""
    
    def analyze_stock(self, symbol: str, period: str = "1y") -> AIAnalysisResult:
        """
        Perform comprehensive AI-powered stock analysis
        
        Args:
            symbol: Stock symbol to analyze
            period: Analysis period
            
        Returns:
            AIAnalysisResult with comprehensive AI insights
        """
        try:
            technical_data = {}
            fundamental_data = {}
            
            # Try to get technical analysis if available
            try:
                technical_analyzer = TechnicalAnalyzer(symbol, period)
                technical_data = technical_analyzer.get_all_indicators()
            except (NameError, ImportError):
                logger.info("Technical analysis not available, using mock data")
                technical_data = {"rsi": 65.0, "macd": "BULLISH", "sma_20": 250.0}
            
            # Try to get fundamental analysis if available
            try:
                fundamental_analyzer = FundamentalAnalyzer(symbol)
                fundamental_data = fundamental_analyzer.get_comprehensive_analysis()
            except (NameError, ImportError):
                logger.info("Fundamental analysis not available, using mock data")
                fundamental_data = {"pe_ratio": 30.0, "revenue_growth": 0.15, "debt_ratio": 0.3}
            
            # Create comprehensive analysis prompt
            prompt = self._create_stock_analysis_prompt(symbol, technical_data, fundamental_data)
            
            # Generate AI insights
            ai_response = self._generate_completion(prompt, max_tokens=3000)
            
            # Parse and structure the response
            analysis_result = self._parse_ai_response(symbol, ai_response, AnalysisType.STOCK_ANALYSIS)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in AI stock analysis for {symbol}: {e}")
            return self._create_fallback_analysis(symbol, AnalysisType.STOCK_ANALYSIS)
    
    def analyze_portfolio(self, portfolio: Dict[str, float], benchmark: str = "^GSPC") -> AIAnalysisResult:
        """
        Perform AI-powered portfolio analysis
        
        Args:
            portfolio: Dictionary of stock symbols and weights
            benchmark: Benchmark for comparison
            
        Returns:
            AIAnalysisResult with portfolio insights
        """
        try:
            # Get portfolio risk analysis
            risk_analyzer = PortfolioRiskAnalyzer(portfolio, benchmark)
            risk_data = risk_analyzer.get_comprehensive_risk_analysis()
            
            # Create portfolio analysis prompt
            prompt = self._create_portfolio_analysis_prompt(portfolio, risk_data)
            
            # Generate AI insights
            ai_response = self._generate_completion(prompt, max_tokens=3000)
            
            # Parse and structure the response
            analysis_result = self._parse_ai_response("PORTFOLIO", ai_response, AnalysisType.PORTFOLIO_ANALYSIS)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in AI portfolio analysis: {e}")
            return self._create_fallback_analysis("PORTFOLIO", AnalysisType.PORTFOLIO_ANALYSIS)
    
    def compare_stocks(self, symbols: List[str], period: str = "1y") -> AIAnalysisResult:
        """
        Perform AI-powered stock comparison analysis
        
        Args:
            symbols: List of stock symbols to compare
            period: Analysis period
            
        Returns:
            AIAnalysisResult with comparison insights
        """
        try:
            comparison_data = {}
            
            for symbol in symbols:
                # Get technical analysis
                technical_analyzer = TechnicalAnalyzer(symbol, period)
                technical_data = technical_analyzer.get_all_indicators()
                
                # Get fundamental analysis
                fundamental_analyzer = FundamentalAnalyzer(symbol)
                fundamental_data = fundamental_analyzer.get_comprehensive_analysis()
                
                comparison_data[symbol] = {
                    'technical': technical_data,
                    'fundamental': fundamental_data
                }
            
            # Create comparison analysis prompt
            prompt = self._create_comparison_analysis_prompt(symbols, comparison_data)
            
            # Generate AI insights
            ai_response = self._generate_completion(prompt, max_tokens=3500)
            
            # Parse and structure the response
            analysis_result = self._parse_ai_response(",".join(symbols), ai_response, AnalysisType.COMPARISON_ANALYSIS)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in AI comparison analysis: {e}")
            return self._create_fallback_analysis(",".join(symbols), AnalysisType.COMPARISON_ANALYSIS)
    
    def _create_stock_analysis_prompt(self, symbol: str, technical_data: Dict, fundamental_data: Dict) -> str:
        """Create detailed prompt for stock analysis"""
        return f"""
Analyze the stock {symbol} based on the following comprehensive data and provide detailed investment insights:

TECHNICAL ANALYSIS DATA:
- Current Price: ${technical_data.get('current_price', 'N/A')}
- RSI (14): {technical_data.get('momentum_indicators', {}).get('rsi', 'N/A')}
- MACD Signal: {technical_data.get('signals', {}).get('macd', 'N/A')}
- Moving Average Trend: {technical_data.get('signals', {}).get('ma_trend', 'N/A')}
- Bollinger Bands Signal: {technical_data.get('signals', {}).get('bollinger', 'N/A')}
- SMA 20: ${technical_data.get('moving_averages', {}).get('sma_20', 'N/A')}
- SMA 50: ${technical_data.get('moving_averages', {}).get('sma_50', 'N/A')}

FUNDAMENTAL ANALYSIS DATA:
- Company: {fundamental_data.get('basic_info', {}).get('company_name', 'N/A')}
- Sector: {fundamental_data.get('basic_info', {}).get('sector', 'N/A')}
- Market Cap: ${fundamental_data.get('basic_info', {}).get('market_cap', 'N/A')}
- P/E Ratio: {fundamental_data.get('valuation_ratios', {}).get('pe_ratio', 'N/A')}
- ROE: {fundamental_data.get('profitability_ratios', {}).get('roe', 'N/A')}
- Revenue Growth: {fundamental_data.get('growth_metrics', {}).get('revenue_growth', 'N/A')}
- Investment Score: {fundamental_data.get('investment_score', {}).get('score', 'N/A')}/100
- Current Rating: {fundamental_data.get('investment_score', {}).get('rating', 'N/A')}

Please provide:
1. **Overall Investment Recommendation** (BUY/HOLD/SELL) with confidence percentage
2. **Investment Thesis** - Clear reasoning for the recommendation
3. **Key Technical Insights** - What the technical indicators suggest
4. **Fundamental Strengths and Weaknesses** - Critical financial health factors
5. **Risk Factors** - Potential downside risks to consider
6. **Price Targets** - Conservative, fair value, and optimistic price levels
7. **Action Items** - Specific steps for investors to take
8. **Time Horizon** - Recommended holding period

Format your response in clear sections with actionable insights.
"""
    
    def _create_portfolio_analysis_prompt(self, portfolio: Dict[str, float], risk_data: Dict) -> str:
        """Create detailed prompt for portfolio analysis"""
        portfolio_summary = "\n".join([f"- {symbol}: {weight:.1%}" for symbol, weight in portfolio.items()])
        
        return f"""
Analyze this investment portfolio and provide comprehensive risk assessment and optimization recommendations:

PORTFOLIO COMPOSITION:
{portfolio_summary}

RISK ANALYSIS DATA:
- Annual Return: {risk_data.get('portfolio_statistics', {}).get('annual_return', 0):.2%}
- Annual Volatility: {risk_data.get('portfolio_statistics', {}).get('annual_volatility', 0):.2%}
- Sharpe Ratio: {risk_data.get('portfolio_statistics', {}).get('sharpe_ratio', 0):.2f}
- Maximum Drawdown: {risk_data.get('portfolio_statistics', {}).get('max_drawdown', 0):.2%}
- Portfolio Beta: {risk_data.get('beta', 'N/A')}
- Effective Number of Assets: {risk_data.get('diversification_metrics', {}).get('effective_assets', 0):.1f}
- Diversification Ratio: {risk_data.get('diversification_metrics', {}).get('diversification_ratio', 0):.2f}
- Value at Risk (5%): {risk_data.get('value_at_risk', {}).get('historical_var', 0):.2%}

RISK ASSESSMENT:
- Volatility Risk: {risk_data.get('risk_assessment', {}).get('volatility_risk', 'N/A')}
- Concentration Risk: {risk_data.get('risk_assessment', {}).get('concentration_risk', 'N/A')}
- Market Risk: {risk_data.get('risk_assessment', {}).get('market_risk', 'N/A')}

Please provide:
1. **Overall Portfolio Health Assessment** with risk rating
2. **Diversification Analysis** - Strengths and weaknesses in allocation
3. **Risk-Return Profile** - Assessment of risk-adjusted returns
4. **Optimization Recommendations** - Specific improvements to consider
5. **Sector and Geographic Diversification** - Gaps and opportunities
6. **Risk Management Strategies** - Hedging and protection recommendations
7. **Rebalancing Guidance** - When and how to adjust allocations
8. **Performance Expectations** - Realistic return and risk projections

Provide actionable recommendations for portfolio improvement.
"""
    
    def _create_comparison_analysis_prompt(self, symbols: List[str], comparison_data: Dict) -> str:
        """Create detailed prompt for stock comparison analysis"""
        comparison_summary = ""
        
        for symbol in symbols:
            tech_data = comparison_data[symbol]['technical']
            fund_data = comparison_data[symbol]['fundamental']
            
            comparison_summary += f"""
{symbol}:
- Price: ${tech_data.get('current_price', 'N/A')}
- RSI: {tech_data.get('momentum_indicators', {}).get('rsi', 'N/A')}
- P/E Ratio: {fund_data.get('valuation_ratios', {}).get('pe_ratio', 'N/A')}
- ROE: {fund_data.get('profitability_ratios', {}).get('roe', 'N/A')}
- Investment Score: {fund_data.get('investment_score', {}).get('score', 'N/A')}/100
- Rating: {fund_data.get('investment_score', {}).get('rating', 'N/A')}
- Sector: {fund_data.get('basic_info', {}).get('sector', 'N/A')}
"""
        
        return f"""
Compare and analyze these stocks to provide investment recommendations:

STOCK COMPARISON DATA:
{comparison_summary}

Please provide:
1. **Ranking and Recommendations** - Order stocks from best to worst investment opportunity
2. **Relative Valuation Analysis** - Which stocks offer better value
3. **Technical Comparison** - Which stocks have better technical setups
4. **Fundamental Comparison** - Strongest and weakest fundamental profiles
5. **Risk-Reward Assessment** - Risk-adjusted return potential for each
6. **Sector and Market Context** - How each fits in current market environment
7. **Portfolio Allocation Suggestions** - How to weight these stocks in a portfolio
8. **Investment Timing** - Which to buy now, which to wait on

Provide specific investment recommendations for each stock with clear reasoning.
"""
    
    def _parse_ai_response(self, symbol: str, ai_response: str, analysis_type: AnalysisType) -> AIAnalysisResult:
        """Parse AI response into structured analysis result"""
        try:
            # Extract key information from AI response
            # This is a simplified parser - in production, you'd want more sophisticated parsing
            
            lines = ai_response.split('\n')
            
            # Extract overall recommendation
            recommendation = "HOLD"
            confidence = 0.75
            
            for line in lines:
                if "BUY" in line.upper() and "RECOMMENDATION" in line.upper():
                    recommendation = "BUY"
                elif "SELL" in line.upper() and "RECOMMENDATION" in line.upper():
                    recommendation = "SELL"
                elif "confidence" in line.lower() and "%" in line:
                    try:
                        confidence = float([s for s in line.split() if '%' in s][0].replace('%', '')) / 100
                    except:
                        pass
            
            # Create structured insights
            key_insights = [
                AIInsight(
                    insight_type="technical_analysis",
                    confidence_score=0.8,
                    recommendation=recommendation,
                    reasoning="Based on technical indicators and price action analysis",
                    key_factors=["RSI levels", "Moving average trends", "Volume patterns"],
                    risk_level="MODERATE",
                    time_horizon="3-6 months",
                    action_items=["Monitor key support/resistance levels", "Watch for volume confirmation"]
                ),
                AIInsight(
                    insight_type="fundamental_analysis",
                    confidence_score=0.75,
                    recommendation=recommendation,
                    reasoning="Based on financial metrics and company fundamentals",
                    key_factors=["Valuation metrics", "Profitability trends", "Growth prospects"],
                    risk_level="MODERATE",
                    time_horizon="6-12 months",
                    action_items=["Review upcoming earnings", "Monitor sector trends"]
                )
            ]
            
            return AIAnalysisResult(
                symbol=symbol,
                analysis_type=analysis_type,
                timestamp=datetime.now().isoformat(),
                overall_recommendation=recommendation,
                confidence_score=confidence,
                investment_thesis=ai_response[:500] + "..." if len(ai_response) > 500 else ai_response,
                key_insights=key_insights,
                risk_factors=["Market volatility", "Sector-specific risks", "Economic uncertainties"],
                opportunities=["Technical breakout potential", "Fundamental improvements", "Market recovery"],
                price_targets={"conservative": 0.0, "fair_value": 0.0, "optimistic": 0.0},
                summary=ai_response
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._create_fallback_analysis(symbol, analysis_type)
    
    def _create_fallback_analysis(self, symbol: str, analysis_type: AnalysisType) -> AIAnalysisResult:
        """Create fallback analysis when AI processing fails"""
        return AIAnalysisResult(
            symbol=symbol,
            analysis_type=analysis_type,
            timestamp=datetime.now().isoformat(),
            overall_recommendation="HOLD",
            confidence_score=0.5,
            investment_thesis="Analysis temporarily unavailable. Please check back later.",
            key_insights=[],
            risk_factors=["Analysis system temporarily unavailable"],
            opportunities=["System will be restored shortly"],
            price_targets={"conservative": 0.0, "fair_value": 0.0, "optimistic": 0.0},
            summary="AI analysis is temporarily unavailable. Please try again later."
        )

# Utility functions for easy integration
def analyze_stock_with_ai(symbol: str, period: str = "1y", provider: LLMProvider = LLMProvider.MOCK) -> Dict:
    """
    Convenient function to analyze a stock with AI
    
    Args:
        symbol: Stock symbol
        period: Analysis period
        provider: LLM provider to use
        
    Returns:
        Dictionary with AI analysis results
    """
    analyzer = AIStockAnalyzer(provider)
    result = analyzer.analyze_stock(symbol, period)
    
    return {
        "symbol": result.symbol,
        "recommendation": result.overall_recommendation,
        "confidence": result.confidence_score,
        "summary": result.summary,
        "key_insights": [
            {
                "type": insight.insight_type,
                "recommendation": insight.recommendation,
                "reasoning": insight.reasoning,
                "confidence": insight.confidence_score
            }
            for insight in result.key_insights
        ],
        "risk_factors": result.risk_factors,
        "opportunities": result.opportunities,
        "timestamp": result.timestamp
    }

def analyze_portfolio_with_ai(portfolio: Dict[str, float], provider: LLMProvider = LLMProvider.MOCK) -> Dict:
    """
    Convenient function to analyze a portfolio with AI
    
    Args:
        portfolio: Portfolio composition
        provider: LLM provider to use
        
    Returns:
        Dictionary with AI portfolio analysis results
    """
    analyzer = AIStockAnalyzer(provider)
    result = analyzer.analyze_portfolio(portfolio)
    
    return {
        "portfolio": portfolio,
        "recommendation": result.overall_recommendation,
        "confidence": result.confidence_score,
        "summary": result.summary,
        "key_insights": [
            {
                "type": insight.insight_type,
                "recommendation": insight.recommendation,
                "reasoning": insight.reasoning,
                "confidence": insight.confidence_score
            }
            for insight in result.key_insights
        ],
        "risk_factors": result.risk_factors,
        "opportunities": result.opportunities,
        "timestamp": result.timestamp
    }

if __name__ == "__main__":
    # Example usage
    print("🤖 AI-Powered Stock Analysis Demo")
    print("=" * 60)
    
    # Test stock analysis
    analyzer = AIStockAnalyzer(LLMProvider.MOCK)
    
    print("📊 Analyzing AAPL...")
    result = analyzer.analyze_stock("AAPL", "1y")
    print(f"Recommendation: {result.overall_recommendation}")
    print(f"Confidence: {result.confidence_score:.1%}")
    print(f"Summary: {result.summary[:200]}...")
    
    print("\n📈 Analyzing Portfolio...")
    portfolio = {"AAPL": 0.3, "MSFT": 0.25, "GOOGL": 0.2, "TSLA": 0.15, "NVDA": 0.1}
    portfolio_result = analyzer.analyze_portfolio(portfolio)
    print(f"Portfolio Recommendation: {portfolio_result.overall_recommendation}")
    print(f"Confidence: {portfolio_result.confidence_score:.1%}")
    
    print("\n✅ AI Analysis Engine Demo Complete!")