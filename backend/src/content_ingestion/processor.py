from typing import List, Dict, Any
from ..shared.models import ContentChunk
from ..shared.utils import chunk_text, hash_content
import logging


class ContentProcessor:
    """
    Class to process and chunk content for embedding
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_content_chunks(self, raw_chunks: List[ContentChunk],
                              chunk_size: int = 512,
                              chunk_overlap: int = 50) -> List[ContentChunk]:
        """
        Process raw content chunks by splitting them into smaller, more manageable chunks
        """
        processed_chunks = []

        for chunk in raw_chunks:
            # Split the content into smaller chunks
            content_subchunks = chunk_text(
                chunk.content,
                chunk_size=chunk_size,
                overlap=chunk_overlap
            )

            # Create new content chunks for each subchunk
            for i, subchunk in enumerate(content_subchunks):
                # Generate a unique ID for the subchunk
                subchunk_id = f"{chunk.id}_part_{i}"

                # Preserve original metadata and add chunk-specific info
                subchunk_metadata = chunk.metadata or {}
                subchunk_metadata.update({
                    'original_chunk_id': chunk.id,
                    'part_number': i,
                    'total_parts': len(content_subchunks),
                    'is_subchunk': True
                })

                processed_chunk = ContentChunk(
                    id=subchunk_id,
                    content=subchunk,
                    source_document=chunk.source_document,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    metadata=subchunk_metadata,
                    embedding=None,
                    hash=hash_content(subchunk)
                )

                processed_chunks.append(processed_chunk)

        self.logger.info(f"Processed {len(raw_chunks)} raw chunks into {len(processed_chunks)} subchunks")
        return processed_chunks

    def clean_content(self, content: str) -> str:
        """
        Clean and normalize content text
        """
        if not content:
            return ""

        # Remove extra whitespace
        import re
        cleaned = re.sub(r'\s+', ' ', content)

        # Remove null bytes and other potentially harmful characters
        cleaned = cleaned.replace('\x00', '')

        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned

    def filter_content_chunks(self, chunks: List[ContentChunk],
                             min_length: int = 10,
                             max_length: int = 2000) -> List[ContentChunk]:
        """
        Filter content chunks based on length and quality criteria
        """
        filtered_chunks = []

        for chunk in chunks:
            # Clean the content
            cleaned_content = self.clean_content(chunk.content)

            # Check if content meets length requirements
            if len(cleaned_content) < min_length:
                self.logger.debug(f"Skipping chunk {chunk.id} - too short ({len(cleaned_content)} chars)")
                continue

            if len(cleaned_content) > max_length:
                self.logger.debug(f"Skipping chunk {chunk.id} - too long ({len(cleaned_content)} chars)")
                continue

            # Update the chunk with cleaned content
            chunk.content = cleaned_content
            filtered_chunks.append(chunk)

        self.logger.info(f"Filtered {len(chunks)} chunks to {len(filtered_chunks)} valid chunks")
        return filtered_chunks

    def deduplicate_chunks(self, chunks: List[ContentChunk]) -> List[ContentChunk]:
        """
        Remove duplicate content chunks based on content hash
        """
        seen_hashes = set()
        unique_chunks = []

        for chunk in chunks:
            if chunk.hash not in seen_hashes:
                seen_hashes.add(chunk.hash)
                unique_chunks.append(chunk)
            else:
                self.logger.debug(f"Skipping duplicate chunk with hash {chunk.hash}")

        self.logger.info(f"Deduplicated {len(chunks)} chunks to {len(unique_chunks)} unique chunks")
        return unique_chunks

    def process(self, raw_chunks: List[ContentChunk],
                chunk_size: int = 512,
                chunk_overlap: int = 50,
                min_length: int = 10,
                max_length: int = 2000) -> List[ContentChunk]:
        """
        Complete processing pipeline: filter, clean, chunk, and deduplicate
        """
        self.logger.info(f"Starting content processing for {len(raw_chunks)} raw chunks")

        # First, filter based on initial criteria
        filtered_chunks = self.filter_content_chunks(raw_chunks, min_length, max_length)

        # Then, process each chunk into smaller subchunks
        subchunked_chunks = self.process_content_chunks(filtered_chunks, chunk_size, chunk_overlap)

        # Finally, deduplicate the results
        unique_chunks = self.deduplicate_chunks(subchunked_chunks)

        self.logger.info(f"Processing complete: {len(raw_chunks)} -> {len(unique_chunks)} chunks")
        return unique_chunks