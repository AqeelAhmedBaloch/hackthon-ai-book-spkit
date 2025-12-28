"""
Page fetcher to retrieve HTML content from book URLs.
"""

import httpx
from typing import Optional
from src.utils.logger import logger


class PageFetchError(Exception):
    """Raised when a page cannot be fetched."""
    pass


async def fetch_page(url: str, timeout: float = 15.0) -> Optional[str]:
    """
    Fetch HTML content from a URL.

    Args:
        url: The page URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content as string, or None if fetch fails

    Raises:
        PageFetchError: If page cannot be fetched after retries
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Check for HTML content
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                logger.warning(f"Skipping non-HTML page: {url} (content-type: {content_type})")
                return None

            html = response.text

            if not html or len(html.strip()) < 100:
                logger.warning(f"Skipping empty or too short page: {url}")
                return None

            logger.debug(f"Successfully fetched page: {url}")
            return html

    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching page {url}: {e.response.status_code}")
        raise PageFetchError(f"HTTP {e.response.status_code} for {url}")
    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching page: {url}")
        raise PageFetchError(f"Timeout for {url}")
    except Exception as e:
        logger.warning(f"Error fetching page {url}: {e}")
        raise PageFetchError(f"Fetch error for {url}: {e}")


async def fetch_pages(urls: list[str], timeout: float = 15.0) -> dict[str, Optional[str]]:
    """
    Fetch multiple pages concurrently.

    Args:
        urls: List of URLs to fetch
        timeout: Request timeout in seconds per page

    Returns:
        Dictionary mapping URL -> HTML content (None for failed fetches)
    """
    import asyncio

    results: dict[str, Optional[str]] = {}

    # Fetch with limited concurrency to avoid overwhelming servers
    semaphore = asyncio.Semaphore(10)

    async def fetch_with_limit(url: str) -> tuple[str, Optional[str]]:
        async with semaphore:
            try:
                html = await fetch_page(url, timeout)
                return (url, html)
            except PageFetchError:
                return (url, None)

    # Create all fetch tasks
    tasks = [fetch_with_limit(url) for url in urls]

    # Execute with progress logging
    completed = 0
    for future in asyncio.as_completed(tasks):
        url, html = await future
        results[url] = html
        completed += 1
        if completed % 10 == 0:
            logger.info(f"Fetched {completed}/{len(urls)} pages")

    success_count = sum(1 for html in results.values() if html is not None)
    logger.info(f"Successfully fetched {success_count}/{len(urls)} pages")

    return results
