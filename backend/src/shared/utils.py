import hashlib
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import tiktoken


def hash_content(content: str) -> str:
    """Generate a hash for content to avoid duplicates"""
    return hashlib.md5(content.encode()).hexdigest()


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of specified size with overlap
    """
    if not text:
        return []

    # Use tiktoken to count tokens more accurately
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)

    chunks = []
    start_idx = 0

    while start_idx < len(tokens):
        end_idx = start_idx + chunk_size
        chunk_tokens = tokens[start_idx:end_idx]

        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Move start index by chunk_size - overlap to create overlap
        start_idx = end_idx - overlap if end_idx < len(tokens) else len(tokens)

    # If the last chunk is too small and not the only chunk, merge it with the previous one
    if len(chunks) > 1 and len(chunks[-1]) < chunk_size // 4:
        chunks[-2] += " " + chunks[-1]
        chunks = chunks[:-1]

    return chunks


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger with consistent formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers to the same logger
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def timing_decorator(func):
    """Decorator to time function execution"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"{func.__name__} executed in {execution_time:.2f} ms")
        return result
    return wrapper


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate a simple similarity score between two texts
    This is a basic implementation - in practice, you'd use vector similarity
    """
    if not text1 or not text2:
        return 0.0

    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return ""

    # Remove null bytes and other potentially harmful characters
    sanitized = text.replace('\x00', '')

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def merge_metadata(meta1: Optional[Dict[str, Any]], meta2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge two metadata dictionaries"""
    if not meta1:
        return meta2 or {}
    if not meta2:
        return meta1
    return {**meta1, **meta2}


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from a text string"""
    import re
    number_pattern = r'-?\d+\.?\d*'
    matches = re.findall(number_pattern, text)
    numbers = []
    for match in matches:
        try:
            numbers.append(float(match))
        except ValueError:
            continue
    return numbers