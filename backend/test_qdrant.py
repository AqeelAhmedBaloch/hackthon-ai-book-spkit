#!/usr/bin/env python3
"""
Test script to understand Qdrant query_points result structure
"""
from agent import RAGAgent
import asyncio

def test_qdrant_structure():
    print("Initializing RAG Agent...")
    agent = RAGAgent()

    print("Testing query with a simple question...")
    try:
        # Use the internal method to see the raw Qdrant results
        query_embedding = agent.embed_text("What is this book about?")
        raw_results = agent.qdrant_client.query_points(
            collection_name=agent.collection_name,
            query=query_embedding,
            limit=2
        )

        print(f"Raw results type: {type(raw_results)}")
        print(f"Has points attribute: {hasattr(raw_results, 'points')}")

        if hasattr(raw_results, 'points'):
            print(f"Number of points: {len(raw_results.points)}")
            if raw_results.points:
                first_point = raw_results.points[0]
                print(f"First point type: {type(first_point)}")
                print(f"First point attributes: {dir(first_point)}")
                print(f"First point payload: {first_point.payload}")
                print(f"First point payload type: {type(first_point.payload)}")
                print(f"First point score: {getattr(first_point, 'score', 'N/A')}")

        # Now test the regular retrieval
        results = agent.retrieve_relevant_content("What is this book about?", limit=2)
        print(f"\nProcessed results: Retrieved {len(results)} results")
        if results:
            print("First processed result structure:")
            print(f"  Content: {results[0].get('content', 'N/A')[:100]}...")
            print(f"  Score: {results[0].get('score', 'N/A')}")
            print(f"  Metadata keys: {list(results[0].get('metadata', {}).keys())}")
            print(f"  Full metadata: {results[0].get('metadata', {})}")
        else:
            print("No processed results found")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qdrant_structure()