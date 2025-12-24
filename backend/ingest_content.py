#!/usr/bin/env python3
"""
Content ingestion script for the Physical AI & Humanoid Robotics book.
This script reads markdown files from the docs directory and stores them in the Qdrant vector database.
"""
import os
import glob
from pathlib import Path
from agent import RAGAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_markdown_file(file_path):
    """Read content from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def extract_title_from_content(content):
    """Extract the title from markdown content (first H1 heading)."""
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip()[2:]  # Remove '# ' prefix
    return "Untitled"

def chunk_content(content, max_chunk_size=1000):
    """
    Split content into smaller chunks to avoid embedding size limits.
    This ensures that large documents are broken down into manageable pieces.
    """
    chunks = []
    paragraphs = content.split('\n\n')

    current_chunk = ""
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the chunk size, save the current chunk
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph

    # Add the last chunk if it has content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # If we still have a chunk that's too large, split by sentences
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            # Split large chunk by sentences
            sentences = chunk.split('. ')
            temp_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip() + '. '
                if len(temp_chunk) + len(sentence) > max_chunk_size and temp_chunk:
                    final_chunks.append(temp_chunk.strip())
                    temp_chunk = sentence
                else:
                    temp_chunk += sentence
            if temp_chunk.strip():
                final_chunks.append(temp_chunk.strip())
        else:
            final_chunks.append(chunk)

    return final_chunks

def ingest_docs_content():
    """Ingest all markdown content from the docs directory into the vector database."""
    print("Initializing RAG Agent...")
    rag_agent = RAGAgent()

    # Path to the docs directory (relative to backend directory)
    docs_path = Path(__file__).parent.parent / "ai_frontend_book" / "docs"

    if not docs_path.exists():
        print(f"Docs directory not found at: {docs_path}")
        return

    print(f"Reading content from: {docs_path}")

    # Find all markdown files in the docs directory and subdirectories
    md_files = list(docs_path.glob("**/*.md"))

    if not md_files:
        print("No markdown files found in the docs directory.")
        return

    print(f"Found {len(md_files)} markdown files to process...")

    total_chunks_stored = 0

    for md_file in md_files:
        print(f"Processing: {md_file}")

        try:
            # Read the content of the markdown file
            content = read_markdown_file(md_file)

            # Extract title from content
            title = extract_title_from_content(content)

            # Create metadata for the content
            relative_path = md_file.relative_to(docs_path.parent)
            metadata = {
                "source": str(relative_path),
                "title": title,
                "file_path": str(md_file),
                "module": str(md_file.parent.name) if "module" in str(md_file) else "intro"
            }

            # Chunk the content to ensure it fits within embedding limits
            content_chunks = chunk_content(content)

            print(f"  - Split into {len(content_chunks)} chunks")

            # Store each chunk in the vector database
            for i, chunk in enumerate(content_chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = i
                chunk_metadata["chunk_count"] = len(content_chunks)

                # Add chunk-specific information to the content for context
                chunk_text = f"Document: {title}\nSection: {md_file.name}\n\n{chunk}"

                rag_agent.store_content(chunk_text, chunk_metadata)
                total_chunks_stored += 1

                print(f"    - Stored chunk {i+1}/{len(content_chunks)}")

                # Add a small delay to respect API rate limits
                import time
                time.sleep(1.5)  # 1.5 second delay to stay under rate limits

        except Exception as e:
            print(f"Error processing {md_file}: {str(e)}")
            continue

    print(f"\nIngestion completed! Stored {total_chunks_stored} content chunks in the vector database.")

if __name__ == "__main__":
    ingest_docs_content()