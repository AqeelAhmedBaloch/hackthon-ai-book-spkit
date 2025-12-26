"""
Enhanced Sitemap Parser Module
Handles XML, XML.GZ, sitemap index, and HTML sitemap formats with proper validation
"""
import gzip
import io
import logging
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


class SitemapParser:
    """
    Enhanced sitemap parser that handles multiple formats:
    - XML sitemaps
    - Gzipped XML sitemaps (.xml.gz)
    - Sitemap index files
    - HTML sitemaps (when XML parsing fails)
    """

    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = requests.Session()
        self.session.max_redirects = max_redirects
        self.logger = logging.getLogger(__name__)

    def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Fetch and parse sitemap with format detection and validation.

        Args:
            sitemap_url: URL of the sitemap to fetch

        Returns:
            List of URLs extracted from the sitemap

        Raises:
            requests.RequestException: For network errors
            ValueError: For invalid sitemap content
        """
        self.logger.info(f"Fetching sitemap from: {sitemap_url}")

        # Fetch the sitemap
        response = self.session.get(sitemap_url, timeout=self.timeout)
        response.raise_for_status()

        # Validate content type before parsing
        content_type = response.headers.get('content-type', '').lower()
        content_encoding = response.headers.get('content-encoding', '').lower()

        self.logger.debug(f"Content-Type: {content_type}, Content-Encoding: {content_encoding}")

        # Determine content format and parse accordingly
        if content_encoding in ['gzip', 'x-gzip'] or sitemap_url.endswith('.gz'):
            # Handle gzipped content, but with fallback if it's not actually gzipped
            try:
                urls = self._parse_gzipped_content(response.content)
            except ValueError:
                # If gzip parsing fails, try to detect actual content type
                urls = self._detect_and_parse_content(response.content, response.text, sitemap_url)
        elif 'text/html' in content_type:
            # Handle HTML content (could be HTML sitemap)
            urls = self._parse_html_content(response.text, sitemap_url)
        elif 'xml' in content_type:
            # Handle XML content
            urls = self._parse_xml_content(response.content)
        else:
            # Try to detect format based on content if content-type is ambiguous
            urls = self._detect_and_parse_content(response.content, response.text, sitemap_url)

        # Validate that we found URLs
        if not urls:
            # If no URLs were found, try common sitemap paths
            common_sitemap_paths = [
                f"{sitemap_url.rstrip('/')}/sitemap.xml",
                f"{sitemap_url.rstrip('/')}/sitemap_index.xml",
                f"{sitemap_url.rstrip('/')}/sitemap.xml.gz",
            ]

            for sitemap_path in common_sitemap_paths:
                try:
                    self.logger.info(f"Trying common sitemap path: {sitemap_path}")
                    # Create a new parser instance to avoid recursion issues
                    temp_parser = SitemapParser(timeout=self.timeout, max_redirects=self.max_redirects)
                    temp_parser.logger = self.logger
                    urls = temp_parser.fetch_sitemap(sitemap_path)
                    if urls:
                        self.logger.info(f"Successfully found {len(urls)} URLs from common sitemap path: {sitemap_path}")
                        return urls
                except Exception as e:
                    self.logger.debug(f"Failed to fetch sitemap from {sitemap_path}: {str(e)}")
                    continue  # Try next path

            # If still no URLs found, raise the error
            error_msg = f"No valid URLs found in sitemap: {sitemap_url}. Content-Type: {content_type}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info(f"Successfully extracted {len(urls)} URLs from sitemap")
        return urls

    def _parse_xml_content(self, content: bytes) -> List[str]:
        """Parse XML sitemap content (regular or sitemap index)."""
        try:
            root = ET.fromstring(content)
            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                        'index': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # Check if this is a sitemap index
            if root.tag.endswith('sitemapindex'):
                return self._parse_sitemap_index(root)
            else:
                # Regular sitemap
                return self._parse_regular_sitemap(root)
        except ET.ParseError as e:
            self.logger.error(f"XML parsing failed: {str(e)}")
            # Fall back to HTML parsing if XML parsing fails
            try:
                return self._parse_html_content(content.decode('utf-8', errors='ignore'))
            except Exception:
                raise ValueError(f"Failed to parse XML content: {str(e)}")

    def _parse_sitemap_index(self, root) -> List[str]:
        """Parse sitemap index file and extract all nested sitemap URLs."""
        urls = []
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Extract sitemap locations
        for sitemap_elem in root.findall('.//sitemap:sitemap/sitemap:loc', namespace):
            if sitemap_elem is not None and sitemap_elem.text:
                nested_sitemap_url = sitemap_elem.text.strip()
                try:
                    # Recursively fetch and parse nested sitemap
                    nested_urls = self.fetch_sitemap(nested_sitemap_url)
                    urls.extend(nested_urls)
                except Exception as e:
                    self.logger.warning(f"Failed to process nested sitemap {nested_sitemap_url}: {str(e)}")
                    continue

        return urls

    def _parse_regular_sitemap(self, root) -> List[str]:
        """Parse regular sitemap and extract URLs."""
        urls = []
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Extract URL locations
        for url_elem in root.findall('.//sitemap:url/sitemap:loc', namespace):
            if url_elem is not None and url_elem.text:
                urls.append(url_elem.text.strip())

        return urls

    def _parse_gzipped_content(self, content: bytes) -> List[str]:
        """Parse gzipped sitemap content."""
        try:
            # Decompress the content
            with gzip.GzipFile(fileobj=io.BytesIO(content)) as gzip_file:
                decompressed_content = gzip_file.read()

            # Parse the decompressed XML
            return self._parse_xml_content(decompressed_content)
        except Exception as e:
            self.logger.error(f"Failed to decompress or parse gzipped content: {str(e)}")
            raise ValueError(f"Failed to process gzipped sitemap: {str(e)}")

    def _parse_html_content(self, html_content: str, base_url: str = "") -> List[str]:
        """Parse HTML content to extract sitemap-related URLs."""
        urls = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Look for sitemap links in various forms
            # 1. <link rel="sitemap"> tags
            for link in soup.find_all('link', rel='sitemap'):
                if link.get('href'):
                    urls.append(urljoin(base_url, link['href']))

            # 2. Links that look like sitemap URLs
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(keyword in href.lower() for keyword in ['sitemap', 'mapa', 'site-map']):
                    urls.append(urljoin(base_url, href))

            # 3. Look for common sitemap patterns in HTML
            # Check for <link rel="sitemap" tags
            for link in soup.find_all('link', rel='sitemap'):
                if link.get('href'):
                    urls.append(urljoin(base_url, link['href']))

            # Check for common sitemap URLs in the HTML
            for link in soup.find_all(['link', 'a']):
                href = link.get('href', '')
                if href and any(pattern in href.lower() for pattern in ['sitemap', 'sitemap.xml']):
                    urls.append(urljoin(base_url, href))

            # Check for common sitemap URLs in text content
            # Common patterns: sitemap.xml, /sitemap, sitemap-index.xml
            import re
            sitemap_patterns = [
                r'(https?://[^\s"\'<>]*sitemap[^\s"\'<>]*\.(xml|gz))',
                r'(/[^\s"\'<>]*sitemap[^\s"\'<>]*\.(xml|gz))',
                r'(sitemap[^\s"\'<>]*\.(xml|gz))'
            ]

            for pattern in sitemap_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        full_url = ''.join(match)
                    else:
                        full_url = match
                    if full_url:
                        urls.append(urljoin(base_url, full_url))

            # Filter out invalid URLs and remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in urls:
                if url not in seen and self._is_valid_url(url):
                    seen.add(url)
                    unique_urls.append(url)

            return unique_urls
        except Exception as e:
            self.logger.error(f"Failed to parse HTML content: {str(e)}")
            raise ValueError(f"Failed to process HTML sitemap: {str(e)}")

    def _is_valid_url(self, url: str) -> bool:
        """Check if a string is a valid URL."""
        from urllib.parse import urlparse
        import re

        # Basic check: URL should contain at least one dot or start with protocol
        if not url or len(url.strip()) < 3:
            return False

        # Skip if it looks like plain text (e.g., "Docusaurus v3.9.2")
        if re.search(r'\b(v\d+\.\d+|\d+\.\d+|v\d+)\b', url) and not re.search(r'https?://', url):
            return False

        try:
            result = urlparse(url)
            # A valid URL should have either:
            # 1. Both scheme and netloc (absolute URL like http://example.com)
            # 2. Just netloc (like example.com - though this is rare in practice)
            # 3. A path that looks like a file path (like /sitemap.xml)
            has_valid_components = (
                all([result.scheme, result.netloc]) or  # Complete URL
                (result.netloc and result.path) or      # Host with path
                (result.path and (result.path.startswith('/') or '.' in result.path))  # Path starting with / or containing file extension
            )
            return bool(has_valid_components)
        except Exception:
            return False

    def _detect_and_parse_content(self, content: bytes, text_content: str, sitemap_url: str) -> List[str]:
        """Detect content format based on content and parse accordingly."""
        content_str = content.decode('utf-8', errors='ignore').strip()

        # Check for gzip indicators (first few bytes) FIRST before other checks
        if len(content) >= 2 and content[0:2] == b'\x1f\x8b':
            try:
                return self._parse_gzipped_content(content)
            except ValueError:
                # If gzip parsing fails, fall back to other detection methods
                pass

        # Check for XML indicators
        if content_str.startswith('<?xml') or '<urlset' in content_str or '<sitemapindex' in content_str:
            return self._parse_xml_content(content)

        # Default to HTML parsing if nothing else matches
        return self._parse_html_content(text_content, sitemap_url)


def fetch_sitemap_with_validation(sitemap_url: str) -> List[str]:
    """
    Convenience function to fetch and validate sitemap with default settings.

    Args:
        sitemap_url: URL of the sitemap to fetch

    Returns:
        List of URLs extracted from the sitemap
    """
    parser = SitemapParser()
    return parser.fetch_sitemap(sitemap_url)