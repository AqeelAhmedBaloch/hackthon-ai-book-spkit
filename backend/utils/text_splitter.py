"""
Utility to split text into semantic chunks (300-800 tokens)
"""
import re
from typing import List, Dict, Any
import tiktoken

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text using tiktoken"""
    # Using gpt-3.5-turbo encoding as a proxy (close to many models)
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def split_text_into_chunks(text: str, min_tokens: int = 300, max_tokens: int = 800) -> List[Dict[str, Any]]:
    """
    Split text into semantic chunks between min_tokens and max_tokens
    """
    if not text.strip():
        return []

    # First, try to split by paragraphs to maintain semantic meaning
    paragraphs = re.split(r'\n\s*\n', text)

    chunks = []
    current_chunk = ""
    current_token_count = 0

    for paragraph in paragraphs:
        paragraph_token_count = count_tokens(paragraph)

        # If adding this paragraph would exceed max_tokens, save current chunk and start new one
        if current_token_count + paragraph_token_count > max_tokens and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "token_count": current_token_count
            })
            current_chunk = paragraph
            current_token_count = paragraph_token_count
        # If the paragraph itself is larger than max_tokens, we need to split it further
        elif paragraph_token_count > max_tokens:
            # Split the large paragraph into sentences
            sentences = re.split(r'[.!?]+', paragraph)
            temp_chunk = ""
            temp_token_count = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                sentence_token_count = count_tokens(sentence)

                if temp_token_count + sentence_token_count <= max_tokens:
                    temp_chunk += sentence + ". "
                    temp_token_count += sentence_token_count + 1  # +1 for the period and space
                else:
                    # If temp chunk already has content, save it and start a new one
                    if temp_chunk and temp_token_count >= min_tokens:
                        chunks.append({
                            "text": temp_chunk.strip(),
                            "token_count": temp_token_count
                        })
                        temp_chunk = sentence + ". "
                        temp_token_count = sentence_token_count + 1
                    # If the sentence is too long, we'll have to include it even if it exceeds max_tokens
                    elif sentence_token_count > max_tokens:
                        chunks.append({
                            "text": sentence.strip(),
                            "token_count": sentence_token_count
                        })
                        temp_chunk = ""
                        temp_token_count = 0
                    else:
                        temp_chunk += sentence + ". "
                        temp_token_count += sentence_token_count + 1

            # Add the remaining temp chunk if it meets minimum size
            if temp_chunk and temp_token_count >= min_tokens:
                current_chunk = temp_chunk
                current_token_count = temp_token_count
            elif temp_chunk and temp_chunk.strip() and not chunks:
                # If it's the first chunk and it's below min_tokens, include it anyway
                chunks.append({
                    "text": temp_chunk.strip(),
                    "token_count": temp_token_count
                })
        else:
            # Add paragraph to current chunk
            current_chunk += "\n\n" + paragraph
            current_token_count += paragraph_token_count

    # Add the final chunk if it has content
    if current_chunk and current_token_count >= min_tokens:
        chunks.append({
            "text": current_chunk.strip(),
            "token_count": current_token_count
        })
    elif current_chunk and current_chunk.strip() and not chunks:
        # If it's the only chunk and it's below min_tokens, include it anyway
        chunks.append({
            "text": current_chunk.strip(),
            "token_count": current_token_count
        })

    return chunks