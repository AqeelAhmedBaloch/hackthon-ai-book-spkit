# Feature Specification: URL Ingestion Pipeline for Book Content

**Feature Branch**: `008-url-ingestion-pipeline`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "Content URL Resolution Clarification

- Sitemap URLs may include the site root or non-content pages
- The ingestion pipeline MUST:
  - Identify actual book content URLs (e.g. /docs/*)
  - Skip base site URLs that do not contain readable book content
  - Only ingest pages that return valid HTML with extractable main content
- A 404 response MUST be treated as a skip, not a failure
- Pages that produce no extractable content MUST NOT be counted as ingested"

## Clarifications

### Session 2025-12-27

- Q: How should URL patterns be defined and managed? → A: Define specific URL patterns (e.g., /docs/*, /book/*) in a configuration file that can be customized per deployment
- Q: What are the performance requirements for URL processing? → A: Process up to 1000 URLs per minute with 95% success rate for valid content
- Q: What security measures are needed for URL processing? → A: Basic validation and rate limiting to prevent abuse when processing external URLs

Target audience:
- AI/Robotics students with basic Python knowledge
- Developers working on book content ingestion systems

Focus:
- Processing sitemap URLs to identify valid book content
- Filtering out non-content pages
- Extracting readable content from valid book pages
- Proper error handling for invalid URLs and content

Core requirement (MANDATORY):
- The ingestion pipeline MUST identify actual book content URLs from sitemap data
- The system MUST skip base site URLs that do not contain readable book content
- The system MUST only ingest pages that return valid HTML with extractable main content
- A 404 response MUST be treated as a skip, not a failure
- Pages that produce no extractable content MUST NOT be counted as ingested

System architecture:
- URL Processor: Handles sitemap parsing and URL filtering
- Content Extractor: Extracts main content from valid pages
- Validation Layer: Checks for valid HTML and extractable content
- Error Handler: Properly handles 404s and other errors

Environment configuration:
- Configuration loaded from .env as needed for API keys or special settings

Data ingestion requirements (CRITICAL):
- Process.py MUST:
  - Parse sitemap URLs to identify potential book content
  - Filter URLs to identify actual book content (e.g. /docs/*)
  - Skip base site URLs that do not contain readable book content
  - Validate that pages return valid HTML with extractable main content
  - Handle 404 responses by skipping the URL (not failing)
  - Skip pages that produce no extractable content
  - Track ingestion statistics accurately (only count actual ingested content)

Constraints:
- Must not fail on 404 responses (should skip instead)
- Must not count non-extractable content as ingested
- Must properly identify book content URLs vs. non-content pages
- URL patterns must be defined in configuration file (no hardcoded patterns)
- Must process up to 1000 URLs per minute with 95% success rate for valid content
- Must implement basic validation and rate limiting to prevent abuse when processing external URLs

Not building:
- Full web crawling functionality beyond sitemap processing
- Content transformation beyond extraction
- Complex error recovery beyond skipping invalid URLs

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Process Sitemap URLs for Book Content (Priority: P1)

A developer working on the AI-native textbook needs to process sitemap URLs to identify and extract actual book content while filtering out non-content pages. The system processes the sitemap and ingests only valid book content pages, skipping non-content pages and handling errors appropriately.

**Why this priority**: This is the core functionality needed to build a reliable ingestion pipeline that can distinguish between actual book content and other site pages.

**Independent Test**: The system can process a sitemap with mixed content URLs and non-content URLs, correctly identifying and ingesting only the actual book content while skipping non-content pages.

**Acceptance Scenarios**:

1. **Given** a sitemap containing both book content URLs (e.g. /docs/*) and non-content URLs, **When** the ingestion pipeline processes the sitemap, **Then** it correctly identifies and processes only the book content URLs
2. **Given** a sitemap with mixed URLs, **When** the pipeline encounters non-content pages, **Then** it skips these pages without failing
3. **Given** a sitemap with valid book content URLs, **When** the pipeline processes these URLs, **Then** it successfully extracts content from them

---

### User Story 2 - Handle Invalid URLs and Content (Priority: P2)

A developer needs the ingestion pipeline to properly handle invalid URLs such as 404 responses and pages with no extractable content. The system should skip these URLs rather than failing the entire ingestion process.

**Why this priority**: Robust error handling is essential for a reliable ingestion pipeline that can handle real-world sitemap data with some invalid or broken URLs.

**Independent Test**: The system can process a sitemap containing 404 URLs and contentless pages, skipping these appropriately without failing the overall process.

**Acceptance Scenarios**:

1. **Given** a sitemap containing 404 URLs, **When** the ingestion pipeline processes these URLs, **Then** it treats them as skips rather than failures
2. **Given** a sitemap containing pages with no extractable content, **When** the pipeline processes these pages, **Then** it skips them and does not count them as ingested
3. **Given** a mixed sitemap with valid and invalid URLs, **When** the pipeline processes it, **Then** it continues processing valid URLs even when encountering invalid ones

---

### User Story 3 - Track Accurate Ingestion Statistics (Priority: P3)

A developer needs to track accurate statistics about the ingestion process, counting only pages with extractable content as successfully ingested, not all attempted URLs.

**Why this priority**: Accurate metrics are important for monitoring the health and effectiveness of the ingestion pipeline.

**Independent Test**: The system maintains accurate counts of actual ingested content versus attempted URLs, providing reliable statistics for monitoring.

**Acceptance Scenarios**:

1. **Given** an ingestion process with mixed results, **When** statistics are calculated, **Then** only pages with extractable content are counted as ingested
2. **Given** pages that return 404 responses, **When** statistics are calculated, **Then** these are not counted as ingested content
3. **Given** pages with no extractable content, **When** statistics are calculated, **Then** these are not counted as ingested content

---

### Edge Cases

- What happens when a URL redirects to a non-content page?
- How does the system handle URLs that return valid HTTP status but with empty or malformed HTML?
- What if the sitemap itself is malformed or contains invalid URLs?
- How does the system handle extremely large sitemaps?
- What happens when content extraction fails due to HTML parsing errors?
- How does the system handle rate limiting from the source server?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse sitemap URLs to identify potential book content pages
- **FR-002**: System MUST filter URLs to identify actual book content (e.g. /docs/*) vs. non-content pages
- **FR-003**: System MUST skip base site URLs that do not contain readable book content
- **FR-004**: System MUST validate that pages return valid HTML with extractable main content
- **FR-005**: System MUST handle 404 responses by skipping the URL, not failing the process
- **FR-006**: System MUST skip pages that produce no extractable content
- **FR-007**: System MUST NOT count non-extractable content as ingested
- **FR-008**: System MUST track accurate ingestion statistics (only count actual ingested content)
- **FR-009**: System MUST provide configuration options for content URL patterns
- **FR-010**: System MUST implement proper error handling and logging
- **FR-011**: System MUST be resilient to invalid or malformed sitemap data
- **FR-012**: System MUST provide clear status updates during the ingestion process
- **FR-013**: System MUST process up to 1000 URLs per minute with 95% success rate for valid content
- **FR-014**: System MUST implement basic validation and rate limiting to prevent abuse when processing external URLs

### Key Entities

- **Sitemap URLs**: The URLs extracted from the sitemap that need to be processed for content
- **Book Content Pages**: Valid pages that contain actual book content (e.g. /docs/* paths)
- **Non-Content Pages**: Pages that do not contain readable book content and should be skipped
- **Content Extractor**: Component responsible for extracting main content from valid HTML pages
- **Ingestion Statistics**: Metrics tracking successful vs. skipped content during the process

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of actual book content URLs from sitemaps are correctly identified and processed
- **SC-002**: 100% of 404 responses are handled as skips rather than failures
- **SC-003**: 0% of non-extractable content pages are counted as successfully ingested
- **SC-004**: The ingestion pipeline processes sitemap URLs with 99% reliability (no crashes on invalid URLs)
- **SC-005**: Content extraction succeeds for 90% of valid book content pages
- **SC-006**: Ingestion statistics accurately reflect only pages with extractable content
- **SC-007**: The system can handle sitemaps of up to 10,000 URLs without performance degradation
- **SC-008**: The system processes up to 1000 URLs per minute with 95% success rate for valid content
- **SC-009**: The system implements security measures including basic validation and rate limiting to prevent abuse