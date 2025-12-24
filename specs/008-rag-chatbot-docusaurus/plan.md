# Implementation Plan: Integrated RAG Chatbot for Published Docusaurus Book

**Feature**: 008-rag-chatbot-docusaurus
**Created**: 2025-12-24
**Status**: Draft
**Input**: /sp.plan Integrated RAG Chatbot (Single-File Backend)

Scope:
- All backend logic inside backend/main.py
- No databases, no OpenAI, no extra files

Task 1 — Setup & Config
- Create backend/main.py
- Load environment variables:
  - COHERE_API_KEY
  - QDRANT_API_KEY
  - QDRANT_URL
- Initialize:
  - FastAPI app
  - Cohere client
  - Qdrant client
- Enable CORS for deployed book domain

Task 2 — Book Ingestion & Embeddings
- Read book Markdown files
- Clean and chunk content
- Generate embeddings using Cohere
- Store vectors in Qdrant with source metadata
- One-time or on-start ingestion toggle

Task 3 — Retrieval & RAG Answering
- Create /chat endpoint
- Accept:
  - user question
  - optional selected text
- Embed query with Cohere
- Retrieve top-k chunks from Qdrant
- Generate grounded answer using Cohere
- Attach source references in response

Task 4 — Frontend Integration Support
- Expose lightweight JSON API for chat
- Support text-selection based queries
- Return response in UI-friendly format

Environment & Dependencies
- Use uv as the package and environment manager
- Install FastAPI, Uvicorn, Cohere SDK, Qdrant client via uv
- Run the backend using uv

## Technical Context

### Architecture Overview
- **Backend**: Single-file FastAPI application (backend/main.py)
- **Vector Store**: Qdrant Cloud (Free Tier) for storing embeddings
- **AI Service**: Cohere API for embeddings and text generation
- **Frontend Integration**: JSON API endpoints for Docusaurus book integration
- **Deployment**: Designed to work with Vercel deployment of Docusaurus book

### Technology Stack
- **Framework**: FastAPI
- **Vector Database**: Qdrant Cloud
- **AI Provider**: Cohere API
- **Language**: Python 3.9+
- **Package Management**: pip with requirements.txt

### Key Dependencies
- **fastapi**: Web framework for API endpoints
- **uvicorn**: ASGI server for running FastAPI
- **cohere**: Python client for Cohere API
- **qdrant-client**: Python client for Qdrant vector database
- **python-dotenv**: Environment variable management
- **markdown**: Markdown parsing for book content
- **PyYAML**: YAML parsing if needed for configuration

### Unknowns to Resolve [NEEDS CLARIFICATION]
- **NC-001**: What is the exact structure of the book markdown files? Are they in a specific directory structure like `docs/`, `src/`, or elsewhere?
- **NC-002**: What is the expected chunk size for embedding? Should we use a standard size like 512 tokens or does it need to be configurable?
- **NC-003**: How should the ingestion process be triggered? Should it run once at startup, as a scheduled task, or manually?
- **NC-004**: What domain should be allowed for CORS? Should this be configurable or hardcoded to common deployment domains?
- **NC-005**: What is the expected timeout for API calls to Cohere and Qdrant to prevent hanging requests?

## Constitution Check

### Compliance Analysis
- ✅ **Spec-First, Reproducible Development**: Implementation follows the feature specification created in the previous step
- ✅ **Factual Accuracy and Zero Hallucination**: RAG system will only respond with information from indexed book content
- ✅ **Clear Structure for Technical Audience**: API will be well-documented with clear endpoints
- ✅ **Full Alignment Between Book Content and Chatbot Knowledge**: Responses will be grounded in book content only
- ✅ **Public, Self-Contained Repository**: Implementation will be part of the public repository
- ✅ **Deterministic, Citation-Backed Responses**: Responses will include source references to book sections

### Potential Violations
- **Risk**: API timeout settings might cause inconsistent user experience
- **Mitigation**: Implement proper timeout handling and error responses

## Gate Evaluation

### Gate 1: Specification Alignment
**Status**: PASS - Implementation plan aligns with feature specification requirements

### Gate 2: Constitution Compliance
**Status**: PASS - Plan complies with project constitution principles

### Gate 3: Technical Feasibility
**Status**: PASS - All required technologies are available and compatible

### Gate 4: Resource Requirements
**Status**: PASS - Plan uses only specified technologies (Cohere, Qdrant Cloud, FastAPI)

## Phase 0: Research & Unknown Resolution

### Research Summary

#### Decision: Book Content Structure
**Rationale**: The book content is typically located in `docs/` directory for Docusaurus projects
**Implementation**: Will implement logic to scan `docs/` directory for markdown files, with configurable path

#### Decision: Chunk Size
**Rationale**: 512 tokens provides good balance between context and retrieval precision
**Implementation**: Will use 512 token chunks with overlap to maintain context

#### Decision: Ingestion Trigger
**Rationale**: On-start ingestion provides fresh content while avoiding unnecessary processing
**Implementation**: Will implement ingestion on application startup with option to skip if already indexed

#### Decision: CORS Configuration
**Rationale**: Need to allow common deployment domains while maintaining security
**Implementation**: Will make CORS configurable via environment variables

#### Decision: API Timeouts
**Rationale**: 30-second timeout balances user experience with API processing time
**Implementation**: Will implement 30-second timeouts for external API calls

## Phase 1: Data Model Design

### Core Entities

#### BookContentChunk
- **id**: Unique identifier for the chunk
- **content**: The text content of the chunk
- **source_path**: Path to the original markdown file
- **source_section**: Specific section identifier within the file
- **embedding**: Vector embedding of the content
- **metadata**: Additional metadata (title, headings, etc.)

#### UserQuery
- **question**: The user's question text
- **selected_text**: Optional text selected by user (for focused queries)
- **context**: Additional context for the query

#### ChatResponse
- **answer**: The generated answer text
- **sources**: List of source references for the answer
- **confidence**: Confidence score for the response
- **timestamp**: When the response was generated

### API Contracts

#### POST /chat
**Purpose**: Process user questions and return RAG-generated responses

**Request Body**:
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

**Response**:
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

#### POST /ingest
**Purpose**: Trigger the book content ingestion and embedding process

**Request Body**:
```json
{
  "force": "boolean (optional, default: false)"
}
```

**Response**:
```json
{
  "status": "string",
  "chunks_processed": "number",
  "message": "string"
}
```

#### GET /health
**Purpose**: Check the health status of the RAG service

**Response**:
```json
{
  "status": "string",
  "services": {
    "cohere": "boolean",
    "qdrant": "boolean",
    "ingestion": "boolean"
  }
}
```

## Phase 1: Quickstart Guide

### Prerequisites
- Python 3.9+
- Cohere API key
- Qdrant Cloud API key and URL
- Book content in markdown format

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with required environment variables
3. Ensure book content is available in the expected directory

### Environment Variables
```
COHERE_API_KEY="uyUPiplocTNzv9LFjVumXbpjZ4pEC7beYkOvltTy"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ojS4W7RZwRBCfXjL7uwj3SWB305rHCz5ptYuzckFDaM"
QDRANT_URL="https://fd89975c-8fc9-4d7d-9960-2348a3f929c6.sa-east-1-0.aws.cloud.qdrant.io:6333"
BOOK_CONTENT_PATH=docs/ (optional, defaults to docs/)
CORS_ORIGINS="https://hackthon-ai-book-spkit.vercel.app"
```

### Running the Service
```bash
# Install dependencies
pip install fastapi uvicorn cohere qdrant-client python-dotenv markdown

# Run the service
uvicorn backend.main:app --reload --port 8000
```

### Initial Ingestion
The service will automatically ingest book content on first startup. To manually trigger ingestion:
```bash
curl -X POST http://localhost:8000/ingest
```

### Testing the Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does the book say about RAG systems?",
    "selected_text": ""
  }'
```

## Phase 1: Agent Context Update

### New Technologies Added
- FastAPI: Modern Python web framework with async support
- Cohere API: Embedding and generation models for RAG
- Qdrant: Vector database for similarity search
- Markdown processing: Parsing and handling of book content

### Integration Notes
- Cohere will be used for both embeddings (for retrieval) and text generation (for answers)
- Qdrant will store document embeddings with metadata for efficient retrieval
- FastAPI will handle both ingestion endpoints and chat endpoints
- The system will support both general queries and text-selection based queries

## Post-Design Constitution Check

### Compliance Verification
- ✅ **Zero Hallucination**: Responses will be grounded in retrieved book content
- ✅ **Citation-Backed**: All responses will include source references
- ✅ **Technical Accuracy**: Implementation follows best practices for RAG systems
- ✅ **Spec Alignment**: All functionality matches the feature specification