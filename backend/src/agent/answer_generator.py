"""
Answer generator using OpenRouter LLM to generate responses based on retrieved context.
"""

from typing import Optional, List
from src.llm.openrouter_client import openrouter_client
from src.agent.retriever import RetrievedContent
from src.models.chat import Source
from src.utils.logger import logger


async def generate_answer(
    question: str,
    retrieved_content: List[RetrievedContent],
    conversation_history: Optional[List[dict]] = None,
) -> tuple[str, List[Source]]:
    """
    Generate an answer to a question using retrieved book content.

    Args:
        question: The user's question
        retrieved_content: Relevant book content passages
        conversation_history: Optional conversation history for context

    Returns:
        Tuple of (answer_text, list of sources)

    Raises:
        RuntimeError: If answer generation fails
    """
    if not retrieved_content:
        logger.warning("No content retrieved for question")
        return (
            "I don't have enough information from the book to answer this question. The book content may not contain details about this topic yet.",
            [],
        )

    # Format context for LLM
    from src.agent.retriever import format_context_for_llm
    context = format_context_for_llm(retrieved_content)

    logger.info(f"Generating answer with context from {len(retrieved_content)} sources")

    try:
        # Generate answer with context
        answer = await openrouter_client.generate_with_context(
            question=question,
            context=context,
            conversation_history=conversation_history,
        )

        # Create source list
        sources = []
        for item in retrieved_content:
            sources.append(
                Source(
                    url=item.url,
                    title=item.title,
                    score=item.score,
                )
            )

        logger.info(f"Generated answer ({len(answer)} chars) with {len(sources)} sources")
        return answer, sources

    except Exception as e:
        logger.error(f"Failed to generate answer with LLM: {e}", exc_info=True)
        # Fallback: return the retrieved content directly when LLM fails
        # But still provide sources so user can navigate to full content

        fallback_answer = "Based on the book content I found:\n\n"
        sources = []

        for i, item in enumerate(retrieved_content[:3], 1):  # Return top 3 results
            # Add to answer
            title_text = item.title if item.title else "Unknown source"
            fallback_answer += f"{i}. {title_text}:\n{item.content[:400]}...\n\n"

            # Add to sources list
            sources.append(
                Source(
                    url=item.url,
                    title=item.title,
                    score=item.score,
                )
            )

        fallback_answer += "\n(Note: This is a direct excerpt from the book. The full answer generation service encountered an issue.)"

        return fallback_answer, sources
