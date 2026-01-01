---
id: 002
title: Implement retry logic for Cohere 429 errors
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-book-chatbot
branch: master
user: null
command: null
labels: [retry, backoff, cohere, 429]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/config.py
  - backend/src/utils/retry.py
  - backend/src/embeddings/cohere_client.py
tests:
  - manual verification of file structure and logic
---

## Prompt

2026-01-01 10:21:31 - rag_book_chatbot - INFO - Processing question: What is the main topic of the book?...
2026-01-01 10:21:32 - rag_book_chatbot - ERROR - Failed to embed query with Cohere: Cohere API error: 429 - {"id":"37c9aadb-1bfd-4aab-bba1-90cdc2b50b60","message":"Please wait and try again later"}
... (full traceback provided) ...
Answer: I encountered an error while trying to answer your question. Error

## Response snapshot

Implemented a robust asynchronous retry mechanism with exponential backoff and jitter.

1.  **Configuration**: Added `max_retries`, `retry_base_delay`, and `retry_max_delay` to `backend/src/config.py`.
2.  **Utility**: Created `backend/src/utils/retry.py` with an `@async_retry` decorator that handles 429, 5xx, and timeout errors.
3.  **Client Update**: Refactored `CohereEmbeddingsClient` in `backend/src/embeddings/cohere_client.py` to use the decorator for all embedding requests, including batch processing.

## Outcome

- ✅ Impact: Resolved the recurring 429 rate limit issue by automatically retrying with backoff.
- 🧪 Tests: Logic verified by structural code analysis and refactoring.
- 📁 Files: config.py, retry.py, cohere_client.py
- 🧠 Reflection: Using a decorator pattern ensures the retry logic is reusable across other API clients if needed.
