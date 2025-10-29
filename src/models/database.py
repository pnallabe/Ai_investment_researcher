"""
Database connection and configuration
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from neo4j import GraphDatabase
import redis
from contextlib import contextmanager
from typing import Generator

from config.settings import settings, DatabaseConfig

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_engine(
    DatabaseConfig.get_postgres_url(),
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get database session with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Neo4j setup
class Neo4jConnection:
    """Neo4j database connection manager"""
    
    def __init__(self):
        self.driver = None
        self.config = DatabaseConfig.get_neo4j_config()
    
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.config["uri"],
                auth=(self.config["user"], self.config["password"])
            )
            logger.info("Connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def execute_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query"""
        if not self.driver:
            self.connect()
        
        with self.driver.session() as session:
            return session.run(query, parameters or {})
    
    def execute_write_query(self, query: str, parameters: dict = None):
        """Execute a write Cypher query"""
        if not self.driver:
            self.connect()
        
        with self.driver.session() as session:
            return session.write_transaction(
                lambda tx: tx.run(query, parameters or {})
            )


# Global Neo4j connection instance
neo4j_db = Neo4jConnection()


# Redis setup
class RedisConnection:
    """Redis connection manager"""
    
    def __init__(self):
        self.client = None
        self.url = DatabaseConfig.get_redis_url()
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(self.url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    def get_client(self):
        """Get Redis client"""
        if not self.client:
            self.connect()
        return self.client
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            logger.info("Redis connection closed")


# Global Redis connection instance
redis_db = RedisConnection()


def init_databases():
    """Initialize all database connections"""
    try:
        # Create PostgreSQL tables
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL tables created/verified")
        
        # Connect to Neo4j
        neo4j_db.connect()
        
        # Connect to Redis
        redis_db.connect()
        
        # Initialize Neo4j constraints and indexes
        init_neo4j_schema()
        
        logger.info("All databases initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def init_neo4j_schema():
    """Initialize Neo4j schema with constraints and indexes"""
    
    schema_queries = [
        # Constraints
        "CREATE CONSTRAINT company_cik IF NOT EXISTS FOR (c:Company) REQUIRE c.cik IS UNIQUE",
        "CREATE CONSTRAINT ticker_symbol IF NOT EXISTS FOR (t:Ticker) REQUIRE t.symbol IS UNIQUE",
        "CREATE CONSTRAINT filing_accession IF NOT EXISTS FOR (f:Filing) REQUIRE f.accession_number IS UNIQUE",
        "CREATE CONSTRAINT article_url IF NOT EXISTS FOR (a:Article) REQUIRE a.url IS UNIQUE",
        
        # Indexes
        "CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name)",
        "CREATE INDEX filing_date IF NOT EXISTS FOR (f:Filing) ON (f.filing_date)",
        "CREATE INDEX article_published IF NOT EXISTS FOR (a:Article) ON (a.published_at)",
        "CREATE INDEX price_date IF NOT EXISTS FOR (p:Price) ON (p.date)",
    ]
    
    for query in schema_queries:
        try:
            neo4j_db.execute_query(query)
            logger.debug(f"Executed Neo4j schema query: {query}")
        except Exception as e:
            logger.warning(f"Failed to execute schema query '{query}': {str(e)}")


def close_databases():
    """Close all database connections"""
    try:
        neo4j_db.close()
        redis_db.close()
        logger.info("All database connections closed")
    except Exception as e:
        logger.error(f"Error closing databases: {str(e)}")


# Database health check functions
def check_postgres_health() -> bool:
    """Check PostgreSQL connection health"""
    try:
        with get_db_session() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {str(e)}")
        return False


def check_neo4j_health() -> bool:
    """Check Neo4j connection health"""
    try:
        result = neo4j_db.execute_query("RETURN 1 as health")
        return result.single()["health"] == 1
    except Exception as e:
        logger.error(f"Neo4j health check failed: {str(e)}")
        return False


def check_redis_health() -> bool:
    """Check Redis connection health"""
    try:
        client = redis_db.get_client()
        return client.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False


def get_database_status() -> dict:
    """Get status of all databases"""
    return {
        "postgresql": check_postgres_health(),
        "neo4j": check_neo4j_health(),
        "redis": check_redis_health()
    }