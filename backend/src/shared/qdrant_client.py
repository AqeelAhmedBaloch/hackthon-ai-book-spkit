from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional, Any
from .models import ContentChunk, EmbeddingRecord
from .config import config
import logging


class QdrantClientWrapper:
    """
    Wrapper class for Qdrant client to handle vector operations
    for the RAG system
    """

    def __init__(self):
        # Initialize Qdrant client based on configuration
        if config.qdrant_api_key:
            self.client = QdrantClient(
                url=config.qdrant_url,
                api_key=config.qdrant_api_key,
                prefer_grpc=True
            )
        else:
            self.client = QdrantClient(
                url=config.qdrant_url,
                prefer_grpc=True
            )

        self.collection_name = config.qdrant_collection
        self.logger = logging.getLogger(__name__)

    def create_collection(self, vector_size: int = 1536) -> bool:
        """
        Create a collection in Qdrant for storing embeddings
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with specified vector size
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                self.logger.info(f"Created collection: {self.collection_name}")
                return True
            else:
                self.logger.info(f"Collection {self.collection_name} already exists")
                return True
        except Exception as e:
            self.logger.error(f"Failed to create collection: {e}")
            return False

    def store_embeddings(self, records: List[EmbeddingRecord]) -> bool:
        """
        Store embeddings in the Qdrant collection
        """
        try:
            points = []
            for record in records:
                points.append(
                    models.PointStruct(
                        id=record.vector_id,
                        vector=record.vector,
                        payload=record.payload
                    )
                )

            # Upload points to the collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            self.logger.info(f"Stored {len(points)} embeddings in collection: {self.collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store embeddings: {e}")
            return False

    def search_similar(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict] = None) -> List[ContentChunk]:
        """
        Search for similar content based on the query vector
        """
        try:
            # Build filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

                if filter_conditions:
                    qdrant_filters = models.Filter(
                        must=filter_conditions
                    )

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filters
            )

            # Convert results to ContentChunk objects
            results = []
            for result in search_results:
                payload = result.payload
                content_chunk = ContentChunk(
                    id=result.id,
                    content=payload.get("content", ""),
                    source_document=payload.get("source_document", ""),
                    page_number=payload.get("page_number"),
                    section=payload.get("section"),
                    metadata=payload.get("metadata"),
                    embedding=None,  # Embedding is not needed in the result
                    hash=payload.get("hash")
                )
                results.append(content_chunk)

            self.logger.info(f"Found {len(results)} similar content chunks")
            return results
        except Exception as e:
            self.logger.error(f"Failed to search similar content: {e}")
            return []

    def get_content_by_id(self, content_id: str) -> Optional[ContentChunk]:
        """
        Retrieve a specific content chunk by its ID
        """
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[content_id]
            )

            if records:
                record = records[0]
                payload = record.payload
                content_chunk = ContentChunk(
                    id=record.id,
                    content=payload.get("content", ""),
                    source_document=payload.get("source_document", ""),
                    page_number=payload.get("page_number"),
                    section=payload.get("section"),
                    metadata=payload.get("metadata"),
                    embedding=None,
                    hash=payload.get("hash")
                )
                return content_chunk
            else:
                self.logger.warning(f"No content found for ID: {content_id}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve content by ID: {e}")
            return None

    def delete_collection(self) -> bool:
        """
        Delete the entire collection (use with caution)
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self.logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete collection: {e}")
            return False

    def count_points(self) -> int:
        """
        Get the number of points (embeddings) in the collection
        """
        try:
            count = self.client.count(
                collection_name=self.collection_name
            )
            return count.count
        except Exception as e:
            self.logger.error(f"Failed to count points: {e}")
            return 0

    def health_check(self) -> bool:
        """
        Check if the Qdrant connection is healthy
        """
        try:
            # Try to get collections to verify connection
            self.client.get_collections()
            return True
        except Exception as e:
            self.logger.error(f"Qdrant health check failed: {e}")
            return False