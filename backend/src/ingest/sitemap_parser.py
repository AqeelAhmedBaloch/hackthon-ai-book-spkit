"""
Sitemap parser to extract page URLs from sitemap.xml files.
"""

import httpx
from xml.etree import ElementTree as ET
from urllib.parse import urljoin
from typing import List

from src.ingest.sitemap_validator import is_valid_book_url
from src.utils.logger import logger


def parse_sitemap(sitemap_url: str) -> List[str]:
    """
    Parse a sitemap XML and extract all page URLs.

    Args:
        sitemap_url: URL of the sitemap.xml file

    Returns:
        List of unique, valid page URLs

    Raises:
        RuntimeError: If sitemap cannot be fetched or parsed
    """
    logger.info(f"Fetching sitemap from: {sitemap_url}")

    try:
        # Fetch the sitemap
        response = httpx.get(sitemap_url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.text)

        logger.info(f"Parsed XML root tag: {root.tag}")

        urls: List[str] = []

        # Check if it's a sitemap index (references other sitemaps)
        if root.tag == "sitemapindex" or root.tag.endswith("}sitemapindex"):
            # This is a sitemap index, extract and recurse
            namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemaps = root.findall(".//sm:sitemap", namespaces) or root.findall(".//sitemap")

            for sitemap in sitemaps:
                loc = sitemap.find("loc")
                if loc is not None:
                    child_sitemap_url = loc.text.strip()
                    logger.info(f"Found child sitemap: {child_sitemap_url}")
                    urls.extend(parse_sitemap(child_sitemap_url))

        # Check if it's a regular sitemap with URLs
        elif root.tag == "urlset" or root.tag.endswith("}urlset"):
            logger.info("Detected urlset sitemap")

            # Extract URLs - use proper namespace handling
            namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Try with namespace first
            url_elements = root.findall(".//sm:url/sm:loc", namespaces)

            # If that doesn't work, try the alternative structure
            if not url_elements:
                # The url elements might have the namespace directly
                url_elements = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")

            logger.info(f"Found {len(url_elements)} URL locations")

            for loc_elem in url_elements:
                if loc_elem is not None and loc_elem.text:
                    page_url = loc_elem.text.strip()
                    logger.debug(f"Found URL: {page_url}")

                    # Validate it's likely a book page (not an asset, API, etc.)
                    if is_valid_book_url(page_url):
                        urls.append(page_url)
                    else:
                        logger.debug(f"Filtered non-book URL: {page_url}")

        else:
            raise RuntimeError(f"Unknown sitemap format: {root.tag}")

        # Deduplicate while preserving order
        unique_urls: List[str] = []
        seen: set = set()
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        logger.info(f"Extracted {len(unique_urls)} unique URLs from sitemap")
        return unique_urls

    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error fetching sitemap: {e.response.status_code}")
    except ET.ParseError as e:
        raise RuntimeError(f"Failed to parse sitemap XML: {e}")
    except Exception as e:
        raise RuntimeError(f"Error parsing sitemap: {e}")
