"""
Framework for the ingestion service
"""
import os
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import requests
import sys
import os
# Add the current directory to the Python path to allow imports from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.html_parser import extract_book_content
from utils.text_splitter import split_text_into_chunks
from services.qdrant_service import QdrantService
from services.embedding_service import EmbeddingService
from config import Config

class IngestionService:
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
        self.sitemap_url = Config.BOOK_SITEMAP_URL

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
                "chapter": self._extract_chapter_from_url(url),  # Extract chapter from URL
                "section": self._extract_section_from_content(chunk['text']),  # Extract section from content
                "book_title": "Physical AI & Humanoid Robotics",
                "source_url": url
            }
            payloads.append(payload)

        return payloads

    def _extract_chapter_from_url(self, url: str) -> str:
        """Extract chapter name from URL"""
        # This is a simple implementation - you might need to adjust based on your URL structure
        # Example: if URLs are like /chapter-1/introduction, extract "Chapter 1"
        import re
        match = re.search(r'/chapter[-_]?(\d+)', url, re.IGNORECASE)
        if match:
            return f"Chapter {match.group(1)}"
        return "Unknown Chapter"

    def _extract_section_from_content(self, content: str) -> str:
        """Extract section name from content"""
        # This is a simple implementation - you might want to use more sophisticated NLP
        # For now, we'll just return the first sentence or first 50 characters
        content = content.strip()
        if not content:
            return "Unknown Section"

        # Try to find a heading pattern or just return first part
        lines = content.split('\n')
        for line in lines[:3]:  # Check first 3 lines for potential section titles
            line = line.strip()
            if len(line) < 100 and line.isupper() or (line and line[0].isupper() and len(line) > 5 and len(line) < 100):
                return line

        # Return first 50 characters if no clear section found
        return content[:50] + "..." if len(content) > 50 else content

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
        print(f"All content stored in Qdrant collection: {Config.QDRANT_COLLECTION_NAME}")

        return total_chunks