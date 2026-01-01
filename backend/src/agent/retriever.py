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
    Returns results above threshold OR best matches if none are above threshold,
    all in a single efficient database query.

    Args:
        query_embedding: The query's vector embedding
        top_k: Number of results to return (defaults to settings)
        score_threshold: Minimum similarity score (0-1)

    Returns:
        List of retrieved content sorted by relevance
    """
    if top_k is None:
        top_k = settings.top_k_results
    if score_threshold is None:
        score_threshold = settings.retrieve_score_threshold

    logger.debug(f"Retrieving top {top_k} results with threshold {score_threshold}")

    try:
        # Single query: Fetch slightly more results than requested to allow for filtering
        # while still having a fallback if threshold is too strict.
        # We don't set score_threshold in the query itself to avoid double-trips.
        results = await qdrant_client.search(
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=None,
        )

        # Process results
        retrieved = []
        above_threshold = []

        for result in results:
            payload = result.payload
            if not payload:
                continue

            content = RetrievedContent(
                url=payload.get("url", ""),
                title=payload.get("title"),
                content=payload.get("content", ""),
                score=getattr(result, "score", 0.0),
            )

            # Keep track of everything for fallback
            retrieved.append(content)

            # Keep track of what's actually "good" based on threshold
            if score_threshold is not None and content.score >= score_threshold:
                above_threshold.append(content)

        # Decision logic:
        # 1. If we found results above threshold, return only those
        if above_threshold:
            logger.info(f"Retrieved {len(above_threshold)} passages above threshold {score_threshold}")
            return above_threshold[:top_k]

        # 2. If nothing above threshold, return the best matches anyway (fallback)
        if retrieved:
            logger.warning(
                f"No results found with threshold {score_threshold}. "
                f"Returning {len(retrieved)} best matches as fallback."
            )
            return retrieved[:top_k]

        return []

    except Exception as e:
        logger.error(f"Failed to retrieve content from Qdrant: {e}", exc_info=True)
        raise RuntimeError(
            f"Failed to search the book database. This may be due to a database connection issue. "
            f"Error: {type(e).__name__}: {str(e)}"
        )


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
