"""
Cohere embeddings client for converting text to vector embeddings.
"""

from typing import List
import httpx
from src.config import settings


class CohereEmbeddingsClient:
    """Client for generating text embeddings using Cohere API."""

    def __init__(self):
        """Initialize Cohere client with API key and model."""
        self.api_key = settings.cohere_api_key
        self.model = settings.cohere_model
        self.base_url = "https://api.cohere.ai/v1"

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embed",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-Client-Name": "rag-book-chatbot",
                    },
                    json={
                        "texts": [text],
                        "model": self.model,
                        "input_type": "search_document",
                        "truncate": "END",
                    },
                )
                response.raise_for_status()

                data = response.json()
                return data["embeddings"][0]

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Cohere API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding with Cohere: {e}")

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

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.base_url}/embed",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "X-Client-Name": "rag-book-chatbot",
                        },
                        json={
                            "texts": batch,
                            "model": self.model,
                            "input_type": "search_document",
                            "truncate": "END",
                        },
                    )
                    response.raise_for_status()

                    data = response.json()
                    all_embeddings.extend(data["embeddings"])

            except httpx.HTTPStatusError as e:
                raise RuntimeError(
                    f"Cohere API error at batch {i//batch_size}: "
                    f"{e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to generate batch embeddings with Cohere: {e}")

        return all_embeddings

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a search query.

        Args:
            query: The search query to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embed",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-Client-Name": "rag-book-chatbot",
                    },
                    json={
                        "texts": [query],
                        "model": self.model,
                        "input_type": "search_query",
                        "truncate": "END",
                    },
                )
                response.raise_for_status()

                data = response.json()
                return data["embeddings"][0]

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Cohere API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate query embedding with Cohere: {e}")


# Global Cohere embeddings client instance
cohere_client = CohereEmbeddingsClient()
