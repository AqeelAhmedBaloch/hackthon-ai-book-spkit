"""
Test script to verify backend module structure and imports.
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all modules can be imported."""
    errors = []

    # Test core modules
    try:
        from src import config
        print("[OK] src.config")
    except Exception as e:
        errors.append(f"src.config: {e}")
        print(f"[FAIL] src.config: {e}")

    try:
        from src.models import BookContent, ChatRequest, ChatResponse
        print("[OK] src.models")
    except Exception as e:
        errors.append(f"src.models: {e}")
        print(f"[FAIL] src.models: {e}")

    try:
        from src.vector_db import qdrant_client
        print("[OK] src.vector_db")
    except Exception as e:
        errors.append(f"src.vector_db: {e}")
        print(f"[FAIL] src.vector_db: {e}")

    try:
        from src.embeddings import cohere_client
        print("[OK] src.embeddings")
    except Exception as e:
        errors.append(f"src.embeddings: {e}")
        print(f"[FAIL] src.embeddings: {e}")

    try:
        from src.llm import openrouter_client
        print("[OK] src.llm")
    except Exception as e:
        errors.append(f"src.llm: {e}")
        print(f"[FAIL] src.llm: {e}")

    try:
        from src.ingest import parse_sitemap, validate_sitemap_url
        print("[OK] src.ingest")
    except Exception as e:
        errors.append(f"src.ingest: {e}")
        print(f"[FAIL] src.ingest: {e}")

    try:
        from src.agent import rag_agent, embed_query
        print("[OK] src.agent")
    except Exception as e:
        errors.append(f"src.agent: {e}")
        print(f"[FAIL] src.agent: {e}")

    try:
        from src.utils import logger
        print("[OK] src.utils")
    except Exception as e:
        errors.append(f"src.utils: {e}")
        print(f"[FAIL] src.utils: {e}")

    return errors

def test_file_structure():
    """Verify all expected files exist."""
    expected_files = [
        "src/__init__.py",
        "src/config.py",
        "src/agent/__init__.py",
        "src/agent/rag_agent.py",
        "src/agent/query_embedder.py",
        "src/agent/retriever.py",
        "src/agent/answer_generator.py",
        "src/embeddings/__init__.py",
        "src/embeddings/cohere_client.py",
        "src/ingest/__init__.py",
        "src/ingest/sitemap_validator.py",
        "src/ingest/sitemap_parser.py",
        "src/ingest/page_fetcher.py",
        "src/ingest/text_extractor.py",
        "src/llm/__init__.py",
        "src/llm/openrouter_client.py",
        "src/models/__init__.py",
        "src/models/book_content.py",
        "src/models/chat.py",
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/vector_db/__init__.py",
        "src/vector_db/qdrant_client.py",
        "ingest.py",
        "agent.py",
        "main.py",
        "pyproject.toml",
        ".env.example",
    ]

    print("\n--- File Structure Check ---")
    missing = []
    for f in expected_files:
        full_path = backend_dir / f
        if full_path.exists():
            print(f"[OK] {f}")
        else:
            print(f"[MISS] {f}")
            missing.append(f)

    return missing

def test_pydantic_models():
    """Test Pydantic models can be instantiated."""
    print("\n--- Pydantic Models Test ---")

    try:
        from src.models.book_content import BookContent
        book = BookContent(
            url="https://example.com",
            title="Test",
            content="Test content"
        )
        print(f"[OK] BookContent model: {book.url}")
    except Exception as e:
        print(f"[FAIL] BookContent model: {e}")

    try:
        from src.models.chat import ChatRequest, ChatResponse, Source
        req = ChatRequest(query="What is this?")
        print(f"[OK] ChatRequest model: {req.query}")
    except Exception as e:
        print(f"[FAIL] ChatRequest model: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Structure Test")
    print("=" * 60)

    missing_files = test_file_structure()

    if missing_files:
        print(f"\n[MISSING] {len(missing_files)} files!")
    else:
        print("\n[OK] All files present")

    print("\n" + "=" * 60)
    print("Import Test")
    print("=" * 60)

    import_errors = test_imports()

    if import_errors:
        print(f"\n[FAIL] {len(import_errors)} import errors!")
    else:
        print("\n[OK] All imports successful")

    test_pydantic_models()

    print("\n" + "=" * 60)
    if not missing_files and not import_errors:
        print("[SUCCESS] Backend structure is valid!")
    else:
        print("[FAIL] Backend has issues")
    print("=" * 60)
