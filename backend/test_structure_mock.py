"""
Test script to verify backend module structure without API keys.
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Mock settings before any imports
class MockSettings:
    app_name = "RAG Book Chatbot Backend"
    app_version = "0.1.0"
    log_level = "INFO"
    openrouter_api_key = "mock_key"
    openrouter_model = "mistralai/devstral-2512:free"
    cohere_api_key = "mock_key"
    cohere_model = "embed-english-v3.0"
    qdrant_url = "http://localhost:6333"
    qdrant_api_key = "mock_key"
    qdrant_collection = "test_collection"
    max_context_tokens = 4000
    top_k_results = 5
    retrieve_score_threshold = 0.5

# Patch settings
import src.config
src.config.settings = MockSettings()

def test_imports():
    """Test that all modules can be imported with mocked settings."""
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

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Structure Test (Mocked Settings)")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("Import Test (with mocked settings)")
    print("=" * 60)

    import_errors = test_imports()

    if import_errors:
        print(f"\n[FAIL] {len(import_errors)} import errors!")
        for err in import_errors:
            print(f"  - {err}")
    else:
        print("\n[OK] All imports successful")

    print("\n" + "=" * 60)
    if not import_errors:
        print("[SUCCESS] Backend structure is valid!")
    else:
        print("[FAIL] Backend has issues")
    print("=" * 60)
