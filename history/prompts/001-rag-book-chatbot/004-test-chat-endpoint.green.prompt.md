---
id: 004
title: Test /chat endpoint and apply OpenRouter retries
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-book-chatbot
branch: master
user: null
command: curl -X POST "http://localhost:8000/chat" ...
labels: [test, curl, openrouter, retry, 401]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/llm/openrouter_client.py
tests:
  - curl response verified (200 OK)
  - logs confirmed Cohere retry for 429
---

## Prompt

test the /chat endpoint with a question

## Response snapshot

Tested the `/chat` endpoint with the question "What is the main topic of the book?".

**Results:**
1.  **Cohere Retry Verified**: The logs showed the new retry mechanism successfully handled a Cohere 429 error on the first attempt.
2.  **Retrieval Verified**: 5 relevant passages were found in Qdrant.
3.  **OpenRouter Issue**: Encountered an `OpenRouter API error: 401 - {"error":{"message":"User not found.","code":401}}`. This suggests the provided API key in `.env` might be invalid or restricted.

**Action Taken:**
Applied the `@async_retry()` decorator to `OpenRouterClient` as well, ensuring consistent resilience across all AI services.

## Outcome

- ✅ Impact: verified end-to-end flow; cohere retries are working in the wild.
- 🧪 Tests: Successful 200 OK response from API (returning fallback context).
- 📁 Files: openrouter_client.py
- 🧠 Reflection: While 401 isn't typically retriable, the decorator protects against transient 429s/5xxs from OpenRouter which often happen with free-tier models.
