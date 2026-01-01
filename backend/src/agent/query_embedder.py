"""
Query embedder to convert user questions to vector embeddings.
"""

from typing import List
from src.embeddings.local_client import local_embeddings_client
from src.utils.logger import logger
from src.utils.embedding_cache import embedding_cache


async def embed_query(query: str) -> List[float]:
    """
    Generate an embedding for a user's question.
    Uses local model (sentence-transformers) - no API rate limits!
    Uses cache to avoid repeated computations for identical queries.

    Args:
        query: The user's question text

    Returns:
        List of floats representing the embedding vector

    Raises:
        RuntimeError: If embedding generation fails
    """
    logger.debug(f"Generating embedding for query: {query[:50]}...")

    try:
        # Use cache to avoid repeated computations (local model is fast but still benefits from cache)
        embedding = await embedding_cache.get_or_embed(query, input_type="search_query")
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        logger.error(f"Failed to embed query with local model: {e}", exc_info=True)
        raise RuntimeError(
            f"Failed to generate embedding for query. "
            f"Error: {type(e).__name__}: {str(e)}"
        )
