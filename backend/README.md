# RAG Chatbot Backend

Backend service for the RAG (Retrieval-Augmented Generation) chatbot integrated into the Physical AI & Humanoid Robotics book.

## Features

- **Question Answering**: Submit questions about the book content and receive accurate answers
- **Content Ingestion**: Automatically process markdown files from the docs directory into the vector database
- **Semantic Search**: Retrieve relevant book content using vector similarity
- **Rate Limiting**: Prevent API abuse with built-in rate limiting
- **CORS Security**: Secure cross-origin requests

## Structure

- `main.py`: FastAPI application with API routes
- `agent.py`: RAG logic for embeddings, retrieval, and answer generation
- `ingest_content.py`: Script to process markdown files from docs directory
- `data/`: Directory containing book content chunks
- `.env`: Environment variables (not committed)
- `requirements.txt`: Python dependencies

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run the server: `uvicorn main:app --reload`

## API Endpoints

- `POST /query` - Submit a question and receive an answer based on book content
- `POST /ingest` - Ingest book content from docs directory into the vector database
- `GET /health` - Health check endpoint

## Content Ingestion

The system can automatically ingest content from the docs directory using two methods:

1. **API Endpoint**: Send a POST request to `/ingest` to start the ingestion process
2. **Direct Script**: Run `python ingest_content.py` to process all markdown files

The ingestion process:
- Reads all `.md` files from the `ai_frontend_book/docs` directory
- Splits large documents into smaller chunks for optimal embedding
- Stores content in Qdrant vector database with metadata
- Preserves source information for citations