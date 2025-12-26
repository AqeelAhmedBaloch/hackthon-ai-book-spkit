from setuptools import setup, find_packages

setup(
    name="rag-chatbot-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "cohere>=5.0.0",
        "qdrant-client>=1.7.0",
        "anthropic>=0.21.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "trafilatura>=1.6.0",
        "pytest>=7.4.0",
        "pydantic>=2.5.0",
        "tiktoken>=0.5.0"
    ],
    python_requires=">=3.11",
)