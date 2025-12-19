# Data Model: Content Ingestion & Embeddings

**Feature**: 1-content-ingestion
**Created**: 2025-12-19

## Entities

### ContentChunk
Represents a segment of extracted text that fits within Cohere's token limits

**Attributes**:
- `text`: str - The actual content text extracted from the source
- `source_url`: str - The original URL where the content was found
- `content_id`: str - Unique identifier for the chunk (generated using content hash)
- `metadata`: Dict[str, Any] - Additional metadata including:
  - `chunk_index`: int - Position of this chunk in the original content
  - `page_title`: str - Title of the source page (extracted from content)
  - `word_count`: int - Number of words in the chunk
  - `timestamp`: int - Unix timestamp when chunk was created

**Relationships**:
- Each ContentChunk is associated with exactly one source URL
- Multiple ContentChunks can originate from the same source page
- Each ContentChunk maps to one embedding vector in the vector database

### Embedding Vector
Represents the numerical representation of content semantics

**Attributes**:
- `vector`: List[float] - The actual embedding vector (1024 dimensions for Cohere's multilingual model)
- `id`: str - Unique identifier that matches the ContentChunk's content_id
- `payload`: Dict[str, Any] - Metadata stored with the vector in Qdrant:
  - `text`: str - Original text content
  - `source_url`: str - Original source URL
  - `timestamp`: int - Unix timestamp
  - Additional metadata from ContentChunk

**Relationships**:
- Each Embedding Vector corresponds to exactly one ContentChunk
- Stored in Qdrant collection with associated metadata

## Data Flow

1. **Source**: Deployed book URLs
2. **Extraction**: ContentExtractor processes URLs → ContentChunk objects
3. **Chunking**: ContentChunker splits content → Multiple ContentChunk objects
4. **Embedding**: EmbeddingGenerator processes text → Embedding vectors
5. **Storage**: VectorStore stores vectors with metadata → Qdrant database

## Validation Rules

- Each ContentChunk.text must be non-empty
- Each ContentChunk.source_url must be a valid URL
- Each ContentChunk.content_id must be unique within the system
- ContentChunk.metadata must include required fields (chunk_index, page_title, word_count)
- Embedding vectors must match the expected dimension (1024 for Cohere model)
- All data must be preserved during the transformation process

## State Transitions

The system follows an immutable pattern where content moves through the pipeline:

1. **Raw URL** → **Crawled Content** → **Chunked Content** → **Embedded Content** → **Stored Content**
2. Each stage adds information but doesn't modify the original source
3. Metadata is accumulated at each step to maintain provenance