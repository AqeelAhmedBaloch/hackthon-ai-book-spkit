# Quickstart: Backend Entry Points

## Overview

The backend provides four required entry-point files:

1. **main.py**: FastAPI web server
2. **ingest.py**: Command-line ingestion tool
3. **agent.py**: Agent SDK wrapper
4. **config.py**: Environment configuration

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn python-dotenv requests beautifulsoup4 lxml
```

2. Set up environment configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Web API (main.py)
```bash
cd backend
python main.py
# Or with uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Manual Ingestion (ingest.py)
```bash
cd backend
python ingest.py https://example.com/sitemap.xml
python ingest.py https://example.com/sitemap.xml --type sitemap-index
python ingest.py https://example.com/sitemap.xml --output urls.txt
```

### Agent Wrapper (agent.py)
```bash
cd backend
python agent.py health
python agent.py process-sitemap https://example.com/sitemap.xml
python agent.py process-sitemap-index https://example.com/sitemap_index.xml
```

### Configuration (config.py)
```bash
cd backend
python config.py  # Shows current configuration
```

## Validation

Verify all required entry-point files exist:
```bash
ls -la backend/main.py backend/ingest.py backend/agent.py backend/config.py
```

Each file should import and use services from the services/ directory:
```bash
python -c "from main import app; from ingest import ingest_sitemap; from agent import AgentWrapper; import config; print('All entry points working correctly')"
```

## Environment Variables

The configuration system supports these environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: False)
- `INGESTION_TIMEOUT`: Request timeout in seconds (default: 30)
- `INGESTION_RATE_LIMIT`: Max requests per minute (default: 1000)
- `QDRANT_URL`: Qdrant vector database URL
- `QDRANT_API_KEY`: Qdrant API key
- And more as defined in config.py

## API Endpoints

When running the main.py server:

- `GET /` - Root endpoint to verify API is running
- `GET /health` - Health check
- `GET /api/v1/health` - API health check
- `POST /api/v1/ingest/sitemap` - Ingest a sitemap
- `POST /api/v1/ingest/sitemap-index` - Ingest a sitemap index

## Error Handling

All entry points include comprehensive error handling:

- Network errors are caught and logged
- Invalid URLs are handled gracefully
- Malformed sitemaps are skipped with appropriate logging
- Rate limiting is enforced according to configuration
- API endpoints return appropriate HTTP status codes

## Testing

Run the following to verify all components work correctly:

```bash
# Verify all files exist and import correctly
python -c "import main; import ingest; import agent; import config; print('All entry points import successfully')"

# Test service integration
python -c "from services.ingestion_service import IngestionService; print('Service imports correctly')"

# Test configuration loading
python config.py
```

## Deployment

For production deployment:

1. Set appropriate environment variables
2. Configure reverse proxy (e.g., nginx) if needed
3. Set up process monitoring
4. Configure logging aggregation
5. Set up health checks for your orchestration system