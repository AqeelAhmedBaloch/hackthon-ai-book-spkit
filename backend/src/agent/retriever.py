"""
Retriever to search Qdrant for relevant book content based on query embedding.
"""

from typing import List, Optional
from qdrant_client.http.models import ScoredPoint

from src.vector_db.qdrant_client import qdrant_client
from src.config import settings
from src.utils.logger import logger


class RetrievedContent:
    """Represents retrieved book content with metadata."""

    def __init__(
        self,
        url: str,
        title: Optional[str],
        content: str,
        score: float,
    ):
        self.url = url
        self.title = title
        self.content = content
        self.score = score


async def retrieve_content(
    query_embedding: List[float],
    top_k: Optional[int] = None,
    score_threshold: Optional[float] = None,
) -> List[RetrievedContent]:
    """
    Search Qdrant for relevant book content.

    Args:
        query_embedding: The query's vector embedding
        top_k: Number of results to return (defaults to settings)
        score_threshold: Minimum similarity score (0-1)

    Returns:
        List of retrieved content sorted by relevance

    Raises:
        RuntimeError: If retrieval fails
    """
    if top_k is None:
        top_k = settings.top_k_results
    if score_threshold is None:
        score_threshold = settings.retrieve_score_threshold

    logger.debug(f"Retrieving top {top_k} results with threshold {score_threshold}")

    try:
        results = qdrant_client.search(
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # Convert to RetrievedContent objects
        retrieved = []
        for result in results:
            payload = result.payload
            content = RetrievedContent(
                url=payload.get("url", ""),
                title=payload.get("title"),
                content=payload.get("content", ""),
                score=getattr(result, "score", 0.0),
            )
            retrieved.append(content)

        logger.info(f"Retrieved {len(retrieved)} relevant passages")
        return retrieved

    except Exception as e:
        logger.error(f"Failed to retrieve content from Qdrant: {e}")
        raise


def format_context_for_llm(retrieved: List[RetrievedContent]) -> str:
    """
    Format retrieved content as context string for LLM.

    Args:
        retrieved: List of retrieved content

    Returns:
        Formatted context string with sources
    """
    if not retrieved:
        return "No relevant content found in the book."

    context_parts = []
    for i, item in enumerate(retrieved, 1):
        title_part = f" from '{item.title}'" if item.title else ""
        context_parts.append(
            f"Source {i}{title_part}:\n{item.content}\n"
        )

    context = "\n".join(context_parts)
    logger.debug(f"Formatted context with {len(context)} characters")
    return context
