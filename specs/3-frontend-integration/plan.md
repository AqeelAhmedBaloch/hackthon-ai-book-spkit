# Implementation Plan: Frontend Integration

**Branch**: `3-frontend-integration` | **Date**: 2025-12-19 | **Spec**: [link to spec.md](../spec.md)
**Input**: Feature specification from `/specs/3-frontend-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of frontend integration to connect the RAG backend with the Docusaurus book site. This involves adding a chatbot UI component to Docusaurus, connecting frontend requests to existing FastAPI endpoints, passing selected text with user queries, and validating end-to-end functionality. The implementation will enable in-page question answering while preserving existing book content.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript/JavaScript for frontend, Python 3.11 for backend integration
**Primary Dependencies**: React, Docusaurus, Axios/Fetch API, existing RAG backend from Spec-3
**Storage**: Browser local storage for session data (optional)
**Testing**: Jest for unit tests, Cypress for end-to-end tests
**Target Platform**: Web browser (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application frontend integration
**Performance Goals**: <200ms UI response time, <500ms total response time including backend
**Constraints**: Must work with existing Docusaurus site without content modifications, no authentication required
**Scale/Scope**: Single page application components, supporting concurrent users on different book pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-First, Reproducible Development: Feature is fully specified in spec.md before implementation
- ✅ Factual Accuracy and Zero Hallucination: Integration will ensure agent responses are fact-based from book content
- ✅ Clear Structure for Technical Audience: Implementation will follow modular, well-documented approach
- ✅ Full Alignment Between Book Content and Chatbot Knowledge: Integration will connect to existing RAG system
- ✅ Public, Self-Contained Repository: Implementation will be fully contained in public repository
- ✅ Deterministic, Citation-Backed Responses: Integration will display proper citations from agent responses

## Project Structure

### Documentation (this feature)

```text
specs/3-frontend-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
ai_frontend_book/
├── src/
│   ├── components/
│   │   ├── RagChat/
│   │   │   ├── RagChat.tsx          # Main chatbot component
│   │   │   ├── RagChat.module.css   # Chat component styles
│   │   │   ├── ChatInput.tsx        # Input component for questions
│   │   │   ├── ChatMessage.tsx      # Message display component
│   │   │   └── SelectedTextHandler.tsx  # Handles selected text functionality
│   │   └── index.tsx                # Export components
│   ├── pages/
│   └── utils/
│       ├── api-client.ts            # API client for backend communication
│       └── text-selection.ts        # Text selection utilities
├── static/
└── docusaurus.config.js
```

**Structure Decision**: Web application frontend integration structure selected as this feature requires adding React components to the Docusaurus site with API client for backend communication.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |