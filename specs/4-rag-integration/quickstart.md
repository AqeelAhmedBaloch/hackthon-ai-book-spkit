# Quickstart: RAG Integration

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm/yarn
- OpenAI API key
- Access to Qdrant instance
- UV package manager
- Docker (optional, for local Qdrant)

## Setup

1. **Install UV package manager**:
   ```bash
   # Install UV (fast Python package installer)
   pip install uv
   ```

2. **Set up backend environment**:
   ```bash
   cd backend
   uv venv  # Create virtual environment
   source .venv/bin/activate  # Activate virtual environment
   uv pip install -r requirements.txt  # Install dependencies
   ```

3. **Configure environment variables**:
   ```bash
   # Create backend environment file
   cat > backend/.env << EOF
   OPENAI_API_KEY=your-openai-api-key
   QDRANT_URL=your-qdrant-url
   QDRANT_API_KEY=your-qdrant-api-key  # if required
   QDRANT_COLLECTION=book_content
   DATABASE_URL=your-neon-postgres-url
   EOF

   # Create frontend environment file
   cat > ai_frontend_book/.env << EOF
   REACT_APP_BACKEND_URL=http://localhost:8000
   EOF
   ```

## Initialize the Complete RAG System

1. **Ingest book content**:
   ```bash
   cd backend
   source .venv/bin/activate
   python -m src.content_ingestion.main --input-path /path/to/book/content --collection-name book_content
   ```

2. **Validate retrieval pipeline**:
   ```bash
   python -m src.retrieval_validation.main --collection-name book_content --validation-type all
   ```

3. **Start the RAG agent service**:
   ```bash
   uvicorn src.rag_agent.main:app --reload --port 8000
   ```

4. **Start the Docusaurus frontend**:
   ```bash
   cd ai_frontend_book
   npm install
   npm run start
   ```

## Using the Complete System

1. **Test the API directly**:
   ```bash
   curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the main concept discussed in the book?",
       "selected_text": "Optional selected text for context"
     }'
   ```

2. **Interact through the frontend**:
   - Navigate to http://localhost:3000
   - Use the integrated chat interface to ask questions about the book content
   - Select text on pages to ask context-specific questions

## System Architecture Overview

The complete RAG system consists of several integrated components:

1. **Content Ingestion Pipeline**: Loads book content, processes it into chunks, and stores embeddings in Qdrant
2. **Retrieval Validation**: Validates that the stored embeddings can be retrieved accurately
3. **RAG Agent**: FastAPI service that combines retrieval with generation to answer questions
4. **Frontend Integration**: Docusaurus components that provide a seamless chat interface

## Configuration Options

### Content Ingestion
```json
{
  "chunk_size": 512,
  "chunk_overlap": 50,
  "model": "text-embedding-ada-002",
  "batch_size": 10,
  "content_format": "markdown"
}
```

### RAG Agent
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

## Troubleshooting

- **Content ingestion fails**: Verify input path exists and contains supported file formats
- **Qdrant connection issues**: Check QDRANT_URL and API key are correctly configured
- **No results returned**: Ensure content ingestion completed successfully and collection name matches
- **Frontend-backend connection issues**: Verify REACT_APP_BACKEND_URL is set correctly and CORS is configured
- **Slow responses**: Check that the embedding model and OpenAI API are responding within expected timeframes