"""
Qdrant vector database client for storing and retrieving book content embeddings.
"""

from typing import Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from src.config import settings


class QdrantClientWrapper:
    """Wrapper for Qdrant client to manage book content vectors."""

    def __init__(self):
        """Initialize Qdrant client with configuration."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection

    def ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1024,  # Cohere embed-english-v3.0 uses 1024 dimensions
                        distance=Distance.COSINE,
                    ),
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to ensure Qdrant collection exists: {e}")

    def upsert_points(self, points: list[PointStruct]) -> None:
        """Insert or update points in the collection."""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upsert points to Qdrant: {e}")

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[models.ScoredPoint]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: The embedding vector to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of scored points sorted by similarity
        """
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            return results.points
        except Exception as e:
            raise RuntimeError(f"Failed to search Qdrant: {e}")

    def get_collection_info(self) -> Optional[models.CollectionInfo]:
        """Get information about the collection."""
        try:
            return self.client.get_collection(self.collection_name)
        except Exception:
            return None

    def delete_collection(self) -> None:
        """Delete the collection (use with caution!)."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception as e:
            raise RuntimeError(f"Failed to delete Qdrant collection: {e}")


# Global Qdrant client instance
qdrant_client = QdrantClientWrapper()
