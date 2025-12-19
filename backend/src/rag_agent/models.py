from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from ..shared.models import QueryRequest, QueryResponse, Citation, ContentChunk, AgentConfig


class QueryStatus(str, Enum):
    """Status of a query processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EnhancedQueryRequest(BaseModel):
    """Enhanced query request with additional metadata"""
    query: str
    selected_text: Optional[str] = None
    page_url: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None
    # Additional options for the query
    include_citations: bool = True
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class EnhancedQueryResponse(BaseModel):
    """Enhanced query response with additional information"""
    response: str
    citations: List[Citation]
    confidence: Optional[float] = None
    retrieved_chunks: Optional[List[ContentChunk]] = None
    processing_time_ms: Optional[float] = None
    request_id: Optional[str] = None
    timestamp: datetime = datetime.now()
    status: QueryStatus = QueryStatus.COMPLETED
    error_message: Optional[str] = None
    # Additional metadata
    token_usage: Optional[Dict[str, int]] = None
    model_used: Optional[str] = None


class ConversationHistory(BaseModel):
    """Model for managing conversation history"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    queries: List[EnhancedQueryRequest] = []
    responses: List[EnhancedQueryResponse] = []
    metadata: Optional[Dict[str, Any]] = None

    def add_interaction(self, request: EnhancedQueryRequest, response: EnhancedQueryResponse):
        """Add a query-response pair to the conversation history"""
        self.queries.append(request)
        self.responses.append(response)
        self.updated_at = datetime.now()


class AgentStatus(BaseModel):
    """Model for agent status information"""
    is_healthy: bool
    model_loaded: bool
    qdrant_connected: bool
    total_documents: int
    last_query_time: Optional[datetime] = None
    error_count: int = 0
    active_sessions: int = 0


class QueryAnalytics(BaseModel):
    """Model for query analytics"""
    query_id: str
    query_text: str
    response_time_ms: float
    tokens_used: int
    citations_count: int
    confidence_score: Optional[float]
    timestamp: datetime = datetime.now()
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source_page: Optional[str] = None
    feedback_score: Optional[int] = None  # 1-5 rating
    feedback_comment: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Model for submitting feedback on a response"""
    query_id: str
    rating: int  # 1-5 scale
    comment: Optional[str] = None
    helpful: bool


class BatchQueryRequest(BaseModel):
    """Model for batch query requests"""
    queries: List[str]
    config: AgentConfig = AgentConfig()
    metadata: Optional[Dict[str, Any]] = None


class BatchQueryResponse(BaseModel):
    """Model for batch query responses"""
    responses: List[EnhancedQueryResponse]
    processing_time_ms: float
    total_queries: int
    successful_queries: int
    failed_queries: int


class AgentCapabilities(BaseModel):
    """Model describing agent capabilities"""
    supports_citations: bool = True
    supports_selected_text: bool = True
    max_context_length: int = 4096
    supported_file_types: List[str] = ["txt", "md", "pdf", "html"]
    max_query_length: int = 1000
    response_modes: List[str] = ["standard", "detailed", "concise"]