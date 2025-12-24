# Data Model: Integrated RAG Chatbot

**Feature**: 008-rag-chatbot-docusaurus
**Date**: 2025-12-24

## Core Entities

### BookContentChunk
- **id**: Unique identifier for the chunk (string, required)
- **content**: The text content of the chunk (string, required)
- **source_path**: Path to the original markdown file (string, required)
- **source_section**: Specific section identifier within the file (string, optional)
- **embedding**: Vector embedding of the content (list of numbers, required)
- **metadata**: Additional metadata (object with title, headings, etc., optional)

### UserQuery
- **question**: The user's question text (string, required)
- **selected_text**: Optional text selected by user (for focused queries) (string, optional)
- **context**: Additional context for the query (object, optional)
  - **page_url**: URL of the page where query originated (string, optional)
  - **section**: Section identifier (string, optional)

### ChatResponse
- **answer**: The generated answer text (string, required)
- **sources**: List of source references for the answer (array of objects, required)
  - **path**: Path to source document (string, required)
  - **section**: Section identifier (string, required)
  - **content**: Excerpt from source (string, required)
  - **relevance_score**: Score indicating relevance (number, required)
- **confidence**: Confidence score for the response (number between 0-1, required)
- **timestamp**: When the response was generated (ISO 8601 datetime string, required)

### IngestionResult
- **status**: Current status of ingestion (string, required)
- **chunks_processed**: Number of content chunks processed (integer, required)
- **message**: Human-readable message about the result (string, required)
- **timestamp**: When the ingestion was completed (ISO 8601 datetime string, required)

## Validation Rules

### BookContentChunk
- Content must be non-empty
- Source path must be a valid file path
- Embedding must be a valid vector (array of numbers)
- Source section should be present if available

### UserQuery
- Question must be non-empty
- Selected text should be shorter than a reasonable limit (e.g., 10,000 characters)
- Context fields should be properly formatted

### ChatResponse
- Answer must be non-empty
- Sources array must contain at least one source when answer is provided
- Confidence must be between 0 and 1
- Timestamp must be in valid ISO 8601 format

### IngestionResult
- Status must be one of: "success", "partial", "failed"
- Chunks processed must be a non-negative integer
- Message should be informative about the outcome