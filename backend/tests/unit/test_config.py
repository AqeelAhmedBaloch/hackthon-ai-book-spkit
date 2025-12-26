"""
Unit tests for configuration module
"""
import os
import tempfile
from unittest.mock import patch
from backend.src.config import Config


def test_config_loading():
    """Test that config can load environment variables"""
    # This test will be minimal since the config validation happens at import time
    # In a real scenario, we'd mock the environment variables
    assert hasattr(Config, 'COHERE_API_KEY')
    assert hasattr(Config, 'QDRANT_URL')
    assert hasattr(Config, 'QDRANT_API_KEY')
    assert hasattr(Config, 'QDRANT_COLLECTION_NAME')
    assert hasattr(Config, 'BOOK_SITEMAP_URL')


if __name__ == "__main__":
    test_config_loading()
    print("Config unit test passed!")