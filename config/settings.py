"""
Configuration module for AI Investment Research Bot
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    env: str = "development"
    debug: bool = True
    
    # Server
    host: str = "localhost"
    port: int = 8000
    
    # Database URLs
    database_url: str = "postgresql://user:password@localhost:5432/investment_research"
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_url: str = "redis://localhost:6379/0"
    
    # ChromaDB (Vector Database)
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection_name: str = "investment_documents"
    
    # API Keys
    openai_api_key: str = ""
    alpha_vantage_api_key: str = ""
    news_api_key: str = ""
    sec_edgar_user_agent: str = "Investment Research Bot (contact@example.com)"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production-make-it-very-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit: int = 100  # requests per minute
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    # AI/NLP Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Data Ingestion
    batch_size: int = 100
    max_workers: int = 4
    retry_attempts: int = 3
    retry_delay: int = 5
    
    # WebSocket Settings
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    # File Upload Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".pdf", ".txt", ".csv", ".json"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


class DatabaseConfig:
    """Database connection configuration"""
    
    @staticmethod
    def get_postgres_url() -> str:
        return settings.DATABASE_URL
    
    @staticmethod
    def get_neo4j_config() -> dict:
        return {
            "uri": settings.NEO4J_URL,
            "user": settings.NEO4J_USER,
            "password": settings.NEO4J_PASSWORD
        }
    
    @staticmethod
    def get_redis_url() -> str:
        return settings.REDIS_URL


class AIConfig:
    """AI/ML model configuration"""
    
    @staticmethod
    def get_openai_config() -> dict:
        return {
            "api_key": settings.OPENAI_API_KEY,
            "max_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE
        }
    
    @staticmethod
    def get_embedding_model() -> str:
        return settings.EMBEDDING_MODEL


class SecurityConfig:
    """Security configuration"""
    
    @staticmethod
    def get_jwt_config() -> dict:
        return {
            "secret_key": settings.SECRET_KEY,
            "algorithm": settings.ALGORITHM,
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }