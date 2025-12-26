"""
Utility to extract main book content from HTML, excluding navigation and footer
"""
from bs4 import BeautifulSoup
from typing import Optional
import re

def extract_book_content(html_content: str) -> str:
    """
    Extract main book content from HTML, excluding navigation, footer, and other non-content elements
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove common non-content elements
    for tag in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']):
        tag.decompose()

    # Remove elements with common class names for navigation/banners
    for element in soup.find_all(['div', 'section', 'article'],
                                class_=re.compile(r'nav|menu|sidebar|header|footer|banner|ad|social|comment|related|similar', re.I)):
        element.decompose()

    # Try to find the main content area
    # Look for semantic HTML5 elements first
    main_content = soup.find('main') or soup.find('article') or soup.find('section')

    if main_content:
        content_text = main_content.get_text(separator=' ', strip=True)
    else:
        # If no semantic elements found, try to find content by common class names
        content_selectors = [
            'content', 'main-content', 'book-content', 'post-content', 'entry-content',
            'article-content', 'page-content', 'text-content', 'body-content'
        ]

        content_text = ""
        for selector in content_selectors:
            content_element = soup.find(class_=re.compile(selector, re.I))
            if content_element:
                content_text = content_element.get_text(separator=' ', strip=True)
                break

        if not content_text:
            # If still no content found, use the body
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator=' ', strip=True)
            else:
                # Fallback to the entire soup
                content_text = soup.get_text(separator=' ', strip=True)

    # Clean up the text
    # Remove extra whitespace and newlines
    content_text = re.sub(r'\s+', ' ', content_text)

    # Remove common navigation text patterns
    content_text = re.sub(r'Next Page|Previous Page|Table of Contents|Chapter \d+|Section \d+', '', content_text, flags=re.I)

    return content_text.strip()