# RAG Chatbot UI Integration Implementation Plan

## Overview
This plan details the implementation of the RAG chatbot UI integration into the Docusaurus book, featuring a floating icon that opens a chat window for users to ask questions about book content.

## Technical Context

### Components to Implement
- **Floating Chatbot Icon**: Always visible button in bottom-right corner
- **Chat Interface**: Modal/sliding panel with message history and input controls
- **Text Selection Capture**: Functionality to detect and capture selected text
- **API Integration**: Connection to existing backend `/query` endpoint
- **Response Rendering**: Display of answers and citations from backend

### Technologies
- **Frontend Framework**: React components for Docusaurus integration
- **Styling**: CSS/SCSS for UI components and animations
- **API Communication**: Fetch/axios for backend API calls
- **State Management**: React hooks for UI state

### Architecture
- Client-side component that integrates with Docusaurus
- Uses existing backend APIs without requiring backend changes
- Self-contained UI component with minimal dependencies

## Constitution Check

### Quality Standards
- Component must follow Docusaurus theming and styling conventions
- Accessibility standards must be maintained (keyboard navigation, screen readers)
- Performance impact on page load should be minimal

### Security Considerations
- No sensitive data should be stored client-side
- API calls should follow proper authentication patterns if required
- Selected text capture should respect user privacy

### Architecture Principles
- Component should be modular and reusable
- UI should be responsive across all device sizes
- Integration should be seamless with existing Docusaurus structure

## Gates Evaluation

### Feasibility Check
- ✅ Docusaurus supports custom components
- ✅ Existing backend API is available for integration
- ✅ Text selection APIs are available in modern browsers
- ✅ No major technical blockers identified

### Risk Assessment
- Low risk: Frontend-only implementation
- Low complexity: Uses existing backend services
- No breaking changes to existing functionality

## Phase 0: Research & Resolution

### Research Tasks Completed
1. **Docusaurus Integration Patterns**: Researched best practices for adding custom UI components to Docusaurus sites
2. **Floating UI Implementation**: Researched patterns for floating action buttons in web applications
3. **Text Selection APIs**: Researched browser APIs for detecting and capturing selected text
4. **Chat Interface Patterns**: Researched UI/UX patterns for chat interfaces in documentation sites

## Phase 1: Design & Architecture

### Data Model
- **ChatMessage**: Represents a single message in the chat history
  - type: "user" | "assistant"
  - content: string (the message text)
  - timestamp: Date
  - citations?: string[] (optional citations for assistant responses)
- **ChatState**: Represents the state of the chat interface
  - isOpen: boolean (whether chat window is open)
  - messages: ChatMessage[] (message history)
  - inputText: string (current input text)
  - selectedText: string | null (currently selected text on page)

### API Contracts
- **POST /query** (existing backend endpoint)
  - Request: `{"question": string, "selected_text": string | null}`
  - Response: `{"answer": string, "sources": string[]}`

### Component Architecture
1. **ChatbotWidget**: Main container component
   - Manages overall state and visibility
   - Contains both the floating icon and chat window
2. **FloatingIcon**: Always-visible button component
   - Positioned in bottom-right corner
   - Handles open/close state
3. **ChatWindow**: The main chat interface
   - Contains message history display
   - Contains input area with text field and send button
4. **MessageDisplay**: Component to render individual messages
   - Handles both user and assistant messages
   - Renders citations for assistant responses

## Implementation Approach

### Step 1: Create Basic Components
- Create the floating icon component with proper positioning
- Create the basic chat window structure
- Implement open/close functionality

### Step 2: Implement Text Selection Capture
- Add event listeners for text selection
- Store selected text in component state
- Pass selected text to query API when available

### Step 3: Integrate with Backend API
- Implement API call to existing `/query` endpoint
- Handle request/response formatting
- Display loading states during API calls

### Step 4: Message History Management
- Implement state management for message history
- Display messages in chronological order
- Add proper styling for different message types

### Step 5: Citations Display
- Parse and display citations from backend responses
- Format citations appropriately in the UI

### Step 6: Testing and Refinement
- Test on multiple book pages
- Ensure responsive design works on all screen sizes
- Optimize performance and fix any issues

## Success Criteria
- Floating icon appears consistently on all book pages
- Chat interface opens and closes smoothly
- Text selection is properly captured and sent with queries
- Backend responses are displayed correctly with citations
- No negative impact on page performance or user experience
- Component works across all major browsers

## Deployment Considerations
- Component should be easily configurable for different Docusaurus themes
- Should work with existing build process without modifications
- Minimal impact on page load times