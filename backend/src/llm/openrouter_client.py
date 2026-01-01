"""
OpenRouter LLM client for generating answers based on retrieved book content.
"""

from typing import Optional, List
import httpx
from src.config import settings
from src.utils.retry import async_retry


class OpenRouterClient:
    """Client for interacting with OpenRouter API to generate responses."""

    def __init__(self):
        """Initialize OpenRouter client with API key and model."""
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create singleton httpx client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=15.0, http2=True)  # Optimized: 15s (down from 30s)
        return self._client

    async def close(self):
        """Close the underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @async_retry()
    async def generate_response(
        self,
        prompt: str,
        conversation_history: Optional[List[dict]] = None,
        max_tokens: int = 500,  # Optimized: 500 (down from 1000) for faster responses
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using the LLM.

        Args:
            prompt: The main prompt/question to answer
            conversation_history: Optional list of previous messages for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1, higher = more creative)

        Returns:
            Generated text response
        """
        messages = []

        # Add system instruction to enforce book-only constraint (shortened for faster processing)
        system_message = {
            "role": "system",
            "content": (
                "Answer ONLY using provided book content. If not found, say so. "
                "Be concise and direct. Use bullet points when appropriate."
            )
        }
        messages.append(system_message)

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            client = self._get_client()
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.TimeoutException as e:
            raise RuntimeError(f"OpenRouter API timeout after 60s: {str(e)}")
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if hasattr(e.response, "text") else str(e)
            raise RuntimeError(f"OpenRouter API error: {e.response.status_code} - {error_text}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate response with OpenRouter: {type(e).__name__}: {str(e)}")

    async def generate_with_context(
        self,
        question: str,
        context: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> str:
        """
        Generate an answer based on retrieved book content.

        Args:
            question: The user's question
            context: Relevant book content passages
            conversation_history: Optional conversation for follow-up questions

        Returns:
            Answer based on the provided context
        """
        # Construct prompt with retrieved context
        prompt = f"""Based on the following book content, answer the user's question.

Book Content:
{context}

Question: {question}"""

        return await self.generate_response(prompt, conversation_history)


# Global OpenRouter client instance
openrouter_client = OpenRouterClient()
