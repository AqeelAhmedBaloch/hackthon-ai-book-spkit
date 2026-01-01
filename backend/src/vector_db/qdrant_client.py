"""
Qdrant vector database client for storing and retrieving book content embeddings.
"""

import asyncio
from typing import Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from src.config import settings


class QdrantClientWrapper:
    """Async wrapper for Qdrant client with optimized timeouts."""

    def __init__(self):
        """Initialize Qdrant client with configuration."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=5,  # Optimized: 5 second timeout (down from 10s)
        )
        self.collection_name = settings.qdrant_collection

    async def ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = await asyncio.to_thread(self.client.get_collections)
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                await asyncio.to_thread(
                    self.client.create_collection,
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dim,  # Use configurable embedding dimension (384 for local, 1024 for Cohere)
                        distance=Distance.COSINE,
                    ),
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to ensure Qdrant collection exists: {e}")

    async def upsert_points(self, points: list[PointStruct]) -> None:
        """Insert or update points in collection."""
        try:
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=self.collection_name,
                points=points,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upsert points to Qdrant: {e}")

    async def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ):
        """
        Search for similar vectors in collection.

        Args:
            query_vector: The embedding vector to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of scored points sorted by similarity
        """
        try:
            results = await asyncio.to_thread(
                self.client.query_points,
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                timeout=5,  # Optimized: 5s (down from 10s)
            )
            return results.points
        except Exception as e:
            raise RuntimeError(f"Failed to search Qdrant: {e}")

    async def get_collection_info(self) -> Optional[models.CollectionInfo]:
        """Get information about collection."""
        try:
            return await asyncio.to_thread(self.client.get_collection, self.collection_name)
        except Exception:
            return None

    async def delete_collection(self) -> None:
        """Delete collection (use with caution!)."""
        try:
            await asyncio.to_thread(self.client.delete_collection, self.collection_name)
        except Exception as e:
            raise RuntimeError(f"Failed to delete Qdrant collection: {e}")

    async def close(self):
        """Close Qdrant client connection."""
        try:
            await asyncio.to_thread(self.client.close)
        except Exception:
            pass


# Global Qdrant client instance
qdrant_client = QdrantClientWrapper()
