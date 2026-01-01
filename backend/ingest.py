"""
Ingestion script: Fetches book content from sitemap and stores in Qdrant.

Usage:
    python ingest.py --sitemap https://example.com/sitemap.xml
"""

import argparse
import asyncio
import sys
from typing import List
from qdrant_client.http.models import PointStruct

# Set console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.config import settings
from src.utils.logger import logger, setup_logger
from src.vector_db.qdrant_client import qdrant_client
from src.embeddings.local_client import local_embeddings_client
from src.ingest.sitemap_validator import validate_sitemap_url
from src.ingest.sitemap_parser import parse_sitemap
from src.ingest.page_fetcher import fetch_pages, PageFetchError
from src.ingest.text_extractor import extract_text_from_html, clean_text_for_embedding
from src.models.book_content import BookContent


async def ingest_from_sitemap(sitemap_url: str, skip_validation: bool = False) -> None:
    """
    Complete ingestion pipeline: sitemap → URLs → content → embeddings → Qdrant.

    Args:
        sitemap_url: URL of the sitemap.xml file
        skip_validation: Skip sitemap validation (for testing)

    Raises:
        RuntimeError: If ingestion fails at any step
    """
    setup_logger(settings.app_name)

    logger.info("=" * 60)
    logger.info("Starting book content ingestion")
    logger.info("=" * 60)

    # Step 1: Validate sitemap URL
    logger.info("Step 1: Validating sitemap URL...")
    if not skip_validation:
        if not validate_sitemap_url(sitemap_url):
            raise RuntimeError(f"Invalid sitemap URL: {sitemap_url}")
    logger.info(f"[OK] Sitemap URL validated: {sitemap_url}")

    # Step 2: Parse sitemap to get URLs
    logger.info("Step 2: Parsing sitemap...")
    urls = parse_sitemap(sitemap_url)
    logger.info(f"[OK] Found {len(urls)} URLs in sitemap")

    if not urls:
        raise RuntimeError("No URLs found in sitemap")

    # Step 3: Fetch HTML content from URLs
    logger.info(f"Step 3: Fetching {len(urls)} pages...")
    url_to_html = await fetch_pages(urls)

    success_fetches = sum(1 for html in url_to_html.values() if html is not None)
    logger.info(f"[OK] Successfully fetched {success_fetches}/{len(urls)} pages")

    # Step 4: Extract and clean text content
    logger.info("Step 4: Extracting and cleaning text...")
    contents: List[BookContent] = []
    failed_extractions = 0

    for url, html in url_to_html.items():
        if html is None:
            continue

        title, text = extract_text_from_html(html, url)

        if text is None:
            failed_extractions += 1
            continue

        # Clean text for embedding
        cleaned_text = clean_text_for_embedding(text)

        content = BookContent(
            url=url,
            title=title,
            content=cleaned_text,
            section=None,  # Could be extracted from URL or HTML hierarchy
        )
        contents.append(content)

    logger.info(f"[OK] Extracted text from {len(contents)} pages")
    if failed_extractions > 0:
        logger.warning(f"[WARN] Failed to extract text from {failed_extractions} pages")

    if not contents:
        raise RuntimeError("No content extracted from fetched pages")

    # Step 5: Generate embeddings
    logger.info(f"Step 5: Generating embeddings for {len(contents)} documents...")
    texts = [c.content for c in contents]

    try:
        embeddings = await local_embeddings_client.embed_texts(texts)
        logger.info(f"[OK] Generated {len(embeddings)} embeddings")
    except Exception as e:
        raise RuntimeError(f"Failed to generate embeddings: {e}")

    # Step 6: Prepare Qdrant points
    logger.info("Step 6: Preparing Qdrant points...")
    points: List[PointStruct] = []

    for i, (content, embedding) in enumerate(zip(contents, embeddings)):
        point = PointStruct(
            id=i,  # Use index as point ID
            vector=embedding,
            payload={
                "url": content.url,
                "title": content.title,
                "content": content.content,
                "section": content.section,
                "ingested_at": content.ingested_at.isoformat(),
            },
        )
        points.append(point)

    logger.info(f"[OK] Prepared {len(points)} points for Qdrant")

    # Step 7: Ensure Qdrant collection exists
    logger.info("Step 7: Ensuring Qdrant collection exists...")
    await qdrant_client.ensure_collection_exists()
    logger.info(f"[OK] Collection ready: {settings.qdrant_collection}")

    # Step 8: Upsert points to Qdrant
    logger.info(f"Step 8: Upserting {len(points)} points to Qdrant...")
    try:
        await qdrant_client.upsert_points(points)
        logger.info(f"[OK] Successfully upserted {len(points)} points")
    except Exception as e:
        raise RuntimeError(f"Failed to upsert points to Qdrant: {e}")

    # Step 9: Verify ingestion
    logger.info("Step 9: Verifying ingestion...")
    collection_info = await qdrant_client.get_collection_info()
    if collection_info:
        total_points = collection_info.points_count
        logger.info(f"[OK] Collection now has {total_points} total points")

    logger.info("=" * 60)
    logger.info("Ingestion completed successfully!")
    logger.info("=" * 60)
    logger.info(f"Sitemap: {sitemap_url}")
    logger.info(f"URLs found: {len(urls)}")
    logger.info(f"Pages fetched: {success_fetches}")
    logger.info(f"Content extracted: {len(contents)}")
    logger.info(f"Points ingested: {len(points)}")
    logger.info("=" * 60)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest book content from sitemap into Qdrant"
    )
    parser.add_argument(
        "--sitemap",
        required=True,
        help="URL of the sitemap.xml file",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip sitemap validation (for testing)",
    )

    args = parser.parse_args()

    try:
        await ingest_from_sitemap(args.sitemap, args.skip_validation)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
