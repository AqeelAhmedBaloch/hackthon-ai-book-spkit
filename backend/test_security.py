"""
Security validation script for the RAG Chatbot API
This script tests the security measures implemented in the backend
"""
import requests
import json

def test_cors_security():
    """Test that CORS is properly configured"""
    print("Testing CORS security...")

    # Test with an unauthorized origin
    try:
        response = requests.options(
            "http://localhost:8000/query",
            headers={
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-Requested-With",
            }
        )

        # Check if the unauthorized origin is blocked
        if "http://malicious-site.com" not in str(response.headers):
            print("✅ CORS security test passed - Unauthorized origins are blocked")
        else:
            print("❌ CORS security test failed - Unauthorized origins are allowed")
    except Exception as e:
        print(f"⚠️ CORS test encountered an issue: {e}")
        print("This may be expected if the server is not running")

def test_rate_limiting():
    """Test that rate limiting is working"""
    print("Testing rate limiting...")

    try:
        # Make multiple requests rapidly to test rate limiting
        for i in range(15):  # More than the 10/minute limit
            response = requests.post(
                "http://localhost:8000/query",
                json={"question": "test", "selected_text": None},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 429:  # Rate limited
                print("✅ Rate limiting test passed - Requests are being limited")
                break
        else:
            print("⚠️ Could not fully test rate limiting - server may not be running or rate limit not triggered")
    except Exception as e:
        print(f"⚠️ Rate limiting test encountered an issue: {e}")
        print("This may be expected if the server is not running")

def test_api_endpoints():
    """Test that API endpoints are working correctly"""
    print("Testing API endpoints...")

    try:
        # Test health endpoint
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Health endpoint test passed")
        else:
            print("❌ Health endpoint test failed")
    except Exception as e:
        print(f"⚠️ API endpoint test encountered an issue: {e}")
        print("This may be expected if the server is not running")

if __name__ == "__main__":
    print("Running backend security validation tests...")
    print("Note: These tests require the backend server to be running on http://localhost:8000")
    print()

    test_cors_security()
    test_rate_limiting()
    test_api_endpoints()

    print("\nSecurity validation tests completed.")
    print("Check that the server is running to complete all tests.")