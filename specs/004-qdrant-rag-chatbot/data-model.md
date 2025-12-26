# Data Model: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book

**Feature**: 004-qdrant-rag-chatbot
**Date**: 2025-12-26

## Entities

### BookContent
**Description**: Represents the book content that is chunked and stored in the vector database

**Fields**:
- `id` (string): Unique identifier for the content chunk
- `text` (string): The actual text content of the chunk
- `chapter` (string): The chapter title or identifier
- `section` (string): The section title or identifier
- `book_title` (string): Title of the book
- `source_url` (string): URL or reference to the original source
- `token_count` (integer): Number of tokens in the text chunk
- `embedding` (vector): The vector embedding of the text

**Validation Rules**:
- `text` must not be empty
- `token_count` must be between 300-800
- `chapter` and `section` must be provided

### UserQuery
**Description**: Represents a user's question or query to the RAG system

**Fields**:
- `id` (string): Unique identifier for the query
- `question` (string): The user's question text
- `selected_text` (string, optional): Any selected text provided with the question
- `timestamp` (datetime): When the query was made
- `session_id` (string, optional): Session identifier for conversation context

**Validation Rules**:
- `question` must not be empty
- `question` must be less than 1000 characters

### Response
**Description**: The system's response to a user query

**Fields**:
- `id` (string): Unique identifier for the response
- `answer` (string): The generated answer based on book content
- `references` (array): List of source references used in the answer
- `query_id` (string): Reference to the original query
- `timestamp` (datetime): When the response was generated
- `confidence_score` (float, optional): Confidence level of the response

**Validation Rules**:
- `answer` must not be empty unless it's the fallback response
- `answer` must be sourced from book content only

### QdrantPayload
**Description**: The payload structure for storing data in Qdrant

**Fields**:
- `text` (string): The text content of the chunk
- `chapter` (string): The chapter title or identifier
- `section` (string): The section title or identifier
- `book_title` (string): Title of the book
- `source_url` (string): URL or reference to the original source

**Validation Rules**:
- All fields are required
- Must match the functional requirements in the spec

## Relationships

- `UserQuery` → `Response`: One-to-one relationship (each query generates one response)
- `Response` → `BookContent`: One-to-many relationship (response may reference multiple content chunks)
- `BookContent` → `QdrantPayload`: One-to-one mapping (content stored in Qdrant with payload structure)

## State Transitions

### Query Processing Flow
1. `UserQuery` created when user submits a question
2. `QueryProcessing` state when system retrieves relevant content from Qdrant
3. `ResponseGeneration` state when answer is being generated from retrieved content
4. `Response` created with either book-sourced answer or fallback message

## Constraints

- All data must be sourced from the Physical AI & Humanoid Robotics book
- No external knowledge or hallucinated content allowed
- Proper attribution to book chapters/sections required
- Content chunks must be between 300-800 tokens
- System must return "This topic is not covered in the book" when no relevant content is found