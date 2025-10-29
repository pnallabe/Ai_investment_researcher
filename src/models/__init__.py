"""
Models package initialization
"""
from .database import (
    Base, engine, SessionLocal, get_db_session, get_db,
    neo4j_db, redis_db, init_databases, close_databases,
    get_database_status
)

from .postgresql import (
    Company, Ticker, DailyPrice, Filing, FinancialStatement,
    NewsArticle, UserQuery, Alert, EmbeddingMetadata
)

from .neo4j_models import (
    Neo4jCompanyModel, Neo4jFilingModel, Neo4jNewsModel,
    Neo4jPersonModel, Neo4jAnalyticsQueries, Neo4jDataLoader
)

from .vector_db import (
    VectorDatabase, vector_db, init_vector_database, get_vector_db
)

__all__ = [
    # Database connections
    'Base', 'engine', 'SessionLocal', 'get_db_session', 'get_db',
    'neo4j_db', 'redis_db', 'init_databases', 'close_databases',
    'get_database_status',
    
    # PostgreSQL models
    'Company', 'Ticker', 'DailyPrice', 'Filing', 'FinancialStatement',
    'NewsArticle', 'UserQuery', 'Alert', 'EmbeddingMetadata',
    
    # Neo4j models
    'Neo4jCompanyModel', 'Neo4jFilingModel', 'Neo4jNewsModel',
    'Neo4jPersonModel', 'Neo4jAnalyticsQueries', 'Neo4jDataLoader',
    
    # Vector database
    'VectorDatabase', 'vector_db', 'init_vector_database', 'get_vector_db'
]