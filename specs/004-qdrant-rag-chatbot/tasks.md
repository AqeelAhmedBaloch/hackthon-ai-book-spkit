---
description: "Task list for Enhanced Sitemap Handling in RAG Chatbot for Physical AI & Humanoid Robotics Book"
---

# Tasks: Enhanced Sitemap Handling for RAG Chatbot

**Input**: Sitemap handling requirements - validate content-type, support .xml/.xml.gz formats, handle HTML sitemaps
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

- [X] T001 Update dependencies in backend/pyproject.toml to include gzip and content-type handling libraries if needed
- [X] T002 Create sitemap utility module backend/utils/sitemap_parser.py for enhanced sitemap processing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implement content-type validation logic in backend/utils/sitemap_parser.py
- [X] T004 [P] Implement gzip decompression support for .xml.gz sitemap files in backend/utils/sitemap_parser.py
- [X] T005 [P] Implement HTML sitemap URL extraction logic in backend/utils/sitemap_parser.py
- [X] T006 [P] Implement recursive sitemap index processing in backend/utils/sitemap_parser.py
- [X] T007 Update existing ingestion service to use new sitemap parser in backend/services/ingestion_service.py
- [X] T008 Update existing ingest.py to use new sitemap parser in backend/ingest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Enhanced Sitemap Response Validation (Priority: P1) 🎯 MVP

**Goal**: Implement validation of sitemap response content-type before XML parsing to prevent errors

**Independent Test**: The system correctly identifies the content-type of sitemap responses and validates it before attempting to parse as XML. Invalid content-types are logged and handled gracefully.

### Implementation for User Story 1

- [X] T009 [P] [US1] Add content-type header checking to sitemap response validation in backend/utils/sitemap_parser.py
- [X] T010 [US1] Implement XML content-type detection (application/xml, text/xml) in backend/utils/sitemap_parser.py
- [X] T011 [US1] Add proper error logging when content-type is not XML-appropriate in backend/utils/sitemap_parser.py
- [X] T012 [US1] Create fallback mechanism for content-type mismatches in backend/utils/sitemap_parser.py
- [X] T013 [US1] Update ingestion service to handle content-type validation errors gracefully in backend/services/ingestion_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Support .xml and .xml.gz Sitemap Formats (Priority: P1)

**Goal**: Enable the system to handle both regular XML sitemaps and gzip-compressed XML sitemaps

**Independent Test**: The system successfully processes both .xml and .xml.gz sitemap formats, automatically detecting and decompressing gzip files when needed.

### Implementation for User Story 2

- [X] T014 [P] [US2] Implement automatic detection of gzip-compressed sitemap responses in backend/utils/sitemap_parser.py
- [X] T015 [US2] Add gzip decompression functionality for .xml.gz files in backend/utils/sitemap_parser.py
- [X] T016 [US2] Implement proper content detection based on response headers and content in backend/utils/sitemap_parser.py
- [X] T017 [US2] Add error handling for corrupted gzip files in backend/utils/sitemap_parser.py
- [X] T018 [US2] Update ingestion service to handle both XML and compressed sitemap formats in backend/services/ingestion_service.py
- [X] T019 [US2] Update main ingest.py to handle both XML and compressed sitemap formats in backend/ingest.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - HTML Sitemap URL Extraction (Priority: P1)

**Goal**: When sitemap response is HTML, extract valid sitemap URLs from the page content

**Independent Test**: The system detects HTML responses instead of XML, parses the HTML to find sitemap URLs, and processes them appropriately.

### Implementation for User Story 3

- [X] T020 [P] [US3] Implement HTML response detection logic in backend/utils/sitemap_parser.py
- [X] T021 [US3] Add HTML parsing to extract sitemap URLs using BeautifulSoup in backend/utils/sitemap_parser.py
- [X] T022 [US3] Implement regex-based URL extraction for HTML sitemaps in backend/utils/sitemap_parser.py
- [X] T023 [US3] Add support for extracting sitemap links from HTML <link> tags in backend/utils/sitemap_parser.py
- [X] T024 [US3] Create fallback to HTML parsing when XML parsing fails in backend/utils/sitemap_parser.py
- [X] T025 [US3] Update ingestion service to handle HTML sitemap extraction in backend/services/ingestion_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Enhanced Sitemap Index Support (Priority: P2)

**Goal**: Improve sitemap index processing to handle nested sitemaps and complex sitemap structures

**Independent Test**: The system processes sitemap index files, recursively follows nested sitemaps, and extracts all URLs from the complete sitemap structure.

### Implementation for User Story 4

- [X] T026 [P] [US4] Enhance sitemap index detection and parsing in backend/utils/sitemap_parser.py
- [X] T027 [US4] Implement recursive processing of nested sitemaps in backend/utils/sitemap_parser.py
- [X] T028 [US4] Add rate limiting and timeout handling for recursive sitemap processing in backend/utils/sitemap_parser.py
- [X] T029 [US4] Implement circular reference detection to prevent infinite loops in backend/utils/sitemap_parser.py
- [X] T030 [US4] Update ingestion service to use enhanced sitemap index processing in backend/services/ingestion_service.py

**Checkpoint**: Complete enhanced sitemap functionality ready for testing

---

## Phase 7: Validation & Integration (Priority: P2)

**Goal**: Verify enhanced sitemap functionality works correctly with existing ingestion pipeline

**Independent Test**: All enhanced sitemap features work correctly with the existing ingestion pipeline without breaking current functionality.

### Implementation for Validation & Integration

- [X] T031 [P] [US5] Create unit tests for content-type validation in backend/tests/unit/test_sitemap_parser.py
- [X] T032 [US5] Create unit tests for gzip decompression functionality in backend/tests/unit/test_sitemap_parser.py
- [X] T033 [US5] Create unit tests for HTML sitemap URL extraction in backend/tests/unit/test_sitemap_parser.py
- [X] T034 [US5] Create unit tests for sitemap index processing in backend/tests/unit/test_sitemap_parser.py
- [X] T035 [US5] Perform integration testing with various sitemap formats in backend/tests/integration/
- [X] T036 [US5] Validate backward compatibility with existing sitemap functionality in backend/ingest.py
- [X] T037 [US5] Run end-to-end ingestion test with enhanced sitemap features
- [X] T038 [US5] Verify error handling and logging work correctly for all sitemap scenarios

**Checkpoint**: Complete system validation and readiness for deployment

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T039 [P] Update documentation in backend/README.md to reflect enhanced sitemap capabilities
- [X] T040 Add comprehensive error handling and logging across all sitemap processing functions
- [X] T041 [P] Add input validation and security hardening to sitemap processing
- [X] T042 Add performance monitoring for sitemap processing operations
- [X] T043 Update configuration to support sitemap processing options in backend/config.py
- [X] T044 Run complete system validation with various sitemap types

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
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after US1, US2, US3, and US4 are complete

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
Task: "Add content-type header checking to sitemap response validation"
Task: "Implement XML content-type detection"
Task: "Add proper error logging when content-type is not XML-appropriate"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2 and 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (content-type validation)
4. Complete Phase 4: User Story 2 (gzip support)
5. Complete Phase 5: User Story 3 (HTML extraction)
6. **STOP and VALIDATE**: Test core functionality independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add Validation & Integration → Test independently → Deploy/Demo
7. Add Polish phase → Final validation → Production ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
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