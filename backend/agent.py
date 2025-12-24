import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Tuple, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGAgent:
    def __init__(self):
        # Initialize Cohere client for embeddings
        self.cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))

        # Initialize Qdrant client for vector storage
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )

        # Collection name for book content
        self.collection_name = "humanoid_ai_book"

        # Initialize the collection if it doesn't exist
        self._init_collection()

    def _init_collection(self):
        """
        Initialize the Qdrant collection for storing book content.
        """
        try:
            # Check if collection exists
            self.qdrant_client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
            )

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text using Cohere.
        """
        response = self.cohere_client.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_document"  # Specify the input type for document search
        )
        return response.embeddings[0]

    def store_content(self, content: str, metadata: dict = None):
        """
        Store book content in the vector database with embeddings.
        """
        if metadata is None:
            metadata = {}

        # Generate embedding for the content
        embedding = self.embed_text(content)

        # Store in Qdrant
        import uuid
        point_id = str(uuid.uuid4())

        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": content,
                        **metadata
                    }
                )
            ]
        )

    def retrieve_relevant_content(self, query: str, limit: int = 5) -> List[dict]:
        """
        Retrieve relevant book content based on the query.
        """
        # Generate embedding for the query
        response = self.cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"  # Specify the input type for search queries
        )
        query_embedding = response.embeddings[0]

        # Search in Qdrant using query_points method
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit
        ).points

        # Extract content from results
        relevant_content = []
        for result in search_results:
            # Check the actual payload structure
            payload = result.payload
            # Based on testing, content is stored in 'text' field, not 'content' field
            content = payload.get("text", "")
            if not content:
                # Fallback: try 'content' field if 'text' doesn't exist
                content = payload.get("content", "")

            # If still no content, try to find the longest string in the payload
            if not content and isinstance(payload, dict):
                for key, value in payload.items():
                    if isinstance(value, str) and len(value) > len(content):  # Find longest string
                        content = value

            relevant_content.append({
                "content": content,
                "score": result.score,
                "metadata": {k: v for k, v in payload.items()}  # Include all metadata
            })

        return relevant_content

    def generate_answer(self, query: str, context: List[dict]) -> str:
        """
        Generate an answer based on the query and retrieved context.
        """
        # Prepare context for the model
        context_str = "\n\n".join([item["content"] for item in context])

        # Create a message for the model using Chat API
        message = f"""
        You are an assistant for the Physical AI & Humanoid Robotics book.
        Answer the user's question based only on the provided context from the book.

        Context:
        {context_str}

        Question: {query}

        Answer:
        """

        # Use Cohere's Chat API instead of the deprecated Generate API
        try:
            response = self.cohere_client.chat(
                model="command-r",
                message=message,
                max_tokens=300,
                temperature=0.3
            )
            return response.text.strip()
        except Exception as e:
            # If Cohere API fails, return a message with the context that was found
            context_str = "\n\n".join([item["content"] for item in context])
            return f"Found relevant information but couldn't generate a response: {context_str[:500]}..."

    def get_answer(self, question: str, selected_text: str = None) -> Tuple[str, List[str]]:
        """
        Main method to get an answer for a question based on book content or selected text.
        If selected_text is provided, answer only from that text.
        Otherwise, retrieve from the vector database.
        Returns the answer and a list of source references.
        """
        if selected_text:
            # If selected_text is provided, answer only from that text
            relevant_content = [{"content": selected_text, "score": 1.0, "metadata": {"source": "Selected Text"}}]
            answer = self.generate_answer_from_text(question, selected_text)
            sources = ["Selected Text"]
        else:
            # Retrieve relevant content from the vector database
            relevant_content = self.retrieve_relevant_content(question)

            if not relevant_content:
                return "This question is not covered in the book.", []

            # Generate answer
            answer = self.generate_answer(question, relevant_content)

            # Extract source information
            sources = [item["metadata"].get("source", "Unknown") for item in relevant_content]

        return answer, sources

    def generate_answer_from_text(self, query: str, text: str) -> str:
        """
        Generate an answer based on the query and a specific text.
        """
        # Create a prompt for the model
        prompt = f"""
        You are an assistant for the Physical AI & Humanoid Robotics book.
        Answer the user's question based only on the provided text.
        Do not use any other knowledge or make up information.

        Provided text:
        {text}

        Question: {query}

        Answer:
        """

        # Use Cohere's Chat API instead of the deprecated Generate API
        try:
            response = self.cohere_client.chat(
                model="command-r",
                message=prompt,
                max_tokens=300,
                temperature=0.3
            )
            return response.text.strip()
        except Exception as e:
            # If Cohere API fails, return a message with the context that was found
            return f"Found relevant information but couldn't generate a response from the selected text."