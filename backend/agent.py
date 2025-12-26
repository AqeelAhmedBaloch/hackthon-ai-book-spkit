"""
RAG Agent using Anthropic Agent SDK to process queries
"""
import os
from typing import Dict, Any, List
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

class AgentResponse(BaseModel):
    answer: str
    references: List[Dict[str, str]]
    confidence_score: float

class RAGAgent:
    def __init__(self):
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def process_query(self, question: str, context: List[Dict[str, Any]]) -> AgentResponse:
        """
        Process a user query using the RAG approach with provided context
        """
        if not context:
            # No relevant content found in the book
            return AgentResponse(
                answer="This topic is not covered in the book",
                references=[],
                confidence_score=0.0
            )

        # Build context from retrieved content
        context_text = "\n\n".join([f"Source: {item.get('chapter', 'Unknown')} - {item.get('section', 'Unknown')}\nContent: {item['text']}" for item in context])

        # Create a prompt for the Anthropic model
        system_prompt = "You are a helpful assistant that answers questions based only on the provided book content. Do not use any external knowledge. If the question cannot be answered from the provided context, respond with exactly: 'This topic is not covered in the book'."

        user_prompt = f"""
        Context:
        {context_text}

        Question: {question}

        Please provide an answer based only on the context provided above.
        """

        try:
            # Use Anthropic's API to generate the response
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",  # or another appropriate model
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            answer = response.content[0].text if response.content else "This topic is not covered in the book"

            # Extract references
            references = []
            for item in context:
                references.append({
                    "chapter": item.get('chapter', ''),
                    "section": item.get('section', ''),
                    "source_url": item.get('source_url', '')
                })

            return AgentResponse(
                answer=answer,
                references=references,
                confidence_score=0.8  # Placeholder confidence score
            )
        except Exception as e:
            # If there's an error with Anthropic API, return fallback response
            print(f"Error calling Anthropic API: {str(e)}")
            return AgentResponse(
                answer="This topic is not covered in the book",
                references=[],
                confidence_score=0.0
            )