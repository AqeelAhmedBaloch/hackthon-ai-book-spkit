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
        fallback_message = (
            "I don't have enough information from the book to confidently answer this question. "
            "The Physical AI - Humanoid Robotics textbook covers ROS 2, NVIDIA Isaac, "
            "and related robotics topics. Could you try rephrasing or asking about "
            "specific topics like 'What is ROS 2?' or 'How does NVIDIA Isaac work?'"
        )
        return (fallback_message, [])

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
        # Fallback: Provide helpful answer using retrieved content directly when LLM fails

        if not retrieved_content:
            fallback_answer = (
                "I couldn't generate a full answer, but I found related content in the book. "
                "Please try asking a more specific question or check the textbook chapters directly."
            )
            sources = []
        else:
            fallback_answer = "Based on the book content I found, here are the most relevant sections:\n\n"
            sources = []

            for i, item in enumerate(retrieved_content[:3], 1):
                title_text = item.title if item.title else "Section from textbook"
                fallback_answer += f"{i}. {title_text}\n"
                sources.append(
                    Source(
                        url=item.url,
                        title=item.title,
                        score=item.score,
                    )
                )

            fallback_answer += "\nI suggest checking these sections for detailed information."

        return fallback_answer, sources
