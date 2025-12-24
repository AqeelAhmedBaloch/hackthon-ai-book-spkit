"""
Simple load testing script for the RAG Chatbot API
"""
import asyncio
import aiohttp
import time
from typing import List
import json

async def make_request(session: aiohttp.ClientSession, url: str, payload: dict):
    """Make a single request to the chat endpoint"""
    try:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            return {
                'status': response.status,
                'response': result,
                'success': response.status == 200
            }
    except Exception as e:
        return {
            'status': 500,
            'response': str(e),
            'success': False
        }

async def run_load_test(base_url: str, num_requests: int = 10, concurrency: int = 5):
    """Run a load test against the API"""
    url = f"{base_url}/chat"

    # Sample questions for testing
    sample_questions = [
        "What is this book about?",
        "Can you explain AI agents?",
        "What are the key concepts?",
        "How does RAG work?",
        "What is the main topic?"
    ]

    # Prepare payloads
    payloads = []
    for i in range(num_requests):
        payload = {
            "question": sample_questions[i % len(sample_questions)],
            "selected_text": "",
            "context": {}
        }
        payloads.append(payload)

    print(f"Starting load test: {num_requests} requests with {concurrency} concurrent connections")
    print(f"Target URL: {url}")

    start_time = time.time()

    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_request(session, url, payload):
        async with semaphore:
            return await make_request(session, url, payload)

    async with aiohttp.ClientSession() as session:
        # Create tasks
        tasks = [
            bounded_request(session, url, payload)
            for payload in payloads
        ]

        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    # Analyze results
    successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
    failed_requests = num_requests - successful_requests

    print(f"\nLoad Test Results:")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Success rate: {(successful_requests/num_requests)*100:.2f}%")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per request: {total_time/num_requests:.2f} seconds")
    print(f"Requests per second: {num_requests/total_time:.2f}")

    # Check for any exceptions
    exceptions = [r for r in results if isinstance(r, Exception)]
    if exceptions:
        print(f"Exceptions occurred: {len(exceptions)}")
        for i, exc in enumerate(exceptions[:5]):  # Show first 5
            print(f"  Exception {i+1}: {exc}")

    return {
        'total_requests': num_requests,
        'successful_requests': successful_requests,
        'failed_requests': failed_requests,
        'success_rate': successful_requests/num_requests,
        'total_time': total_time,
        'requests_per_second': num_requests/total_time,
        'exceptions': len(exceptions)
    }

async def main():
    """Main function to run the load test"""
    print("RAG Chatbot API Load Testing")
    print("="*50)

    # Test configuration
    base_url = "http://localhost:8000"  # Adjust as needed
    num_requests = 20
    concurrency = 5

    print(f"Test Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Number of requests: {num_requests}")
    print(f"  Concurrency level: {concurrency}")

    # Run the load test
    results = await run_load_test(base_url, num_requests, concurrency)

    print("\nLoad testing completed!")

    # Basic performance assessment
    if results['success_rate'] >= 0.95:
        print("✅ Performance: Good - High success rate")
    elif results['success_rate'] >= 0.80:
        print("⚠️  Performance: Fair - Moderate success rate")
    else:
        print("❌ Performance: Poor - Low success rate")

    if results['requests_per_second'] >= 2:
        print("✅ Throughput: Good - High requests per second")
    elif results['requests_per_second'] >= 1:
        print("⚠️  Throughput: Fair - Moderate requests per second")
    else:
        print("❌ Throughput: Poor - Low requests per second")

if __name__ == "__main__":
    # Install aiohttp if not already installed: pip install aiohttp
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLoad test interrupted by user")
    except Exception as e:
        print(f"Error running load test: {e}")
        print("Make sure you have aiohttp installed: pip install aiohttp")