---
id: 2
title: "Backend Tasks for RAG Chatbot"
stage: "tasks"
date_iso: "2025-12-26"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "004-qdrant-rag-chatbot"
branch: "005-rag-chatbot"
user: "user"
command: "/sp.tasks"
labels: ["tasks", "backend", "rag", "qdrant"]
links:
  spec: "specs/004-qdrant-rag-chatbot/spec.md"
  plan: "specs/004-qdrant-rag-chatbot/plan.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files_yaml: |
  - specs/004-qdrant-rag-chatbot/tasks.md
tests_yaml: |
  - "Tasks generated and validated"
  - "Task dependencies mapped"
  - "Parallel execution opportunities identified"
---

# Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Backend-only)

## PROMPT_TEXT

```
/sp.task Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Backend-only)

Scope:
All implementation work must be done inside the backend/ folder only.
No frontend or deployment changes are allowed.

---

T1. Backend Initialization (P1)
- Create backend/ folder at project root
- Initialize Python 3.11 environment using uv
- Create core backend files:
  - main.py
  - agent.py
  - ingest.py
  - config.py
- Configure loading of environment variables from .env only

Output:
- Backend environment activates without errors

---

T2. Sitemap-Based Book Ingestion (P1)
- Fetch sitemap.xml from the published book site
- Parse sitemap and extract all book page URLs
- For each URL:
  - Fetch page HTML
  - Extract main book content (exclude navigation and footer)
- Split extracted text into semantic chunks (300–800 tokens)
- Generate embeddings using Cohere
- Ensure Qdrant collection exists
- Upsert embeddings and payload into Qdrant with fields:
  - text
  - chapter
  - section
  - book_title
  - source_url
- Implement ingest.py as a one-time manual script

Output:
- Qdrant collection contains vectors with metadata (count > 0)

---

T3. RAG Agent Implementation (Agent SDK) (P1)
- Implement RAG agent using an Agent SDK inside agent.py
- For each user query:
  - Generate query embedding
  - Retrieve top-K relevant chunks from Qdrant
  - Build context strictly from retrieved chunks
  - Generate answer only from book content
- Implement exact fallback response when no data is found:
  "This topic is not covered in the book"

Output:
- Agent returns correct answers for covered topics
- Agent returns fallback response for non-covered topics

---

T4. FastAPI Backend API (P1)
- Create FastAPI application in main.py
- Expose /chat endpoint
- Accept input:
  - user question
  - optional selected text
- Return output:
  - answer
  - chapter/section reference
  - source_url (if available)

Output:
- /chat endpoint responds correctly via API testing

---

T5. Validation & Readiness (P2)
- Verify Qdrant data persistence
```

## RESPONSE_TEXT

Generated comprehensive task list for the backend implementation of the RAG chatbot system in specs/004-qdrant-rag-chatbot/tasks.md with the following structure:

1. Phase 1: Setup (project initialization)
2. Phase 2: Foundational (blocking prerequisites)
3. Phase 3: User Story 1 - Ask Questions About Book Content (P1)
4. Phase 4: User Story 2 - Access Contextual Book Information (P2)
5. Phase 5: User Story 3 - Sitemap-Based Book Ingestion (P1)
6. Phase 6: Validation & Readiness (P2)
7. Phase 7: Polish & Cross-Cutting Concerns

The tasks follow the required format with IDs, story labels, and file paths. The implementation strategy focuses on the backend only, with all work contained within the backend/ directory. Parallel execution opportunities are identified, and dependencies are clearly mapped between phases and user stories.

## OUTCOME

The tasks.md file contains 141 specific tasks organized by user story priority, enabling independent implementation and testing of each feature. Tasks are formatted with checkboxes, IDs, and file paths as required. The implementation plan supports the backend-only scope with all components contained within the backend directory structure.