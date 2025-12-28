"""
FastAPI application for RAG Book Chatbot backend.

Exposes /chat endpoint for querying system.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from src.config import settings
from src.utils.logger import logger, setup_logger
from src.agent.rag_agent import rag_agent
from src.models.chat import ChatRequest, ChatResponse, Answer
from src.vector_db.qdrant_client import qdrant_client


# Setup logger on module load
setup_logger(settings.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RAG Book Chatbot Backend...")
    logger.info(f"Version: {settings.app_version}")
    logger.info(f"Qdrant Collection: {settings.qdrant_collection}")
    logger.info(f"LLM Model: {settings.openrouter_model}")

    # Ensure Qdrant collection exists
    try:
        qdrant_client.ensure_collection_exists()
        logger.info("[OK] Qdrant collection verified")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant: {e}")
        raise RuntimeError(f"Cannot start without Qdrant access: {e}")

    logger.info("[OK] Application started successfully")
    yield

    # Shutdown
    logger.info("Shutting down RAG Book Chatbot Backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend-only RAG chatbot for answering book questions",
    lifespan=lifespan,
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Status of application and its dependencies
    """
    # Check Qdrant connection
    qdrant_status = "healthy"
    try:
        collection_info = qdrant_client.get_collection_info()
        if collection_info is None:
            qdrant_status = "error"
            points_count = 0
        else:
            points_count = collection_info.points_count
    except Exception as e:
        qdrant_status = f"error: {str(e)}"
        points_count = 0

    return {
        "status": "healthy" if qdrant_status == "healthy" else "degraded",
        "qdrant": {
            "status": qdrant_status,
            "collection": settings.qdrant_collection,
            "points": points_count,
        },
    }


@app.post("/chat", tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - answer questions about book.

    Args:
        request: ChatRequest with user's question and optional conversation_id

    Returns:
        ChatResponse with generated answer, sources, and metadata

    Raises:
        HTTPException: If question processing fails
    """
    start_time = time.time()
    logger.info(f"Received chat request: {request.query[:50]}...")

    # Validate query is not empty
    query = request.query.strip()
    if not query:
        logger.warning("Empty query received")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )

    try:
        # Answer question using RAG agent
        # Note: Conversation history support will be added in User Story 3
        answer: Answer = await rag_agent.answer_question(
            question=query,
            conversation_history=None,  # Will implement in US3
        )

        # Calculate response time
        response_time = time.time() - start_time
        logger.info(f"Completed chat request in {response_time:.2f}s with {len(answer.sources)} sources")

        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"chat-{int(time.time())}"

        # Return response
        return ChatResponse(
            answer=answer.text,
            sources=answer.sources,
            conversation_id=conversation_id,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question. Please try again.",
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
