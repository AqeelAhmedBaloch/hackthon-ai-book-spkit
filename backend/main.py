from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG Chatbot for Physical AI & Humanoid Robotics Book")

import sys
import os
# Add the current directory to the Python path to allow imports from subdirectories
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import services after app initialization to avoid circular imports
from services.rag_service import RAGService
from models.query import QueryRequest, QueryResponse, Reference

# Initialize RAG service
rag_service = RAGService()

class ChatRequest(BaseModel):
    question: str
    selected_text: Optional[str] = ""

@app.get("/")
async def root():
    return {"message": "RAG Chatbot for Physical AI & Humanoid Robotics Book API"}

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a user question and return an answer based on book content.
    """
    try:
        # Validate input
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Process the query using RAG service
        response = await rag_service.process_query(request.question, request.selected_text)
        return response
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        # Log the actual error for debugging (optional - you might want to add proper logging)
        print(f"Error processing query: {str(e)}")
        # According to spec: If retrieval returns no results, respond EXACTLY: "This topic is not covered in the book"
        # No generic error messages should be returned to the user
        # Return a response with the specific fallback message instead of an HTTP error
        from datetime import datetime
        import uuid
        return QueryResponse(
            id=str(uuid.uuid4()),
            answer="This topic is not covered in the book",
            references=[],
            timestamp=datetime.now()
        )