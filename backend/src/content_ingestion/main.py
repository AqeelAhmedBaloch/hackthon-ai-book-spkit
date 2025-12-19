import asyncio
from typing import List
import time
import logging
from pathlib import Path

from ..shared.models import ContentChunk
from .loader import ContentLoader
from .processor import ContentProcessor
from .embedder import Embedder
from .models import IngestionConfig, IngestionRequest, IngestionResponse, IngestionProgress
from ..shared.qdrant_client import QdrantClientWrapper
from ..shared.config import config


class ContentIngestionService:
    """
    Main service class for content ingestion pipeline
    """

    def __init__(self):
        self.loader = ContentLoader()
        self.processor = ContentProcessor()
        self.embedder = Embedder()
        self.qdrant_client = QdrantClientWrapper()
        self.logger = logging.getLogger(__name__)

    async def ingest_content(self, request: IngestionRequest) -> IngestionResponse:
        """
        Main ingestion pipeline: Load -> Process -> Embed -> Store
        """
        start_time = time.time()

        try:
            # Step 1: Create collection if it doesn't exist
            collection_name = request.collection_name or config.qdrant_collection
            self.qdrant_client.create_collection()

            # Step 2: Load content from source
            self.logger.info(f"Loading content from: {request.source_path}")
            source_path = Path(request.source_path)

            if source_path.is_file():
                raw_chunks = self.loader.load_from_file(request.source_path)
            elif source_path.is_dir():
                raw_chunks = self.loader.load_from_directory(request.source_path)
            else:
                raise ValueError(f"Source path does not exist: {request.source_path}")

            self.logger.info(f"Loaded {len(raw_chunks)} raw content chunks")

            # Step 3: Process content (clean, chunk, filter, deduplicate)
            self.logger.info("Processing content chunks...")
            processed_chunks = self.processor.process(
                raw_chunks,
                chunk_size=request.config.chunk_size,
                chunk_overlap=request.config.chunk_overlap,
                min_length=request.config.min_chunk_length,
                max_length=request.config.max_chunk_length
            )

            self.logger.info(f"Processed into {len(processed_chunks)} final chunks")

            # Step 4: Generate and store embeddings
            self.logger.info("Generating and storing embeddings...")
            embed_success = self.embedder.embed_chunks_batch(
                processed_chunks,
                batch_size=request.config.batch_size,
                model=request.config.model
            )

            if not embed_success:
                raise Exception("Embedding generation failed")

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Prepare response
            response = IngestionResponse(
                status="success",
                processed_chunks=len(processed_chunks),
                collection_name=collection_name,
                processing_time_ms=processing_time
            )

            self.logger.info(f"Ingestion completed successfully in {processing_time:.2f}ms")
            return response

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"Ingestion failed: {e}")

            response = IngestionResponse(
                status="failed",
                processed_chunks=0,
                collection_name=request.collection_name or config.qdrant_collection,
                processing_time_ms=processing_time,
                errors=[str(e)]
            )
            return response

    def get_ingestion_progress(self, ingestion_id: str) -> IngestionProgress:
        """
        Get the progress of a specific ingestion job
        Note: This is a simplified implementation. In a real system, you'd track
        ingestion jobs in a database or cache.
        """
        # This is a placeholder implementation
        # In a real system, you'd track the actual progress of ingestion jobs
        return IngestionProgress(
            total_files=0,
            processed_files=0,
            total_chunks=0,
            processed_chunks=0,
            current_file=None,
            status="completed",  # Default to completed for this simplified version
            progress_percentage=100.0
        )


def main():
    """
    Command-line interface for content ingestion
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Content Ingestion Pipeline")
    parser.add_argument("source", help="Path to source content (file or directory)")
    parser.add_argument("--chunk-size", type=int, default=512, help="Size of content chunks")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks")
    parser.add_argument("--model", default="text-embedding-ada-002", help="Embedding model to use")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for embedding")
    parser.add_argument("--collection", default=None, help="Qdrant collection name")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create ingestion service
    service = ContentIngestionService()

    # Create ingestion config
    config = IngestionConfig(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        model=args.model,
        batch_size=args.batch_size
    )

    # Create ingestion request
    request = IngestionRequest(
        source_path=args.source,
        config=config,
        collection_name=args.collection
    )

    # Run ingestion
    try:
        # Since the method is async, we need to run it in an event loop
        response = asyncio.run(service.ingest_content(request))

        if response.status == "success":
            print(f"Ingestion completed successfully!")
            print(f"Processed {response.processed_chunks} content chunks")
            print(f"Processing time: {response.processing_time_ms:.2f}ms")
            print(f"Stored in collection: {response.collection_name}")
        else:
            print(f"Ingestion failed!")
            if response.errors:
                print(f"Errors: {response.errors}")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()