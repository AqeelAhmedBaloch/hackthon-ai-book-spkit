from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import RAGAgent
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG Chatbot API",
    description="API for the RAG chatbot integrated into the Physical AI & Humanoid Robotics book",
    version="1.0.0"
)

# Add CORS middleware - restrict to book domain only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aqeelahmedbaloch.github.io",  # GitHub Pages domain for the book
        "https://hackthon-ai-book-spkit.vercel.app",  # Vercel deployment
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the RAG agent
rag_agent = RAGAgent()

class QuestionRequest(BaseModel):
    question: str
    selected_text: str = None

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/query", response_model=AnswerResponse)
async def query(question_request: QuestionRequest):
    """
    Submit a question and receive an answer based on the book content or selected text.
    If selected_text is provided, answer only from that text.
    Otherwise, retrieve from the vector database.
    """
    try:
        answer, sources = rag_agent.get_answer(question_request.question, question_request.selected_text)
        return AnswerResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_content():
    """
    Ingest book content from docs directory into the vector database.
    This endpoint processes all markdown files from the docs directory and stores them
    in the Qdrant vector database for semantic search.
    """
    try:
        from ingest_content import ingest_docs_content
        import threading

        # Run ingestion in a separate thread to avoid blocking
        def run_ingestion():
            try:
                ingest_docs_content()
            except Exception as e:
                print(f"Ingestion error: {str(e)}")

        thread = threading.Thread(target=run_ingestion)
        thread.start()

        return {"status": "ingestion started", "message": "Book content ingestion process initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)