"""
Content Ingestion Pipeline for Docusaurus Book to Qdrant Vector Database

This script implements the content ingestion pipeline that:
1. Crawls deployed book URLs and extracts clean textual content
2. Chunks content and generates embeddings using Cohere
3. Stores embeddings and metadata in Qdrant Cloud (Free Tier)
"""

import asyncio
import os
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class ContentChunk:
    """Represents a segment of extracted text that fits within Cohere's token limits"""
    text: str
    source_url: str
    content_id: str
    metadata: Dict[str, Any]


class ContentExtractor:
    """Extracts clean textual content from deployed book URLs"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_from_url(self, url: str) -> str:
        """Extract clean text content from a single URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Focus on main content areas (Docusaurus specific selectors)
            content_selectors = [
                'article',  # Main article content
                '.markdown',  # Markdown content
                '.theme-doc-markdown',  # Docusaurus markdown container
                '.main-wrapper',  # Docusaurus main content wrapper
                '.container',  # General container
                'main'  # Main content area
            ]

            text_content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text_content += element.get_text(separator=' ', strip=True) + "\n\n"
                    break

            # If no specific content found, get all text
            if not text_content.strip():
                text_content = soup.get_text(separator=' ', strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text_content.splitlines() if line.strip()]
            text_content = '\n'.join(lines)

            return text_content
        except Exception as e:
            logging.error(f"Error extracting content from {url}: {str(e)}")
            raise

    def crawl_book(self, base_url: str) -> List[str]:
        """Crawl a deployed book and extract all accessible content URLs"""
        urls = set()

        def extract_links_from_page(url: str, visited: set):
            if url in visited or len(visited) > 100:  # Limit to prevent infinite crawling
                return

            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all internal links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)

                    # Only follow links within the same domain
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        if full_url.startswith(base_url) and full_url not in visited:
                            urls.add(full_url)
                            if len(urls) < 50:  # Limit number of pages to crawl
                                extract_links_from_page(full_url, visited)

                visited.add(url)
            except Exception as e:
                logging.warning(f"Error crawling {url}: {str(e)}")

        extract_links_from_page(base_url, set())
        return list(urls)


class ContentChunker:
    """Chunks extracted content into appropriate sizes for Cohere embedding models"""

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.max_chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.max_chunk_size

            # If we're not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the boundary
                chunk = text[start:end]
                last_sentence = max(
                    chunk.rfind('.'),
                    chunk.rfind('!'),
                    chunk.rfind('?'),
                    chunk.rfind('\n')
                )

                if last_sentence > self.max_chunk_size // 2:  # Only break if we're not cutting too early
                    end = start + last_sentence + 1
                else:
                    # If no good break point, just cut at max
                    pass

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)

            # Move start position with overlap
            start = end - self.overlap if end < len(text) else end

        return [chunk for chunk in chunks if chunk.strip()]


class EmbeddingGenerator:
    """Generates vector embeddings using Cohere's embedding models"""

    def __init__(self, cohere_api_key: str):
        self.client = cohere.Client(cohere_api_key)
        self.model = "embed-multilingual-v3.0"  # Cohere's latest embedding model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"
            )
            return [embedding for embedding in response.embeddings]
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            raise


class VectorStore:
    """Stores embeddings and metadata in Qdrant vector database"""

    def __init__(self, qdrant_url: str, qdrant_api_key: str, collection_name: str = "humanoid_ai_book"):
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            prefer_grpc=False  # Using HTTP for compatibility
        )
        self.collection_name = collection_name

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """Create the collection for storing embeddings"""
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Cohere's embedding dimension for multilingual model
                    distance=models.Distance.COSINE
                )
            )

    def store_embeddings(self, content_chunks: List[ContentChunk], embeddings: List[List[float]]):
        """Store embeddings and metadata in Qdrant"""
        points = []

        for chunk, embedding in zip(content_chunks, embeddings):
            point = models.PointStruct(
                id=chunk.content_id,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "source_url": chunk.source_url,
                    "timestamp": int(time.time()),
                    **chunk.metadata
                }
            )
            points.append(point)

        # Upload in batches to handle large amounts of data
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

        logging.info(f"Stored {len(points)} embeddings in Qdrant collection '{self.collection_name}'")


class ContentIngestionPipeline:
    """Main pipeline orchestrating content extraction, embedding, and storage"""

    def __init__(self, cohere_api_key: str, qdrant_url: str, qdrant_api_key: str):
        self.extractor = ContentExtractor()
        self.chunker = ContentChunker()
        self.embedder = EmbeddingGenerator(cohere_api_key)
        self.vector_store = VectorStore(qdrant_url, qdrant_api_key)

        logging.basicConfig(level=logging.INFO)

    def run_ingestion(self, base_url: str):
        """Run the complete ingestion pipeline"""
        logging.info(f"Starting content ingestion from: {base_url}")

        # Step 1: Extract content from all pages
        logging.info("Crawling and extracting content...")
        urls = self.extractor.crawl_book(base_url)
        logging.info(f"Found {len(urls)} pages to process")

        all_chunks = []
        for i, url in enumerate(urls):
            logging.info(f"Processing page {i+1}/{len(urls)}: {url}")

            try:
                content = self.extractor.extract_from_url(url)

                # Create content chunks
                chunks = self.chunker.chunk_text(content)

                # Create ContentChunk objects
                for j, chunk_text in enumerate(chunks):
                    content_id = hashlib.md5(f"{url}_{j}_{chunk_text[:50]}".encode()).hexdigest()

                    chunk_obj = ContentChunk(
                        text=chunk_text,
                        source_url=url,
                        content_id=content_id,
                        metadata={
                            "chunk_index": j,
                            "page_title": self._extract_title(content),
                            "word_count": len(chunk_text.split())
                        }
                    )
                    all_chunks.append(chunk_obj)

            except Exception as e:
                logging.error(f"Error processing {url}: {str(e)}")
                continue

        logging.info(f"Created {len(all_chunks)} content chunks")

        if not all_chunks:
            logging.warning("No content chunks were created. Exiting.")
            return

        # Step 2: Generate embeddings
        logging.info("Generating embeddings...")
        texts = [chunk.text for chunk in all_chunks]

        # Process in batches to respect API limits
        batch_size = 96  # Cohere has limits, using 96 to be safe
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedder.generate_embeddings(batch_texts)
            all_embeddings.extend(batch_embeddings)
            logging.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

        # Step 3: Store in vector database
        logging.info("Storing embeddings in Qdrant...")
        self.vector_store.store_embeddings(all_chunks, all_embeddings)

        logging.info("Content ingestion pipeline completed successfully!")

    def _extract_title(self, content: str) -> str:
        """Extract page title from content"""
        # Simple approach: take first line if it looks like a title
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100:  # Reasonable title length
                # If it starts with #, remove markdown header
                if line.startswith('#'):
                    return line.lstrip('# ').strip()
                # If it's capitalized and looks like a title
                elif line.isupper() or len(line.split()) < 10:
                    return line

        return "Untitled Page"


def main():
    """Main function to run the content ingestion pipeline"""

    # Load environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    book_url = os.getenv("BOOK_URL")

    if not all([cohere_api_key, qdrant_url, qdrant_api_key, book_url]):
        print("Missing required environment variables:")
        print("- COHERE_API_KEY: Cohere API key for embeddings")
        print("- QDRANT_URL: Qdrant Cloud URL")
        print("- QDRANT_API_KEY: Qdrant Cloud API key")
        print("- BOOK_URL: URL of the deployed Docusaurus book to ingest")
        return

    # Create pipeline instance
    pipeline = ContentIngestionPipeline(
        cohere_api_key=cohere_api_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key
    )

    # Run ingestion
    try:
        pipeline.run_ingestion(book_url)
        print("Content ingestion completed successfully!")
    except Exception as e:
        logging.error(f"Content ingestion failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()