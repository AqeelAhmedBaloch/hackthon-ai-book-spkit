# API Contract: RAG Chatbot for Physical AI & Humanoid Robotics Book

**Feature**: 004-qdrant-rag-chatbot
**Date**: 2025-12-26

## Overview

This document defines the API contracts for the RAG chatbot system that answers questions from Physical AI & Humanoid Robotics book content.

## Endpoints

### POST /chat

Process a user question and return an answer based on book content.

#### Request

**Path**: `/chat`

**Method**: `POST`

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "question": "What is the main concept of Physical AI?",
  "selected_text": "Optional selected text from the book"
}
```

**Fields**:
- `question` (string, required): The user's question about the book content
- `selected_text` (string, optional): Any selected text context provided by the user

#### Response

**Success Response (200 OK)**:

```json
{
  "id": "response-12345",
  "answer": "Physical AI is a field that combines physical systems with artificial intelligence...",
  "references": [
    {
      "chapter": "Introduction to Physical AI",
      "section": "Core Concepts",
      "source_url": "https://book-url.com/chapter1"
    }
  ],
  "timestamp": "2025-12-26T10:30:00Z"
}
```

**Fields**:
- `id` (string): Unique identifier for the response
- `answer` (string): The answer generated from book content
- `references` (array): List of book sections used to generate the answer
  - `chapter` (string): Chapter title
  - `section` (string): Section title
  - `source_url` (string): URL reference to the source
- `timestamp` (string): ISO 8601 timestamp of response generation

**Not Found Response (200 OK)**:

When no relevant content is found in the book:

```json
{
  "id": "response-12346",
  "answer": "This topic is not covered in the book",
  "references": [],
  "timestamp": "2025-12-26T10:30:01Z"
}
```

#### Error Responses

**Bad Request (400)**:
- When question is missing or empty
- When request body is malformed

**Server Error (500)**:
- When there's an internal server error
- When Qdrant or Cohere services are unavailable

## Data Models

### QueryRequest

**Description**: The request model for user queries

**Fields**:
- `question` (string, required): The user's question, minimum 1 character, maximum 1000 characters
- `selected_text` (string, optional): Additional context from selected text, maximum 5000 characters

### QueryResponse

**Description**: The response model for query results

**Fields**:
- `id` (string, required): Unique response identifier
- `answer` (string, required): The answer text (or "This topic is not covered in the book")
- `references` (array, required): List of source references
- `timestamp` (string, required): ISO 8601 formatted timestamp

### Reference

**Description**: A reference to the book content used in the answer

**Fields**:
- `chapter` (string, required): Chapter name or identifier
- `section` (string, required): Section name or identifier
- `source_url` (string, required): URL reference to the original content

## Validation Rules

1. The `question` field must be present and non-empty
2. The `answer` field must be sourced from book content only
3. If no relevant content is found, the answer must be exactly "This topic is not covered in the book"
4. All responses must include proper attribution in the `references` field
5. Response time should be under 10 seconds

## Security Considerations

1. No sensitive data should be logged from user queries
2. API keys should be properly secured and not exposed in responses
3. Input validation should prevent injection attacks
4. Rate limiting should be implemented to prevent abuse