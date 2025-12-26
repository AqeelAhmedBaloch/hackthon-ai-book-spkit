---
description: "Task list for Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book"
---

# Tasks: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Backend-only)

**Input**: Design documents from `/specs/004-qdrant-rag-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend only**: All files in `backend/` directory

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend/ directory at project root
- [X] T002 Initialize Python 3.11 project with FastAPI, Cohere, Qdrant, Agent SDK dependencies in backend/pyproject.toml
- [X] T003 [P] Create core backend files: main.py, agent.py, ingest.py, config.py in backend/
- [X] T004 Create .env.example file with required environment variables in backend/
- [X] T005 Create directory structure: backend/{models,services,utils}

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement config.py to load environment variables from .env in backend/config.py
- [X] T007 [P] Create BookContent, UserQuery, and Response models in backend/models/
- [X] T008 [P] Create Qdrant service to handle vector database operations in backend/services/qdrant_service.py
- [X] T009 [P] Create embedding service using Cohere in backend/services/embedding_service.py
- [X] T101 Create text splitter utility for 300-800 token chunks in backend/utils/text_splitter.py
- [X] T102 Create HTML parser utility to extract book content in backend/utils/html_parser.py
- [X] T103 Setup FastAPI application structure in backend/main.py
- [X] T104 [P] Create ingestion service framework in backend/services/ingestion_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ask Questions About Book Content (Priority: P1) 🎯 MVP

**Goal**: Enable users to ask questions about book content and receive accurate answers based solely on the book content

**Independent Test**: The user can ask a question about a specific concept in the book and receive an accurate answer that is sourced from the book content. If the topic isn't covered in the book, the system responds with "This topic is not covered in the book".

### Implementation for User Story 1

- [X] T105 [P] [US1] Implement RAG service in backend/services/rag_service.py
- [X] T106 [US1] Implement agent.py using Agent SDK to process queries
- [X] T107 [US1] Create POST /chat endpoint in backend/main.py
- [X] T108 [US1] Implement query validation logic for question field
- [X] T109 [US1] Implement fallback response logic: "This topic is not covered in the book"
- [X] T110 [US1] Add proper attribution to book chapters/sections in responses
- [X] T111 [US1] Add response time validation (under 10 seconds)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Access Contextual Book Information (Priority: P2)

**Goal**: Enable users to get detailed information about specific chapters, sections, or topics from the book with proper attribution

**Independent Test**: The user can ask for specific chapter information or detailed explanations of concepts and receive responses that include proper attribution to book sections and page references.

### Implementation for User Story 2

- [X] T112 [P] [US2] Enhance RAG service to retrieve specific chapter/section content
- [X] T113 [US2] Add chapter and section reference extraction to response formatting
- [X] T114 [US2] Implement query processing for specific book sections
- [X] T115 [US2] Add source URL attribution to responses
- [X] T116 [US2] Validate that responses are properly attributed to book content

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Sitemap-Based Book Ingestion (Priority: P1)

**Goal**: Implement ingestion system that fetches book content from sitemap.xml, processes it, and stores in Qdrant

**Independent Test**: The ingestion process successfully processes all book content into appropriately sized chunks (300-800 tokens) and stores them in the vector database with required metadata.

### Implementation for User Story 3

- [X] T117 [P] [US3] Implement sitemap parsing to extract book page URLs in backend/services/ingestion_service.py
- [X] T118 [US3] Add HTTP client to fetch book page content from URLs
- [X] T119 [US3] Implement content extraction to get main book text (exclude navigation/footer)
- [X] T120 [US3] Integrate text splitter to create 300-800 token chunks
- [X] T121 [US3] Generate embeddings using Cohere service for each chunk
- [X] T122 [US3] Ensure Qdrant collection exists (create if missing)
- [X] T123 [US3] Implement upsert of embeddings with payload (text, chapter, section, book_title, source_url) into Qdrant
- [X] T124 [US3] Create command-line interface for ingest.py to run as one-time manual script
- [X] T125 [US3] Add validation that Qdrant collection contains vectors with metadata (count > 0)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Validation & Readiness (Priority: P2)

**Goal**: Verify system functionality and data persistence

**Independent Test**: Qdrant data persistence is verified and system meets all success criteria.

### Implementation for Validation & Readiness

- [X] T126 [P] [US4] Verify Qdrant data persistence and content integrity
- [X] T127 [US4] Test that 95% of valid questions return relevant answers sourced from book
- [X] T128 [US4] Validate that 100% of non-covered topics return exact fallback response
- [X] T129 [US4] Verify all required metadata is stored in Qdrant (text, chapter, section, book_title, source)
- [X] T130 [US4] Run end-to-end integration tests
- [X] T131 [US4] Validate zero hallucinated answers during testing scenarios
- [X] T132 [US4] Performance test to ensure responses within 10 seconds
- [X] T133 [US4] Run quickstart.md validation steps

**Checkpoint**: Complete system validation and readiness for deployment

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T134 [P] Documentation updates in backend/README.md
- [X] T135 Error handling and logging implementation across all services
- [X] T136 Input validation and security hardening
- [X] T137 [P] Add unit tests in backend/tests/unit/
- [X] T138 Add integration tests in backend/tests/integration/
- [X] T139 Performance optimization across all services
- [X] T140 Security validation and hardening
- [X] T141 Run complete system validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 components
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after US1, US2, and US3 are complete

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1, 2, and 3 can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all components for User Story 1 together:
Task: "Implement RAG service in backend/services/rag_service.py"
Task: "Implement agent.py using Agent SDK to process queries"
Task: "Create POST /chat endpoint in backend/main.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. Complete Phase 5: User Story 3 (ingestion)
5. **STOP and VALIDATE**: Test core functionality independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test independently → Deploy/Demo
4. Add User Story 2 → Test independently → Deploy/Demo
5. Add Validation & Readiness → Test independently → Deploy/Demo
6. Add Polish phase → Final validation → Production ready
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 3 (ingestion)
   - Developer C: User Story 2
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence