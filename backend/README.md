# RAG Chatbot Backend

Backend service for the RAG (Retrieval-Augmented Generation) chatbot integrated into the Physical AI & Humanoid Robotics book.

## Structure

- `main.py`: FastAPI application with API routes
- `agent.py`: RAG logic for embeddings, retrieval, and answer generation
- `data/`: Directory containing book content chunks
- `.env`: Environment variables (not committed)
- `requirements.txt`: Python dependencies

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run the server: `uvicorn main:app --reload`

## API Endpoints

- `POST /chat`: Submit user questions and receive answers