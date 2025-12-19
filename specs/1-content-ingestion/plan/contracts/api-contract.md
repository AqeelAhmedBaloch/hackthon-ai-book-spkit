# API Contract: Content Ingestion Service

**Feature**: 1-content-ingestion
**Version**: 1.0
**Created**: 2025-12-19

## Overview

The Content Ingestion Service is a command-line application that processes deployed book content and stores vector embeddings in Qdrant. The service is configured through environment variables and executed as a single command.

## Configuration Interface

### Environment Variables

The service requires the following environment variables to operate:

#### Required Variables

- `COHERE_API_KEY` (string)
  - Description: API key for Cohere embedding service
  - Format: Alphanumeric string
  - Required: Yes

- `QDRANT_URL` (string)
  - Description: URL for Qdrant Cloud instance
  - Format: Valid URL with protocol and port
  - Required: Yes

- `QDRANT_API_KEY` (string)
  - Description: API key for Qdrant Cloud instance
  - Format: Alphanumeric string
  - Required: Yes

- `BOOK_URL` (string)
  - Description: Base URL of the deployed book to ingest
  - Format: Valid URL
  - Required: Yes

## Execution Interface

### Command Line Interface

The service is executed as a Python script with no command-line arguments:

```bash
python main.py
```

### Expected Behavior

When executed successfully, the service will:
1. Validate all required environment variables are present
2. Initialize connections to Cohere and Qdrant services
3. Crawl the specified BOOK_URL to discover content pages
4. Extract and process content from each page
5. Generate embeddings for content chunks
6. Store embeddings with metadata in Qdrant
7. Log progress and completion status

## Data Contracts

### Input Data Flow

- **Source**: Deployed book accessible at BOOK_URL
- **Format**: HTML content from web pages
- **Processing**: Text extraction, cleaning, and chunking

### Output Data Structure

The service stores data in Qdrant with the following structure:

#### Vector Payload Schema

```json
{
  "text": "string, the original content chunk",
  "source_url": "string, URL where content was found",
  "timestamp": "integer, Unix timestamp",
  "chunk_index": "integer, position of chunk in original content",
  "page_title": "string, extracted title of source page",
  "word_count": "integer, number of words in the chunk"
}
```

## Error Handling Contract

### Expected Error Scenarios

1. **Missing Environment Variables**
   - Condition: Required environment variables are not set
   - Response: Print error message listing missing variables
   - Exit Code: 1

2. **Network Connectivity Issues**
   - Condition: Unable to reach Cohere, Qdrant, or source book
   - Response: Log error and attempt retry with exponential backoff
   - Behavior: Continue processing other content when possible

3. **Invalid URLs**
   - Condition: BOOK_URL is malformed or inaccessible
   - Response: Log error and terminate gracefully
   - Exit Code: 1

4. **API Limitations**
   - Condition: Rate limits or quota exceeded on external services
   - Response: Implement retry logic with appropriate delays
   - Behavior: Continue processing after delay

## Success Criteria

### Expected Outcomes

- Content from all accessible pages is extracted and embedded
- Embeddings are stored in Qdrant with complete metadata
- Process completes without errors
- Appropriate logging throughout the process

### Performance Expectations

- Process rate: Dependent on network speed and API response times
- Memory usage: Managed through chunking and batch processing
- Error resilience: Continue processing despite individual page failures

## Security Considerations

- API keys are accessed only through environment variables
- No sensitive data is logged or stored in code
- URL validation prevents access to unintended resources
- Domain restriction ensures crawling stays within intended site