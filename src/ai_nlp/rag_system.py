"""
RAG (Retrieval-Augmented Generation) system for financial research queries
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import openai
from openai import AsyncOpenAI

from config.settings import settings, AIConfig
from src.models.vector_db import get_vector_db
from src.models.database import get_db_session
from src.models.postgresql import Company, NewsArticle, Filing

logger = logging.getLogger(__name__)


@dataclass
class QueryContext:
    """Context for a research query"""
    query: str
    user_id: str
    query_type: str
    filters: Dict[str, Any]
    max_results: int = 10
    include_news: bool = True
    include_filings: bool = True
    include_financials: bool = True


@dataclass
class RetrievedDocument:
    """A document retrieved for RAG context"""
    content: str
    source_type: str  # news, filing, financial_statement
    metadata: Dict[str, Any]
    relevance_score: float


@dataclass
class RAGResponse:
    """Response from RAG system"""
    answer: str
    sources: List[RetrievedDocument]
    confidence: float
    query: str
    response_time_ms: int
    metadata: Dict[str, Any]


class DocumentRetriever:
    """Retrieve relevant documents for queries"""
    
    def __init__(self):
        self.vector_db = get_vector_db()
    
    async def retrieve_documents(self, query_context: QueryContext) -> List[RetrievedDocument]:
        """Retrieve relevant documents for a query"""
        try:
            retrieved_docs = []
            
            # Build search filters based on query context
            where_filter = self._build_search_filters(query_context.filters)
            
            # Search vector database
            search_results = self.vector_db.search_similar(
                query=query_context.query,
                n_results=query_context.max_results * 2,  # Get more to filter and rank
                where_filter=where_filter
            )
            
            # Convert search results to RetrievedDocument objects
            for result in search_results[:query_context.max_results]:
                doc = RetrievedDocument(
                    content=result["document"],
                    source_type=result["metadata"].get("document_type", "unknown"),
                    metadata=result["metadata"],
                    relevance_score=result["similarity"]
                )
                retrieved_docs.append(doc)
            
            # Enhance with database context if needed
            enhanced_docs = await self._enhance_with_database_context(retrieved_docs, query_context)
            
            logger.info(f"Retrieved {len(enhanced_docs)} documents for query")
            return enhanced_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def _build_search_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build search filters for vector database"""
        where_filter = {}
        
        if "company_cik" in filters:
            where_filter["company_cik"] = filters["company_cik"]
        
        if "document_type" in filters:
            where_filter["document_type"] = filters["document_type"]
        
        if "source" in filters:
            where_filter["source"] = filters["source"]
        
        return where_filter if where_filter else None
    
    async def _enhance_with_database_context(self, docs: List[RetrievedDocument], 
                                           query_context: QueryContext) -> List[RetrievedDocument]:
        """Enhance retrieved documents with additional database context"""
        enhanced_docs = []
        
        with get_db_session() as db:
            for doc in docs:
                enhanced_doc = doc
                
                try:
                    # Add company context if available
                    if "company_cik" in doc.metadata:
                        company_cik = doc.metadata["company_cik"]
                        company = db.query(Company).filter(Company.cik == company_cik).first()
                        
                        if company:
                            enhanced_doc.metadata["company_name"] = company.name
                            enhanced_doc.metadata["company_sector"] = company.sector
                            enhanced_doc.metadata["company_industry"] = company.industry
                    
                    # Add temporal context
                    if "filing_date" in doc.metadata:
                        enhanced_doc.metadata["temporal_context"] = self._get_temporal_context(doc.metadata["filing_date"])
                    elif "published_at" in doc.metadata:
                        enhanced_doc.metadata["temporal_context"] = self._get_temporal_context(doc.metadata["published_at"])
                    
                except Exception as e:
                    logger.warning(f"Error enhancing document context: {str(e)}")
                
                enhanced_docs.append(enhanced_doc)
        
        return enhanced_docs
    
    def _get_temporal_context(self, date_str: str) -> str:
        """Get temporal context for a date"""
        try:
            if "T" in date_str:
                doc_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                doc_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            days_ago = (datetime.now() - doc_date).days
            
            if days_ago < 7:
                return "recent"
            elif days_ago < 30:
                return "this_month"
            elif days_ago < 90:
                return "last_quarter"
            elif days_ago < 365:
                return "this_year"
            else:
                return "historical"
        
        except Exception:
            return "unknown"


class ResponseGenerator:
    """Generate responses using LLM with retrieved context"""
    
    def __init__(self):
        self.client = None
        self.model_config = AIConfig.get_openai_config()
        
    async def initialize(self):
        """Initialize OpenAI client"""
        if self.model_config["api_key"]:
            self.client = AsyncOpenAI(api_key=self.model_config["api_key"])
        else:
            logger.warning("OpenAI API key not configured")
    
    async def generate_response(self, query: str, context_docs: List[RetrievedDocument],
                              query_type: str = "general") -> str:
        """Generate response using LLM with retrieved context"""
        if not self.client:
            await self.initialize()
        
        if not self.client:
            return "I'm sorry, but I cannot generate a response at this time due to configuration issues."
        
        try:
            # Build context from retrieved documents
            context = self._build_context_from_documents(context_docs)
            
            # Create prompt based on query type
            prompt = self._create_prompt(query, context, query_type)
            
            # Generate response
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(query_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.model_config["max_tokens"],
                temperature=self.model_config["temperature"]
            )
            
            answer = response.choices[0].message.content
            return answer
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}"
    
    def _build_context_from_documents(self, docs: List[RetrievedDocument]) -> str:
        """Build context string from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(docs):
            source_info = f"Source {i+1}"
            
            # Add source metadata
            if "company_name" in doc.metadata:
                source_info += f" - {doc.metadata['company_name']}"
            
            if doc.source_type == "news_article":
                source_info += " (News Article)"
                if "published_at" in doc.metadata:
                    source_info += f" - {doc.metadata['published_at'][:10]}"
                if "source" in doc.metadata:
                    source_info += f" from {doc.metadata['source']}"
                    
            elif doc.source_type == "sec_filing":
                source_info += " (SEC Filing)"
                if "form_type" in doc.metadata:
                    source_info += f" - {doc.metadata['form_type']}"
                if "filing_date" in doc.metadata:
                    source_info += f" - {doc.metadata['filing_date']}"
                    
            elif doc.source_type == "financial_statement":
                source_info += " (Financial Statement)"
                if "statement_type" in doc.metadata:
                    source_info += f" - {doc.metadata['statement_type']}"
                if "period_end" in doc.metadata:
                    source_info += f" - {doc.metadata['period_end']}"
            
            context_parts.append(f"{source_info}:\n{doc.content}\n")
        
        return "\n---\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, query_type: str) -> str:
        """Create prompt for LLM"""
        base_prompt = f"""
Based on the following context information, please answer the user's question about financial/investment research.

Context Information:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to fully answer the question, please indicate what additional information might be needed. Always cite your sources when making specific claims.
"""
        
        if query_type == "company_analysis":
            additional_instruction = """
Focus on providing insights about the company's financial health, business operations, recent developments, and investment considerations. Include relevant financial metrics, trends, and risk factors when available.
"""
        elif query_type == "market_analysis":
            additional_instruction = """
Focus on market trends, sector analysis, and broader economic factors. Compare companies or sectors when relevant and provide context about market conditions.
"""
        elif query_type == "risk_assessment":
            additional_instruction = """
Focus on identifying and analyzing potential risks, including financial risks, operational risks, regulatory risks, and market risks. Provide a balanced assessment of risk factors.
"""
        else:
            additional_instruction = """
Provide a well-reasoned analysis based on the available information. Structure your response clearly and support your conclusions with evidence from the provided context.
"""
        
        return base_prompt + additional_instruction
    
    def _get_system_prompt(self, query_type: str) -> str:
        """Get system prompt based on query type"""
        base_system = """
You are a knowledgeable financial research analyst AI assistant. Your role is to help users understand financial information, analyze companies and markets, and provide insights based on factual data.

Important guidelines:
1. Always base your responses on the provided context information
2. Clearly distinguish between facts and analysis/opinions
3. Cite specific sources when making claims
4. If information is insufficient, clearly state what additional data would be helpful
5. Avoid giving direct investment advice - focus on analysis and information
6. Be precise with financial figures and dates
7. Acknowledge limitations and uncertainties in the data
8. Use clear, professional language appropriate for financial analysis
"""
        
        if query_type == "company_analysis":
            return base_system + "\nSpecialize in company financial analysis, business model evaluation, and corporate performance assessment."
        elif query_type == "market_analysis":
            return base_system + "\nSpecialize in market trends, sector analysis, and macroeconomic factors affecting investments."
        elif query_type == "risk_assessment":
            return base_system + "\nSpecialize in identifying, analyzing, and communicating various types of investment and business risks."
        else:
            return base_system


class QueryProcessor:
    """Process and classify user queries"""
    
    def __init__(self):
        self.query_patterns = self._load_query_patterns()
    
    def _load_query_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for query classification"""
        return {
            "company_analysis": [
                "analyze", "analysis", "performance", "financials", "revenue", "profit",
                "earnings", "balance sheet", "income statement", "cash flow", "ratios",
                "growth", "margins", "debt", "equity", "valuation"
            ],
            "market_analysis": [
                "market", "sector", "industry", "trends", "outlook", "forecast",
                "comparison", "peers", "competitive", "macroeconomic", "economy"
            ],
            "risk_assessment": [
                "risk", "risks", "volatility", "uncertainty", "threats", "challenges",
                "regulatory", "compliance", "litigation", "debt", "leverage"
            ],
            "news_summary": [
                "news", "recent", "latest", "updates", "developments", "announcements",
                "press release", "media", "headlines"
            ],
            "financial_metrics": [
                "metrics", "kpi", "ratios", "indicators", "benchmarks", "compare",
                "pe ratio", "roa", "roe", "current ratio", "debt ratio"
            ]
        }
    
    def classify_query(self, query: str) -> str:
        """Classify query type based on content"""
        query_lower = query.lower()
        
        scores = {}
        for query_type, keywords in self.query_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[query_type] = score
        
        # Return the type with highest score, or 'general' if no clear match
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return "general"
    
    def extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters and parameters from query"""
        filters = {}
        
        # Extract company mentions (basic approach)
        # In production, you'd use the EntityExtractor here
        import re
        
        # Look for ticker symbols
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        tickers = re.findall(ticker_pattern, query)
        if tickers:
            filters["tickers"] = tickers
        
        # Look for time periods
        if any(word in query.lower() for word in ["recent", "latest", "last month", "this quarter"]):
            filters["time_period"] = "recent"
        elif any(word in query.lower() for word in ["historical", "past year", "annual"]):
            filters["time_period"] = "historical"
        
        # Look for specific document types
        if any(word in query.lower() for word in ["10-k", "10-q", "8-k", "filing"]):
            filters["document_type"] = "sec_filing"
        elif any(word in query.lower() for word in ["news", "article", "press"]):
            filters["document_type"] = "news_article"
        
        return filters


class RAGSystem:
    """Main RAG system orchestrating retrieval and generation"""
    
    def __init__(self):
        self.retriever = DocumentRetriever()
        self.generator = ResponseGenerator()
        self.query_processor = QueryProcessor()
    
    async def initialize(self):
        """Initialize the RAG system"""
        await self.generator.initialize()
    
    async def process_query(self, query_context: QueryContext) -> RAGResponse:
        """Process a complete research query"""
        start_time = datetime.now()
        
        try:
            # Classify query and extract additional filters
            query_type = self.query_processor.classify_query(query_context.query)
            extracted_filters = self.query_processor.extract_filters(query_context.query)
            
            # Merge filters
            combined_filters = {**query_context.filters, **extracted_filters}
            enhanced_context = QueryContext(
                query=query_context.query,
                user_id=query_context.user_id,
                query_type=query_type,
                filters=combined_filters,
                max_results=query_context.max_results,
                include_news=query_context.include_news,
                include_filings=query_context.include_filings,
                include_financials=query_context.include_financials
            )
            
            # Retrieve relevant documents
            retrieved_docs = await self.retriever.retrieve_documents(enhanced_context)
            
            if not retrieved_docs:
                answer = "I couldn't find relevant information to answer your query. This might be because the information isn't available in our database or your query needs to be more specific."
                confidence = 0.1
            else:
                # Generate response
                answer = await self.generator.generate_response(
                    query_context.query, 
                    retrieved_docs, 
                    query_type
                )
                
                # Calculate confidence based on retrieval quality
                avg_relevance = sum(doc.relevance_score for doc in retrieved_docs) / len(retrieved_docs)
                confidence = min(0.9, avg_relevance)  # Cap at 0.9
            
            # Calculate response time
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            response = RAGResponse(
                answer=answer,
                sources=retrieved_docs,
                confidence=confidence,
                query=query_context.query,
                response_time_ms=response_time,
                metadata={
                    "query_type": query_type,
                    "filters_used": combined_filters,
                    "num_sources": len(retrieved_docs),
                    "avg_relevance_score": avg_relevance if retrieved_docs else 0
                }
            )
            
            logger.info(f"Processed query in {response_time}ms with {len(retrieved_docs)} sources")
            return response
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {str(e)}")
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return RAGResponse(
                answer=f"I apologize, but I encountered an error while processing your query: {str(e)}",
                sources=[],
                confidence=0.0,
                query=query_context.query,
                response_time_ms=response_time,
                metadata={"error": str(e)}
            )
    
    async def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        # This could be enhanced with more sophisticated suggestion algorithms
        suggestions = []
        
        common_queries = [
            "Analyze the financial performance of",
            "What are the main risks for",
            "Compare the market position of",
            "What's the latest news about",
            "Show me the key financial metrics for",
            "What are the growth prospects for",
            "Analyze the sector trends in",
            "What are the competitive advantages of"
        ]
        
        partial_lower = partial_query.lower()
        
        for query_template in common_queries:
            if any(word in partial_lower for word in query_template.lower().split()[:3]):
                suggestions.append(query_template + " [company name]")
        
        return suggestions[:5]  # Return top 5 suggestions