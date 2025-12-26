"""
Sitemap-based book content ingestion script
This script should be run as a one-time manual process
"""
import os
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import requests
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import sys
import os
# Add the current directory to the Python path to allow imports from subdirectories
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.html_parser import extract_book_content
from utils.text_splitter import split_text_into_chunks
from services.qdrant_service import QdrantService
from services.embedding_service import EmbeddingService

# Load environment variables
load_dotenv()

class BookIngestor:
    def __init__(self):
        self.sitemap_url = os.getenv("BOOK_SITEMAP_URL")
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()

        if not self.sitemap_url:
            raise ValueError("BOOK_SITEMAP_URL environment variable is required")

    def fetch_sitemap(self) -> List[str]:
        """Fetch and parse sitemap.xml to extract all book page URLs"""
        response = requests.get(self.sitemap_url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        urls = []

        # Handle both regular sitemap and sitemap index
        for url_element in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            urls.append(url_element.text)

        return urls

    def fetch_page_content(self, url: str) -> str:
        """Fetch content from a single book page URL"""
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def process_book_content(self, url: str, html_content: str) -> List[Dict[str, Any]]:
        """Extract main book content from HTML and split into chunks"""
        # Extract main book content (excluding navigation, footer, etc.)
        main_content = extract_book_content(html_content)

        # Split content into semantic chunks (300-800 tokens)
        chunks = split_text_into_chunks(main_content)

        # Create payload for each chunk
        payloads = []
        for chunk in chunks:
            payload = {
                "text": chunk['text'],
                "chapter": chunk.get('chapter', ''),
                "section": chunk.get('section', ''),
                "book_title": "Physical AI & Humanoid Robotics",
                "source_url": url
            }
            payloads.append(payload)

        return payloads

    async def ingest_book_content(self):
        """Main ingestion process"""
        print("Starting book content ingestion...")

        # Fetch all URLs from sitemap
        urls = self.fetch_sitemap()
        print(f"Found {len(urls)} URLs in sitemap")

        # Process each URL
        total_chunks = 0
        for i, url in enumerate(urls):
            print(f"Processing {i+1}/{len(urls)}: {url}")

            try:
                # Fetch page content
                html_content = self.fetch_page_content(url)

                # Process content into chunks
                payloads = self.process_book_content(url, html_content)

                # Generate embeddings and upsert to Qdrant
                await self.qdrant_service.upsert_embeddings(payloads)

                total_chunks += len(payloads)
                print(f"  Processed {len(payloads)} chunks")

            except Exception as e:
                print(f"  Error processing {url}: {str(e)}")
                continue

        print(f"Ingestion complete! Processed {total_chunks} content chunks.")
        print(f"All content stored in Qdrant collection: {os.getenv('QDRANT_COLLECTION_NAME')}")

async def main():
    """Main entry point for the ingestion script"""
    ingestor = BookIngestor()
    await ingestor.ingest_book_content()

if __name__ == "__main__":
    asyncio.run(main())