from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
import hashlib
from datetime import datetime, timedelta


# Data Models
class BookContentChunk(BaseModel):
    """
    Model for book content chunks stored in the vector database
    """
    id: str
    content: str
    source_path: str
    source_section: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = {}


class UserQuery(BaseModel):
    """
    Model for user queries to the chatbot
    """
    question: str
    selected_text: Optional[str] = ""
    context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    """
    Model for responses from the chatbot
    """
    answer: str
    sources: List[Dict[str, Any]]
    confidence: Optional[float] = None
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="API for RAG-based question answering from book content",
    version="0.1.0"
)

# Configure CORS middleware to allow Docusaurus book domain
# Get allowed origins from environment variable or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "https://hackthon-ai-book-spkit.vercel.app")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Additional origins that might be needed for development
    # allow_origins_regex="https://.*\.vercel\.app"  # For Vercel deployments
)

# Initialize Cohere client with proper error handling and timeout
try:
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        raise ValueError("COHERE_API_KEY environment variable is not set")
    cohere_client = cohere.Client(cohere_api_key, timeout=30)  # 30 second timeout
    print("Cohere client initialized successfully")
except Exception as e:
    print(f"Error initializing Cohere client: {e}")
    cohere_client = None

# Initialize Qdrant client with proper error handling
try:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables are not set")
    qdrant_client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=30  # 30 second timeout as per requirement
    )
    print("Qdrant client initialized successfully")
except Exception as e:
    print(f"Error initializing Qdrant client: {e}")
    qdrant_client = None

import re
from datetime import datetime
import time

# Simple in-memory cache for embeddings
embedding_cache = {}
CACHE_EXPIRY_SECONDS = 3600  # 1 hour expiry


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of specified size with overlap to maintain context
    """
    if not text:
        return []

    # Split text into sentences to avoid cutting in the middle of sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding the sentence would exceed chunk size
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())

            # Add overlap by including part of the previous chunk
            if overlap > 0:
                # Get the last 'overlap' characters from current chunk to start next chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    # Add the last chunk if it exists
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # If we still have chunks that are too large, split them by character count
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            final_chunks.append(chunk)
        else:
            # Split by character count if sentence splitting didn't work
            for i in range(0, len(chunk), chunk_size - overlap):
                sub_chunk = chunk[i:i + chunk_size]
                if sub_chunk.strip():
                    final_chunks.append(sub_chunk)

    return final_chunks


def sanitize_input(text: str) -> str:
    """
    Sanitize input text to prevent injection attacks
    """
    if not text:
        return ""

    # Remove potentially dangerous characters/sequences
    sanitized = text.replace('<script', '').replace('</script>', '')
    sanitized = sanitized.replace('javascript:', '')
    sanitized = sanitized.replace('vbscript:', '')
    sanitized = sanitized.replace('onerror', '').replace('onload', '')
    sanitized = sanitized.replace('onmouseover', '').replace('onclick', '')

    # Limit length to prevent overly large inputs
    if len(sanitized) > 10000:  # 10KB limit
        sanitized = sanitized[:10000]

    return sanitized.strip()


def clean_markdown_content(content: str) -> str:
    """
    Clean and preprocess markdown content for better embedding
    """
    import re

    # Remove markdown headers but keep the text
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

    # Remove markdown links but keep the link text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

    # Remove markdown bold/italic formatting
    content = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', content)
    content = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', content)

    # Remove code blocks and inline code
    content = re.sub(r'```[\s\S]*?```', '', content)  # Remove code blocks
    content = re.sub(r'`([^`]+)`', r'\1', content)  # Replace inline code with plain text

    # Remove excessive whitespace and newlines
    content = re.sub(r'\n\s*\n', '\n\n', content)  # Remove extra blank lines
    content = re.sub(r'[ \t]+', ' ', content)  # Replace multiple spaces/tabs with single space

    # Strip leading/trailing whitespace
    content = content.strip()

    return content


def read_book_content(book_path: str = "ai_frontend_book/docs/") -> List[Dict[str, str]]:
    """
    Read book markdown content from the specified directory
    """
    import os
    import glob

    content_list = []

    # Check if the book path exists
    if not os.path.exists(book_path):
        print(f"Warning: Book content path '{book_path}' does not exist")
        return content_list

    # Find all markdown files in the book path and subdirectories
    md_files = glob.glob(os.path.join(book_path, "**/*.md"), recursive=True)
    md_files += glob.glob(os.path.join(book_path, "**/*.mdx"), recursive=True)  # Include MDX files too

    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Clean the markdown content
                cleaned_content = clean_markdown_content(content)

                # Extract relative path for source tracking
                relative_path = os.path.relpath(file_path, book_path)

                content_list.append({
                    "content": cleaned_content,
                    "source_path": relative_path,
                    "file_path": file_path
                })
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    return content_list


# Create Qdrant collection for storing book content chunks
def create_qdrant_collection(collection_name: str = "book_content_chunks"):
    """
    Create a Qdrant collection for storing book content chunks with embeddings
    """
    if not qdrant_client:
        print("Qdrant client not initialized, cannot create collection")
        return False

    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if collection_name not in collection_names:
            # Create collection with vector configuration
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Cohere embeddings are typically 1024 dimensions
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{collection_name}' created successfully")
        else:
            print(f"Collection '{collection_name}' already exists")

        return True
    except Exception as e:
        print(f"Error creating Qdrant collection: {e}")
        return False


# Initialize the collection when the application starts
create_qdrant_collection()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Cohere with caching
    """
    if not cohere_client:
        print("Cohere client not initialized, cannot generate embeddings")
        return []

    # Create cache key based on the texts
    cache_key = hashlib.md5(str(texts).encode()).hexdigest()

    # Check if embeddings are in cache and not expired
    if cache_key in embedding_cache:
        cached_data, timestamp = embedding_cache[cache_key]
        if time.time() - timestamp < CACHE_EXPIRY_SECONDS:
            print(f"Using cached embeddings for key: {cache_key[:8]}...")
            return cached_data

    try:
        # Generate embeddings using Cohere
        response = cohere_client.embed(
            texts=texts,
            model="embed-english-v3.0",  # Using Cohere's English embedding model
            input_type="search_document",  # Specify the input type for better embeddings
            timeout=30  # 30-second timeout
        )

        # Extract embeddings from response
        embeddings = [embedding for embedding in response.embeddings]

        # Cache the embeddings
        embedding_cache[cache_key] = (embeddings, time.time())
        print(f"Cached embeddings for key: {cache_key[:8]}...")

        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []


def store_chunks_in_qdrant(chunks: List[Dict], collection_name: str = "book_content_chunks") -> bool:
    """
    Store content chunks in Qdrant with source metadata
    """
    if not qdrant_client:
        print("Qdrant client not initialized, cannot store chunks")
        return False

    try:
        # Prepare points for Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            # Generate embeddings for the content
            embeddings = generate_embeddings([chunk["content"]])
            if not embeddings or len(embeddings) == 0:
                print(f"Failed to generate embedding for chunk {i}, skipping...")
                continue

            embedding = embeddings[0]

            # Create a point for Qdrant
            point = models.PointStruct(
                id=str(i),  # Using index as ID, in production you'd want UUIDs
                vector=embedding,
                payload={
                    "content": chunk["content"],
                    "source_path": chunk["source_path"],
                    "file_path": chunk["file_path"],
                    "chunk_id": f"chunk_{i}"
                }
            )
            points.append(point)

        # Upload points to Qdrant
        if points:
            qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            print(f"Successfully stored {len(points)} chunks in Qdrant collection '{collection_name}'")
            return True
        else:
            print("No points to store in Qdrant")
            return False

    except Exception as e:
        print(f"Error storing chunks in Qdrant: {e}")
        return False


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rag_chatbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    # Check if Cohere client is initialized
    cohere_status = cohere_client is not None

    # Check if Qdrant client is initialized and accessible
    qdrant_status = False
    if qdrant_client:
        try:
            # Try to get collections to verify connection
            qdrant_client.get_collections()
            qdrant_status = True
        except:
            qdrant_status = False

    # Check if ingestion is ready (collection exists)
    ingestion_status = False
    if qdrant_client and qdrant_status:
        try:
            collections = qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            ingestion_status = "book_content_chunks" in collection_names
        except:
            ingestion_status = False

    health_data = {
        "status": "healthy",
        "service": "RAG Chatbot Backend",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "cohere": cohere_status,
            "qdrant": qdrant_status,
            "ingestion": ingestion_status
        }
    }

    logger.info(f"Health check requested - Status: {health_data['status']}")
    return health_data


# Ingestion endpoint
@app.post("/ingest")
async def ingest_content(force: bool = False):
    """
    Trigger the book content ingestion and embedding process
    """
    logger.info("Ingestion endpoint called")
    try:
        # Read book content
        book_path = os.getenv("BOOK_CONTENT_PATH", "../ai_frontend_book/docs/")
        logger.info(f"Reading book content from: {book_path}")
        content_list = read_book_content(book_path)

        if not content_list:
            logger.warning(f"No markdown files found in {book_path}")
            return {
                "status": "no_content",
                "chunks_processed": 0,
                "message": f"No markdown files found in {book_path}"
            }

        # Process each content item
        all_chunks = []
        for item in content_list:
            logger.info(f"Processing file: {item['source_path']}")
            # Chunk the content
            chunks = chunk_text(item["content"])

            for i, chunk_text in enumerate(chunks):
                chunk_info = {
                    "content": chunk_text,
                    "source_path": item["source_path"],
                    "file_path": item["file_path"],
                    "chunk_index": i
                }
                all_chunks.append(chunk_info)

        logger.info(f"Prepared {len(all_chunks)} chunks from {len(content_list)} files for ingestion")

        # Store chunks in Qdrant
        success = store_chunks_in_qdrant(all_chunks)

        if success:
            logger.info(f"Ingestion completed successfully: {len(all_chunks)} chunks from {len(content_list)} files")
            return {
                "status": "success",
                "chunks_processed": len(all_chunks),
                "message": f"Successfully ingested {len(all_chunks)} content chunks from {len(content_list)} files"
            }
        else:
            logger.error("Failed to store content in vector database")
            return {
                "status": "error",
                "chunks_processed": 0,
                "message": "Failed to store content in vector database"
            }

    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return {
            "status": "error",
            "chunks_processed": 0,
            "message": f"Ingestion failed with error: {str(e)}"
        }

# Placeholder for other endpoints that will be implemented in later phases
@app.get("/")
async def root():
    return {"message": "RAG Chatbot Backend API", "status": "running"}


# Chat endpoint
@app.post("/chat")
async def chat_endpoint(user_query: UserQuery):
    """
    Process user questions and return RAG-generated responses
    """
    # Validate input
    if not user_query.question or len(user_query.question.strip()) == 0:
        logger.warning("Empty question received")
        return {
            "answer": "Please provide a question to answer.",
            "sources": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }

    # Sanitize inputs
    sanitized_question = sanitize_input(user_query.question)
    sanitized_selected_text = sanitize_input(user_query.selected_text) if user_query.selected_text else ""

    logger.info(f"Chat endpoint called - Question: {sanitized_question[:50]}...")
    try:
        question = sanitized_question
        selected_text = sanitized_selected_text
        context = user_query.context

        # Validate question length
        if len(question) > 1000:
            logger.warning("Question too long")
            return {
                "answer": "Your question is too long. Please keep it under 1000 characters.",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }

        # If selected text is provided, prioritize it in the search
        search_text = selected_text if selected_text else question

        # Generate embedding for the query
        query_embeddings = generate_embeddings([search_text])
        if not query_embeddings or len(query_embeddings) == 0:
            logger.warning("Could not generate embeddings for the query")
            return {
                "answer": "Sorry, I couldn't process your query. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }

        query_embedding = query_embeddings[0]

        # Retrieve relevant chunks from Qdrant
        relevant_chunks = retrieve_relevant_chunks(query_embedding, question, selected_text)

        if not relevant_chunks:
            logger.info("No relevant chunks found for the query")
            return {
                "answer": "I couldn't find relevant information in the book to answer your question.",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }

        # Generate response using Cohere with retrieved context
        answer = generate_rag_response(question, relevant_chunks)

        # Format sources
        sources = []
        for chunk in relevant_chunks:
            source = {
                "path": chunk.get("source_path", ""),
                "section": "",  # Could extract section from context if available
                "content": chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", ""),
                "relevance_score": chunk.get("score", 0.0)
            }
            sources.append(source)

        logger.info(f"Chat response generated successfully for question: {question[:30]}...")
        return ChatResponse(
            answer=answer,
            sources=sources,
            confidence=0.8,  # Placeholder confidence, could be calculated based on scores
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {
            "answer": "An error occurred while processing your query. Please try again.",
            "sources": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }


def retrieve_relevant_chunks(query_embedding: List[float], question: str, selected_text: str = "") -> List[Dict]:
    """
    Retrieve relevant chunks from Qdrant based on query embedding
    """
    if not qdrant_client:
        logger.warning("Qdrant client not initialized, cannot retrieve chunks")
        # Return empty list but allow graceful degradation
        return []

    try:
        # Search for similar vectors in the collection
        search_results = qdrant_client.search(
            collection_name="book_content_chunks",
            query_vector=query_embedding,
            limit=5,  # Retrieve top 5 most relevant chunks
            with_payload=True
        )

        # Format the results
        relevant_chunks = []
        for result in search_results:
            chunk = {
                "content": result.payload.get("content", ""),
                "source_path": result.payload.get("source_path", ""),
                "file_path": result.payload.get("file_path", ""),
                "score": result.score
            }
            relevant_chunks.append(chunk)

        return relevant_chunks

    except Exception as e:
        logger.error(f"Error retrieving chunks from Qdrant: {e}")
        # Return empty list but log the error for graceful degradation
        return []


def generate_rag_response(question: str, relevant_chunks: List[Dict]) -> str:
    """
    Generate a response using Cohere with retrieved context
    """
    if not cohere_client:
        logger.warning("Cohere client not initialized, using fallback response")
        # Provide a helpful fallback message
        return "I'm sorry, but I'm unable to generate a detailed response right now. The AI service is not available. Please try again later."

    try:
        # Combine the relevant chunks into context
        context_text = "\n\n".join([chunk["content"] for chunk in relevant_chunks if chunk["content"]])

        # Create a prompt for Cohere
        prompt = f"""
        Based on the following context, please answer the question.
        If the context doesn't contain enough information to answer the question, please say so.

        Context: {context_text}

        Question: {question}

        Answer:
        """

        # Generate response using Cohere
        response = cohere_client.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=500,
            temperature=0.3,
            timeout=30  # 30-second timeout
        )

        return response.generations[0].text.strip()

    except Exception as e:
        logger.error(f"Error generating RAG response: {e}")
        # Provide a fallback response when Cohere fails
        return "I'm sorry, but I'm unable to generate a detailed response right now due to a service issue. Please try again later."


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)