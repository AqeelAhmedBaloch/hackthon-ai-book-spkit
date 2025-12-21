# Implementation Plan: Content Ingestion & Embeddings

**Feature**: 5-content-ingestion
**Created**: 2025-12-21
**Status**: Draft
**Author**: Claude AI Assistant

## Technical Context

### Architecture Overview
- **Backend Framework**: FastAPI application using UV for dependency management
- **Content Extraction**: Web crawling and HTML parsing for Docusaurus sites
- **Embedding Service**: Cohere API integration for vector generation
- **Vector Database**: Qdrant Cloud (Free Tier) for storage and retrieval
- **Environment**: Python 3.11+ with async/await patterns

### Core Technologies
- **Language**: Python 3.11+
- **Dependency Management**: UV (as specified in user requirements)
- **Web Crawling**: aiohttp for async HTTP requests, BeautifulSoup4 for HTML parsing
- **Embeddings**: Cohere Python SDK
- **Vector DB**: Qdrant Python client
- **Configuration**: Pydantic Settings for environment management
- **Async Processing**: asyncio for concurrent operations

### Infrastructure Components
- **Content Extractor**: Async crawler to extract text from Docusaurus URLs
- **Content Chunker**: Text processing module to split content into manageable chunks
- **Embedding Generator**: Cohere integration for vector generation
- **Storage Manager**: Qdrant client for vector storage and metadata
- **Progress Tracker**: Status tracking for ingestion runs

## Constitution Check

### Compliance Verification
- ✅ **Spec-First Development**: Proceeding from well-defined spec in `specs/5-content-ingestion/spec.md`
- ✅ **Factual Accuracy**: Content extraction will preserve original book content without modification
- ✅ **Clear Structure**: Following modular architecture with well-defined components
- ✅ **Public Repository**: All code will be in public GitHub repo
- ✅ **Deterministic Responses**: Not applicable for ingestion pipeline (only for chatbot responses)
- ✅ **Technical Standards**: Using FastAPI, Qdrant Cloud, Cohere as per constitution

### Potential Issues
- **Qdrant Cloud Free Tier Limitations**: Need to ensure implementation respects free tier constraints
- **External Dependencies**: Reliance on Cohere API and Qdrant Cloud - need proper error handling

## Gates Evaluation

### Gate 1: Technical Feasibility ✅
- Cohere embeddings API is accessible via Python SDK
- Qdrant Cloud supports vector storage with Python client
- Docusaurus sites are crawlable with standard web scraping techniques
- UV dependency management is compatible with Python projects

### Gate 2: Architecture Alignment ✅
- Aligns with constitution's technical standards (FastAPI, Qdrant, Cohere)
- Follows modular, testable architecture principles
- Supports deterministic processing of content

### Gate 3: Resource Constraints ✅
- Qdrant Cloud Free Tier supports required operations
- Cohere API has sufficient rate limits for ingestion
- Implementation will include proper error handling and retry logic

## Phase 0: Research & Unknown Resolution

### Research Tasks

#### 0.1: Docusaurus Content Extraction Patterns
**Task**: Research best practices for extracting content from Docusaurus-generated sites
- Identify common HTML structures and selectors used by Docusaurus
- Determine how to extract clean text content while preserving document hierarchy
- Handle navigation, sidebar, and other non-content elements

#### 0.2: Cohere Embedding Model Selection
**Task**: Research optimal Cohere embedding models for documentation content
- Compare available models for text similarity tasks
- Consider token limits and cost implications
- Evaluate performance characteristics for technical documentation

#### 0.3: Qdrant Cloud Free Tier Constraints
**Task**: Research limitations and best practices for Qdrant Cloud Free Tier
- Storage limits and vector count restrictions
- API rate limits and concurrent request limits
- Optimal vector dimensions and collection management

#### 0.4: Content Chunking Strategy
**Task**: Research optimal text chunking strategies for semantic search
- Determine appropriate chunk sizes for embedding models
- Consider overlap strategies to preserve context
- Evaluate different splitting approaches (sentence, paragraph, semantic)

## Phase 1: Design & Contracts

### 1.1: Data Model Design

#### Content Chunk Entity
- **id**: Unique identifier for the chunk
- **content**: The actual text content (string)
- **source_url**: Original URL where content was found (string)
- **title**: Page title or section header (string)
- **position**: Position in the original document (integer)
- **metadata**: Additional metadata dictionary (dict)
- **created_at**: Timestamp of creation (datetime)

#### Embedding Vector Entity
- **chunk_id**: Reference to the content chunk (string)
- **vector**: The embedding vector array (list[float])
- **vector_size**: Dimension of the embedding (integer)
- **model_used**: Cohere model identifier (string)
- **created_at**: Timestamp of embedding creation (datetime)

#### Ingestion Record Entity
- **id**: Unique identifier for the ingestion run (string)
- **source_url**: Root URL being ingested (string)
- **status**: Current status (enum: pending, processing, completed, failed)
- **total_pages**: Total number of pages processed (integer)
- **processed_pages**: Number of pages successfully processed (integer)
- **total_chunks**: Total number of content chunks created (integer)
- **start_time**: When ingestion started (datetime)
- **end_time**: When ingestion completed (datetime, nullable)
- **error_log**: Any errors encountered (string, nullable)

### 1.2: API Contract Design

#### Content Extraction Service
```
POST /api/v1/ingest
Request: { "url": "https://example-docusaurus-site.com", "chunk_size": 1000 }
Response: { "ingestion_id": "uuid", "status": "processing", "estimated_time": "PT5M" }

GET /api/v1/ingest/{ingestion_id}
Response: { "status": "completed", "processed_pages": 42, "total_chunks": 1200, "error_log": null }
```

#### Vector Storage Service
```
POST /api/v1/vectors
Request: { "chunk_id": "uuid", "content": "text content", "embedding": [0.1, 0.2, ...], "metadata": {} }
Response: { "vector_id": "uuid", "status": "stored" }
```

### 1.3: Quickstart Guide

#### Backend Setup
```bash
# Create backend directory
mkdir backend
cd backend

# Initialize with UV
uv init
uv add fastapi uvicorn python-dotenv cohere-sdk qdrant-client beautifulsoup4 aiohttp pydantic

# Set up environment variables
cat > .env << EOF
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
EOF
```

#### Running the Ingestion Service
```bash
# Install dependencies
uv sync

# Run the service
uv run uvicorn main:app --reload
```

## Phase 2: Implementation Approach

### 2.1: Component Architecture
1. **ContentExtractor**: Handles URL validation and HTML content extraction
2. **ContentChunker**: Processes raw text into manageable chunks
3. **EmbeddingService**: Interfaces with Cohere API for vector generation
4. **VectorStorage**: Manages Qdrant operations for vector storage
5. **IngestionManager**: Coordinates the entire ingestion workflow
6. **ProgressTracker**: Tracks and reports ingestion status

### 2.2: Error Handling Strategy
- Graceful degradation when URLs are inaccessible
- Retry mechanisms for API failures
- Validation of extracted content quality
- Proper logging and monitoring

### 2.3: Performance Considerations
- Async processing for concurrent URL crawling
- Batch operations for vector storage
- Memory management for large content chunks
- Rate limiting to respect API constraints

## Next Steps

1. Implement Phase 0 research tasks to resolve any remaining questions
2. Create the data models based on the design
3. Develop the core components following the architectural approach
4. Create comprehensive tests for each component
5. Integrate components and test the full ingestion pipeline