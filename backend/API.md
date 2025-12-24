# RAG Chatbot API Documentation

## Overview
The RAG Chatbot API provides a question-answering service that retrieves information from book content using Retrieval-Augmented Generation (RAG). The API allows users to ask questions about book content and receive answers grounded in the indexed book materials.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check the health status of the RAG service.

#### Response
```json
{
  "status": "healthy",
  "service": "RAG Chatbot Backend",
  "timestamp": "2025-12-24T17:30:00.123456",
  "services": {
    "cohere": true,
    "qdrant": true,
    "ingestion": true
  }
}
```

### 2. Ingest Book Content
**POST** `/ingest`

Trigger the book content ingestion and embedding process.

#### Query Parameters
- `force` (boolean, optional): Force reprocessing of content (default: false)

#### Response
```json
{
  "status": "success",
  "chunks_processed": 125,
  "message": "Successfully ingested 125 content chunks from 18 files"
}
```

Possible Status Values:
- `success`: Content was successfully ingested
- `no_content`: No markdown files found to process
- `error`: An error occurred during ingestion

### 3. Chat
**POST** `/chat`

Process user questions and return RAG-generated responses.

#### Request Body
```json
{
  "question": "string",
  "selected_text": "string (optional)",
  "context": {
    "page_url": "string (optional)",
    "section": "string (optional)"
  }
}
```

#### Request Fields
- `question` (string, required): The user's question text
- `selected_text` (string, optional): Optional text selected by user for focused queries
- `context` (object, optional): Additional context for the query

#### Response
```json
{
  "answer": "string",
  "sources": [
    {
      "path": "string",
      "section": "string",
      "content": "string",
      "relevance_score": "number"
    }
  ],
  "confidence": "number (0-1)",
  "timestamp": "ISO 8601 datetime"
}
```

#### Response Fields
- `answer` (string): The generated answer text
- `sources` (array): List of source references for the answer
- `confidence` (number): Confidence score for the response (0-1)
- `timestamp` (string): When the response was generated

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "answer": "Please provide a question to answer.",
  "sources": [],
  "confidence": 0.0,
  "timestamp": "2025-12-24T17:30:00.123456"
}
```

#### 500 Internal Server Error
```json
{
  "answer": "An error occurred while processing your query. Please try again.",
  "sources": [],
  "confidence": 0.0,
  "timestamp": "2025-12-24T17:30:00.123456"
}
```

## Environment Variables

The application requires the following environment variables:

- `COHERE_API_KEY`: Your Cohere API key for embeddings and generation
- `QDRANT_API_KEY`: Your Qdrant Cloud API key
- `QDRANT_URL`: Your Qdrant Cloud cluster URL
- `BOOK_CONTENT_PATH`: Path to book markdown files (default: `../ai_frontend_book/docs/`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: `http://localhost:3000,http://localhost:3001,https://your-docusaurus-site.vercel.app`)

## Setup

### Prerequisites
- Python 3.9+
- Cohere API key
- Qdrant Cloud API key and URL
- Book content in markdown format

### Installation
1. Install dependencies: `pip install -e .`
2. Create `.env` file with required environment variables
3. Ensure book content is available in the expected directory

### Running the Service
```bash
uvicorn main:app --reload --port 8000
```

## Security Considerations

- Input sanitization is performed on all user inputs
- Content length is limited to prevent overly large requests
- XSS prevention through input sanitization
- Proper error handling to prevent information disclosure

## Performance

- 30-second timeout for external API calls (Cohere and Qdrant)
- Caching for embeddings to avoid reprocessing unchanged content
- In-memory cache with 1-hour expiry

## Logging

The application logs to both file (`rag_chatbot.log`) and console with the following format:
```
YYYY-MM-DD HH:MM:SS,mmm - rag_chatbot - LEVEL - Message
```