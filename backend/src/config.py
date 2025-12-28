"""
Environment configuration for the RAG Book Chatbot.
Loads settings from environment variables using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="RAG Book Chatbot Backend", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # OpenRouter Configuration
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="mistralai/devstral-2512:free", alias="OPENROUTER_MODEL")

    # Cohere Configuration
    cohere_api_key: str = Field(..., alias="COHERE_API_KEY")
    cohere_model: str = Field(default="embed-english-v3.0", alias="COHERE_MODEL")

    # Qdrant Configuration
    qdrant_url: str = Field(..., alias="QDRANT_URL")
    qdrant_api_key: str = Field(..., alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="book_content", alias="QDRANT_COLLECTION")

    # RAG Settings
    max_context_tokens: int = Field(default=4000, alias="MAX_CONTEXT_TOKENS")
    top_k_results: int = Field(default=5, alias="TOP_K_RESULTS")
    retrieve_score_threshold: float = Field(default=0.5, alias="RETRIEVE_SCORE_THRESHOLD")


# Global settings instance
settings = Settings()
