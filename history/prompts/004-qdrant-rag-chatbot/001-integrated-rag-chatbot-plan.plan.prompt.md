---
id: 1
title: "Integrated RAG Chatbot Plan"
stage: "plan"
date_iso: "2025-12-26"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "004-qdrant-rag-chatbot"
branch: "005-rag-chatbot"
user: "user"
command: "/sp.plan"
labels: ["plan", "rag", "qdrant", "ai-book"]
links:
  spec: "specs/004-qdrant-rag-chatbot/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files_yaml: |
  - specs/004-qdrant-rag-chatbot/plan.md
  - specs/004-qdrant-rag-chatbot/research.md
  - specs/004-qdrant-rag-chatbot/data-model.md
  - specs/004-qdrant-rag-chatbot/quickstart.md
  - specs/004-qdrant-rag-chatbot/contracts/api-contract.md
tests_yaml: |
  - "Plan document created and validated"
  - "Research document completed"
  - "Data model defined"
  - "API contracts documented"
---

# Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Sitemap-based)

## PROMPT_TEXT

```
/sp.plan Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Sitemap-based)

Objective:
Build an embedded RAG chatbot that answers questions strictly from book content stored in Qdrant.

---

Phase 1: Backend Foundation
- Create backend/ folder at project root
- Initialize Python 3.11 environment using uv
- Add core files:
  - main.py
  - agent.py
  - ingest.py
  - config.py
- Load all settings from .env only

Checkpoint:
- Backend environment activates without errors

---

Phase 2: Book Ingestion (Sitemap → Qdrant)
- Fetch sitemap.xml from the published book site
- Extract all book page URLs from sitemap
- For each URL:
  - Fetch page content
  - Extract main book text (ignore nav/footer)
- Split content into 300–800 token chunks
- Generate embeddings using Cohere
- Ensure Qdrant collection exists
- Upsert embeddings + payload into Qdrant:
  - text
  - chapter / section
  - book_title
  - source_url
- Run ingest.py as a one-time manual process

Checkpoint:
- Qdrant collection contains vectors (count > 0) with metadata

---

Phase 3: RAG Agent (Agent SDK)
- Implement agent using Agent SDK
- For each user query:
  - Generate query embedding
  - Retrieve top-K chunks from Qdrant
  - Build context strictly from retrieved chunks
  - Generate answer from book content only
- If no relevant data is found, return exactly:
  "This topic is not covered in the book"

Checkpoint:
- Agent returns correct answers for known topics
- Returns fallback response for unknown topics

---

Phase 4: FastAPI Integration
- Create FastAPI app
- Expose /chat endpoint
- Input:
  - user question
  - optional selected text
- Output:
  - answer
  - chapter/section references
  - source_url (if available)

Checkpoint:
- /chat endpoint responds correctly via API test

---

Phase 5: Frontend Connection
- Connect existing chat window to /chat endpoint
- Display answers and references inside book UI

Checkpoint:
- Chatbot works inside the book without page reload

---

Completion Criteria:
- Book content fully indexed in Qdrant
- A
```

## RESPONSE_TEXT

Created comprehensive implementation plan for the RAG chatbot system with the following artifacts:

1. Plan document (plan.md) - Technical architecture and project structure
2. Research document (research.md) - Technology decisions and rationale
3. Data model (data-model.md) - Entity definitions and relationships
4. Quickstart guide (quickstart.md) - Setup and running instructions
5. API contracts (contracts/api-contract.md) - API specification

The plan defines a web application structure with a dedicated backend for RAG processing, using Python 3.11, FastAPI, Cohere, Qdrant, and Anthropic Agent SDK. It addresses all phases from the prompt: backend foundation, book ingestion from sitemap, RAG agent implementation, FastAPI integration, and frontend connection.

## OUTCOME

The implementation plan is complete with all required documentation artifacts. The system architecture supports sitemap-based content ingestion, vector storage in Qdrant, and a RAG agent that strictly uses book content for responses. The API contract defines the /chat endpoint with proper request/response models and validation rules.