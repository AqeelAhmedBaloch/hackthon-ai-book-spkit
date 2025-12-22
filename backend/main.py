from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import RAGAgent
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
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

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize the RAG agent
rag_agent = RAGAgent()

class QuestionRequest(BaseModel):
    question: str
    selected_text: str = None

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/query", response_model=AnswerResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def query(request, question_request: QuestionRequest):
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

@app.get("/health")
@limiter.limit("30/minute")  # Limit to 30 requests per minute per IP for health checks
async def health_check(request):
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)