# Data Model: Frontend Integration

## ChatRequest
- **query**: String - The user's question or request for information
- **selected_text**: String (Optional) - Text that the user has selected on the page for context
- **page_url**: String - URL of the current page where the question was asked
- **session_id**: String (Optional) - Identifier for the conversation session
- **timestamp**: DateTime - When the request was created

## ChatResponse
- **response**: String - The RAG agent's answer to the query
- **citations**: List[Citation] - References to specific book sections used in the response
- **confidence**: Float - Confidence score for the response (0.0-1.0)
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

## ApiConfig
- **backend_url**: String - Base URL for the RAG backend API
- **timeout_ms**: Integer - Request timeout in milliseconds (default: 30000)
- **retries**: Integer - Number of retry attempts for failed requests (default: 3)
- **headers**: Dict - Additional headers to include with requests

## TextSelection
- **selected_text**: String - The text that was selected by the user
- **element_id**: String - ID of the element where the selection occurred
- **page_url**: String - URL of the page where the selection occurred
- **timestamp**: DateTime - When the selection was made
- **coordinates**: Dict - X,Y coordinates of the selection for visual feedback