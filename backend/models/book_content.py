"""
Data model for book content chunks
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookContent(BaseModel):
    """
    Represents the book content that is chunked and stored in the vector database
    """
    id: Optional[str] = Field(None, description="Unique identifier for the content chunk")
    text: str = Field(..., min_length=1, description="The actual text content of the chunk")
    chapter: str = Field(..., min_length=1, description="The chapter title or identifier")
    section: str = Field(..., min_length=1, description="The section title or identifier")
    book_title: str = Field(..., min_length=1, description="Title of the book")
    source_url: str = Field(..., min_length=1, description="URL or reference to the original source")
    token_count: Optional[int] = Field(None, ge=300, le=800, description="Number of tokens in the text chunk")
    embedding: Optional[list] = Field(None, description="The vector embedding of the text")
    created_at: datetime = Field(default_factory=datetime.now, description="When this content was created")

    class Config:
        # Allow extra fields for flexibility when storing in Qdrant
        extra = "allow"