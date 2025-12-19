# Content Ingestion Backend

This backend service implements the content ingestion pipeline that extracts content from deployed Docusaurus books, generates embeddings using Cohere, and stores them in Qdrant Cloud.

## Features

- Crawls deployed book URLs to extract all accessible content
- Uses BeautifulSoup for clean text extraction from HTML
- Implements intelligent content chunking for optimal embedding
- Generates embeddings using Cohere's multilingual model
- Stores embeddings and metadata in Qdrant vector database
- Handles errors and retries for robust operation

## Requirements

- Python 3.8+
- Cohere API key
- Qdrant Cloud account and API key
- Access to deployed Docusaurus book URLs

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys and URLs
```

## Environment Variables

Create a `.env` file with the following variables:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
BOOK_URL=the_url_of_the_deployed_book_to_ingest
```

## Usage

Run the content ingestion pipeline:

```bash
python main.py
```

The script will:
1. Crawl the provided book URL to find all accessible pages
2. Extract clean text content from each page
3. Chunk the content into appropriate sizes for embedding
4. Generate vector embeddings using Cohere
5. Store the embeddings and metadata in Qdrant

## Architecture

The system consists of several components:

- `ContentExtractor`: Handles crawling and text extraction from HTML
- `ContentChunker`: Splits content into appropriately sized chunks
- `EmbeddingGenerator`: Creates vector embeddings using Cohere API
- `VectorStore`: Manages storage in Qdrant vector database
- `ContentIngestionPipeline`: Orchestrates the entire process

## Error Handling

The system includes comprehensive error handling:
- Network timeouts and retries
- API rate limiting considerations
- Graceful handling of malformed content
- Logging for debugging and monitoring

## Configuration

You can adjust the following parameters in the code:
- `max_chunk_size`: Maximum size of text chunks (default: 1000 characters)
- `overlap`: Overlap between chunks (default: 100 characters)
- `model`: Cohere embedding model to use
- `collection_name`: Qdrant collection name