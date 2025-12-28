"""
Data models for book content entities.
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class BookContent(BaseModel):
    """
    Represents a single page of book material.

    Attributes:
        url: The URL of the book page
        title: The page title (extracted from HTML)
        content: The cleaned text content of the page
        section: Optional section or chapter information
        ingested_at: Timestamp when content was ingested
    """

    url: str = Field(..., description="URL of the book page")
    title: Optional[str] = Field(None, description="Page title from HTML")
    content: str = Field(..., description="Cleaned text content")
    section: Optional[str] = Field(None, description="Section or chapter info")
    ingested_at: datetime = Field(default_factory=datetime.utcnow, description="Ingestion timestamp")

    def model_post_init(self, __context: object) -> None:
        """Validate content is not empty."""
        if not self.content or not self.content.strip():
            raise ValueError("Book content cannot be empty")


class IngestedContent(BookContent):
    """
    Book content that has been ingested with embedding metadata.

    Attributes:
        embedding_id: Unique identifier in vector database
        embedding: The vector embedding of the content
    """

    embedding_id: Optional[int] = Field(None, description="ID in vector database")
    embedding: Optional[list[float]] = Field(None, description="Vector embedding")
