# Data Model: Retrieval Validation

## ValidationResult
- **id**: String - Unique identifier for the validation run
- **timestamp**: DateTime - When the validation was performed
- **query_text**: String - The original query text used for retrieval
- **query_vector**: List[float] - Vector representation of the query
- **retrieved_chunks**: List[ContentChunk] - Chunks retrieved from Qdrant
- **expected_chunks**: List[ContentChunk] - Expected relevant chunks (if known)
- **accuracy_score**: Float - Accuracy metric (0.0-1.0)
- **metadata_preservation_rate**: Float - Percentage of metadata preserved (0.0-1.0)
- **consistency_score**: Float - Consistency metric across multiple queries (0.0-1.0)
- **retrieval_time_ms**: Float - Time taken for retrieval operation
- **status**: String - Overall validation status (PASS/FAIL/WARNING)

## ContentChunk
- **id**: String - Unique identifier for the content chunk
- **content**: String - The actual text content of the chunk
- **vector**: List[float] - Vector representation of the content
- **metadata**: Dict - Associated metadata (source document, page number, section, etc.)
- **similarity_score**: Float - Similarity score relative to query
- **rank**: Integer - Position in retrieval results

## ValidationResult
- **validation_type**: String - Type of validation performed (accuracy, metadata, consistency)
- **passed**: Boolean - Whether the validation passed
- **expected**: Any - Expected value for the validation
- **actual**: Any - Actual value observed
- **threshold**: Any - Threshold value for the validation
- **details**: String - Additional details about the validation

## ValidationConfig
- **top_k**: Integer - Number of top results to retrieve (default: 5)
- **similarity_threshold**: Float - Minimum similarity score for relevance (default: 0.7)
- **consistency_runs**: Integer - Number of times to repeat query for consistency check (default: 5)
- **test_queries**: List[String] - Predefined test queries to use for validation
- **expected_accuracy_threshold**: Float - Minimum accuracy required (default: 0.9)
- **metadata_preservation_threshold**: Float - Minimum metadata preservation required (default: 1.0)
- **consistency_threshold**: Float - Minimum consistency required (default: 0.95)