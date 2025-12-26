# Quickstart Guide: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book

**Feature**: 004-qdrant-rag-chatbot
**Date**: 2025-12-26

## Overview

This guide provides instructions to set up and run the RAG chatbot system that answers questions from Physical AI & Humanoid Robotics book content stored in Qdrant.

## Prerequisites

- Python 3.11+
- `uv` package manager (or pip)
- Access to Cohere API
- Access to Qdrant Cloud
- Book sitemap.xml accessible via HTTP

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
# Navigate to your project directory
cd path/to/project
```

### 2. Create Backend Directory Structure

```bash
mkdir -p backend/src/{models,services,utils}
mkdir -p backend/tests/{unit,integration,contract}
```

### 3. Set up Python Environment

```bash
cd backend
uv venv  # or python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Create pyproject.toml

```toml
[project]
name = "rag-chatbot"
version = "0.1.0"
description = "RAG Chatbot for Physical AI & Humanoid Robotics Book"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "python-dotenv>=1.0.0",
    "cohere>=5.0.0",
    "qdrant-client>=1.7.0",
    "anthropic>=0.21.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
    "trafilatura>=1.6.0",
    "pytest>=7.4.0",
    "pydantic>=2.5.0"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### 5. Install Dependencies

```bash
uv pip install -e .  # or pip install -e .
```

### 6. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=physical_ai_humanoid_book
BOOK_SITEMAP_URL=https://your-book-site.com/sitemap.xml
```

Create an example file `.env.example`:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=physical_ai_humanoid_book
BOOK_SITEMAP_URL=https://your-book-site.com/sitemap.xml
```

## Running the Application

### 1. Run Content Ingestion

First, you need to ingest the book content into Qdrant:

```bash
cd backend
python -m src.ingest
```

This will:
- Fetch the sitemap.xml from BOOK_SITEMAP_URL
- Extract all book page URLs
- Fetch content from each page
- Chunk content into 300-800 token pieces
- Generate embeddings using Cohere
- Store in Qdrant with proper metadata

### 2. Start the Backend Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 3. Test the API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main concept of Physical AI?",
    "selected_text": ""
  }'
```

## Key Components

### Main Files Structure
- `src/main.py`: FastAPI application entry point
- `src/agent.py`: RAG agent implementation using Agent SDK
- `src/ingest.py`: Content ingestion script
- `src/config.py`: Configuration loading from environment
- `src/models/`: Data models for requests/responses
- `src/services/`: Business logic services
- `src/utils/`: Utility functions

### API Endpoints
- `POST /chat`: Process user questions and return answers from book content

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Environment Setup for Development

1. Activate virtual environment
2. Install development dependencies if needed
3. Ensure all environment variables are set
4. Run ingestion before testing the RAG functionality

## Troubleshooting

- If ingestion fails, verify that the sitemap URL is accessible
- If Qdrant connection fails, check URL and API key in environment variables
- If embeddings fail, verify Cohere API key and quota
- If responses are empty, ensure content was successfully ingested into Qdrant