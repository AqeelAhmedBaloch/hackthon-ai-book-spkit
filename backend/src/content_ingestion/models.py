from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class ContentFormat(str, Enum):
    """Supported content formats for ingestion"""
    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"


class IngestionConfig(BaseModel):
    """Configuration for content ingestion"""
    chunk_size: int = 512
    chunk_overlap: int = 50
    model: str = "text-embedding-ada-002"
    batch_size: int = 10
    content_format: ContentFormat = ContentFormat.TEXT
    min_chunk_length: int = 10
    max_chunk_length: int = 2000
    enable_deduplication: bool = True
    preserve_metadata: bool = True
    process_images: bool = False  # Whether to extract and process images
    process_tables: bool = True   # Whether to specially handle table content


class IngestionRequest(BaseModel):
    """Request model for content ingestion"""
    source_path: str
    config: IngestionConfig = IngestionConfig()
    collection_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IngestionResponse(BaseModel):
    """Response model for content ingestion"""
    status: str  # 'success', 'partial', 'failed'
    processed_chunks: int
    collection_name: str
    processing_time_ms: float
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class IngestionProgress(BaseModel):
    """Model to track ingestion progress"""
    total_files: int
    processed_files: int
    total_chunks: int
    processed_chunks: int
    current_file: Optional[str] = None
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    progress_percentage: float = 0.0
    estimated_completion_time: Optional[float] = None  # in seconds