# RAG System Deployment Instructions

## Overview

This document provides instructions for deploying the RAG (Retrieval-Augmented Generation) system that integrates with the Docusaurus-based book frontend.

## Prerequisites

### Backend Requirements
- Python 3.11+
- pip or uv package manager
- OpenAI API key
- Qdrant vector database (cloud or self-hosted)

### Frontend Requirements
- Node.js 18+
- npm or yarn package manager
- Docusaurus prerequisites

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo

# Qdrant Configuration
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here  # if required
QDRANT_COLLECTION=book_content

# Application Configuration
APP_TITLE=Book RAG System
APP_VERSION=1.0.0
DEBUG=false

# Agent Configuration
AGENT_TEMPERATURE=0.1
AGENT_MAX_TOKENS=1000
RETRIEVAL_TOP_K=5
SIMILARITY_THRESHOLD=0.7
CITATION_REQUIRED=true

# API Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend Environment Variables

Create a `.env` file in the `ai_frontend_book/` directory with the following variables:

```bash
# Backend API URL
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

## Backend Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackthon-ai-book-spkit
```

### 2. Set Up Backend Environment

```bash
cd backend

# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ingest Content

Before starting the service, you need to ingest your book content:

```bash
# Make sure your environment variables are set
source .env

# Run content ingestion
python -m src.content_ingestion.main /path/to/your/book/content
```

### 4. Start the Backend Service

```bash
cd backend
source .venv/bin/activate  # Activate your virtual environment
uvicorn src.rag_agent.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For production, consider using a process manager like systemd or Docker.

## Frontend Deployment

### 1. Install Dependencies

```bash
cd ai_frontend_book
npm install
```

### 2. Build the Site

```bash
npm run build
```

### 3. Serve the Site

```bash
npm run serve
```

## Docker Deployment (Optional)

### Backend Dockerfile

Create a `Dockerfile` in the `backend/` directory:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.rag_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run Backend Container

```bash
cd backend
docker build -t rag-backend .
docker run -d -p 8000:8000 --env-file .env rag-backend
```

## Configuration and Customization

### Content Ingestion Configuration

Adjust the content ingestion parameters in `backend/src/content_ingestion/models.py`:

- `chunk_size`: Size of content chunks (default: 512)
- `chunk_overlap`: Overlap between chunks (default: 50)
- `model`: Embedding model to use (default: "text-embedding-ada-002")

### Agent Configuration

Adjust the agent parameters in `backend/src/rag_agent/config.py`:

- `temperature`: Creativity of responses (lower = more factual)
- `max_tokens`: Maximum tokens in response
- `retrieval_top_k`: Number of results to retrieve
- `similarity_threshold`: Minimum similarity for relevance

## Monitoring and Maintenance

### Health Checks

The backend provides a health check endpoint:
- `GET /health` - Returns system health status

### Logging

Logs are written to stdout by default. Configure your deployment environment to capture and store logs as needed.

### Performance Monitoring

Monitor the following metrics:
- API response times
- Error rates
- Qdrant query performance
- Content ingestion performance

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured"**
   - Verify `OPENAI_API_KEY` is set in your environment variables
   - Check that the API key has the required permissions

2. **"Qdrant connection failed"**
   - Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
   - Check that the Qdrant service is running and accessible

3. **"No content found"**
   - Ensure content ingestion was completed successfully
   - Verify the correct collection name is being used

4. **"CORS errors"**
   - Check that `ALLOWED_ORIGINS` includes your frontend URL
   - Verify the frontend is making requests from an allowed origin

### Debugging

Enable debug mode by setting `DEBUG=true` in your environment variables. This will provide more detailed error messages but should not be used in production.

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple backend instances behind a load balancer
- Ensure Qdrant can handle the increased query load
- Consider using a message queue for heavy ingestion tasks

### Performance Optimization
- Use a CDN for frontend assets
- Implement caching for frequently accessed content
- Optimize embedding model usage based on query patterns

## Security Considerations

- Never commit API keys or sensitive configuration to version control
- Use environment variables or secure configuration management
- Implement proper authentication if required for your use case
- Regularly update dependencies to address security vulnerabilities