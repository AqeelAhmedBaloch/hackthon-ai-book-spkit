"""
OpenRouter LLM client for generating answers based on retrieved book content.
"""

from typing import Optional
import httpx
from src.config import settings


class OpenRouterClient:
    """Client for interacting with OpenRouter API to generate responses."""

    def __init__(self):
        """Initialize OpenRouter client with API key and model."""
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"

    async def generate_response(
        self,
        prompt: str,
        conversation_history: Optional[list[dict]] = None,
        max_tokens: int = 1000,
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

        # Add system instruction to enforce book-only constraint
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful assistant that answers questions based ONLY on the "
                "provided book content. If the information is not in the provided "
                "content, clearly state that you don't have enough information from the book. "
                "Do not use outside knowledge or make assumptions beyond what's given."
            )
        }
        messages.append(system_message)

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            # Use http2=False to avoid potential compatibility issues with alpha Python
            async with httpx.AsyncClient(timeout=60.0, http2=False) as client:
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
