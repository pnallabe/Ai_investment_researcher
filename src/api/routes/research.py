"""
Research query API routes for the AI Investment Research Bot.

Handles intelligent research queries using the RAG system.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
import logging
import asyncio
from datetime import datetime

from src.models.postgresql import User
from src.ai_nlp.rag_system import RAGSystem, QueryContext, QueryResponse
from ..auth import get_current_active_user
from ..dependencies import get_rag_system, get_request_context, PaginationParams, get_pagination_params

logger = logging.getLogger(__name__)

research_router = APIRouter()


class ResearchQuery(BaseModel):
    """Research query request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Research question")
    query_type: str = Field(default="general", description="Type of query (general, company_analysis, market_analysis, etc.)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Query filters (ticker, sector, date range, etc.)")
    include_sources: bool = Field(default=True, description="Include source documents in response")
    max_results: int = Field(default=10, le=50, description="Maximum number of results to return")


class ResearchResponse(BaseModel):
    """Research query response model."""
    query_id: str
    query: str
    answer: str
    confidence_score: float
    processing_time: float
    sources: Optional[List[Dict[str, Any]]] = None
    related_queries: Optional[List[str]] = None
    metadata: Dict[str, Any]
    created_at: datetime


class QueryHistory(BaseModel):
    """Query history item model."""
    query_id: str
    query: str
    query_type: str
    answer_preview: str
    confidence_score: float
    created_at: datetime
    processing_time: float


class QueryHistoryResponse(BaseModel):
    """Query history response model."""
    queries: List[QueryHistory]
    total_count: int
    page: int
    page_size: int
    has_next: bool


@research_router.post("/query", response_model=ResearchResponse)
async def execute_research_query(
    query_data: ResearchQuery,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    rag_system: RAGSystem = Depends(get_rag_system),
    context: dict = Depends(get_request_context)
):
    """
    Execute an intelligent research query using the RAG system.
    
    Args:
        query_data: Research query data
        background_tasks: Background tasks for async processing
        current_user: Current authenticated user
        rag_system: RAG system instance
        context: Request context
        
    Returns:
        Research query response with answer and sources
    """
    try:
        start_time = datetime.utcnow()
        
        logger.info(
            f"Executing research query",
            extra={
                "user_id": str(current_user.id),
                "query": query_data.query,
                "query_type": query_data.query_type,
                "request_id": context.get("request_id")
            }
        )
        
        # Create query context
        query_context = QueryContext(
            query=query_data.query,
            user_id=str(current_user.id),
            query_type=query_data.query_type,
            filters=query_data.filters or {},
            max_results=query_data.max_results,
            include_sources=query_data.include_sources
        )
        
        # Execute query with timeout
        try:
            response = await asyncio.wait_for(
                rag_system.process_query(query_context),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Query processing timed out"
            )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Store query in history (background task)
        background_tasks.add_task(
            store_query_history,
            query_context,
            response,
            processing_time,
            current_user.id
        )
        
        # Prepare response
        research_response = ResearchResponse(
            query_id=response.query_id,
            query=query_data.query,
            answer=response.answer,
            confidence_score=response.confidence_score,
            processing_time=processing_time,
            sources=response.sources if query_data.include_sources else None,
            related_queries=response.related_queries,
            metadata=response.metadata,
            created_at=start_time
        )
        
        logger.info(
            f"Research query completed",
            extra={
                "user_id": str(current_user.id),
                "query_id": response.query_id,
                "confidence_score": response.confidence_score,
                "processing_time": processing_time,
                "request_id": context.get("request_id")
            }
        )
        
        return research_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Research query failed",
            extra={
                "user_id": str(current_user.id),
                "query": query_data.query,
                "error": str(e),
                "request_id": context.get("request_id")
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process research query"
        )


@research_router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    query_type: Optional[str] = None
):
    """
    Get user's query history.
    
    Args:
        current_user: Current authenticated user
        pagination: Pagination parameters
        query_type: Filter by query type
        
    Returns:
        Paginated query history
    """
    try:
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        mock_queries = [
            QueryHistory(
                query_id=f"query_{i}",
                query=f"Sample query {i}",
                query_type="general",
                answer_preview=f"This is a preview of answer {i}...",
                confidence_score=0.85,
                created_at=datetime.utcnow(),
                processing_time=1.5
            )
            for i in range(1, 21)
        ]
        
        # Apply query type filter
        if query_type:
            mock_queries = [q for q in mock_queries if q.query_type == query_type]
        
        # Apply pagination
        total_count = len(mock_queries)
        start_idx = pagination.offset
        end_idx = start_idx + pagination.limit
        paginated_queries = mock_queries[start_idx:end_idx]
        
        return QueryHistoryResponse(
            queries=paginated_queries,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=end_idx < total_count
        )
        
    except Exception as e:
        logger.error(f"Failed to get query history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve query history"
        )


@research_router.get("/query/{query_id}", response_model=ResearchResponse)
async def get_query_result(
    query_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific query result by ID.
    
    Args:
        query_id: Query identifier
        current_user: Current authenticated user
        
    Returns:
        Query result
    """
    try:
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        return ResearchResponse(
            query_id=query_id,
            query="Sample query",
            answer="This is a sample answer to the research query.",
            confidence_score=0.85,
            processing_time=1.5,
            sources=[
                {
                    "document_id": "doc_1",
                    "title": "Sample Document",
                    "content_snippet": "Relevant content snippet...",
                    "relevance_score": 0.9,
                    "source_type": "filing"
                }
            ],
            related_queries=["Related query 1", "Related query 2"],
            metadata={"tokens_used": 150, "model": "gpt-4"},
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get query result: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve query result"
        )


@research_router.post("/query/{query_id}/feedback")
async def submit_query_feedback(
    query_id: str,
    feedback_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit feedback for a query result.
    
    Args:
        query_id: Query identifier
        feedback_data: Feedback data (rating, comments, etc.)
        current_user: Current authenticated user
        
    Returns:
        Success response
    """
    try:
        # Validate feedback data
        rating = feedback_data.get("rating")
        if rating is not None and (rating < 1 or rating > 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Store feedback (would be implemented with database)
        logger.info(
            f"Query feedback submitted",
            extra={
                "user_id": str(current_user.id),
                "query_id": query_id,
                "rating": rating,
                "has_comments": bool(feedback_data.get("comments"))
            }
        )
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@research_router.get("/suggestions")
async def get_query_suggestions(
    current_user: User = Depends(get_current_active_user),
    query_prefix: Optional[str] = None,
    limit: int = 5
):
    """
    Get query suggestions based on user input or history.
    
    Args:
        current_user: Current authenticated user
        query_prefix: Partial query text for suggestions
        limit: Maximum number of suggestions
        
    Returns:
        List of query suggestions
    """
    try:
        # Sample suggestions (would be generated based on user history and common queries)
        suggestions = [
            "What is Apple's current debt-to-equity ratio?",
            "Analyze Tesla's revenue growth over the past 5 years",
            "Compare Microsoft and Google's profit margins",
            "What are the key risks for the semiconductor industry?",
            "Explain Amazon's recent earnings report"
        ]
        
        # Filter by prefix if provided
        if query_prefix:
            suggestions = [
                s for s in suggestions 
                if query_prefix.lower() in s.lower()
            ]
        
        return {"suggestions": suggestions[:limit]}
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get query suggestions"
        )


async def store_query_history(
    query_context: QueryContext,
    response: QueryResponse,
    processing_time: float,
    user_id: str
):
    """
    Store query and response in history (background task).
    
    Args:
        query_context: Original query context
        response: Query response
        processing_time: Processing time in seconds
        user_id: User ID
    """
    try:
        # In a real implementation, this would store in database
        logger.info(
            f"Storing query history",
            extra={
                "user_id": user_id,
                "query_id": response.query_id,
                "query_type": query_context.query_type,
                "processing_time": processing_time
            }
        )
        
        # Would implement database storage here
        # await store_in_database(query_context, response, processing_time, user_id)
        
    except Exception as e:
        logger.error(f"Failed to store query history: {e}", exc_info=True)
        # Don't raise exception as this is a background task