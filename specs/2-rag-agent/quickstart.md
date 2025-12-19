# Quickstart: RAG Agent Implementation

## Prerequisites

- Python 3.11+
- OpenAI API key
- Access to Qdrant instance with embedded book content
- Required Python packages (see requirements.txt)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   # Set environment variables
   export OPENAI_API_KEY="your-openai-api-key"
   export QDRANT_URL="your-qdrant-url"
   export QDRANT_API_KEY="your-api-key"  # if required
   export QDRANT_COLLECTION="your-collection-name"
   export DATABASE_URL="your-neon-postgres-url"  # if using metadata storage
   ```

3. **Verify setup**:
   ```bash
   python -c "import openai; import qdrant_client; print('Dependencies available')"
   ```

## Running the RAG Agent Service

1. **Start the FastAPI server**:
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```

2. **Test the endpoint**:
   ```bash
   curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the main concept discussed in the book?"}'
   ```

## Using the RAG Agent

1. **Send a query**:
   ```python
   import requests

   response = requests.post("http://localhost:8000/query", json={
       "query": "Explain the implementation details of the system"
   })

   result = response.json()
   print(result["response"])
   print("Citations:", result["citations"])
   ```

2. **Query with filters**:
   ```python
   response = requests.post("http://localhost:8000/query", json={
       "query": "What does the book say about AI agents?",
       "context_filters": {
           "chapter": "module1"
       }
   })
   ```

## Configuration

Create a config file to customize agent behavior:

```json
{
  "model": "gpt-4-turbo",
  "temperature": 0.1,
  "max_tokens": 1000,
  "retrieval_top_k": 5,
  "similarity_threshold": 0.7,
  "citation_required": true
}
```

## API Endpoints

### POST /query
Submit a query to the RAG agent.

Request body:
```json
{
  "query": "Your question here",
  "user_id": "optional user identifier",
  "session_id": "optional session identifier",
  "context_filters": {}
}
```

Response:
```json
{
  "response": "Agent's answer",
  "citations": [
    {
      "source_document": "document name",
      "page_number": 123,
      "section": "section name",
      "text_snippet": "brief excerpt",
      "similarity_score": 0.95
    }
  ],
  "confidence": 0.95,
  "retrieved_chunks": [...],
  "processing_time_ms": 1250,
  "query_id": "unique-id"
}
```

### GET /health
Check the health status of the service.

Response:
```json
{
  "status": "healthy",
  "openai_connected": true,
  "qdrant_connected": true,
  "message": "All services operational"
}
```

## Troubleshooting

- **OpenAI API errors**: Verify OPENAI_API_KEY is set correctly and you have sufficient credits
- **Qdrant connection issues**: Check QDRANT_URL and API key are correctly configured
- **No results returned**: Ensure the Qdrant collection contains embedded book content
- **Hallucination issues**: Adjust temperature lower and verify retrieval integration is working properly