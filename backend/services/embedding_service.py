"""
Service to handle text embeddings using Cohere
"""
import os
import cohere
from typing import List
import sys

# Add the current directory to the Python path to allow imports from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import Config

class EmbeddingService:
    def __init__(self):
        # Initialize Cohere client
        if not Config.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(Config.COHERE_API_KEY)
        self.model = "embed-multilingual-v3.0"  # Using a multilingual model for book content

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        # Note: Cohere's API is synchronous, so we'll make it appear async
        # In a real async environment, you might use aiohttp to call the API
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"  # Using search_document for content retrieval
        )

        return response.embeddings

    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="search_query"  # Using search_query for user queries
        )

        return response.embeddings[0]