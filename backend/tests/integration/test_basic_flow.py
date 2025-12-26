"""
Basic integration test for the RAG chatbot system
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_basic_imports():
    """Test that all core modules can be imported without errors"""
    try:
        # Test main components
        from backend.src.main import app
        from backend.src.agent import RAGAgent
        from backend.src.ingest import BookIngestor
        from backend.src.services.rag_service import RAGService
        from backend.src.services.qdrant_service import QdrantService
        from backend.src.services.embedding_service import EmbeddingService
        from backend.src.models.query import QueryRequest, QueryResponse
        from backend.src.models.book_content import BookContent

        print("All modules imported successfully")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False


def test_directory_structure():
    """Test that required directories exist"""
    required_dirs = [
        'backend/src/models',
        'backend/src/services',
        'backend/src/utils',
        'backend/tests/unit',
        'backend/tests/integration'
    ]

    all_exist = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"Directory exists: {directory}")
        else:
            print(f"Directory missing: {directory}")
            all_exist = False

    return all_exist


if __name__ == "__main__":
    print("Running basic integration tests...")

    imports_ok = test_basic_imports()
    structure_ok = test_directory_structure()

    if imports_ok and structure_ok:
        print("\nAll integration tests passed!")
    else:
        print("\nSome integration tests failed!")
        exit(1)