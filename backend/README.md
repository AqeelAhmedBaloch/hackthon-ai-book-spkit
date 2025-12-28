# RAG Book Chatbot Backend

A backend-only RAG (Retrieval-Augmented Generation) chatbot that answers questions about a published book using sitemap-based content ingestion.

## Features

- **Sitemap-based Ingestion**: Automatically fetch and ingest book pages from a sitemap.xml
- **Vector Search**: Store book content as embeddings for efficient semantic search
- **Book-Only Answers**: All answers are based exclusively on ingested book content
- **FastAPI Endpoint**: Public `/chat` endpoint for querying the system
- **Conversation Context**: Maintains context across follow-up questions

## Tech Stack

- **Language**: Python 3.10+
- **API Framework**: FastAPI
- **Vector Database**: Qdrant Cloud
- **LLM Provider**: OpenRouter (using mistralai/devstral-2512:free)
- **Embeddings**: Cohere API
- **Package Manager**: uv

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Valid API keys for OpenRouter, Cohere, and Qdrant

### Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run ingestion** (first time only):
   ```bash
   python ingest.py --sitemap https://your-book-site.com/sitemap.xml
   ```

4. **Start the server**:
   ```bash
   uv run uvicorn main:app --reload
   ```

5. **Query the chatbot**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is this book about?"}'
   ```

## Usage

### Ingest Book Content

```bash
python ingest.py --sitemap https://example.com/sitemap.xml
```

The ingestion process will:
1. Fetch and parse the sitemap
2. Extract all page URLs
3. Fetch content from each page
4. Generate embeddings using Cohere
5. Store vectors in Qdrant

### Chat API

**Endpoint**: `POST /chat`

**Request**:
```json
{
  "query": "Your question about the book",
  "conversation_id": "optional-session-id"
}
```

**Response**:
```json
{
  "answer": "The answer based on book content...",
  "sources": [
    {"url": "https://example.com/chapter1", "title": "Chapter 1"}
  ],
  "conversation_id": "session-id"
}
```

## Project Structure

```
.
├── src/
│   ├── config.py              # Environment configuration
│   ├── models/
│   │   ├── book_content.py   # Book content data models
│   │   └── chat.py          # Chat request/response models
│   ├── vector_db/
│   │   └── qdrant_client.py  # Qdrant integration
│   ├── llm/
│   │   └── openrouter_client.py # LLM integration
│   ├── embeddings/
│   │   └── cohere_client.py  # Embedding generation
│   ├── ingest/
│   │   ├── sitemap_parser.py  # Sitemap parsing
│   │   ├── page_fetcher.py   # Page content fetching
│   │   ├── text_extractor.py  # Text extraction/cleaning
│   │   └── sitemap_validator.py # URL validation
│   ├── agent/
│   │   ├── query_embedder.py  # Query embedding
│   │   ├── retriever.py      # Vector retrieval
│   │   ├── answer_generator.py # Answer generation
│   │   └── context_manager.py # Conversation context
│   └── utils/
│       └── logger.py        # Logging utilities
├── tests/                    # Test files
├── main.py                  # FastAPI application
├── agent.py                 # RAG agent coordinator
├── ingest.py                # Ingestion script
└── pyproject.toml           # Project configuration
```

## Development

### Install dev dependencies
```bash
uv sync --extra dev
```

### Run tests
```bash
uv run pytest
```

### Format code
```bash
uv run black .
uv run ruff check --fix .
```

## Success Criteria

- 95% of valid sitemap URLs ingested within 5 minutes per 100 pages
- 90% of book-related questions receive relevant answers
- 100% of answers based exclusively on ingested content
- Average response time under 3 seconds
- Follow-up questions maintain context 85% of the time
- Unanswerable questions correctly indicated 95% of the time

## License

MIT
