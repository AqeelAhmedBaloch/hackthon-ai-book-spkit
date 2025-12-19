from typing import List, Dict, Any
import numpy as np
from openai import OpenAI
from ..shared.models import ContentChunk, EmbeddingRecord
from ..shared.config import config
from ..shared.qdrant_client import QdrantClientWrapper
from ..shared.utils import hash_content, get_logger
import logging


class Embedder:
    """
    Class to generate embeddings for content chunks using OpenAI or other embedding models
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.openai_client = OpenAI(api_key=config.openai_api_key) if config.openai_api_key else None
        self.qdrant_client = QdrantClientWrapper()

    def generate_embeddings_openai(self, texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """
        Generate embeddings using OpenAI's embedding API
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        try:
            response = self.openai_client.embeddings.create(
                input=texts,
                model=model
            )

            embeddings = []
            for data in response.data:
                embeddings.append(data.embedding)

            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating OpenAI embeddings: {e}")
            raise

    def generate_embeddings_local(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using a local model (placeholder implementation)
        In a real implementation, this would use a local embedding model like Sentence Transformers
        """
        # This is a placeholder implementation
        # In a real implementation, you would use a local model like:
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # embeddings = model.encode(texts).tolist()
        # return embeddings

        self.logger.warning("Local embedding generation not implemented, using random vectors as placeholder")
        # Placeholder: return random vectors of appropriate size
        embedding_size = 1536  # Size of OpenAI's text-embedding-ada-002
        return [[np.random.random() for _ in range(embedding_size)] for _ in texts]

    def create_embedding_records(self, chunks: List[ContentChunk], model: str = "text-embedding-ada-002") -> List[EmbeddingRecord]:
        """
        Create embedding records from content chunks
        """
        if not chunks:
            return []

        # Extract text content from chunks
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings_openai(texts, model)

        # Create embedding records
        records = []
        for chunk, embedding in zip(chunks, embeddings):
            record = EmbeddingRecord(
                vector_id=chunk.id,
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "source_document": chunk.source_document,
                    "page_number": chunk.page_number,
                    "section": chunk.section,
                    "metadata": chunk.metadata or {},
                    "hash": chunk.hash
                },
                collection_name=config.qdrant_collection
            )
            records.append(record)

        return records

    def store_embeddings(self, chunks: List[ContentChunk], model: str = "text-embedding-ada-002") -> bool:
        """
        Generate embeddings for content chunks and store them in Qdrant
        """
        try:
            # Create embedding records
            records = self.create_embedding_records(chunks, model)

            # Store in Qdrant
            success = self.qdrant_client.store_embeddings(records)

            if success:
                self.logger.info(f"Successfully stored {len(records)} embeddings in Qdrant collection '{config.qdrant_collection}'")
            else:
                self.logger.error("Failed to store embeddings in Qdrant")

            return success
        except Exception as e:
            self.logger.error(f"Error storing embeddings: {e}")
            return False

    def embed_chunks_batch(self, chunks: List[ContentChunk], batch_size: int = 10, model: str = "text-embedding-ada-002") -> bool:
        """
        Process and store embeddings in batches to handle large datasets efficiently
        """
        if not chunks:
            self.logger.info("No chunks to embed")
            return True

        success_count = 0
        total_batches = (len(chunks) + batch_size - 1) // batch_size  # Ceiling division

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{total_batches} with {len(batch)} chunks")

            try:
                batch_success = self.store_embeddings(batch, model)
                if batch_success:
                    success_count += 1
                else:
                    self.logger.error(f"Failed to process batch {i//batch_size + 1}")
            except Exception as e:
                self.logger.error(f"Error processing batch {i//batch_size + 1}: {e}")

        success_rate = success_count / total_batches if total_batches > 0 else 0
        self.logger.info(f"Batch processing complete. Success rate: {success_rate:.2%} ({success_count}/{total_batches})")

        return success_rate > 0.5  # Consider successful if more than 50% of batches succeeded