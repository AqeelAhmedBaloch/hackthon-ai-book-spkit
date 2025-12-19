# Research: Content Ingestion & Embeddings

**Feature**: 1-content-ingestion
**Created**: 2025-12-19

## Decision: Cohere Embedding Model Selection

**Rationale**: Chose Cohere's `embed-multilingual-v3.0` model for its robust support of multiple languages and proven performance for document embedding tasks. This model produces 1024-dimensional vectors which balance quality and efficiency.

**Alternatives considered**:
- `embed-english-v3.0`: Limited to English content, but slightly more efficient
- OpenAI embeddings: Would violate constraint of using Cohere only
- Sentence Transformers: Self-hosted option but would require more infrastructure

## Decision: Content Extraction Strategy

**Rationale**: Implemented a multi-selector approach targeting Docusaurus-specific CSS classes (`article`, `.markdown`, `.theme-doc-markdown`, `.main-wrapper`) to extract clean content while preserving document structure. Falls back to general selectors if specific ones aren't found.

**Alternatives considered**:
- Generic HTML parsing: Would extract more noise (navigation, footer)
- Custom parsing rules per site: Too specific and not reusable
- Headless browser approach: More complex and slower

## Decision: Content Chunking Algorithm

**Rationale**: Implemented overlapping chunks of 1000 characters with 100-character overlap. This size fits well within Cohere's token limits while maintaining context. The algorithm tries to break at sentence boundaries when possible.

**Alternatives considered**:
- Fixed token count: More precise but requires tokenization library
- Semantic chunking: More sophisticated but complex to implement
- Header-based chunking: Would work well for documentation but less generalizable

## Decision: Qdrant Collection Configuration

**Rationale**: Created a collection with 1024-dimensional vectors using cosine distance, which is optimal for Cohere embeddings. Collection name defaults to "book_embeddings" but is configurable.

**Alternatives considered**:
- Different distance metrics: Euclidean or Manhattan distance would be less appropriate for embeddings
- Different vector sizes: Would require different embedding models
- Multiple collections: More complex management without clear benefits

## Decision: Error Handling and Resilience

**Rationale**: Implemented comprehensive error handling with logging at each stage, retry logic for network operations, and graceful degradation when individual pages fail. This ensures the pipeline continues processing even when some content is inaccessible.

**Alternatives considered**:
- Fail-fast approach: Would stop the entire process on first error
- Silent error suppression: Would make debugging difficult
- Separate error queue: More complex but better for large-scale processing

## Decision: Crawling Strategy

**Rationale**: Implemented breadth-first crawling with domain restriction and page limits to prevent infinite crawling while ensuring comprehensive coverage of the book. Limits to 50 pages to stay within free tier constraints.

**Alternatives considered**:
- Depth-first crawling: Might miss content if early branches are too deep
- Sitemap-based crawling: Requires sitemap to be available
- Manual URL list: Less automated but more controlled

## Technology Integration Patterns

**Web Scraping**: Used requests + BeautifulSoup for efficient and reliable content extraction. Session management and proper headers ensure good behavior with target servers.

**API Integration**: Implemented batch processing to respect rate limits and optimize API usage. Cohere's embedding API accepts up to 96 texts per request.

**Vector Database**: Used Qdrant's upsert functionality for idempotent operations and batch uploads for efficiency.

## Performance Considerations

- Batch processing to minimize API calls
- Memory management through chunking
- Network efficiency with proper session reuse
- Rate limiting compliance