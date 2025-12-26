"""
Configuration loader for the RAG Chatbot
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    # Cohere configuration
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")

    # Anthropic configuration
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Qdrant configuration
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "ai_book_vdb")

    # Book configuration
    BOOK_SITEMAP_URL: Optional[str] = os.getenv("BOOK_SITEMAP_URL")

    # Token limits
    MIN_TOKENS_PER_CHUNK: int = 300
    MAX_TOKENS_PER_CHUNK: int = 800


    # Validation
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "COHERE_API_KEY",
            "ANTHROPIC_API_KEY",
            "QDRANT_URL",
            "QDRANT_API_KEY",
            "QDRANT_COLLECTION_NAME",
            "BOOK_SITEMAP_URL"
        ]

        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        return True

    @classmethod
    def validate_for_deployment(cls):
        """Validate configuration for deployment (with required vars)"""
        cls.validate()