"""
Data models for chat/question-answer interactions.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Question(BaseModel):
    """
    Represents a user question submitted to the system.

    Attributes:
        query: The user's question text
        conversation_id: Optional session identifier for context
        timestamp: When the question was submitted
    """

    query: str = Field(..., description="User's question", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Session identifier for context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Question timestamp")


class Source(BaseModel):
    """
    Reference to a source document used for an answer.

    Attributes:
        url: URL of the source page
        title: Title of the source page
        score: Relevance score (0-1)
    """

    url: str = Field(..., description="Source URL")
    title: Optional[str] = Field(None, description="Source page title")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")


class Answer(BaseModel):
    """
    Represents the system response to a user question.

    Attributes:
        text: The generated answer
        sources: List of source references from the book
        confidence: Overall confidence in the answer (0-1)
        conversation_id: Session identifier
        timestamp: When the answer was generated
    """

    text: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source references")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Answer confidence")
    conversation_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Answer timestamp")


class Message(BaseModel):
    """
    Represents a message in a conversation.

    Attributes:
        role: Either 'user' or 'assistant'
        content: The message content
        timestamp: When the message was sent
    """

    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class Conversation(BaseModel):
    """
    Represents a session of questions and answers.

    Attributes:
        conversation_id: Unique session identifier
        messages: History of messages in the conversation
        created_at: When the conversation started
        last_updated: Last activity timestamp
    """

    conversation_id: str = Field(..., description="Session identifier")
    messages: List[Message] = Field(default_factory=list, description="Message history")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update")

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
        self.last_updated = datetime.utcnow()

    def get_history_for_llm(self) -> List[dict]:
        """Get conversation history formatted for LLM (excluding timestamps)."""
        return [{"role": m.role, "content": m.content} for m in self.messages[:-1]]


# API Request/Response Models
class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""

    query: str = Field(..., description="User's question", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Optional session ID")


class ChatResponse(BaseModel):
    """Response model for /chat endpoint."""

    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source references")
    conversation_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response time")
