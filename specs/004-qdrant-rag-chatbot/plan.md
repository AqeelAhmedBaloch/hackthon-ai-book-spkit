# Implementation Plan: Enhanced Sitemap Source Fetching and Validation

**Branch**: `005-sitemap-enhancement` | **Date**: 2025-12-26 | **Spec**: [specs/004-qdrant-rag-chatbot/spec.md](../004-qdrant-rag-chatbot/spec.md)

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement enhanced sitemap fetching and validation functionality that can handle XML, XML.GZ, and sitemap index formats. The system will validate content-type before parsing, support compressed sitemap files, and extract URLs from HTML responses when needed. This will improve the reliability and robustness of the book content ingestion process.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: requests, xml.etree.ElementTree, gzip, BeautifulSoup4, urllib
**Storage**: In-memory processing for sitemap URLs
**Testing**: pytest
**Target Platform**: Linux server
**Performance Goals**: <5 seconds to fetch and parse typical sitemap
**Constraints**: Must handle various sitemap formats without breaking existing functionality, proper error handling and logging
**Scale/Scope**: Single sitemap source per ingestion run, multiple URLs extracted per sitemap

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the project constitution, this implementation follows the principles of:
- Using secure and robust code practices for external content fetching
- Maintaining clear separation between ingestion and processing components
- Implementing proper error handling and fallback responses
- Ensuring data integrity and proper validation of external sources
- Following security best practices for handling external URLs and content
- Implementing proper validation for input sources and system responses
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
│       ├── html_parser.py
│       └── sitemap_parser.py        # NEW: Enhanced sitemap handling
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
| Multiple utility files | Modularity and maintainability | Single file would be too complex to maintain |
| External dependencies (BeautifulSoup4) | Required for HTML parsing when sitemap is in HTML format | Feature specifically requires HTML parsing capabilities |