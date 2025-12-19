import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from ..shared.models import ContentChunk
from ..shared.utils import hash_content


class ContentLoader:
    """
    Class to load content from various sources (files, directories, URLs)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.txt', '.md', '.markdown', '.pdf', '.html', '.htm']

    def load_from_file(self, file_path: str) -> List[ContentChunk]:
        """
        Load content from a single file
        """
        file_path = Path(file_path)

        if not file_path.exists():
            self.logger.error(f"File does not exist: {file_path}")
            return []

        extension = file_path.suffix.lower()

        if extension not in self.supported_formats:
            self.logger.warning(f"Unsupported file format: {extension}")
            return []

        try:
            if extension in ['.txt', '.md', '.markdown']:
                return self._load_text_file(file_path)
            elif extension == '.pdf':
                return self._load_pdf_file(file_path)
            elif extension in ['.html', '.htm']:
                return self._load_html_file(file_path)
            else:
                self.logger.warning(f"Format not yet implemented: {extension}")
                return []
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return []

    def load_from_directory(self, directory_path: str) -> List[ContentChunk]:
        """
        Load content from all supported files in a directory
        """
        directory_path = Path(directory_path)

        if not directory_path.exists():
            self.logger.error(f"Directory does not exist: {directory_path}")
            return []

        all_chunks = []

        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    chunks = self.load_from_file(str(file_path))
                    all_chunks.extend(chunks)
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {e}")
                    continue

        return all_chunks

    def _load_text_file(self, file_path: Path) -> List[ContentChunk]:
        """
        Load content from a text-based file (txt, md)
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        chunk = ContentChunk(
            id=f"file_{file_path.name}_{hash_content(content[:50])}",
            content=content,
            source_document=file_path.name,
            page_number=None,
            section=None,
            metadata={
                'file_path': str(file_path),
                'file_type': 'text',
                'size': file_path.stat().st_size,
                'hash': hash_content(content)
            },
            hash=hash_content(content)
        )

        return [chunk]

    def _load_pdf_file(self, file_path: Path) -> List[ContentChunk]:
        """
        Load content from a PDF file
        """
        try:
            import PyPDF2

            chunks = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    content = page.extract_text()

                    if content.strip():  # Only add if content is not empty
                        chunk = ContentChunk(
                            id=f"pdf_{file_path.name}_page_{page_num}_{hash_content(content[:50])}",
                            content=content,
                            source_document=file_path.name,
                            page_number=page_num,
                            section=f"Page {page_num}",
                            metadata={
                                'file_path': str(file_path),
                                'file_type': 'pdf',
                                'page_number': page_num,
                                'size': file_path.stat().st_size,
                                'hash': hash_content(content)
                            },
                            hash=hash_content(content)
                        )
                        chunks.append(chunk)

            return chunks
        except ImportError:
            self.logger.error("PyPDF2 not installed. Please install it with: pip install PyPDF2")
            return []
        except Exception as e:
            self.logger.error(f"Error reading PDF file {file_path}: {e}")
            return []

    def _load_html_file(self, file_path: Path) -> List[ContentChunk]:
        """
        Load content from an HTML file, extracting only the text content
        """
        try:
            from bs4 import BeautifulSoup

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            soup = BeautifulSoup(content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text_content = soup.get_text()

            # Clean up text (remove extra whitespace)
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)

            chunk = ContentChunk(
                id=f"html_{file_path.name}_{hash_content(text_content[:50])}",
                content=text_content,
                source_document=file_path.name,
                page_number=None,
                section=None,
                metadata={
                    'file_path': str(file_path),
                    'file_type': 'html',
                    'size': file_path.stat().st_size,
                    'hash': hash_content(text_content)
                },
                hash=hash_content(text_content)
            )

            return [chunk]
        except ImportError:
            self.logger.error("BeautifulSoup4 not installed. Please install it with: pip install beautifulsoup4")
            return []
        except Exception as e:
            self.logger.error(f"Error reading HTML file {file_path}: {e}")
            return []

    def load_from_url(self, url: str) -> List[ContentChunk]:
        """
        Load content from a URL (web page)
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text_content = soup.get_text()

            # Clean up text (remove extra whitespace)
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)

            chunk = ContentChunk(
                id=f"url_{hash_content(url[:30])}_{hash_content(text_content[:50])}",
                content=text_content,
                source_document=url,
                page_number=None,
                section=None,
                metadata={
                    'url': url,
                    'file_type': 'web',
                    'hash': hash_content(text_content)
                },
                hash=hash_content(text_content)
            )

            return [chunk]
        except ImportError:
            self.logger.error("requests or BeautifulSoup4 not installed. Please install them with: pip install requests beautifulsoup4")
            return []
        except Exception as e:
            self.logger.error(f"Error reading URL {url}: {e}")
            return []