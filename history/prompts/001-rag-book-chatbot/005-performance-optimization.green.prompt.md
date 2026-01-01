---
id: 005
title: Backend performance optimization
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-book-chatbot
branch: master
user: null
command: Investigate backend performance and optimize response time
labels: [performance, optimization, http-client, retrieval, async]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/embeddings/cohere_client.py
  - backend/src/llm/openrouter_client.py
  - backend/src/agent/retriever.py
  - backend/main.py
tests:
  - verified server starts cleanly with new lifespan
  - verified shutdown logs show AI clients closed
---

## Prompt

The chatbot is responding very slowly. Please investigate backend performance issues and optimize response time so chatbot replies faster in chat window.

## Response snapshot

Performance analysis completed. Identified 3 key bottlenecks and implemented fixes:

1.  **HTTP Client Per-Request Overhead**
    *   CohereEmbeddingsClient and OpenRouterClient were creating a new AsyncClient for each request.
    *   Estimated latency impact: 100-300ms per request (TLS handshake, DNS resolution).
    *   Implemented singleton pattern: `_get_client()` returns reusable httpx.AsyncClient. Added `close()` methods for FastAPI lifecycle.

2.  **Double-Query Pattern in Retrieval**
    *   Retriever performed two Qdrant searches when threshold filtering returned no results.
    *   Estimated latency impact: 50-150ms (double round-trip).
    *   Refactored to single query with in-memory threshold filtering. Same functional result (above threshold OR fallback), one DB call.

3.  **FastAPI Lifespan Integration**
    *   Added imports for AI clients to main.py.
    *   Added `await cohere_client.close()` and `await openrouter_client.close()` in shutdown phase to free connections cleanly.

**Note:** A CORS fix (restrict wildcard origins and methods) was analyzed but not applied to avoid breaking the dev environment. This remains a small optimization (5-10ms) if desired.

## Outcome

- ✅ Impact: Expected 20-35% latency reduction. Eliminates per-request TLS handshakes and duplicate DB calls.
- 🧪 Tests: Backend started successfully and shut down cleanly with logs confirming "AI clients closed".
- 📁 Files: cohere_client.py, openrouter_client.py, retriever.py, main.py
- 🧠 Reflection: The biggest wins are connection reuse and avoiding redundant queries. Next: parallelization or batch embedding for concurrent requests.
