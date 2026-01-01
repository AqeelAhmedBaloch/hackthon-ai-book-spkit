"""
Cohere embeddings client for converting text to vector embeddings.
"""

from typing import List, Optional
import httpx
from src.config import settings
from src.utils.retry import async_retry


class CohereEmbeddingsClient:
    """Client for generating text embeddings using Cohere API."""

    def __init__(self):
        """Initialize Cohere client with API key and model."""
        self.api_key = settings.cohere_api_key
        self.model = settings.cohere_model
        self.base_url = "https://api.cohere.ai/v1"
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create singleton httpx client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0, http2=False)
        return self._client

    async def close(self):
        """Close the underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @async_retry()
    async def _execute_embedding_request(
        self, texts: List[str], input_type: str = "search_document"
    ) -> List[List[float]]:
        """
        Internal method to execute an embedding request with retry logic.
        """
        try:
            client = self._get_client()
            response = await client.post(
                f"{self.base_url}/embed",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Client-Name": "rag-book-chatbot",
                },
                json={
                    "texts": texts,
                    "model": self.model,
                    "input_type": input_type,
                    "truncate": "END",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"]

        except httpx.TimeoutException as e:
            raise RuntimeError(f"Cohere API timeout: {str(e)}")
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if hasattr(e.response, "text") else str(e)
            raise RuntimeError(f"Cohere API error: {e.response.status_code} - {error_text}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding with Cohere: {type(e).__name__}: {str(e)}")

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        embeddings = await self._execute_embedding_request([text], input_type="search_document")
        return embeddings[0]

    async def embed_texts(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched for efficiency).

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per request

        Returns:
            List of embedding vectors (one per input text)
        """
        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = await self._execute_embedding_request(batch, input_type="search_document")
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a search query.

        Args:
            query: The search query to embed

        Returns:
            List of floats representing the embedding vector
        """
        embeddings = await self._execute_embedding_request([query], input_type="search_query")
        return embeddings[0]


# Global Cohere embeddings client instance
cohere_client = CohereEmbeddingsClient()
