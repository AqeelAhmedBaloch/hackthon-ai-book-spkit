"""
End-to-end test for the RAG system
This test verifies the complete flow from query to response
"""
import asyncio
import time
from src.shared.models import QueryRequest
from src.rag_agent.agent import RAGAgent
from src.content_ingestion.main import ContentIngestionService
from src.content_ingestion.models import IngestionRequest, IngestionConfig


def test_e2e_functionality():
    """
    Test end-to-end functionality from query to response
    """
    print("Starting end-to-end functionality test...")

    # Initialize the RAG agent
    agent = RAGAgent()

    # Create a test query
    test_query = QueryRequest(
        query="What is the main concept of this book?",
        selected_text=None,
        page_url="test://e2e-test",
        session_id="test-session-123"
    )

    print("Processing test query...")
    start_time = time.time()

    # Process the query
    response = agent.query(test_query)

    processing_time = time.time() - start_time

    print(f"Response received in {processing_time:.2f}s")
    print(f"Response: {response.response[:100]}...")
    print(f"Citations: {len(response.citations)} found")
    print(f"Confidence: {response.confidence}")

    # Verify response has expected elements
    assert response.response is not None, "Response should not be None"
    assert len(response.response) > 0, "Response should not be empty"
    print("✓ Response is not empty")

    # Verify citations are included
    assert response.citations is not None, "Citations should not be None"
    print(f"✓ Citations included: {len(response.citations)} found")

    # Verify processing time is reasonable (under 10 seconds for test)
    assert processing_time < 10.0, f"Processing time should be under 10s, was {processing_time}s"
    print(f"✓ Processing time is acceptable: {processing_time:.2f}s")

    print("End-to-end functionality test completed successfully!")
    return True


def test_selected_text_functionality():
    """
    Test functionality with selected text
    """
    print("\nStarting selected text functionality test...")

    # Initialize the RAG agent
    agent = RAGAgent()

    # Create a test query with selected text
    test_query = QueryRequest(
        query="Explain this concept further",
        selected_text="The main concept of the book is about artificial intelligence and robotics",
        page_url="test://selected-text-test",
        session_id="test-session-456"
    )

    print("Processing test query with selected text...")
    start_time = time.time()

    # Process the query
    response = agent.query(test_query)

    processing_time = time.time() - start_time

    print(f"Response received in {processing_time:.2f}s")
    print(f"Response: {response.response[:100]}...")

    # Verify response has expected elements
    assert response.response is not None, "Response should not be None"
    assert len(response.response) > 0, "Response should not be empty"
    print("✓ Response with selected text is not empty")

    print("Selected text functionality test completed successfully!")
    return True


if __name__ == "__main__":
    try:
        test_e2e_functionality()
        test_selected_text_functionality()
        print("\n✓ All end-to-end tests passed!")
    except Exception as e:
        print(f"\n✗ End-to-end test failed: {e}")
        raise