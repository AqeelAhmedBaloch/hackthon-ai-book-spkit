# Data Model: RAG Integration

## ContentChunk
- **id**: String - Unique identifier for the content chunk
- **content**: String - The actual text content of the chunk
- **source_document**: String - Name or identifier of the source document
- **page_number**: Integer - Page number in the source
- **section**: String - Section or chapter name
- **metadata**: Dict - Additional metadata associated with the chunk
- **embedding**: List[float] - Vector representation of the content
- **hash**: String - Hash of the content for deduplication

## EmbeddingRecord
- **vector_id**: String - Identifier in the vector database
- **vector**: List[float] - The embedding vector
- **payload**: Dict - Metadata associated with the vector (content, source, etc.)
- **collection_name**: String - Name of the Qdrant collection

## IngestionConfig
- **chunk_size**: Integer - Size of content chunks in tokens (default: 512)
- **chunk_overlap**: Integer - Overlap between chunks in tokens (default: 50)
- **model**: String - Embedding model to use (default: text-embedding-ada-002)
- **batch_size**: Integer - Number of chunks to process in each batch (default: 10)
- **content_format**: String - Format of the input content (pdf, markdown, etc.)

## QueryRequest
- **query**: String - The user's question or request for information
- **selected_text**: String (Optional) - Text that the user has selected on the page for context
- **page_url**: String - URL of the current page where the question was asked
- **session_id**: String (Optional) - Identifier for the conversation session
- **timestamp**: DateTime - When the request was created

## QueryResponse
- **response**: String - The RAG agent's answer to the query
- **citations**: List[Citation] - References to specific book sections used in the response
- **confidence**: Float - Confidence score for the response (0.0-1.0)
- **retrieved_chunks**: List[ContentChunk] - Content chunks retrieved during processing
- **processing_time_ms**: Float - Time taken to process the query
- **request_id**: String - Unique identifier for the original request
- **timestamp**: DateTime - When the response was received

## Citation
- **source_document**: String - Name or identifier of the source document
- **page_number**: Integer - Page number in the source
- **section**: String - Section or chapter name
- **text_snippet**: String - Brief excerpt from the cited content
- **similarity_score**: Float - How relevant this citation was to the query (0.0-1.0)

## ChatMessage
- **id**: String - Unique identifier for the message
- **content**: String - The content of the message
- **sender**: String - Who sent the message ('user' or 'assistant')
- **timestamp**: DateTime - When the message was created
- **citations**: List[Citation] - Citations associated with this message (for assistant messages)
- **status**: String - Status of the message ('sent', 'pending', 'received', 'error')

## ChatSession
- **session_id**: String - Unique identifier for the conversation session
- **created_at**: DateTime - When the session was created
- **last_activity**: DateTime - When the session was last used
- **messages**: List[ChatMessage] - History of messages in the session
- **current_page**: String - Current page URL where the session is active

## ValidationResult
- **id**: String - Unique identifier for the validation run
- **timestamp**: DateTime - When the validation was performed
- **query_text**: String - The original query text used for retrieval
- **retrieved_chunks**: List[ContentChunk] - Chunks retrieved from Qdrant
- **expected_chunks**: List[ContentChunk] - Expected relevant chunks (if known)
- **accuracy_score**: Float - Accuracy metric (0.0-1.0)
- **metadata_preservation_rate**: Float - Percentage of metadata preserved (0.0-1.0)
- **consistency_score**: Float - Consistency metric across multiple queries (0.0-1.0)
- **retrieval_time_ms**: Float - Time taken for retrieval operation
- **status**: String - Overall validation status (PASS/FAIL/WARNING)

## AgentConfig
- **model**: String - OpenAI model to use for the agent (default: gpt-4-turbo)
- **temperature**: Float - Temperature setting for response creativity (default: 0.1 for factual accuracy)
- **max_tokens**: Integer - Maximum tokens in the response (default: 1000)
- **retrieval_top_k**: Integer - Number of content chunks to retrieve (default: 5)
- **similarity_threshold**: Float - Minimum similarity for content inclusion (default: 0.7)
- **citation_required**: Boolean - Whether citations are mandatory in responses (default: true)