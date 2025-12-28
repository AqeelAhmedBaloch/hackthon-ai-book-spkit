"""
Ingestion module for sitemap parsing and content extraction.
"""
from src.ingest.sitemap_validator import validate_sitemap_url, is_valid_book_url
from src.ingest.sitemap_parser import parse_sitemap
from src.ingest.page_fetcher import fetch_page, fetch_pages, PageFetchError
from src.ingest.text_extractor import extract_text_from_html, clean_text_for_embedding

__all__ = [
    "validate_sitemap_url",
    "is_valid_book_url",
    "parse_sitemap",
    "fetch_page",
    "fetch_pages",
    "PageFetchError",
    "extract_text_from_html",
    "clean_text_for_embedding",
]
