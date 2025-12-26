# Implementation Plan: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Sitemap-based)

**Branch**: `005-rag-chatbot` | **Date**: 2025-12-26 | **Spec**: [specs/004-qdrant-rag-chatbot/spec.md](../004-qdrant-rag-chatbot/spec.md)

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an embedded RAG chatbot that answers questions strictly from book content stored in Qdrant. The system will use sitemap-based ingestion to extract book content, create vector embeddings using Cohere, store them in Qdrant, and provide a FastAPI backend with an Agent SDK-based RAG system that returns answers sourced only from the book content.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Anthropic Agent SDK, Cohere, Qdrant, uv
**Storage**: Qdrant Cloud vector database
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: web
**Performance Goals**: <10 seconds response time for user queries
**Constraints**: No external knowledge beyond book content, no hallucinated answers, proper attribution to book sections
**Scale/Scope**: Single book content, multiple concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the project constitution, this implementation follows the principles of:
- Using secure environment variables for configuration (COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME)
- Maintaining clear separation between frontend and backend components
- Implementing proper error handling and fallback responses ("This topic is not covered in the book")
- Ensuring data integrity and source attribution with chapter/section references
- Following security best practices for API keys and sensitive data
- Validating that responses are sourced only from book content with no hallucinated answers
- Implementing proper validation for user inputs and system responses
- Ensuring proper logging and monitoring practices

## Project Structure

### Documentation (this feature)

```text
specs/004-qdrant-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py
│   ├── agent.py
│   ├── ingest.py
│   ├── config.py
│   ├── models/
│   │   ├── book_content.py
│   │   └── query.py
│   ├── services/
│   │   ├── ingestion_service.py
│   │   ├── embedding_service.py
│   │   ├── qdrant_service.py
│   │   └── rag_service.py
│   └── utils/
│       ├── text_splitter.py
│       └── html_parser.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── .env.example
├── pyproject.toml
└── README.md
```

**Structure Decision**: Web application structure with dedicated backend for RAG processing and API endpoints, following the requirement for separation between frontend and backend components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple service files | Modularity and maintainability | Single file would be too complex to maintain |
| External dependencies (Cohere, Qdrant) | Required by feature specification | Feature specifically requires these technologies |