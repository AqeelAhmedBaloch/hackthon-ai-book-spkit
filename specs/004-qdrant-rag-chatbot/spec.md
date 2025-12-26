# Feature Specification: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Qdrant-Backed)

**Feature Branch**: `004-qdrant-rag-chatbot`
**Created**: 2025-12-26
**Status**: Draft
**Input**: User description: "Integrated RAG Chatbot for Physical AI & Humanoid Robotics Book (Qdrant-Backed)

Target audience:
- Readers of the published textbook
- Students and professionals learning Physical AI and Humanoid Robotics

Focus:
- Answering questions strictly from the book content using RAG
- Persisting all book embeddings in Qdrant Cloud
- Agent SDK must read answers only from Qdrant-stored data

Core requirement (MANDATORY):
- All book content MUST be embedded and SAVED into Qdrant Cloud
- The RAG agent MUST read context ONLY from Qdrant
- No in-memory or temporary storage is allowed for book data

System architecture:
- Frontend: Embedded chat window in the book UI
- Backend: FastAPI
- RAG Agent: Python Agent implemented using Agent SDK
- Embeddings: Cohere
- Vector Database: Qdrant Cloud (Free Tier)

Environment configuration (MUST be used exactly):
- COHERE_API_KEY loaded from .env
- QDRANT_URL loaded from .env
- QDRANT_API_KEY loaded from .env
- QDRANT_COLLECTION_NAME loaded from .env

Data ingestion requirements (CRITICAL):
- ingest.py MUST:
  - Load Qdrant configuration from .env
  - Ensure the Qdrant collection exists (create if missing)
  - Split book content into 300–800 token chunks
  - Generate embeddings using Cohere
  - UPSERT embeddings into Qdrant with payload:
    - text
    - chapter
    - section
    - book_title
    - source or page reference
- ingest.py is a one-time script and MUST NOT auto-run

Agent behavior requirements:
- Agent SDK MUST query Qdrant for every user question
- Agent MUST NOT answer if Qdrant returns no relevant vectors
- If no relevant data is found in Qdrant, respond exactly:
  "This topic is not covered in the book"

Constraints:
- No external knowledge outside Qdrant-stored book data
- No hallucinated answers
- No hardcoded API keys or URLs
- Backend must be isolated from frontend

Not building:
- Web search or browsing
- Model training or fine-tuning
- Authentication or analytics"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask Questions About Book Content (Priority: P1)

A student or professional reading the Physical AI & Humanoid Robotics book wants to ask questions about specific concepts, chapters, or sections of the book and receive accurate answers based solely on the book content. The user opens the embedded chat window in the book UI and types their question, then receives a response that references the relevant parts of the book.

**Why this priority**: This is the core functionality that delivers the primary value of the feature - enabling users to get answers from the book content through natural language queries.

**Independent Test**: The user can ask a question about a specific concept in the book and receive an accurate answer that is sourced from the book content. If the topic isn't covered in the book, the system responds with "This topic is not covered in the book".

**Acceptance Scenarios**:

1. **Given** the book content has been successfully embedded in Qdrant, **When** a user asks a question about a topic covered in the book, **Then** the system returns an accurate answer based on the book content with proper context
2. **Given** the book content has been successfully embedded in Qdrant, **When** a user asks a question about a topic not covered in the book, **Then** the system responds with "This topic is not covered in the book"
3. **Given** the system is operational, **When** a user asks a question, **Then** the response is provided within an acceptable time frame (e.g., under 10 seconds)

---

### User Story 2 - Access Contextual Book Information (Priority: P2)

A reader wants to get detailed information about specific chapters, sections, or topics from the Physical AI & Humanoid Robotics book. The user interacts with the chatbot to get specific information that is properly attributed to the relevant parts of the book, including chapter, section, and source references.

**Why this priority**: This enhances the user experience by providing properly sourced information with references to where in the book the information can be found.

**Independent Test**: The user can ask for specific chapter information or detailed explanations of concepts and receive responses that include proper attribution to book sections and page references.

**Acceptance Scenarios**:

1. **Given** a user asks for information about a specific chapter or section, **When** the query is processed, **Then** the response includes the relevant content along with proper book references (chapter, section, source/page)
2. **Given** the system has embedded book content, **When** a user asks for a summary of a specific topic, **Then** the response is accurate and properly attributed to the book

---

### User Story 3 - Use Embedded Chat Interface (Priority: P3)

A student reading the book wants to access the RAG chatbot directly from the book interface without leaving the reading environment. The user can seamlessly interact with the chatbot while reading the book content.

**Why this priority**: This provides a convenient user experience by keeping the Q&A functionality within the book reading environment.

**Independent Test**: The user can access the chat interface from within the book UI and interact with the RAG system without navigating away from the book.

**Acceptance Scenarios**:

1. **Given** the book UI with embedded chat window, **When** a user opens the chat interface, **Then** the chat functionality is accessible and responsive
2. **Given** the embedded chat window is available, **When** a user submits a question, **Then** the backend processes the request and returns a response to the frontend

---

### Edge Cases

- What happens when Qdrant is temporarily unavailable?
- How does the system handle malformed or extremely long user queries?
- What if the book content embedding process fails or is incomplete?
- How does the system handle multiple concurrent users asking questions?
- What happens when the vector search returns low-confidence matches?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST embed all book content into a vector database using text embeddings
- **FR-002**: System MUST ensure the vector database collection exists (create if missing) when ingesting content
- **FR-003**: System MUST split book content into appropriately sized chunks (300–800 tokens) during ingestion
- **FR-004**: System MUST store book content in the vector database with metadata containing: text, chapter, section, book_title, and source/page reference
- **FR-005**: System MUST retrieve relevant context from the vector database for every user question
- **FR-006**: System MUST NOT provide answers if no relevant content is found in the vector database for a query
- **FR-007**: System MUST respond with exactly "This topic is not covered in the book" when no relevant data is found in the vector database
- **FR-008**: System MUST load configuration from secure environment variables
- **FR-009**: System MUST NOT use any external knowledge outside of the stored book data
- **FR-010**: System MUST NOT generate hallucinated answers
- **FR-011**: System MUST provide a one-time data ingestion process that does NOT auto-run
- **FR-012**: System MUST provide a backend service that processes user queries and returns responses
- **FR-013**: System MUST provide an embedded chat interface in the book UI
- **FR-014**: System MUST maintain separation between frontend and backend components

### Key Entities

- **Book Content**: Represents the Physical AI & Humanoid Robotics book content that will be chunked and stored in the vector database
- **Vector Database**: System storing the embedded book content with metadata for retrieval
- **User Query**: Natural language questions from readers seeking information from the book
- **Response**: Answers generated by the system based solely on book content, with proper attribution

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can ask questions about the Physical AI & Humanoid Robotics book content and receive accurate answers within 10 seconds
- **SC-002**: 95% of valid questions about book content return relevant answers sourced from the book
- **SC-003**: 100% of questions about topics not covered in the book return the exact response "This topic is not covered in the book"
- **SC-004**: Book content is successfully embedded into the vector database with all required metadata (text, chapter, section, book_title, source)
- **SC-005**: The system demonstrates zero hallucinated answers during testing scenarios
- **SC-006**: The embedded chat interface is accessible and functional within the book UI
- **SC-007**: The ingestion process successfully processes all book content into appropriately sized chunks (300-800 tokens) and stores them in the vector database