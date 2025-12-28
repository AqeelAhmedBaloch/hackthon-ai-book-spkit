"""
Query embedder to convert user questions to vector embeddings.
"""

from typing import List
from src.embeddings.cohere_client import cohere_client
from src.utils.logger import logger


async def embed_query(query: str) -> List[float]:
    """
    Generate an embedding for a user's question.

    Args:
        query: The user's question text

    Returns:
        List of floats representing the embedding vector

    Raises:
        RuntimeError: If embedding generation fails
    """
    logger.debug(f"Generating embedding for query: {query[:50]}...")

    try:
        embedding = await cohere_client.embed_query(query)
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        logger.error(f"Failed to embed query: {e}")
        raise
