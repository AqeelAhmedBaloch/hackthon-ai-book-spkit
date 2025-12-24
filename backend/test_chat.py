"""
Simple test script for the RAG chatbot functionality
"""
import asyncio
from main import read_book_content, chunk_text, clean_markdown_content

def test_chat_functionality():
    print("Testing RAG Chatbot functionality...")

    # Test reading book content
    print("\n1. Testing book content reading...")
    content_list = read_book_content('../ai_frontend_book/docs/')
    print(f"Found {len(content_list)} content files")

    if content_list:
        print("Sample content files:")
        for i, item in enumerate(content_list[:3]):  # Show first 3 files
            print(f"  - {item['source_path']}: {len(item['content'])} chars")

    # Test content cleaning
    print("\n2. Testing content cleaning...")
    if content_list:
        sample_content = content_list[0]['content'][:500]  # First 500 chars
        print(f"Original content sample: {sample_content[:100]}...")
        cleaned = clean_markdown_content(sample_content)
        print(f"Cleaned content sample: {cleaned[:100]}...")

    # Test chunking
    print("\n3. Testing content chunking...")
    if content_list:
        sample_content = content_list[0]['content'][:1000]  # First 1000 chars
        chunks = chunk_text(sample_content, chunk_size=512, overlap=50)
        print(f"Generated {len(chunks)} chunks from sample content")
        if chunks:
            print(f"First chunk length: {len(chunks[0])} chars")
            print(f"First chunk sample: {chunks[0][:100]}...")

if __name__ == "__main__":
    test_chat_functionality()
    print("\nTest completed successfully!")