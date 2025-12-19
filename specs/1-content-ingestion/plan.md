# Implementation Plan: Content Ingestion & Embeddings

**Feature**: 1-content-ingestion
**Created**: 2025-12-19
**Status**: Draft

## Technical Context

This implementation creates a content ingestion pipeline that extracts content from deployed Docusaurus books, generates embeddings using Cohere, and stores them in Qdrant Cloud. The system is designed to handle the complete workflow from URL crawling to vector storage.

### Architecture Overview

The system consists of several key components:
- **ContentExtractor**: Crawls and extracts clean text from deployed book URLs
- **ContentChunker**: Splits content into appropriately sized chunks for embedding
- **EmbeddingGenerator**: Creates vector embeddings using Cohere API
- **VectorStore**: Stores embeddings and metadata in Qdrant database
- **ContentIngestionPipeline**: Orchestrates the entire process

### Technology Stack

- **Backend**: Python 3.8+
- **Web Scraping**: BeautifulSoup4 for HTML parsing
- **Embeddings**: Cohere API for vector generation
- **Vector Database**: Qdrant Cloud (Free Tier)
- **HTTP Client**: Requests for web crawling
- **Project Management**: UV (as requested)

### Dependencies

- `requests`: For HTTP requests and crawling
- `beautifulsoup4`: For HTML parsing and content extraction
- `cohere`: For embedding generation
- `qdrant-client`: For vector database operations
- `python-dotenv`: For environment variable management

## Constitution Check

### Alignment with Project Principles

✅ **Spec-First, Reproducible Development**: Implementation follows the feature specification created in `specs/1-content-ingestion/spec.md`

✅ **Factual Accuracy and Zero Hallucination**: The system only processes content from the provided book URLs without generating new content

✅ **Clear Structure for Technical Audience**: The code is organized in a modular fashion with clear class responsibilities

✅ **Full Alignment Between Content and Storage**: All content stored in Qdrant is directly extracted from the source book URLs

✅ **Public, Self-Contained Repository**: The implementation is contained within this repository with all necessary dependencies specified

✅ **Deterministic, Citation-Backed Storage**: Each vector is stored with metadata linking back to the original source URL and content location

### Compliance Verification

- [x] All functionality aligns with the feature specification
- [x] Implementation respects the constraints (Cohere models only, Qdrant Cloud, deployed URLs only)
- [x] No external sources beyond the specified book URLs are used
- [x] Metadata preservation ensures proper citation capabilities

## Phase 0: Research & Resolution

### Key Decisions Made

1. **Embedding Model**: Using Cohere's `embed-multilingual-v3.0` model for robust multilingual support
2. **Chunking Strategy**: 1000-character chunks with 100-character overlap to maintain context while respecting API limits
3. **Crawling Approach**: Breadth-first crawling with domain restriction to stay within book boundaries
4. **Error Handling**: Comprehensive error handling with logging for debugging and monitoring
5. **Batch Processing**: Processing in batches to respect API rate limits and memory constraints

### Technical Unknowns Resolved

- **Qdrant Vector Size**: Cohere's multilingual model produces 1024-dimensional vectors
- **Content Extraction**: Using CSS selectors specific to Docusaurus sites for optimal content extraction
- **URL Crawling**: Implementing a breadth-first approach with domain restrictions to prevent infinite crawling
- **Duplicate Handling**: Using content hashing to identify and potentially filter duplicates

## Phase 1: Design & Contracts

### Data Model

#### ContentChunk
- `text`: str - The actual content text
- `source_url`: str - Original URL where content was found
- `content_id`: str - Unique identifier for the chunk
- `metadata`: Dict[str, Any] - Additional metadata including page title, word count, etc.

#### Content Extraction Process
- Input: Base URL of deployed book
- Output: List of ContentChunk objects
- Process: Crawl → Extract → Chunk → Prepare for embedding

### API Contracts

This backend service is designed as a command-line application that processes content and stores it in Qdrant. The main interface is through environment variables and command-line execution.

#### Environment Variables
- `COHERE_API_KEY`: uyUPiplocTNzv9LFjVumXbpjZ4pEC7beYkOvltTy
- `QDRANT_URL`: https://07d61841-ecc3-4128-a1ec-3e2361d704b5.europe-west3-0.gcp.cloud.qdrant.io:6333
- `QDRANT_API_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ZRgIENdG3QuLyxSzzutL-jWNapexFP1PNWOhEF9sBIA
- `BOOK_URL`: https://hackthon-ai-book-spkit.vercel.app/

### Quickstart Guide

1. Set up the project environment:
   ```bash
   # Create backend directory and initialize with UV
   mkdir backend && cd backend
   uv init  # If UV is available, otherwise use pip
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and book URL
   ```

4. Run the ingestion pipeline:
   ```bash
   python main.py
   ```

### Agent Context Updates

The following technologies have been added to the project context:
- Cohere API integration for embeddings
- Qdrant Cloud vector database operations
- Web crawling and content extraction techniques
- Content chunking algorithms for optimal embedding

## Re-evaluation: Post-Design Constitution Check

### Updated Compliance Status

✅ **All implementation decisions align with the project constitution**
✅ **Technical approach maintains factual accuracy requirements**
✅ **System design supports deterministic, citation-backed operations**
✅ **Architecture enables full content-to-storage alignment**

### Risk Mitigation

- **Rate Limiting**: Batch processing prevents API abuse
- **Memory Management**: Processing in chunks prevents memory overflow
- **Network Resilience**: Error handling and retry logic for network operations
- **Data Integrity**: Content hashing and metadata preservation