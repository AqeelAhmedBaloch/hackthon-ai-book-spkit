"""
Local embeddings client using sentence-transformers.
No API rate limits - runs entirely on your machine.
"""

from typing import List
from sentence_transformers import SentenceTransformer
import asyncio
from src.utils.logger import logger


class LocalEmbeddingsClient:
    """Client for generating embeddings locally using sentence-transformers."""

    def __init__(self):
        """Initialize local embedding model.
        Uses all-MiniLM-L6-v2 which is fast and produces 384-dim embeddings.
        """
        self.model_name = "all-MiniLM-L6-v2"
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        """Get or create singleton model instance."""
        if self._model is None:
            logger.info(f"Loading local embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimensions: {self._model.get_sentence_embedding_dimension()}")
        return self._model

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            model = self._get_model()
            # Run in thread pool to avoid blocking async event loop
            embedding = await asyncio.to_thread(model.encode, text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate local embedding: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate embedding: {type(e).__name__}: {str(e)}")

    async def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched for efficiency).

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per request

        Returns:
            List of embedding vectors (one per input text)
        """
        try:
            model = self._get_model()
            # Run in thread pool to avoid blocking async event loop
            embeddings = await asyncio.to_thread(
                model.encode,
                texts,
                batch_size=batch_size,
                show_progress_bar=False
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate local embeddings: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate embeddings: {type(e).__name__}: {str(e)}")

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a search query.
        Same as embed_text for local models (no input_type distinction).

        Args:
            query: The search query to embed

        Returns:
            List of floats representing the embedding vector
        """
        return await self.embed_text(query)

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        model = self._get_model()
        return model.get_sentence_embedding_dimension()

    async def close(self):
        """Clean up resources (no-op for local models)."""
        # No connection to close for local models
        pass


# Global local embeddings client instance
local_embeddings_client = LocalEmbeddingsClient()
