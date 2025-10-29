"""
LLM integration and prompt management
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json
import asyncio

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """Request to LLM"""
    prompt: str
    system_prompt: str = ""
    max_tokens: int = 2000
    temperature: float = 0.1
    model: str = "gpt-3.5-turbo"


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    tokens_used: int
    response_time_ms: int
    metadata: Dict[str, Any] = None


class PromptTemplate:
    """Template for generating prompts"""
    
    def __init__(self, template: str, required_variables: List[str]):
        self.template = template
        self.required_variables = required_variables
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables"""
        missing_vars = [var for var in self.required_variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return self.template.format(**kwargs)


class PromptManager:
    """Manage prompts and templates for different tasks"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, PromptTemplate]:
        """Load prompt templates"""
        return {
            "company_analysis": PromptTemplate(
                template="""
Analyze the following company based on the provided financial and business information:

Company: {company_name}
Sector: {sector}
Industry: {industry}

Financial Data:
{financial_data}

Recent News and Developments:
{news_data}

SEC Filings Summary:
{filing_data}

Please provide a comprehensive analysis covering:
1. Financial Health and Performance
2. Business Strategy and Operations
3. Recent Developments and News Impact
4. Strengths and Competitive Advantages
5. Key Risks and Challenges
6. Investment Considerations

Be specific and cite the provided data sources. Highlight any notable trends or concerns.
""",
                required_variables=["company_name", "sector", "industry", "financial_data", "news_data", "filing_data"]
            ),
            
            "financial_summary": PromptTemplate(
                template="""
Provide a clear and concise summary of the following financial information:

Company: {company_name}
Period: {period}

Financial Metrics:
{metrics}

Key Financial Statement Items:
{financial_items}

Focus on:
1. Key performance indicators
2. Profitability trends
3. Financial position (liquidity, leverage)
4. Notable changes from previous periods
5. Areas of concern or strength

Present the information in a way that's accessible to both financial professionals and general investors.
""",
                required_variables=["company_name", "period", "metrics", "financial_items"]
            ),
            
            "risk_analysis": PromptTemplate(
                template="""
Analyze the risks associated with the following company based on the provided information:

Company: {company_name}
Business Description: {business_description}

Financial Information:
{financial_info}

Recent Developments:
{recent_developments}

Industry Context:
{industry_context}

Please identify and analyze:
1. Financial Risks (leverage, liquidity, profitability)
2. Operational Risks (business model, competition, execution)
3. Market Risks (sector trends, economic sensitivity)
4. Regulatory and Legal Risks
5. ESG and Reputation Risks

For each risk category, provide:
- Specific risk factors
- Potential impact level (High/Medium/Low)
- Likelihood assessment
- Mitigation factors or company responses

Conclude with an overall risk assessment and key monitoring points.
""",
                required_variables=["company_name", "business_description", "financial_info", "recent_developments", "industry_context"]
            ),
            
            "market_outlook": PromptTemplate(
                template="""
Provide a market outlook analysis based on the following information:

Sector/Industry: {sector}
Time Period: {time_period}

Market Data and Trends:
{market_data}

Key Companies and Developments:
{company_developments}

Economic Factors:
{economic_factors}

Regulatory Environment:
{regulatory_environment}

Please analyze:
1. Current Market Conditions and Trends
2. Growth Drivers and Headwinds
3. Key Players and Competitive Dynamics
4. Technology and Innovation Impact
5. Regulatory and Policy Implications
6. Investment Themes and Opportunities
7. Risk Factors and Challenges

Provide both short-term (6-12 months) and longer-term (2-3 years) perspectives.
""",
                required_variables=["sector", "time_period", "market_data", "company_developments", "economic_factors", "regulatory_environment"]
            ),
            
            "news_impact_analysis": PromptTemplate(
                template="""
Analyze the potential impact of recent news on the following company:

Company: {company_name}
Current Stock Price: {stock_price} (if available)

Recent News Articles:
{news_articles}

Company Background:
{company_background}

For each significant news item, analyze:
1. Nature and significance of the development
2. Potential impact on business operations
3. Financial implications (revenue, costs, profitability)
4. Market reaction and investor sentiment
5. Short-term vs long-term effects
6. Comparison to peer companies or industry trends

Conclude with:
- Overall impact assessment (Positive/Negative/Neutral)
- Key factors to monitor going forward
- Potential investment implications
""",
                required_variables=["company_name", "news_articles", "company_background"]
            ),
            
            "peer_comparison": PromptTemplate(
                template="""
Compare the following companies within their sector:

Primary Company: {primary_company}
Peer Companies: {peer_companies}
Sector: {sector}

Comparison Data:
{comparison_data}

Financial Metrics Comparison:
{metrics_comparison}

Please provide:
1. Relative Financial Performance
   - Revenue growth and profitability
   - Efficiency metrics
   - Financial position and leverage
   
2. Business Model and Strategy Comparison
   - Market positioning
   - Competitive advantages
   - Strategic initiatives
   
3. Valuation Analysis
   - Trading multiples comparison
   - Relative attractiveness
   
4. Risk Profile Comparison
   - Business risk factors
   - Financial risk levels
   
5. Investment Ranking and Rationale

Highlight the strengths and weaknesses of each company relative to peers.
""",
                required_variables=["primary_company", "peer_companies", "sector", "comparison_data", "metrics_comparison"]
            )
        }
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        return self.templates.get(template_name)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with provided variables"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        return template.format(**kwargs)


class LLMClient:
    """Client for interacting with language models"""
    
    def __init__(self):
        self.openai_client = None
        self.fallback_responses = self._load_fallback_responses()
    
    async def initialize(self):
        """Initialize LLM clients"""
        try:
            if settings.OPENAI_API_KEY:
                # Import here to avoid import errors if package not installed
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OpenAI API key not configured")
        except ImportError:
            logger.warning("OpenAI package not available")
        except Exception as e:
            logger.error(f"Error initializing LLM client: {str(e)}")
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using configured LLM"""
        start_time = datetime.now()
        
        try:
            if self.openai_client:
                response = await self._call_openai(request)
            else:
                # Fallback to rule-based response
                response = self._generate_fallback_response(request)
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            response.response_time_ms = response_time
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            
            # Return error response
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return LLMResponse(
                content=f"I apologize, but I'm unable to generate a response at this time: {str(e)}",
                model="error",
                tokens_used=0,
                response_time_ms=response_time,
                metadata={"error": str(e)}
            )
    
    async def _call_openai(self, request: LLMRequest) -> LLMResponse:
        """Call OpenAI API"""
        messages = []
        
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        messages.append({"role": "user", "content": request.prompt})
        
        response = await self.openai_client.chat.completions.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=request.model,
            tokens_used=response.usage.total_tokens,
            response_time_ms=0,  # Will be set by caller
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        )
    
    def _generate_fallback_response(self, request: LLMRequest) -> LLMResponse:
        """Generate fallback response when LLM is unavailable"""
        # Simple keyword-based response generation
        prompt_lower = request.prompt.lower()
        
        if any(word in prompt_lower for word in ["analyze", "analysis"]):
            if "company" in prompt_lower:
                content = self.fallback_responses["company_analysis"]
            elif "market" in prompt_lower or "sector" in prompt_lower:
                content = self.fallback_responses["market_analysis"]
            elif "risk" in prompt_lower:
                content = self.fallback_responses["risk_analysis"]
            else:
                content = self.fallback_responses["general_analysis"]
        
        elif any(word in prompt_lower for word in ["compare", "comparison"]):
            content = self.fallback_responses["comparison"]
        
        elif any(word in prompt_lower for word in ["forecast", "predict", "outlook"]):
            content = self.fallback_responses["forecast"]
        
        else:
            content = self.fallback_responses["default"]
        
        return LLMResponse(
            content=content,
            model="fallback",
            tokens_used=0,
            response_time_ms=0,
            metadata={"method": "fallback"}
        )
    
    def _load_fallback_responses(self) -> Dict[str, str]:
        """Load fallback responses for when LLM is unavailable"""
        return {
            "company_analysis": """
I understand you're looking for a company analysis. While I cannot provide a detailed AI-generated analysis at this time, I can offer some general guidance:

For comprehensive company analysis, consider examining:
1. Financial statements (income statement, balance sheet, cash flow)
2. Key financial ratios (profitability, liquidity, leverage, efficiency)
3. Recent SEC filings and earnings reports
4. Industry position and competitive advantages
5. Management quality and corporate governance
6. Recent news and market developments

Please check back later for enhanced AI-powered analysis capabilities.
""",
            
            "market_analysis": """
For market and sector analysis, I recommend examining:
1. Industry growth trends and forecasts
2. Key market drivers and challenges
3. Regulatory environment and policy changes
4. Competitive landscape and market share dynamics
5. Technology disruption and innovation trends
6. Economic factors affecting the sector

I'm currently unable to provide detailed AI analysis, but these factors should guide your research.
""",
            
            "risk_analysis": """
Risk analysis should consider multiple dimensions:
1. Financial risks: liquidity, credit, market, operational leverage
2. Business risks: competition, execution, market demand
3. Regulatory risks: compliance, policy changes
4. Environmental and social risks
5. Technology and disruption risks

For specific risk assessment, please consult detailed financial statements and industry reports.
""",
            
            "comparison": """
For company comparisons, focus on:
1. Financial performance metrics (growth, profitability, efficiency)
2. Business model differences
3. Market position and competitive advantages
4. Valuation multiples
5. Risk profiles
6. Strategic direction and management quality

Detailed comparative analysis requires access to comprehensive financial data.
""",
            
            "forecast": """
Financial forecasting involves:
1. Historical trend analysis
2. Industry growth projections
3. Company-specific factors and guidance
4. Economic environment considerations
5. Scenario analysis and sensitivity testing

For specific forecasts, please refer to company guidance, analyst reports, and detailed financial models.
""",
            
            "general_analysis": """
I understand you're seeking financial analysis. While detailed AI analysis is currently unavailable, I recommend:

1. Reviewing recent financial statements and SEC filings
2. Analyzing key performance metrics and trends
3. Considering industry context and competitive position
4. Evaluating recent news and developments
5. Consulting professional research reports

Please try again later for enhanced AI-powered analysis.
""",
            
            "default": """
I'm currently unable to provide detailed analysis due to system limitations. 

For financial research and analysis, I recommend:
1. Reviewing company financial statements and SEC filings
2. Analyzing industry reports and market research
3. Consulting professional investment research
4. Monitoring recent news and developments

Please check back later for enhanced AI capabilities.
"""
        }


class ConversationManager:
    """Manage conversation context and history"""
    
    def __init__(self, max_history: int = 10):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history = max_history
    
    def add_exchange(self, user_id: str, query: str, response: str, metadata: Dict[str, Any] = None):
        """Add a query-response exchange to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        exchange = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "response": response,
            "metadata": metadata or {}
        }
        
        self.conversations[user_id].append(exchange)
        
        # Trim history if too long
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]
    
    def get_conversation_context(self, user_id: str, last_n: int = 3) -> str:
        """Get recent conversation context for a user"""
        if user_id not in self.conversations:
            return ""
        
        recent_exchanges = self.conversations[user_id][-last_n:]
        
        context_parts = []
        for exchange in recent_exchanges:
            context_parts.append(f"Previous Query: {exchange['query']}")
            context_parts.append(f"Previous Response: {exchange['response'][:200]}...")  # Truncate
        
        return "\n".join(context_parts)
    
    def clear_conversation(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]