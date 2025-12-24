"""
Script to start the RAG Chatbot backend server
"""
import subprocess
import sys
import os

def start_server():
    """Start the FastAPI server using uvicorn"""
    print("Starting RAG Chatbot Backend Server...")
    print("Make sure you have set your environment variables in .env file")

    # Change to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Start the server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"  # Enable auto-reload for development
    ]

    print(f"Running command: {' '.join(cmd)}")
    print("Server will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()