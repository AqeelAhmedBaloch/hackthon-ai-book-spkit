"""
Service to handle vector database operations with Qdrant
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import sys
import os
# Add the current directory to the Python path to allow imports from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from services.embedding_service import EmbeddingService
from config import Config

class QdrantService:
    def __init__(self):
        # Initialize Qdrant client for Qdrant Cloud
        # For Qdrant Cloud, we only need the URL and API key
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY,
            check_compatibility=False  # Avoid version check warnings for Qdrant Cloud
        )

        self.collection_name = Config.QDRANT_COLLECTION_NAME
        self.embedding_service = EmbeddingService()

        # Don't automatically check/create collection during initialization
        # This will be handled in methods that need the collection
        self._collection_verified = False

    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists, create if it doesn't"""
        try:
            # Try to get collection info
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists")
        except:
            # Collection doesn't exist, create it
            print(f"Creating collection '{self.collection_name}'...")

            # Assuming Cohere embeddings are 1024-dimensional (this might vary)
            # We'll use a reasonable default, but in practice you'd check the embedding dimension
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),  # Adjust size as needed
            )

            print(f"Collection '{self.collection_name}' created successfully")

    async def upsert_embeddings(self, payloads: List[Dict[str, Any]]):
        """Upsert embeddings and payload into Qdrant"""
        # Ensure collection exists before upserting
        if not self._collection_verified:
            self._ensure_collection_exists()
            self._collection_verified = True

        # Generate embeddings for each payload
        texts = [payload['text'] for payload in payloads]
        embeddings = await self.embedding_service.generate_embeddings(texts)

        # Prepare points for upsert
        points = []
        for i, (payload, embedding) in enumerate(zip(payloads, embeddings)):
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": payload['text'],
                    "chapter": payload.get('chapter', ''),
                    "section": payload.get('section', ''),
                    "book_title": payload.get('book_title', ''),
                    "source_url": payload.get('source_url', '')
                }
            )
            points.append(point)

        # Upsert the points
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search_similar(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in Qdrant"""
        # Ensure collection exists before searching
        if not self._collection_verified:
            self._ensure_collection_exists()
            self._collection_verified = True

        # Generate embedding for the query
        query_embedding = await self.embedding_service.generate_single_embedding(query_text)

        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )

        # Extract the results with payload
        results = []
        for hit in search_results:
            result = {
                "text": hit.payload.get("text", ""),
                "chapter": hit.payload.get("chapter", ""),
                "section": hit.payload.get("section", ""),
                "book_title": hit.payload.get("book_title", ""),
                "source_url": hit.payload.get("source_url", ""),
                "score": hit.score
            }
            results.append(result)

        return results

    def get_total_count(self) -> int:
        """Get the total number of vectors in the collection"""
        # Ensure collection exists before getting count
        if not self._collection_verified:
            self._ensure_collection_exists()
            self._collection_verified = True

        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except:
            return 0