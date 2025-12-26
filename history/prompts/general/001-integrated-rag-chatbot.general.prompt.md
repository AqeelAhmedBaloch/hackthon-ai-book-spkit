---
id: 1
title: "Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book"
stage: "spec"
date_iso: "2025-12-26"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "master"
user: "user"
command: "/sp.specify"
labels: ["spec", "rag", "qdrant", "ai-book"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files_yaml: |
  - specs/004-qdrant-rag-chatbot/spec.md
  - specs/004-qdrant-rag-chatbot/checklists/requirements.md
tests_yaml: |
  - "Specification validation completed"
  - "Quality checklist created and validated"
---

# Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book

## PROMPT_TEXT

```
/sp.specify Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Qdrant-Backed)

Target audience:
- Readers of the published textbook
- Students and professionals learning Physical AI and Humanoid Robotics

Focus:
- Answering questions strictly from the book content using RAG
- Persisting all book embeddings in Qdrant Cloud
- Agent SDK must read answers only from Qdrant-stored data

Core requirement (MANDATORY):
- All book content MUST be embedded and SAVED into Qdrant Cloud
- The RAG agent MUST read context ONLY from Qdrant
- No in-memory or temporary storage is allowed for book data

System architecture:
- Frontend: Embedded chat window in the book UI
- Backend: FastAPI
- RAG Agent: Python Agent implemented using Agent SDK
- Embeddings: Cohere
- Vector Database: Qdrant Cloud (Free Tier)

Environment configuration (MUST be used exactly):
- COHERE_API_KEY loaded from .env
- QDRANT_URL loaded from .env
- QDRANT_API_KEY loaded from .env
- QDRANT_COLLECTION_NAME loaded from .env

Data ingestion requirements (CRITICAL):
- ingest.py MUST:
  - Load Qdrant configuration from .env
  - Ensure the Qdrant collection exists (create if missing)
  - Split book content into 300–800 token chunks
  - Generate embeddings using Cohere
  - UPSERT embeddings into Qdrant with payload:
    - text
    - chapter
    - section
    - book_title
    - source or page reference
- ingest.py is a one-time script and MUST NOT auto-run

Agent behavior requirements:
- Agent SDK MUST query Qdrant for every user question
- Agent MUST NOT answer if Qdrant returns no relevant vectors
- If no relevant data is found in Qdrant, respond exactly:
  "This topic is not covered in the book"

Constraints:
- No external knowledge outside Qdrant-stored book data
- No hallucinated answers
- No hardcoded API keys or URLs
- Backend must be isolated from frontend

Not building:
- Web search or browsing
- Model training or fine-tuning
- Authentication or analytics
```

## RESPONSE_TEXT

Created specification for Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Qdrant-Backed) in specs/004-qdrant-rag-chatbot/spec.md with the following key elements:

- User scenarios for asking questions about book content, accessing contextual information, and using the embedded chat interface
- Functional requirements focused on embedding book content, retrieving relevant context, and ensuring answers come only from book data
- Success criteria with measurable outcomes for response accuracy, time, and system behavior
- Technology-agnostic approach removing implementation details while preserving functional requirements
- Quality checklist validation confirming spec completeness

## OUTCOME

Specification successfully created and validated. The spec defines a RAG chatbot system that allows readers to ask questions about Physical AI & Humanoid Robotics book content, with responses sourced only from the book data stored in a vector database. The system ensures no hallucinated answers and provides proper attribution to book sections.