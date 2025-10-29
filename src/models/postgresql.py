"""
PostgreSQL SQLAlchemy models
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional

from .database import Base


class Company(Base):
    """Company entity model"""
    __tablename__ = "companies"
    
    company_id = Column(Integer, primary_key=True, index=True)
    cik = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    sector = Column(String(100))
    industry = Column(String(100))
    description = Column(Text)
    market_cap = Column(Float)
    enterprise_value = Column(Float)
    employees = Column(Integer)
    website = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tickers = relationship("Ticker", back_populates="company", cascade="all, delete-orphan")
    filings = relationship("Filing", back_populates="company", cascade="all, delete-orphan")
    prices = relationship("DailyPrice", back_populates="company", cascade="all, delete-orphan")
    financial_statements = relationship("FinancialStatement", back_populates="company", cascade="all, delete-orphan")
    news_articles = relationship("NewsArticle", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(cik='{self.cik}', name='{self.name}')>"


class Ticker(Base):
    """Stock ticker model"""
    __tablename__ = "tickers"
    
    ticker_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    exchange = Column(String(50))
    currency = Column(String(3), default="USD")
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="tickers")
    
    def __repr__(self):
        return f"<Ticker(symbol='{self.symbol}', exchange='{self.exchange}')>"


class DailyPrice(Base):
    """Daily stock price data"""
    __tablename__ = "daily_prices"
    
    price_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    ticker_symbol = Column(String(10), index=True, nullable=False)
    date = Column(Date, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    adj_close_price = Column(Float)
    volume = Column(Integer)
    daily_return = Column(Float)  # Percentage return for the day
    price_range = Column(Float)   # High - Low
    price_range_pct = Column(Float)  # (High - Low) / Open * 100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="prices")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('ix_daily_prices_company_date', 'company_id', 'date'),
        Index('ix_daily_prices_ticker_date', 'ticker_symbol', 'date'),
    )
    
    def __repr__(self):
        return f"<DailyPrice(ticker='{self.ticker_symbol}', date='{self.date}', close={self.close_price})>"


class Filing(Base):
    """SEC filing model"""
    __tablename__ = "filings"
    
    filing_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    accession_number = Column(String(20), unique=True, index=True, nullable=False)
    form_type = Column(String(10), nullable=False, index=True)
    filing_date = Column(Date, nullable=False, index=True)
    period_end = Column(Date)
    file_number = Column(String(20))
    description = Column(Text)
    url = Column(String(500))
    content = Column(Text)  # Extracted text content
    content_length = Column(Integer)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="filings")
    
    # Indexes
    __table_args__ = (
        Index('ix_filings_company_form_date', 'company_id', 'form_type', 'filing_date'),
    )
    
    def __repr__(self):
        return f"<Filing(accession='{self.accession_number}', form='{self.form_type}')>"


class FinancialStatement(Base):
    """Financial statement line items"""
    __tablename__ = "financial_statements"
    
    fs_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    filing_id = Column(Integer, ForeignKey("filings.filing_id"))
    statement_type = Column(String(50), nullable=False)  # balance_sheet, income_statement, cash_flow
    line_item = Column(String(255), nullable=False)
    value = Column(Float)
    period_end = Column(Date, nullable=False)
    period_type = Column(String(20))  # annual, quarterly
    units = Column(String(20))  # USD, shares, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="financial_statements")
    filing = relationship("Filing")
    
    # Indexes
    __table_args__ = (
        Index('ix_financial_statements_company_period', 'company_id', 'period_end'),
        Index('ix_financial_statements_line_item', 'statement_type', 'line_item'),
    )
    
    def __repr__(self):
        return f"<FinancialStatement(company_id={self.company_id}, item='{self.line_item}', value={self.value})>"


class NewsArticle(Base):
    """News article model"""
    __tablename__ = "news_articles"
    
    article_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    content = Column(Text)
    author = Column(String(255))
    source = Column(String(100), index=True)
    published_at = Column(DateTime(timezone=True), index=True)
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_label = Column(String(20))  # positive, negative, neutral
    word_count = Column(Integer)
    company_mentions = Column(Text)  # JSON array as text
    tags = Column(Text)  # JSON array as text
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="news_articles")
    
    # Indexes
    __table_args__ = (
        Index('ix_news_articles_company_published', 'company_id', 'published_at'),
        Index('ix_news_articles_source_published', 'source', 'published_at'),
        Index('ix_news_articles_sentiment', 'sentiment_label', 'published_at'),
    )
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', source='{self.source}')>"


class UserQuery(Base):
    """User query log for analytics and improvement"""
    __tablename__ = "user_queries"
    
    query_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))  # Can be session ID or actual user ID
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # research, company_analysis, market_overview, etc.
    response_text = Column(Text)
    response_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    context_companies = Column(Text)  # JSON array of company CIKs used in response
    context_documents = Column(Text)  # JSON array of document IDs used
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_user_queries_user_created', 'user_id', 'created_at'),
        Index('ix_user_queries_type_created', 'query_type', 'created_at'),
    )
    
    def __repr__(self):
        return f"<UserQuery(query='{self.query_text[:50]}...', type='{self.query_type}')>"


class Alert(Base):
    """User alerts and notifications"""
    __tablename__ = "alerts"
    
    alert_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    alert_type = Column(String(50), nullable=False)  # price_change, filing, news, earnings
    condition = Column(Text)  # JSON configuration for alert conditions
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime(timezone=True))
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    
    # Indexes
    __table_args__ = (
        Index('ix_alerts_user_active', 'user_id', 'is_active'),
        Index('ix_alerts_company_type', 'company_id', 'alert_type'),
    )
    
    def __repr__(self):
        return f"<Alert(user='{self.user_id}', type='{self.alert_type}', active={self.is_active})>"


class EmbeddingMetadata(Base):
    """Metadata for vector embeddings"""
    __tablename__ = "embedding_metadata"
    
    embedding_id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), nullable=False)  # filing, news, financial_statement
    document_id = Column(Integer, nullable=False)  # Reference to the actual document
    chunk_index = Column(Integer)  # For documents split into chunks
    chunk_text = Column(Text)
    embedding_model = Column(String(100))  # Model used to create embedding
    vector_id = Column(String(100))  # ID in vector database
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_embedding_metadata_document', 'document_type', 'document_id'),
        Index('ix_embedding_metadata_vector', 'vector_id'),
    )
    
    def __repr__(self):
        return f"<EmbeddingMetadata(type='{self.document_type}', doc_id={self.document_id})>"