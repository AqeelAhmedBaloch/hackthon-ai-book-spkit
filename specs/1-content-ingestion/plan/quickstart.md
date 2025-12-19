# Quickstart Guide: Content Ingestion Pipeline

**Feature**: 1-content-ingestion
**Created**: 2025-12-19

## Prerequisites

- Python 3.8 or higher
- Cohere API key
- Qdrant Cloud account and API key
- Access to a deployed Docusaurus book URL

## Setup Instructions

### 1. Initialize the Backend Project

```bash
# Create and navigate to backend directory
mkdir backend && cd backend

# If using UV (as specified in requirements):
uv init
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv

# Alternative using pip:
pip install requests beautifulsoup4 cohere qdrant-client python-dotenv
```

### 2. Clone or Download the Code

The main implementation is in `backend/main.py` with supporting files:
- `requirements.txt` - Project dependencies
- `.env.example` - Environment configuration template
- `README.md` - Detailed documentation

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values:
```

Edit the `.env` file with your specific values:
```env
# Cohere API Configuration
COHERE_API_KEY=your_actual_cohere_api_key_here

# Qdrant Cloud Configuration
QDRANT_URL=your_actual_qdrant_cloud_url_here
QDRANT_API_KEY=your_actual_qdrant_api_key_here

# Book Source Configuration
BOOK_URL=https://your-deployed-book-url.com
```

### 4. Run the Ingestion Pipeline

```bash
# Execute the content ingestion pipeline
python main.py
```

## Expected Output

The pipeline will:
1. Crawl the specified book URL and discover all accessible pages
2. Extract clean text content from each page
3. Chunk the content into appropriately sized segments
4. Generate embeddings using Cohere
5. Store the embeddings and metadata in Qdrant

Example output:
```
INFO: Starting content ingestion from: https://example-book.com
INFO: Crawling and extracting content...
INFO: Found 25 pages to process
INFO: Processing page 1/25: https://example-book.com/intro
INFO: Processing page 2/25: https://example-book.com/chapter-1
...
INFO: Created 142 content chunks
INFO: Generating embeddings...
INFO: Processed batch 1/2
INFO: Storing embeddings in Qdrant...
INFO: Stored 142 embeddings in Qdrant collection 'book_embeddings'
INFO: Content ingestion pipeline completed successfully!
```

## Verification

After running the pipeline, you can verify the ingestion by:
1. Checking your Qdrant Cloud dashboard for the "book_embeddings" collection
2. Verifying the number of stored vectors matches the expected count
3. Inspecting a few sample vectors to ensure metadata is correctly stored

## Troubleshooting

### Common Issues

**API Rate Limits**: If you encounter rate limit errors, the system has built-in retry logic, but you may want to reduce the number of concurrent requests.

**Content Extraction**: If content isn't being extracted properly, check that the book URL is accessible and that the site doesn't have anti-bot measures.

**Qdrant Connection**: Ensure your QDRANT_URL and QDRANT_API_KEY are correct and that your account is active.

### Logging

The system logs detailed information at each stage. Check the console output for any errors or warnings during the ingestion process.

## Next Steps

After successful ingestion:
1. Implement the retrieval component to query the stored embeddings
2. Build the RAG chatbot to use the ingested content
3. Add monitoring and alerting for the ingestion pipeline