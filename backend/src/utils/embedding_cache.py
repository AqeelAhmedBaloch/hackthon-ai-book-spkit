"""
Simple embedding cache to avoid repeated computations for identical queries.
"""

import time
from typing import Optional, List
from src.embeddings.local_client import local_embeddings_client


class EmbeddingCache:
    """Thread-safe in-memory cache for query embeddings."""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.cache: dict[str, tuple[List[float], float]] = {}
        self.ttl = ttl_seconds

    async def get_or_embed(
        self,
        query: str,
        input_type: str = "search_query",
    ) -> List[float]:
        """
        Get embedding from cache or compute and store.
        Uses local model (sentence-transformers) - no API calls!

        Args:
            query: The text query to embed
            input_type: Type of embedding (search_query or search_document) - local model treats them the same

        Returns:
            The embedding vector
        """
        now = time.time()

        # Check cache for valid entry
        if query in self.cache:
            embedding, timestamp = self.cache[query]
            if now - timestamp < self.ttl:
                return embedding
            else:
                # Expired, remove
                del self.cache[query]

        # Cache miss - compute embedding with local model
        # Note: Local model doesn't distinguish input_type, so we use embed_text for both
        embedding = await local_embeddings_client.embed_text(query)

        # Store in cache
        self.cache[query] = (embedding, now)

        return embedding

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "ttl_seconds": self.ttl,
        }


# Global cache instance
embedding_cache = EmbeddingCache()
