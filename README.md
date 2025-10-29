# AI Investment Research Bot

A comprehensive AI-powered investment research platform that automates data ingestion, analysis, and provides intelligent insights through a chat interface.

## Project Overview

This system implements the complete architecture described in the System Design Document (SDD), featuring:

- **Multi-source Data Ingestion**: SEC EDGAR filings, financial news, market data
- **Advanced Analytics**: Financial metrics computation, time-series forecasting, entity linking
- **AI-Powered Research**: RAG (Retrieval-Augmented Generation) system with LLM integration
- **Graph Database**: Neo4j for relationship mapping between entities
- **Vector Database**: ChromaDB for semantic search and document retrieval
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **React Frontend**: Modern TypeScript-based UI with Material-UI components
- **Real-time Chat Interface**: AI-powered research assistant with WebSocket support

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Frontend UI   │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • SEC EDGAR     │    │ • React Chat    │    │ • Prometheus    │
│ • News APIs     │◄───┤ • Dashboards    │    │ • Grafana       │
│ • Market Data   │    │ • Visualizations│    │ • Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Data Ingestion  │    │   FastAPI       │    │   Security      │
│                 │    │   Backend       │    │                 │
│ • ETL Pipelines │    │                 │    │ • JWT Auth      │
│ • Rate Limiting │◄───┤ • REST APIs     │    │ • Role-based    │
│ • Data Cleaning │    │ • WebSocket     │    │ • Encryption    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                │
│                                                                 │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │   PostgreSQL    │ │     Neo4j       │ │   ChromaDB      │   │
│ │                 │ │                 │ │                 │   │
│ │ • Companies     │ │ • Relationships │ │ • Embeddings    │   │
│ │ • Financials    │ │ • Graph Queries │ │ • Vector Search │   │
│ │ • News Articles │ │ • Entity Links  │ │ • Semantic Sim. │   │
│ │ • Price Data    │ │ • Network Anal. │ │ • RAG Context   │   │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Analytics Engine                              │
│                                                                 │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │ Financial       │ │ Time Series     │ │ Entity Linking  │   │
│ │ Metrics         │ │ Forecasting     │ │ & Extraction    │   │
│ │                 │ │                 │ │                 │   │
│ │ • Ratios        │ │ • Price Pred.   │ │ • NER           │   │
│ │ • Benchmarks    │ │ • Trend Anal.   │ │ • Relationships │   │
│ │ • Risk Assess.  │ │ • Seasonality   │ │ • Graph Build   │   │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI/NLP Layer                               │
│                                                                 │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │ RAG System      │ │ LLM Integration │ │ Query Processing│   │
│ │                 │ │                 │ │                 │   │
│ │ • Doc Retrieval │ │ • OpenAI GPT    │ │ • Classification│   │
│ │ • Context Build │ │ • Prompt Mgmt   │ │ • Intent Detect │   │
│ │ • Response Gen  │ │ • Conversation  │ │ • Filter Extract│   │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Implemented Modules

### ✅ 1. Project Structure & Configuration
- **Location**: `/config/`, `/docker/`, `/frontend/`, `requirements.txt`
- **Features**:
  - Environment configuration management
  - Docker containerization setup
  - Database connection configurations
  - React TypeScript frontend with Material-UI
  - Full-stack startup scripts and documentation

### ✅ 2. Data Ingestion Layer
- **Location**: `/src/data_ingestion/`
- **Modules**:
  - `base.py`: Abstract base classes for ingesters
  - `sec_edgar.py`: SEC EDGAR filings ingestion
  - `market_data.py`: Yahoo Finance & Alpha Vantage integration
  - `news.py`: RSS feeds & News API integration
  - `orchestrator.py`: Job scheduling and coordination
- **Features**:
  - Rate limiting and retry mechanisms
  - ETL pipeline with error handling
  - Batch processing capabilities
  - Data validation and cleaning

### ✅ 3. Database Models & Schemas
- **Location**: `/src/models/`
- **Components**:
  - `postgresql.py`: SQLAlchemy models for structured data
  - `neo4j_models.py`: Graph database operations
  - `vector_db.py`: ChromaDB vector database integration
  - `database.py`: Connection management
- **Features**:
  - Comprehensive data models for financial entities
  - Graph relationship mapping
  - Vector embedding storage
  - Database health monitoring

### ✅ 4. Analytics Engine
- **Location**: `/src/analytics/`
- **Modules**:
  - `financial_metrics.py`: 20+ financial ratios and metrics
  - `forecasting.py`: Multiple forecasting algorithms
  - `entity_linking.py`: Named entity recognition and linking
- **Features**:
  - Financial ratio computation and interpretation
  - Time series forecasting (SMA, exponential smoothing, linear regression)
  - Entity extraction and relationship mapping
  - Trend analysis and benchmarking

### ✅ 5. AI/NLP Layer with RAG
- **Location**: `/src/ai_nlp/`
- **Components**:
  - `rag_system.py`: Complete RAG implementation
  - `llm_integration.py`: OpenAI integration with fallbacks
- **Features**:
  - Semantic document retrieval
  - Context-aware response generation
  - Query classification and intent detection
  - Conversation management
  - Prompt templating system

### ✅ 6. FastAPI Backend Services
- **Location**: `/src/api/`
- **Components**:
  - `auth.py`: JWT authentication and user management
  - `routes/`: Comprehensive API endpoint modules
  - `middleware.py`: CORS, rate limiting, and security
  - `websocket.py`: Real-time communication support
- **Features**:
  - 25+ REST API endpoints for all system functions
  - JWT-based authentication with refresh tokens
  - Role-based access control and security middleware
  - Interactive API documentation with Swagger/OpenAPI
  - Real-time WebSocket connections for live updates

### ✅ 7. React Frontend Interface
- **Location**: `/frontend/`
- **Components**:
  - `src/pages/`: Login, Dashboard, Research, Portfolio, Companies, Analytics, Profile
  - `src/components/`: Reusable UI components with Material-UI
  - `src/services/`: API integration and authentication services
  - `src/hooks/`: Custom React hooks for state management
- **Features**:
  - Modern React 18 with TypeScript and Vite build system
  - Responsive Material-UI design system with custom theming
  - JWT authentication with automatic token refresh
  - Interactive AI research chat interface with real-time responses
  - Portfolio management dashboard with performance metrics
  - Company analysis tools with financial data visualization
  - Advanced analytics dashboard with risk assessment charts

## Key Features Implemented

### 🔄 Data Processing Pipeline
- **SEC EDGAR Integration**: Automated filing retrieval and content extraction
- **Market Data Feeds**: Real-time price data from multiple sources
- **News Aggregation**: Multi-source news ingestion with sentiment analysis
- **Data Orchestration**: Scheduled jobs with monitoring and error handling

### 📊 Financial Analytics
- **Metrics Engine**: 15+ financial ratios with industry benchmarking
- **Forecasting**: Multiple algorithms for price and financial metric prediction
- **Risk Assessment**: Comprehensive risk analysis framework
- **Trend Analysis**: Historical pattern recognition and extrapolation

### 🤖 AI-Powered Research
- **RAG System**: Retrieval-augmented generation for contextual responses
- **Entity Linking**: Automatic entity recognition and knowledge graph building
- **Semantic Search**: Vector-based document similarity and retrieval
- **Intelligent Querying**: Natural language query processing and routing

### 🗄️ Multi-Database Architecture
- **PostgreSQL**: Structured financial and company data
- **Neo4j**: Entity relationships and graph analytics  
- **ChromaDB**: Vector embeddings for semantic search
- **Redis**: Caching and session management

### ⚛️ Modern Frontend Interface
- **React 18 + TypeScript**: Type-safe component development
- **Material-UI Components**: Professional design system with responsive layout
- **Authentication System**: JWT-based login with automatic token refresh
- **Interactive Dashboard**: Portfolio overview with real-time metrics
- **AI Chat Interface**: Natural language research queries with context
- **Data Visualization**: Charts and analytics for portfolio insights
- **Real-time Updates**: WebSocket integration for live data feeds

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Neo4j 5.x
- Redis 7.x

### Environment Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Ai_investment_researcher
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys and database configurations
```

4. **Start services with Docker**:
```bash
docker-compose up -d
```

### 🚀 Quick Start (Full Stack)

The fastest way to get both backend and frontend running:

```bash
# Make the startup script executable
chmod +x start_fullstack.sh

# Start both backend and frontend
./start_fullstack.sh
```

This will:
- Start the simplified MVP backend on `http://localhost:8000`
- Start the React frontend on `http://localhost:3000`
- Provide demo credentials and API documentation links

**Demo Credentials:**
- Email: `demo@example.com`
- Password: `demo123`

**Access Points:**
- 🌐 **Frontend Application**: http://localhost:3000
- 📡 **Backend API**: http://localhost:8000  
- 📚 **API Documentation**: http://localhost:8000/docs

### Manual Setup

#### Backend Only
```bash
# Start simplified MVP backend
python mvp_simple.py
```

#### Frontend Only
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

5. **Initialize databases**:
```bash
python -c "from src.models.database import init_databases; init_databases()"
```

### Configuration

Edit `.env` file with your configurations:

```env
# Database URLs
DATABASE_URL=postgresql://user:password@localhost:5432/investment_research
NEO4J_URL=bolt://localhost:7687
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here

# Security
SECRET_KEY=your_secret_key_here
```

## Usage Examples

### Data Ingestion
```python
from src.data_ingestion import IngestionOrchestrator

# Initialize orchestrator
orchestrator = IngestionOrchestrator({})
orchestrator.setup_default_jobs()

# Run all ingestion jobs
results = await orchestrator.run_all_jobs()
```

### Financial Analysis
```python
from src.analytics import FinancialMetricsEngine

# Initialize metrics engine
engine = FinancialMetricsEngine()

# Compute financial metrics
financial_data = {...}  # From database
metrics = engine.compute_metrics(financial_data)
```

### AI Research Query
```python
from src.ai_nlp import RAGSystem, QueryContext

# Initialize RAG system
rag = RAGSystem()
await rag.initialize()

# Process research query
context = QueryContext(
    query="Analyze Apple's financial performance",
    user_id="analyst_1",
    query_type="company_analysis",
    filters={"company_cik": "0000320193"}
)

response = await rag.process_query(context)
print(response.answer)
```

## API Endpoints (Planned)

The system is designed with the following API structure:

- `POST /v1/query` - Execute research query (RAG)
- `GET /v1/company/{ticker}/summary` - Company analysis
- `POST /v1/ingest/filing` - Trigger filing ingestion
- `GET /v1/portfolio/impact` - Scenario impact analysis
- `POST /v1/alerts` - Manage user alerts

## Development Status

### ✅ Completed Modules
1. Project structure and configuration
2. Data ingestion layer (SEC, news, market data)
3. Database models and schemas (PostgreSQL, Neo4j, ChromaDB)
4. Analytics engine (metrics, forecasting, entity linking)
5. AI/NLP layer with RAG system

### 🚧 In Progress
6. FastAPI backend services
7. React frontend interface
8. Monitoring and security features

### 📋 Implementation Roadmap (Remaining 3 weeks)

**Week 6**: Complete FastAPI backend
- Authentication and authorization
- All API endpoints implementation
- WebSocket for real-time features
- API documentation

**Week 7**: React frontend development
- Chat interface for research queries
- Financial dashboards
- Data visualization components
- User management interface

**Week 8**: Final integration and deployment
- Monitoring and logging setup
- Security hardening
- Performance optimization
- Documentation and testing

## Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **Databases**: PostgreSQL, Neo4j, ChromaDB, Redis
- **AI/ML**: OpenAI GPT, Sentence Transformers, scikit-learn
- **Data Processing**: Pandas, NumPy, BeautifulSoup
- **Task Queue**: Celery with Redis

### Frontend (Planned)
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Material-UI
- **Charts**: Chart.js/D3.js
- **Real-time**: Socket.IO

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (production)
- **Monitoring**: Prometheus, Grafana
- **Logging**: Structured logging with JSON
- **Deployment**: AWS/GCP with CI/CD pipelines

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---

**Note**: This system is designed for research and analysis purposes. It should not be used as the sole basis for investment decisions. Always consult with qualified financial professionals and conduct your own due diligence.