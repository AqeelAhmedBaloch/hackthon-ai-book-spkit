"""
Text extractor to clean and extract meaningful text from HTML.
"""

from bs4 import BeautifulSoup
from typing import Optional, Tuple
from src.utils.logger import logger


def extract_text_from_html(html: str, url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract meaningful text content and title from HTML.

    Args:
        html: Raw HTML content
        url: Source URL (for logging)

    Returns:
        Tuple of (title, cleaned_text) - either can be None
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = None
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            title = title_tag.string.strip()

        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
            element.decompose()

        # Try to find main content area
        main_content = None
        for selector in ["main", "article", '[role="main"]', "#content", ".content"]:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find("body")

        if not main_content:
            return title, None

        # Get text with whitespace normalization
        text = main_content.get_text(separator=" ", strip=True)

        # Clean up excessive whitespace
        import re
        text = re.sub(r"\s+", " ", text)

        # Filter out very short content
        if len(text) < 50:
            logger.warning(f"Too short text from {url}: {len(text)} chars")
            return title, None

        logger.debug(f"Extracted {len(text)} chars from {url}")
        return title, text

    except Exception as e:
        logger.warning(f"Error extracting text from {url}: {e}")
        return None, None


def clean_text_for_embedding(text: str) -> str:
    """
    Clean text for embedding generation.

    Args:
        text: Raw text content

    Returns:
        Cleaned text suitable for embeddings
    """
    # Normalize whitespace
    import re
    text = re.sub(r"\s+", " ", text)

    # Remove special characters that don't add meaning
    text = re.sub(r"[^\w\s.!?;:,-]", " ", text)

    # Truncate if too long (Cohere has token limits)
    max_chars = 4000  # Safe limit for embeddings
    if len(text) > max_chars:
        text = text[:max_chars]
        logger.debug(f"Truncated text to {max_chars} chars for embedding")

    return text.strip()
