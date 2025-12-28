"""
Sitemap URL validator to ensure provided URL is a valid sitemap.
"""

import httpx
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


def validate_sitemap_url(url: str) -> bool:
    """
    Validate that a URL points to a valid sitemap.

    Args:
        url: The sitemap URL to validate

    Returns:
        True if valid sitemap, False otherwise
    """
    try:
        # Validate URL format
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False

        # Only allow HTTP/HTTPS
        if parsed.scheme not in ("http", "https"):
            return False

        # Try to fetch and parse the sitemap
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get("content-type", "")
        if "xml" not in content_type.lower():
            # Could still be XML, so try parsing
            pass

        # Try to parse as XML
        try:
            root = ET.fromstring(response.text)
            # Check for sitemap namespace or standard sitemap structure
            if root.tag in ("sitemapindex", "urlset") or root.tag.endswith("}sitemapindex") or root.tag.endswith("}urlset"):
                return True
        except ET.ParseError:
            return False

        return False

    except httpx.HTTPError:
        return False
    except Exception:
        return False


def is_valid_book_url(url: str) -> bool:
    """
    Basic validation for book page URLs (can be customized per project).

    Args:
        url: URL to validate

    Returns:
        True if likely a book page, False otherwise
    """
    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        return False

    # Common book page patterns (customize as needed)
    path = parsed.path.lower()

    # Exclude common non-content paths
    excluded_paths = [
        "/assets/", "/images/", "/css/", "/js/", "/api/",
        "/static/", "/media/", "/search/", "/login/", "/register/",
    ]
    if any(excluded in path for excluded in excluded_paths):
        return False

    # Accept clean URLs (no extension) and .html/.htm files
    # Clean URLs are common in modern static site generators (Docusaurus, Next.js, etc.)
    return True
