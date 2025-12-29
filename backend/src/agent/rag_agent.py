"""
RAG agent coordinator: Orchestrates query embedding, retrieval, and answer generation.
"""

from typing import Optional, List
from src.agent.query_embedder import embed_query
from src.agent.retriever import retrieve_content, RetrievedContent
from src.agent.answer_generator import generate_answer
from src.models.chat import Answer, Source
from src.utils.logger import logger


class RAGAgent:
    """
    Retrieval-Augmented Generation agent for answering book questions.

    This agent ensures all answers are based ONLY on ingested book content.
    """

    def __init__(self):
        """Initialize RAG agent with required components."""
        # Components are initialized as module-level imports for efficiency

    async def answer_question(
        self,
        question: str,
        conversation_history: Optional[List[dict]] = None,
    ) -> Answer:
        """
        Answer a user's question based on ingested book content.

        Args:
            question: The user's question
            conversation_history: Optional conversation for follow-up context

        Returns:
            Answer object with text, sources, and metadata

        Note:
            This method never raises - it always returns an Answer object,
            even when services fail. This ensures the API always returns
            valid JSON responses.
        """
        logger.info(f"Processing question: {question[:100]}...")

        try:
            # Step 1: Embed the query
            logger.debug("Step 1: Embedding query...")
            query_embedding = await embed_query(question)

            # Step 2: Retrieve relevant content from Qdrant
            logger.debug("Step 2: Retrieving relevant content...")
            retrieved = await retrieve_content(query_embedding)

            # Step 3: Generate answer with retrieved context
            logger.debug("Step 3: Generating answer...")
            answer_text, sources = await generate_answer(
                question,
                retrieved,
                conversation_history,
            )

            # Calculate confidence based on retrieval scores
            confidence = 0.0
            if retrieved:
                # Average score of top results
                confidence = sum(r.score for r in retrieved[:3]) / min(len(retrieved), 3)

            logger.info(f"Generated answer with {len(sources)} sources and {confidence:.2f} confidence")

            # Return complete answer
            return Answer(
                text=answer_text,
                sources=sources,
                confidence=confidence,
            )

        except Exception as e:
            # Catch ALL exceptions to ensure we always return a valid Answer
            # This prevents the API from crashing and returns helpful error messages
            logger.error(f"RAG pipeline error: {type(e).__name__}: {e}", exc_info=True)

            # Return a fallback answer instead of crashing
            error_type = type(e).__name__
            error_msg = str(e)

            fallback_answer = (
                f"I encountered an error while trying to answer your question. "
                f"Error: {error_type}: {error_msg}. "
                f"Please check if the backend services (Cohere, OpenRouter, Qdrant) are running properly. "
                f"You can also try asking a different question."
            )

            return Answer(
                text=fallback_answer,
                sources=[],
                confidence=0.0,
            )


# Global RAG agent instance
rag_agent = RAGAgent()
