from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime


class ContentChunk(BaseModel):
    """Model for content chunks stored in the vector database"""
    id: str
    content: str
    source_document: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    hash: Optional[str] = None


class EmbeddingRecord(BaseModel):
    """Model for embedding records in the vector database"""
    vector_id: str
    vector: List[float]
    payload: Dict[str, Any]
    collection_name: str


class IngestionConfig(BaseModel):
    """Configuration for content ingestion"""
    chunk_size: int = 512
    chunk_overlap: int = 50
    model: str = "text-embedding-ada-002"
    batch_size: int = 10
    content_format: str = "markdown"


class QueryRequest(BaseModel):
    """Model for query requests to the RAG agent"""
    query: str
    selected_text: Optional[str] = None
    page_url: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = datetime.now()


class QueryResponse(BaseModel):
    """Model for query responses from the RAG agent"""
    response: str
    citations: List['Citation']
    confidence: Optional[float] = None
    retrieved_chunks: Optional[List[ContentChunk]] = None
    processing_time_ms: Optional[float] = None
    request_id: Optional[str] = None
    timestamp: datetime = datetime.now()


class Citation(BaseModel):
    """Model for citations in agent responses"""
    source_document: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    text_snippet: str
    similarity_score: Optional[float] = None


class ChatMessage(BaseModel):
    """Model for chat messages in conversation history"""
    id: str
    content: str
    sender: str  # 'user' or 'assistant'
    timestamp: datetime = datetime.now()
    citations: Optional[List[Citation]] = None
    status: str = "sent"  # 'sent', 'pending', 'received', 'error'


class ChatSession(BaseModel):
    """Model for chat session management"""
    session_id: str
    created_at: datetime = datetime.now()
    last_activity: datetime = datetime.now()
    messages: List[ChatMessage] = []
    current_page: Optional[str] = None


class ValidationResult(BaseModel):
    """Model for validation results"""
    id: str
    timestamp: datetime = datetime.now()
    query_text: str
    retrieved_chunks: List[ContentChunk]
    expected_chunks: Optional[List[ContentChunk]] = None
    accuracy_score: Optional[float] = None
    metadata_preservation_rate: Optional[float] = None
    consistency_score: Optional[float] = None
    retrieval_time_ms: Optional[float] = None
    status: str  # 'PASS', 'FAIL', 'WARNING'


class AgentConfig(BaseModel):
    """Configuration for the RAG agent"""
    model: str = "gpt-4-turbo"
    temperature: float = 0.1
    max_tokens: int = 1000
    retrieval_top_k: int = 5
    similarity_threshold: float = 0.7
    citation_required: bool = True


class HealthResponse(BaseModel):
    """Model for health check responses"""
    status: str  # 'healthy', 'unhealthy'
    openai_connected: bool = False
    qdrant_connected: bool = False
    database_connected: bool = False
    message: str = ""


# Update forward references
QueryResponse.update_forward_refs()