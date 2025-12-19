# Data Model: RAG Agent Implementation

## QueryRequest
- **query**: String - The user's question or request for information
- **user_id**: String (Optional) - Identifier for the user making the request
- **session_id**: String (Optional) - Identifier for the conversation session
- **context_filters**: Dict (Optional) - Filters to apply when retrieving context (e.g., specific chapters, sections)

## QueryResponse
- **response**: String - The agent's answer to the query
- **citations**: List[Citation] - References to specific book sections used in the response
- **confidence**: Float - Confidence score for the response (0.0-1.0)
- **retrieved_chunks**: List[ContentChunk] - Content chunks retrieved during processing
- **processing_time_ms**: Float - Time taken to process the query
- **query_id**: String - Unique identifier for this query

## Citation
- **source_document**: String - Name or identifier of the source document
- **page_number**: Integer - Page number in the source
- **section**: String - Section or chapter name
- **text_snippet**: String - Brief excerpt from the cited content
- **similarity_score**: Float - How relevant this citation was to the query (0.0-1.0)

## ContentChunk
- **id**: String - Unique identifier for the content chunk
- **content**: String - The actual text content of the chunk
- **metadata**: Dict - Associated metadata (source document, page number, section, etc.)
- **similarity_score**: Float - Similarity score relative to the query
- **vector_id**: String - Identifier in the vector database

## AgentConfig
- **model**: String - OpenAI model to use for the agent (default: gpt-4-turbo)
- **temperature**: Float - Temperature setting for response creativity (default: 0.1 for factual accuracy)
- **max_tokens**: Integer - Maximum tokens in the response (default: 1000)
- **retrieval_top_k**: Integer - Number of content chunks to retrieve (default: 5)
- **similarity_threshold**: Float - Minimum similarity for content inclusion (default: 0.7)
- **citation_required**: Boolean - Whether citations are mandatory in responses (default: true)

## AgentSession
- **session_id**: String - Unique identifier for the conversation session
- **created_at**: DateTime - When the session was created
- **last_activity**: DateTime - When the session was last used
- **conversation_history**: List[Message] - History of messages in the session
- **user_context**: Dict - User-specific context information

## Message
- **message_id**: String - Unique identifier for the message
- **role**: String - Role of the message sender (user, assistant, system)
- **content**: String - The content of the message
- **timestamp**: DateTime - When the message was created
- **citations**: List[Citation] - Citations associated with this message (for assistant messages)