# Tasks: RAG Book Chatbot Backend

**Input**: Design documents from `/specs/001-rag-book-chatbot/`
**Prerequisites**: spec.md (user stories with priorities), user-provided task context

**Tests**: Tests are not explicitly requested in specification - implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Python backend**: `src/`, `tests/` at repository root
- Tech stack: Python, FastAPI, uv, Qdrant, OpenRouter, Cohere embeddings, Neon PostgreSQL

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure: src/, tests/, .env.example, pyproject.toml
- [X] T002 Initialize Python project with uv and add FastAPI dependencies
- [X] T003 [P] Create .gitignore for Python project (venv, .env, __pycache__, etc.)
- [X] T004 [P] Create README.md with project description and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create environment configuration module in src/config.py for API keys and settings
- [X] T006 [P] Implement Qdrant client initialization in src/vector_db/qdrant_client.py
- [X] T007 [P] Implement OpenRouter client initialization in src/llm/openrouter_client.py
- [X] T008 [P] Implement Cohere embeddings client initialization in src/embeddings/cohere_client.py
- [X] T009 Create data models for Book Content in src/models/book_content.py
- [X] T010 Create data models for Question/Answer in src/models/chat.py
- [X] T011 Configure logging infrastructure in src/utils/logger.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ingest Book Content from Sitemap (Priority: P1) 🎯 MVP

**Goal**: The system automatically discovers and ingests all book pages from a provided sitemap URL

**Independent Test**: Provide a valid sitemap URL and verify that all listed pages are successfully ingested and stored in Qdrant

### Implementation for User Story 1

- [X] T012 [US1] Implement sitemap URL parser in src/ingest/sitemap_parser.py to extract all page URLs
- [X] T013 [US1] Implement page fetcher in src/ingest/page_fetcher.py to retrieve content from URLs
- [X] T014 [US1] Implement text extractor in src/ingest/text_extractor.py to clean and extract meaningful text from HTML
- [X] T015 [US1] Implement sitemap validator in src/ingest/sitemap_validator.py to validate URL is a valid sitemap
- [X] T016 [US1] Implement ingestion coordinator in ingest.py that orchestrates: fetch sitemap → extract URLs → fetch pages → clean text → generate embeddings → store in Qdrant
- [X] T017 [US1] Add error handling for invalid/unreachable sitemap URLs with informative messages
- [X] T018 [US1] Add error handling for page fetch failures with graceful continuation
- [X] T019 [US1] Add deduplication logic for duplicate pages in sitemap
- [X] T020 [US1] Add logging for ingestion progress and errors in ingest.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Ask Questions About the Book (Priority: P1) 🎯 MVP

**Goal**: Users can ask questions about the book's content through a chat interface endpoint

**Independent Test**: Submit variety of questions and verify answers are based solely on book content and relevant

### Implementation for User Story 2

- [X] T021 [US2] Implement query embedding in src/agent/query_embedder.py to convert user questions to vectors
- [X] T022 [US2] Implement Qdrant retriever in src/agent/retriever.py to search for relevant book content
- [X] T023 [US2] Implement answer generator in src/agent/answer_generator.py using OpenRouter LLM
- [X] T024 [US2] Implement RAG agent in agent.py that coordinates: embed query → retrieve context → generate answer → return with source references
- [X] T025 [US2] Implement book-only constraint in agent.py to ensure answers based ONLY on ingested content
- [X] T026 [US2] Add source/reference tracking in agent.py to provide citations for each answer
- [X] T027 [US2] Add handling for questions with no matching content (gracefully indicate not available)
- [X] T028 [US2] Create FastAPI app in main.py with health check endpoint
- [X] T029 [US2] Implement /chat POST endpoint in main.py to connect frontend with RAG agent
- [X] T030 [US2] Add request/response models in src/models/chat.py for /chat endpoint
- [X] T031 [US2] Add input validation for /chat endpoint
- [X] T032 [US2] Add error handling for /chat endpoint (internal errors, timeouts, etc.)
- [X] T033 [US2] Add logging for chat requests and responses in main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently as core MVP

---

## Phase 5: User Story 3 - Handle Multiple Questions in Conversation Context (Priority: P2)

**Goal**: Users can ask follow-up questions that reference previous answers with maintained context

**Independent Test**: Send sequence of related questions and verify system maintains context across conversation

### Implementation for User Story 3

- [ ] T034 [US3] Create Conversation model in src/models/chat.py to store session history
- [ ] T035 [US3] Implement context manager in src/agent/context_manager.py to maintain conversation state
- [ ] T036 [US3] Implement pronoun resolution logic in src/agent/context_manager.py to interpret "it", "that" references
- [ ] T037 [US3] Update agent.py to use conversation context for follow-up questions
- [ ] T038 [US3] Add conversation history to LLM prompt when available
- [ ] T039 [US3] Add context tracking and validation in main.py /chat endpoint
- [ ] T040 [US3] Add logging for context operations in context_manager.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T041 [P] Create comprehensive .env.example with all required API keys and configuration
- [ ] T042 [P] Update README.md with deployment instructions and API endpoint documentation
- [ ] T043 [P] Add comprehensive error messages for all failure scenarios
- [ ] T044 [P] Add performance monitoring/logging for ingestion and query latency
- [ ] T045 Validate SC-001: Test ingestion of 100+ pages completes within 5 minutes
- [ ] T046 Validate SC-002: Test 90%+ relevance on sample questions from book content
- [ ] T047 Validate SC-003: Verify all answers include source references from book
- [ ] T048 Validate SC-004: Measure and optimize response time to <3 seconds average
- [ ] T049 Validate SC-005: Test follow-up questions maintain context 85%+ of time
- [ ] T050 Validate SC-006: Verify system indicates unanswerable questions 95%+ correctly
- [ ] T051 [P] Code review and cleanup for beginner-readability
- [ ] T052 [P] Add inline comments explaining RAG pipeline components
- [ ] T053 [P] Security review: Ensure no secrets in code, proper .env handling
- [ ] T054 Prepare deployment configuration for FastAPI backend

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - P1, MVP scope
- **User Story 2 (Phase 4)**: Depends on Foundational - P1, MVP scope
- **User Story 3 (Phase 5)**: Depends on User Story 2 - P2, builds on chat endpoint
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on US1 (independent feature)
- **User Story 3 (P2)**: Depends on User Story 2 - requires /chat endpoint and conversation models

### Within Each User Story

- Sequential execution within each story phase
- Models and services before endpoints
- Core implementation before error handling and logging
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004)
- All Foundational tasks marked [P] can run in parallel (T006, T007, T008)
- Phase 6 Polish tasks marked [P] can run in parallel (T041, T042, T043, T052)
- User Stories 1 and 2 can be implemented in parallel after Foundational phase

---

## Parallel Example: User Stories 1 & 2

```bash
# After Foundational phase completes, can launch US1 and US2 in parallel:
Task: "Implement sitemap URL parser in src/ingest/sitemap_parser.py"
Task: "Implement query embedding in src/agent/query_embedder.py"

# Models within US1 can run in parallel:
Task: "Implement sitemap URL parser in src/ingest/sitemap_parser.py"
Task: "Implement page fetcher in src/ingest/page_fetcher.py"
Task: "Implement text extractor in src/ingest/text_extractor.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Ingestion)
4. Complete Phase 4: User Story 2 (Chat/Q&A)
5. **STOP and VALIDATE**: Test ingestion + chat independently
6. Deploy/demo if ready (core MVP: ingest book, ask questions)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (ingestion works!)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP complete!)
4. Add User Story 3 → Test independently → Deploy/Demo (conversation context)
5. Polish phase → Final validation against success criteria

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Ingestion pipeline)
   - Developer B: User Story 2 (RAG agent + API)
3. Stories complete and integrate independently
4. Developer A or B: User Story 3 (Conversation context)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4 (Stories 1 & 2)
- User Story 3 is enhancement (P2) but requires Story 2
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at checkpoints to validate story independently
- Success criteria validation in Phase 6 ensures measurable outcomes
