# Data Model: Retrieval Validation

**Feature**: 6-retrieval-validation
**Created**: 2025-12-21
**Status**: Draft

## Query Request Entity

**Description**: Represents a search query request for validation testing

### Fields
- `id` (string, required): Unique identifier for the query request (UUID)
- `query_text` (string, required): The search query text to be validated
- `similarity_threshold` (float, optional): Minimum similarity score threshold (0.0-1.0, default 0.5)
- `top_k` (integer, optional): Number of top results to return (default 5)
- `parameters` (dict, optional): Additional search parameters dictionary
  - `search_params` (dict): Qdrant-specific search parameters
  - `with_payload` (bool): Whether to include payload in results (default true)
  - `with_vectors` (bool): Whether to include vectors in results (default false)
- `expected_content_ids` (list[string], optional): Expected content chunk IDs for relevance testing
- `created_at` (datetime, required): Timestamp of query creation
- `updated_at` (datetime, optional): Timestamp of last update

### Validation Rules
- `query_text` must not be empty
- `similarity_threshold` must be between 0.0 and 1.0 if provided
- `top_k` must be a positive integer
- `expected_content_ids` must contain valid UUIDs if provided

## Retrieval Result Entity

**Description**: Contains a single result from a similarity search operation

### Fields
- `id` (string, required): Unique identifier for the result (UUID)
- `query_id` (string, required): Reference to the query request (foreign key)
- `content_chunk_id` (string, required): ID of the retrieved content chunk
- `content` (string, required): The retrieved content text
- `similarity_score` (float, required): Similarity score between query and result (0.0-1.0)
- `rank` (integer, required): Position in the result set (1-based)
- `metadata` (dict, required): Retrieved metadata dictionary
  - `source_url` (string): Original URL where content was found
  - `title` (string): Page title or section header
  - `position` (integer): Position in original document
  - `hierarchy_path` (string, optional): Document hierarchy path
- `retrieved_at` (datetime, required): Timestamp of retrieval
- `is_relevant` (boolean, optional): Whether this result is considered relevant to the query

### Validation Rules
- `similarity_score` must be between 0.0 and 1.0
- `rank` must be a positive integer
- `metadata` must contain required fields: source_url, title, position
- `is_relevant` is computed based on comparison with expected results

## Validation Report Entity

**Description**: Summary of retrieval validation metrics and outcomes

### Fields
- `id` (string, required): Unique identifier for the validation report (UUID)
- `validation_type` (string, required): Type of validation test performed (enum: similarity, metadata, consistency)
- `test_queries_count` (integer, required): Total number of test queries executed
- `total_retrievals` (integer, required): Total number of retrieval operations performed
- `relevant_results_count` (integer, required): Count of relevant results found
- `relevance_percentage` (float, required): Percentage of relevant results (0.0-100.0)
- `top_k_accuracy` (dict, required): Accuracy metrics for different k values
  - `top_1` (float): Accuracy for top 1 result (0.0-100.0)
  - `top_3` (float): Accuracy for top 3 results (0.0-100.0)
  - `top_5` (float): Accuracy for top 5 results (0.0-100.0)
- `mean_reciprocal_rank` (float, required): Mean Reciprocal Rank score
- `metadata_accuracy` (float, required): Percentage of metadata fields preserved correctly (0.0-100.0)
- `consistency_score` (float, required): Consistency measurement across repeated queries (0.0-100.0)
- `jaccard_similarity` (float, optional): Jaccard similarity for consistency measurement (0.0-1.0)
- `start_time` (datetime, required): When validation started
- `end_time` (datetime, required): When validation completed
- `metrics` (dict, optional): Additional validation metrics dictionary
  - `average_response_time` (float): Average time per query in seconds
  - `queries_per_second` (float): Throughput measurement
  - `error_rate` (float): Percentage of queries that failed
- `errors` (list[dict], optional): List of any errors encountered
  - `error_type` (string): Type of error
  - `error_message` (string): Error description
  - `query_id` (string, optional): Query associated with error
  - `timestamp` (datetime): When error occurred
- `configuration` (dict, required): Configuration used for validation
  - `similarity_threshold` (float): Threshold used for validation
  - `top_k` (integer): Number of results requested
  - `consistency_iterations` (integer): Number of iterations for consistency test
- `passed_criteria` (dict, required): Success criteria validation results
  - `sc_001_top_3_accuracy` (boolean): Whether SC-001 was met (≥90%)
  - `sc_002_metadata_accuracy` (boolean): Whether SC-002 was met (100%)
  - `sc_003_consistency` (boolean): Whether SC-003 was met (≥95%)
  - `sc_004_scale_test` (boolean): Whether SC-004 was met (≥10,000 embeddings)

### Validation Rules
- `relevance_percentage`, `metadata_accuracy`, `consistency_score` must be between 0.0 and 100.0
- `mean_reciprocal_rank` must be between 0.0 and 1.0
- `jaccard_similarity` must be between 0.0 and 1.0 if provided
- `top_k_accuracy` values must be between 0.0 and 100.0
- `start_time` must be before `end_time`
- All success criteria in `passed_criteria` must align with actual measurements

## Validation Test Suite Entity

**Description**: Collection of test queries and expected results for comprehensive validation

### Fields
- `id` (string, required): Unique identifier for the test suite (UUID)
- `name` (string, required): Name/description of the test suite
- `description` (string, optional): Detailed description of test suite purpose
- `query_requests` (list[string], required): List of query request IDs in this suite
- `expected_results` (dict, required): Expected results mapping for relevance testing
  - keys: query request IDs
  - values: list of expected content chunk IDs
- `validation_config` (dict, required): Configuration for running this test suite
  - `similarity_threshold` (float): Default threshold for this suite
  - `top_k` (integer): Default top-k for this suite
  - `consistency_iterations` (integer): Default iterations for consistency tests
- `created_at` (datetime, required): When test suite was created
- `updated_at` (datetime, optional): When test suite was last updated

### Validation Rules
- `query_requests` must contain valid query request IDs
- `expected_results` must have corresponding entries for all query requests
- `validation_config` must have valid parameter values

## Relationships

### Query Request → Retrieval Results
- One-to-many relationship: Each query request can have multiple retrieval results
- Foreign key: `query_id` in Retrieval Result references `id` in Query Request

### Validation Report → Query Requests
- Many-to-many relationship (indirect): Validation report covers multiple query requests
- Through the test suite entity

### Validation Test Suite → Query Requests
- Many-to-many relationship: Test suite contains multiple query requests
- Foreign key: `query_requests` array contains IDs referencing Query Request entities

## State Transitions (Validation Report)

### Status Transitions
- `pending` → `running`: When validation starts
- `running` → `completed`: When validation finishes successfully
- `running` → `failed`: When validation encounters unrecoverable errors
- `completed` → `re-run`: When validation is re-executed (optional)

### Progress Tracking
- `total_retrievals` updates as each query is processed
- `relevant_results_count` updates as relevance is determined
- `metrics` updates incrementally during validation
- `errors` array grows as errors are encountered