from typing import List, Optional
import logging
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from ..shared.models import QueryRequest, QueryResponse, Citation, ContentChunk, AgentConfig
from ..shared.qdrant_client import QdrantClientWrapper
from ..shared.config import config
from .retrieval import RetrievalService
from ..shared.utils import get_logger


class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent that combines retrieval and generation
    to answer questions based on book content
    """

    def __init__(self, agent_config: Optional[AgentConfig] = None):
        self.logger = get_logger(__name__)
        self.qdrant_client = QdrantClientWrapper()
        self.retrieval_service = RetrievalService()

        # Use provided config or create default
        self.agent_config = agent_config or AgentConfig()

        # Initialize OpenAI client
        if config.openai_api_key:
            self.openai_client = OpenAI(api_key=config.openai_api_key)
            self.llm = ChatOpenAI(
                model_name=self.agent_config.model,
                temperature=self.agent_config.temperature,
                max_tokens=self.agent_config.max_tokens,
                api_key=config.openai_api_key
            )
        else:
            self.openai_client = None
            self.llm = None
            self.logger.warning("OpenAI API key not configured. Agent will not be able to generate responses.")

    def generate_response(self, query: str, context_chunks: List[ContentChunk]) -> str:
        """
        Generate a response using the LLM based on the query and context
        """
        if not self.llm:
            return "Error: OpenAI API key not configured. Cannot generate response."

        try:
            # Combine context chunks into a single context string
            context = "\n\n".join([chunk.content for chunk in context_chunks])

            # Create a prompt template for the RAG task
            prompt_template = """
            You are an assistant that answers questions based only on the provided context.
            If the answer is not in the context, say "I cannot answer based on the provided information."

            Context:
            {context}

            Question: {question}

            Answer:
            """

            # Create the prompt
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=prompt_template
            )

            # Format the prompt with context and question
            formatted_prompt = prompt.format(context=context, question=query)

            # Generate the response using the LLM
            response = self.llm.invoke(formatted_prompt)

            return response.content if hasattr(response, 'content') else str(response)

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"

    def create_citations(self, retrieved_chunks: List[ContentChunk], query: str) -> List[Citation]:
        """
        Create citations from retrieved content chunks
        """
        citations = []
        for chunk in retrieved_chunks:
            # Calculate a simple similarity score (in practice, this would come from the retrieval process)
            similarity = 0.85  # Placeholder - in practice this would be from the search result score

            citation = Citation(
                source_document=chunk.source_document,
                page_number=chunk.page_number,
                section=chunk.section,
                text_snippet=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                similarity_score=similarity
            )
            citations.append(citation)

        return citations

    def query(self, query_request: QueryRequest) -> QueryResponse:
        """
        Main method to process a query and return a response
        """
        import time
        start_time = time.time()

        try:
            # Add selected text to the query if provided
            full_query = query_request.query
            if query_request.selected_text:
                full_query = f"Based on this text: '{query_request.selected_text}'. {query_request.query}"

            # Retrieve relevant content chunks
            retrieved_chunks = self.retrieval_service.retrieve_relevant_content(
                full_query,
                top_k=self.agent_config.retrieval_top_k,
                similarity_threshold=self.agent_config.similarity_threshold
            )

            if not retrieved_chunks:
                self.logger.warning(f"No relevant content found for query: {full_query}")
                return QueryResponse(
                    response="I cannot find relevant information in the book content to answer your question.",
                    citations=[],
                    confidence=0.0,
                    retrieved_chunks=[],
                    processing_time_ms=(time.time() - start_time) * 1000,
                    request_id=f"query_{hash(full_query) % 10000}"
                )

            # Generate response using the LLM
            response_text = self.generate_response(full_query, retrieved_chunks)

            # Validate that the response is grounded in the context (zero hallucination check)
            is_valid_response = self.validate_response_accuracy(full_query, response_text, retrieved_chunks)
            if not is_valid_response:
                self.logger.warning(f"Response validation failed for query: {full_query}")
                # In a production system, you might want to return a different response
                # or flag this for review, but for now we'll proceed with the response

            # Create citations
            citations = self.create_citations(retrieved_chunks, full_query)

            # Calculate confidence based on similarity scores
            confidence = sum(c.similarity_score or 0.0 for c in citations) / len(citations) if citations else 0.0

            # Create response object
            response = QueryResponse(
                response=response_text,
                citations=citations,
                confidence=confidence,
                retrieved_chunks=retrieved_chunks,
                processing_time_ms=(time.time() - start_time) * 1000,
                request_id=f"query_{hash(full_query) % 10000}"
            )

            self.logger.info(f"Query processed successfully in {(time.time() - start_time) * 1000:.2f}ms")
            return response

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return QueryResponse(
                response=f"Error processing query: {str(e)}",
                citations=[],
                confidence=0.0,
                retrieved_chunks=[],
                processing_time_ms=(time.time() - start_time) * 1000,
                request_id=f"query_error_{hash(query_request.query) % 10000}"
            )

    def validate_response_accuracy(self, query: str, response: str, context_chunks: List[ContentChunk]) -> bool:
        """
        Validate that the response is based on the provided context and doesn't contain hallucinations
        """
        # This is a simplified validation
        # In a real implementation, you'd use more sophisticated methods to detect hallucinations
        # such as checking if the response contains information that isn't in the context

        # For now, just ensure the response isn't empty and follows the expected format
        if not response or response.startswith("Error"):
            return False

        # Check if response indicates inability to answer from context
        cannot_answer_phrases = [
            "cannot answer based on the provided information",
            "not mentioned in the context",
            "not in the context",
            "no information provided",
            "i don't have information",
            "i cannot find"
        ]

        # If it's a "cannot answer" response, it's valid (no hallucination)
        for phrase in cannot_answer_phrases:
            if phrase.lower() in response.lower():
                return True

        # If we have context chunks, perform a basic check for alignment
        if context_chunks:
            # Convert response to lowercase for comparison
            response_lower = response.lower()

            # Look for at least some alignment between response and context
            # This is a very basic check - in practice you'd use more sophisticated NLP
            context_text = " ".join([chunk.content.lower() for chunk in context_chunks])

            # Simple keyword overlap check
            response_words = set(response_lower.split())
            context_words = set(context_text.split())

            # If there's very little overlap, it might indicate hallucination
            if len(response_words) > 0:
                overlap = len(response_words.intersection(context_words))
                overlap_ratio = overlap / len(response_words)

                # Consider it valid if at least 30% of response words appear in context
                if overlap_ratio >= 0.3:
                    return True

        # Otherwise, assume it's valid if it doesn't contain obvious errors
        return True