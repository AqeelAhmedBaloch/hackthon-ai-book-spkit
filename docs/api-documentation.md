# RAG System API Documentation

## Overview

The RAG (Retrieval-Augmented Generation) system provides a RESTful API for querying book content and receiving AI-generated responses with citations. The API is built with FastAPI and follows standard REST conventions.

## Base URL

```
http://localhost:8000
```

## Authentication

The API does not require authentication for basic operations, but the backend services (OpenAI, Qdrant) require their respective API keys to be configured in the environment.

## Endpoints

### GET /health

Health check endpoint to verify all services are accessible.

**Response:**
```json
{
  "status": "healthy",
  "openai_connected": true,
  "qdrant_connected": true,
  "database_connected": false,
  "message": "All services operational"
}
```

### POST /query

Process user queries and return RAG agent responses.

**Request Body:**
```json
{
  "query": "Your question here",
  "selected_text": "Optional selected text for context",
  "page_url": "Optional page URL",
  "session_id": "Optional session identifier"
}
```

**Response:**
```json
{
  "response": "The AI-generated response",
  "citations": [
    {
      "source_document": "document_name",
      "page_number": 123,
      "section": "section_name",
      "text_snippet": "brief excerpt",
      "similarity_score": 0.95
    }
  ],
  "confidence": 0.85,
  "retrieved_chunks": [],
  "processing_time_ms": 125.5,
  "request_id": "request_identifier",
  "timestamp": "2023-12-19T10:00:00"
}
```

### POST /query/enhanced

Enhanced endpoint with additional metadata and options.

**Request Body:**
```json
{
  "query": "Your question here",
  "selected_text": "Optional selected text for context",
  "page_url": "Optional page URL",
  "session_id": "Optional session identifier",
  "user_id": "Optional user identifier",
  "metadata": {},
  "include_citations": true,
  "max_tokens": 1000,
  "temperature": 0.1
}
```

**Response:**
```json
{
  "response": "The AI-generated response",
  "citations": [...],
  "confidence": 0.85,
  "retrieved_chunks": [],
  "processing_time_ms": 125.5,
  "request_id": "request_identifier",
  "timestamp": "2023-12-19T10:00:00",
  "status": "completed",
  "error_message": null,
  "token_usage": {},
  "model_used": "gpt-4-turbo"
}
```

### POST /validate-query

Validate a query without processing it.

**Request Body:**
```json
{
  "query": "Your question here",
  "selected_text": "Optional selected text",
  "page_url": "Optional page URL",
  "session_id": "Optional session identifier"
}
```

**Response:**
```json
{
  "valid": true,
  "errors": []
}
```

### GET /config

Return current configuration (excluding sensitive data).

**Response:**
```json
{
  "openai_api_key": "***",
  "qdrant_url": "http://localhost:6333",
  "app_title": "Book RAG System",
  "debug": false,
  "...": "other config values"
}
```

### GET /stats

Get statistics about the RAG system.

**Response:**
```json
{
  "total_documents": 150,
  "qdrant_health": true,
  "model": "gpt-4-turbo",
  "last_query_time": null
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `400`: Bad request (validation error)
- `401`: Unauthorized (if authentication was required)
- `404`: Not found
- `500`: Internal server error

Error responses follow this format:
```json
{
  "detail": "Error message"
}
```

## Rate Limiting

The API does not implement rate limiting by default. This should be handled at the infrastructure level.

## Request/Response Limits

- Query text: maximum 1000 characters
- Selected text: maximum 2000 characters
- Page URL: maximum 2000 characters

## Logging

All API requests are logged with:
- Timestamp
- Request ID
- Endpoint
- Processing time
- Error details (if applicable)

## CORS

The API supports CORS for the following origins (configurable):
- `http://localhost:3000`
- `http://localhost:8000`

## Content Types

- Request: `application/json`
- Response: `application/json`

## Versioning

The API version is included in the response headers and can be retrieved from the `/` endpoint.