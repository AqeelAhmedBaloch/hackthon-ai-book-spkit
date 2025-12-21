# Quickstart Guide: Content Ingestion & Embeddings

**Feature**: 5-content-ingestion
**Created**: 2025-12-21

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Cohere API key
- Qdrant Cloud account and API key

## Setup

### 1. Create Backend Directory
```bash
mkdir backend
cd backend
```

### 2. Initialize Project with UV
```bash
# Initialize new Python project
uv init

# Add required dependencies
uv add fastapi uvicorn python-dotenv cohere-sdk qdrant-client beautifulsoup4 aiohttp pydantic httpx
```

### 3. Set Up Environment Variables
Create a `.env` file in the backend directory:

```bash
cat > .env << EOF
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
ENVIRONMENT=development
LOG_LEVEL=info
EOF
```

## Project Structure

```
backend/
├── .env
├── pyproject.toml
├── main.py                 # FastAPI application entry point
├── settings.py             # Configuration management
├── models/
│   ├── __init__.py
│   ├── content_chunk.py    # Content chunk data model
│   ├── embedding.py        # Embedding vector model
│   └── ingestion.py        # Ingestion record model
├── services/
│   ├── __init__.py
│   ├── content_extractor.py # Content extraction service
│   ├── content_chunker.py   # Content chunking service
│   ├── embedding_service.py # Cohere integration
│   ├── vector_storage.py    # Qdrant integration
│   └── ingestion_manager.py # Main orchestration service
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── router.py       # API endpoints
├── utils/
│   ├── __init__.py
│   ├── validators.py       # Input validation utilities
│   └── helpers.py          # General utility functions
└── tests/
    ├── __init__.py
    ├── test_content_extractor.py
    └── test_embedding_service.py
```

## Core Implementation

### 1. Settings Configuration (`settings.py`)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    environment: str = "development"
    log_level: str = "info"
    chunk_size: int = 500  # tokens
    overlap_size: int = 50  # tokens
    embedding_model: str = "embed-multilingual-v3.0"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Main Application (`main.py`)
```python
from fastapi import FastAPI
from settings import settings
import uvicorn

app = FastAPI(
    title="Content Ingestion & Embeddings API",
    description="API for extracting content from Docusaurus sites, generating embeddings, and storing in Qdrant",
    version="1.0.0"
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-12-21T00:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
```

## Running the Service

### Development
```bash
# Install dependencies
uv sync

# Run the service
uv run python main.py
```

### Alternative Development (using uvicorn directly)
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage Example

### Start an Ingestion
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example-docusaurus-site.com",
    "chunk_size": 500,
    "overlap_size": 50
  }'
```

### Check Ingestion Status
```bash
curl -X GET http://localhost:8000/api/v1/ingest/{ingestion_id}
```

## Testing

### Run Tests
```bash
# Install test dependencies
uv add pytest pytest-asyncio httpx

# Run tests
uv run pytest tests/ -v
```

## Environment Configuration

### Production Environment
For production deployment, ensure these environment variables are set securely:

```bash
COHERE_API_KEY=your_production_cohere_api_key
QDRANT_URL=your_production_qdrant_url
QDRANT_API_KEY=your_production_qdrant_api_key
ENVIRONMENT=production
LOG_LEVEL=warning
```

## Next Steps

1. Implement the content extraction service
2. Build the embedding generation service
3. Create the Qdrant storage integration
4. Develop the ingestion orchestration logic
5. Add comprehensive error handling and logging
6. Implement the API endpoints as defined in the contract