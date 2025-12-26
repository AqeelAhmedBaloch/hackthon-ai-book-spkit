# RAG Chatbot for Physical AI & Humanoid Robotics Book

This is a backend service that provides a RAG (Retrieval-Augmented Generation) chatbot for the Physical AI & Humanoid Robotics book. It allows users to ask questions about the book content and receive accurate answers based solely on the book's text.

## Features

- **Sitemap-based Ingestion**: Automatically fetches and processes book content from a sitemap.xml
- **Vector Storage**: Stores book content in Qdrant vector database with proper metadata
- **RAG Processing**: Uses Cohere embeddings and Anthropic models for question answering
- **Accurate Attribution**: Provides proper references to book chapters and sections
- **Fallback Handling**: Responds with "This topic is not covered in the book" when content isn't found

## Architecture

The system consists of:
- FastAPI backend with `/chat` endpoint
- Ingestion pipeline for processing book content
- Vector database (Qdrant) for content storage and retrieval
- RAG service for processing user queries

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Copy the environment file and add your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

## Usage

### 1. Ingest Book Content

Run the ingestion script to process book content from the sitemap:

```bash
python -m src.ingest
```

This will:
- Fetch all URLs from the sitemap
- Extract book content from each page
- Split content into 300-800 token chunks
- Generate embeddings using Cohere
- Store in Qdrant with proper metadata

### 2. Start the API Server

```bash
uvicorn src.main:app --reload --port 8000
```

### 3. Query the Chatbot

Send a POST request to the `/chat` endpoint:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main concept of Physical AI?",
    "selected_text": ""
  }'
```

## Environment Variables

- `COHERE_API_KEY`: "ctx7sk-245b924d-db37-4e45-9c92-acbdc4066128"
- `QDRANT_URL`: "https://07d61841-ecc3-4128-a1ec-3e2361d704b5.europe-west3-0.gcp.cloud.qdrant.io"
- `QDRANT_API_KEY`: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.lsSUxQBchrDmqJGlviVxLenFRbzu-56mVJNJqFqJ1_8"
- `QDRANT_COLLECTION_NAME`: "ai_book_vdb"
- `BOOK_SITEMAP_URL`: "https://hackthon-ai-book-spkit.vercel.app/sitemap.xml"
- `ANTHROPIC_API_KEY`: "your-anthropic-api-key-here"

## API Endpoints

### `POST /chat`

Process a user question and return an answer based on book content.

Request body:
```json
{
  "question": "Your question about the book",
  "selected_text": "Optional selected text context"
}
```

Response:
```json
{
  "id": "response-uuid",
  "answer": "The answer based on book content",
  "references": [
    {
      "chapter": "Chapter name",
      "section": "Section name",
      "source_url": "URL to the source"
    }
  ],
  "timestamp": "2025-12-26T10:30:00"
}
```

## Project Structure

```
backend/
├── src/
│   ├── main.py          # FastAPI application
│   ├── agent.py         # RAG agent implementation
│   ├── ingest.py        # Content ingestion script
│   ├── config.py        # Configuration loader
│   ├── models/          # Data models
│   │   ├── book_content.py
│   │   └── query.py
│   ├── services/        # Business logic services
│   │   ├── ingestion_service.py
│   │   ├── embedding_service.py
│   │   ├── qdrant_service.py
│   │   └── rag_service.py
│   └── utils/           # Utility functions
│       ├── text_splitter.py
│       └── html_parser.py
├── pyproject.toml       # Project dependencies
└── .env.example        # Environment variables template
```

## Development

Run tests:
```bash
pytest tests/
```

## Security

- All API keys are loaded from environment variables
- Input validation is performed on all requests
- No sensitive data is logged