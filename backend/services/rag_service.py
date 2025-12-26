"""
RAG Service to process queries using retrieved context from Qdrant
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
import sys
import os
# Add the current directory to the Python path to allow imports from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from models.query import QueryRequest, QueryResponse, Reference
from services.qdrant_service import QdrantService
from agent import RAGAgent
from config import Config

class RAGService:
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.agent = RAGAgent()

    async def process_query(self, question: str, selected_text: str = "") -> QueryResponse:
        """
        Process a user query by retrieving relevant context from Qdrant and generating a response
        """
        try:
            # Search for relevant content in Qdrant
            search_results = await self.qdrant_service.search_similar(question, top_k=5)

            # If no relevant content is found, return the fallback response
            if not search_results:
                response = QueryResponse(
                    id=str(uuid.uuid4()),
                    answer="This topic is not covered in the book",
                    references=[],
                    timestamp=datetime.now()
                )
                return response

            # Process the query with the RAG agent using the retrieved context
            agent_response = await self.agent.process_query(question, search_results)

            # Convert agent response to QueryResponse format
            references = [
                Reference(
                    chapter=ref.get('chapter', ''),
                    section=ref.get('section', ''),
                    source_url=ref.get('source_url', '')
                )
                for ref in agent_response.references
            ]

            response = QueryResponse(
                id=str(uuid.uuid4()),
                answer=agent_response.answer,
                references=references,
                timestamp=datetime.now()
            )

            return response
        except Exception as e:
            # Log the error for debugging
            print(f"Error in RAGService.process_query: {str(e)}")
            # According to spec: If retrieval returns no results, respond EXACTLY: "This topic is not covered in the book"
            # No generic error messages should be returned to the user
            return QueryResponse(
                id=str(uuid.uuid4()),
                answer="This topic is not covered in the book",
                references=[],
                timestamp=datetime.now()
            )
