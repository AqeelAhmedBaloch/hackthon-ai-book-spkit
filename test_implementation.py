"""
Basic test to verify the RAG chatbot implementation
"""
import os

def test_directory_structure():
    """Test that required directories and files exist"""
    print("Testing directory structure...")

    required_dirs = [
        'backend',
        'backend/src',
        'backend/src/models',
        'backend/src/services',
        'backend/src/utils',
    ]

    required_files = [
        'backend/pyproject.toml',
        'backend/src/main.py',
        'backend/src/agent.py',
        'backend/src/ingest.py',
        'backend/src/config.py',
        'backend/.env.example',
        'backend/README.md'
    ]

    all_good = True

    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"[OK] Directory exists: {directory}")
        else:
            print(f"[ERROR] Directory missing: {directory}")
            all_good = False

    for file in required_files:
        if os.path.isfile(file):
            print(f"[OK] File exists: {file}")
        else:
            print(f"[ERROR] File missing: {file}")
            all_good = False

    return all_good

def test_file_contents():
    """Test that key files have expected content"""
    print("\nTesting file contents...")

    # Test main.py has FastAPI import
    with open('backend/src/main.py', 'r') as f:
        main_content = f.read()
        if 'FastAPI' in main_content and 'app = FastAPI' in main_content:
            print("[OK] main.py contains FastAPI application")
        else:
            print("[ERROR] main.py missing FastAPI application")
            return False

    # Test ingest.py has ingestion logic
    with open('backend/src/ingest.py', 'r') as f:
        ingest_content = f.read()
        if 'fetch_sitemap' in ingest_content and 'process_book_content' in ingest_content:
            print("[OK] ingest.py contains ingestion logic")
        else:
            print("[ERROR] ingest.py missing ingestion logic")
            return False

    # Test config.py has environment loading
    with open('backend/src/config.py', 'r') as f:
        config_content = f.read()
        if 'load_dotenv' in config_content and 'COHERE_API_KEY' in config_content:
            print("[OK] config.py contains environment configuration")
        else:
            print("[ERROR] config.py missing environment configuration")
            return False

    return True

if __name__ == "__main__":
    print("Running basic verification of RAG Chatbot implementation...")

    structure_ok = test_directory_structure()
    content_ok = test_file_contents()

    if structure_ok and content_ok:
        print("\n[SUCCESS] All basic checks passed! The RAG Chatbot backend is properly set up.")
        print("\nNext steps:")
        print("1. Set up your environment variables in a .env file")
        print("2. Install dependencies: pip install -e .")
        print("3. Run the ingestion: python -m src.ingest")
        print("4. Start the server: uvicorn src.main:app --reload")
    else:
        print("\n[FAILURE] Some checks failed. Please review the output above.")
        exit(1)