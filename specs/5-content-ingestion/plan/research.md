# Research Document: Content Ingestion & Embeddings

**Feature**: 5-content-ingestion
**Created**: 2025-12-21
**Status**: Completed

## 0.1: Docusaurus Content Extraction Patterns

### Decision: Use semantic HTML selectors for content extraction
**Rationale**: Docusaurus sites follow consistent HTML patterns with semantic class names and structure that can be reliably targeted.

**Key Findings**:
- Main content is typically in `<main>` tag or elements with class `main-wrapper`
- Content sections use classes like `docItemContainer`, `theme-doc-markdown`
- Navigation and sidebar elements can be excluded using selectors for `.navbar`, `.sidebar`, `.menu`
- Article content is usually within `<article>` tags or elements with `doc-wrapper`

**Implementation Strategy**:
- Use CSS selectors to target main content containers
- Exclude common navigation elements
- Preserve document hierarchy and section titles
- Handle both Markdown and MDX content formats

**Alternatives Considered**:
- Generic web scraping: Less reliable for content extraction
- Custom HTML parsing: More complex but potentially more accurate

## 0.2: Cohere Embedding Model Selection

### Decision: Use Cohere's embed-multilingual-v3.0 model
**Rationale**: Best balance of performance, cost, and compatibility with technical documentation content.

**Key Findings**:
- `embed-multilingual-v3.0` supports 1024 dimensions with good performance
- Maximum context length of 512 tokens per chunk
- Optimized for retrieval tasks
- Cost-effective for batch processing
- Handles technical terminology well

**Technical Specifications**:
- Input: Text up to 512 tokens per request
- Output: 1024-dimensional vector
- Rate limits: 100 requests/minute for free tier
- Supports multiple languages (beneficial for diverse documentation)

**Alternatives Considered**:
- `embed-english-v3.0`: Good but multilingual provides more flexibility
- Older v2 models: Less efficient than v3.0

## 0.3: Qdrant Cloud Free Tier Constraints

### Decision: Optimize for Qdrant Cloud Free Tier limitations
**Rationale**: Need to respect storage and rate limits while maintaining functionality.

**Key Findings**:
- Storage limit: 1 GB (sufficient for initial implementation)
- Vector count limit: 100,000 vectors
- API rate limit: 10 requests/second
- Maximum payload size: 10 MB per request
- Collections: Up to 10 collections

**Implementation Strategy**:
- Batch vector uploads to minimize API calls
- Implement rate limiting to respect 10 req/sec limit
- Use efficient vector quantization if needed
- Monitor storage usage during ingestion

**Alternatives Considered**:
- Self-hosted Qdrant: More resources but requires infrastructure management
- Other vector DBs: Would violate constraint of using Qdrant only

## 0.4: Content Chunking Strategy

### Decision: Use 500-token chunks with 50-token overlap
**Rationale**: Balances context preservation with embedding model constraints and search effectiveness.

**Key Findings**:
- Cohere v3 models handle up to 512 tokens, so 500 provides safety margin
- 50-token overlap preserves context across chunk boundaries
- Sentence-aware splitting maintains readability
- Average chunk size of ~1000-1500 characters for English text

**Implementation Strategy**:
- Split by semantic boundaries (paragraphs, sections) when possible
- Maintain document hierarchy in chunk metadata
- Include overlap to preserve context
- Track original document position for citations

**Alternatives Considered**:
- Fixed character limits: Less context-aware
- Pure sentence splitting: May break semantic meaning
- Larger chunks: Risk of exceeding model limits