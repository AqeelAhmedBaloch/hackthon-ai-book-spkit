"""
Data models for user queries and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """
    The request model for user queries
    """
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question about the book content")
    selected_text: Optional[str] = Field("", max_length=5000, description="Additional context from selected text")


class Reference(BaseModel):
    """
    A reference to the book content used in the answer
    """
    chapter: str = Field(..., description="Chapter name or identifier")
    section: str = Field(..., description="Section name or identifier")
    source_url: str = Field(..., description="URL reference to the original content")


class QueryResponse(BaseModel):
    """
    The response model for query results
    """
    id: str
    answer: str = Field(..., description="The answer text (or 'This topic is not covered in the book')")
    references: List[Reference] = Field(..., description="List of source references")
    timestamp: datetime = Field(default_factory=datetime.now, description="ISO 8601 formatted timestamp")