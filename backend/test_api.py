"""
API test script for the RAG Chatbot
"""
import requests
import json
import time

def test_api_endpoints():
    base_url = "http://localhost:8000"

    print("Testing RAG Chatbot API endpoints...")

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Health check: {health_data['status']}")
            print(f"   Services: {health_data['services']}")
        else:
            print(f"   Health check failed with status: {response.status_code}")
    except Exception as e:
        print(f"   Error testing health endpoint: {e}")

    # Test ingest endpoint (if we have content to ingest)
    print("\n2. Testing ingest endpoint...")
    try:
        response = requests.post(f"{base_url}/ingest")
        if response.status_code in [200, 400, 500]:  # Various possible responses
            ingest_data = response.json()
            print(f"   Ingest response: {ingest_data['status']}")
            print(f"   Message: {ingest_data['message']}")
        else:
            print(f"   Ingest failed with status: {response.status_code}")
    except Exception as e:
        print(f"   Error testing ingest endpoint: {e}")

    # Test chat endpoint
    print("\n3. Testing chat endpoint...")
    try:
        chat_payload = {
            "question": "What is this book about?",
            "selected_text": "",
            "context": {}
        }

        response = requests.post(
            f"{base_url}/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(chat_payload)
        )

        if response.status_code == 200:
            chat_data = response.json()
            print(f"   Answer: {chat_data['answer'][:100]}...")
            print(f"   Sources: {len(chat_data['sources'])} source(s) provided")
            print(f"   Timestamp: {chat_data['timestamp']}")
        else:
            print(f"   Chat failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error testing chat endpoint: {e}")

    # Test chat endpoint with selected text
    print("\n4. Testing chat endpoint with selected text...")
    try:
        chat_payload = {
            "question": "Can you explain this concept?",
            "selected_text": "This is some sample text that has been selected by the user",
            "context": {}
        }

        response = requests.post(
            f"{base_url}/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(chat_payload)
        )

        if response.status_code == 200:
            chat_data = response.json()
            print(f"   Answer with selected text: {chat_data['answer'][:100]}...")
            print(f"   Sources: {len(chat_data['sources'])} source(s) provided")
        else:
            print(f"   Chat with selected text failed with status: {response.status_code}")
    except Exception as e:
        print(f"   Error testing chat endpoint with selected text: {e}")

    print("\nAPI testing completed!")

if __name__ == "__main__":
    test_api_endpoints()