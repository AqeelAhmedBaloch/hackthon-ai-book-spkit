# Enhanced RAG Agent Implementation Plan

## Overview
This plan details the implementation of the enhanced RAG agent that supports both full-book context and user-selected text context for answering questions.

## Architecture Changes

### Components to Update
- **API Schema** (`main.py`): Update the query endpoint to accept optional selected_text parameter
- **RAG Agent Logic** (`agent.py`): Implement conditional logic for context selection
- **Response Handling**: Add citation labels to indicate source of information

### Technical Approach
- Conditional processing based on presence of selected_text parameter
- Maintaining existing Qdrant integration for full-book context mode
- Implementing direct text processing for selected text mode
- Preserving no-hallucination rule across both modes

## Implementation Steps

### 1. API Schema Update
- Modify the query endpoint in `main.py` to accept the optional `selected_text` parameter
- Update the request model to include the new field
- Ensure backward compatibility with existing API consumers

### 2. RAG Agent Enhancement
- Update the `get_answer` method in `agent.py` to handle both context modes
- Implement logic to check for selected_text parameter
- Create separate answer generation paths for each context mode
- Maintain consistent response format across both modes

### 3. Context Processing Logic
- **Full-book mode**: Use existing Qdrant retrieval and Cohere generation
- **Selected text mode**: Generate answer directly from provided text without vector search
- Implement validation to ensure selected text is meaningful before processing

### 4. Response Enhancement
- Add source attribution to responses indicating whether answer came from "Selected Text" or specific book sections
- Maintain consistent response format with sources field
- Update error handling for both context modes

### 5. Quality Assurance
- Ensure no hallucinations in either context mode
- Implement fallback responses when no answer can be found
- Validate response consistency across both modes

## Technical Specifications

### API Changes
- Update POST `/query` endpoint to accept optional `selected_text` parameter
- Request body: `{"question": "string", "selected_text": "string | null"}`
- Response format remains consistent with source attribution

### Processing Logic
- If `selected_text` is provided (not null/empty): Answer only from the provided text
- If `selected_text` is not provided: Use Qdrant retrieval from book chunks
- Both modes enforce no-hallucination rule
- Both modes return "This question is not covered in the book." when no answer found

### Source Attribution
- Responses from selected text include "Selected Text" as source
- Responses from book chunks include appropriate chapter/section references
- Maintain existing sources field structure in responses

## Success Criteria
- API endpoint accepts new selected_text parameter without breaking existing functionality
- System correctly switches between context modes based on parameter presence
- Both context modes prevent hallucinations and provide accurate answers
- Response time remains acceptable in both modes
- Proper source attribution is provided in responses

## Risk Mitigation
- Validate selected text length to prevent performance issues with very long inputs
- Maintain backward compatibility for existing API consumers
- Implement proper error handling for edge cases with selected text
- Ensure consistent quality of responses across both context modes