from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import os
from datetime import datetime

# Import from our modules
from .config import agent_config
from ..shared.models import HealthResponse, QueryRequest, QueryResponse
from ..shared.qdrant_client import QdrantClientWrapper
from .agent import RAGAgent
from .models import EnhancedQueryRequest, EnhancedQueryResponse
from .retrieval import RetrievalService
from ..shared.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title=agent_config.app_title,
    version=agent_config.app_version,
    description="RAG System for Book Content Question Answering"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=agent_config.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Agent
rag_agent = RAGAgent()


@app.get("/")
async def root():
    """Root endpoint to confirm the service is running"""
    return {
        "message": "Book RAG System API",
        "version": agent_config.app_version,
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify all services are accessible"""
    logger.info("Health check requested")
    try:
        # Check Qdrant connection
        qdrant_client = QdrantClientWrapper()
        qdrant_connected = qdrant_client.health_check()
        logger.info(f"Qdrant health check: {'OK' if qdrant_connected else 'FAILED'}")

        # Check OpenAI connection by checking if API key is set
        openai_connected = bool(agent_config.openai_api_key)
        logger.info(f"OpenAI API key configured: {openai_connected}")

        # Check database connection (simplified check)
        database_connected = bool(agent_config.database_url)
        logger.info(f"Database URL configured: {database_connected}")

        # Determine overall status
        overall_status = "healthy" if all([qdrant_connected, openai_connected]) else "unhealthy"

        message = "All services operational" if overall_status == "healthy" else "Some services may be unavailable"
        logger.info(f"Health check result: {overall_status} - {message}")

        health_response = HealthResponse(
            status=overall_status,
            openai_connected=openai_connected,
            qdrant_connected=qdrant_connected,
            database_connected=database_connected,
            message=message
        )

        return health_response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(query_request: QueryRequest):
    """Endpoint to process user queries and return RAG agent responses"""
    request_id = f"req_{hash(str(query_request.query)) % 1000000}"
    logger.info(f"[{request_id}] Processing query: {query_request.query[:50]}...")

    try:
        # Validate input
        if not query_request.query or not query_request.query.strip():
            logger.warning(f"[{request_id}] Empty query received")
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if len(query_request.query) > 1000:  # Example limit
            logger.warning(f"[{request_id}] Query too long: {len(query_request.query)} characters")
            raise HTTPException(status_code=400, detail="Query too long, maximum 1000 characters")

        if query_request.selected_text and len(query_request.selected_text) > 2000:  # Example limit
            logger.warning(f"[{request_id}] Selected text too long: {len(query_request.selected_text)} characters")
            raise HTTPException(status_code=400, detail="Selected text too long, maximum 2000 characters")

        logger.debug(f"[{request_id}] Input validation passed")

        # Process the query using the RAG agent
        response = rag_agent.query(query_request)

        # Validate response
        if not response.response:
            logger.error(f"[{request_id}] Agent returned empty response")
            raise HTTPException(status_code=500, detail="Agent returned empty response")

        logger.info(f"[{request_id}] Query processed successfully in {response.processing_time_ms}ms")
        return response
    except HTTPException as e:
        logger.error(f"[{request_id}] HTTP error in query processing: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in query processing: {str(e)}", exc_info=True)
        import traceback
        error_details = f"Query processing failed: {str(e)}"
        # In production, you might not want to return the full traceback
        if agent_config.debug:
            error_details += f"\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_details)


@app.post("/query/enhanced", response_model=EnhancedQueryResponse)
async def enhanced_query_endpoint(query_request: EnhancedQueryRequest):
    """Enhanced endpoint with additional metadata and options"""
    try:
        # Validate input
        if not query_request.query or not query_request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if len(query_request.query) > 1000:  # Example limit
            raise HTTPException(status_code=400, detail="Query too long, maximum 1000 characters")

        if query_request.selected_text and len(query_request.selected_text) > 2000:  # Example limit
            raise HTTPException(status_code=400, detail="Selected text too long, maximum 2000 characters")

        # Convert EnhancedQueryRequest to QueryRequest for the agent
        base_request = QueryRequest(
            query=query_request.query,
            selected_text=query_request.selected_text,
            page_url=query_request.page_url,
            session_id=query_request.session_id,
            timestamp=query_request.timestamp
        )

        # Process the query using the RAG agent
        base_response = rag_agent.query(base_request)

        # Convert to EnhancedQueryResponse
        enhanced_response = EnhancedQueryResponse(
            response=base_response.response,
            citations=base_response.citations,
            confidence=base_response.confidence,
            retrieved_chunks=base_response.retrieved_chunks,
            processing_time_ms=base_response.processing_time_ms,
            request_id=base_response.request_id,
            timestamp=base_response.timestamp,
            status="completed"  # In a real implementation, you'd track actual status
        )

        return enhanced_response
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_details = f"Enhanced query processing failed: {str(e)}"
        # In production, you might not want to return the full traceback
        if agent_config.debug:
            error_details += f"\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_details)


@app.post("/validate-query")
async def validate_query(query_request: QueryRequest):
    """Validate a query without processing it"""
    try:
        # Perform validation checks
        errors = []

        if not query_request.query or not query_request.query.strip():
            errors.append("Query cannot be empty")

        if len(query_request.query) > 1000:
            errors.append("Query too long, maximum 1000 characters")

        if query_request.selected_text and len(query_request.selected_text) > 2000:
            errors.append("Selected text too long, maximum 2000 characters")

        if query_request.page_url and len(query_request.page_url) > 2000:
            errors.append("Page URL too long, maximum 2000 characters")

        if errors:
            return {"valid": False, "errors": errors}
        else:
            return {"valid": True, "errors": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/config")
async def get_config():
    """Return current configuration (excluding sensitive data)"""
    config_dict = agent_config.dict()

    # Remove sensitive information from the response
    sensitive_keys = ['openai_api_key', 'qdrant_api_key', 'database_url']
    for key in sensitive_keys:
        if key in config_dict:
            config_dict[key] = "***" if config_dict[key] else ""

    return config_dict


@app.get("/stats")
async def get_stats():
    """Get statistics about the RAG system"""
    qdrant_client = QdrantClientWrapper()
    retrieval_service = RetrievalService()

    stats = {
        "total_documents": qdrant_client.count_points(),
        "qdrant_health": qdrant_client.health_check(),
        "model": agent_config.openai_model,
        "last_query_time": None,  # Would track actual last query time in a real implementation
    }

    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )