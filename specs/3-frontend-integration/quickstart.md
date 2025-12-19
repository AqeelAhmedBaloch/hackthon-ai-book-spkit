# Quickstart: Frontend Integration

## Prerequisites

- Node.js 18+ and npm/yarn
- Running RAG backend service (from Spec-3)
- Docusaurus project set up in the ai_frontend_book directory

## Setup

1. **Install dependencies**:
   ```bash
   cd ai_frontend_book
   npm install
   # or
   yarn install
   ```

2. **Configure backend connection**:
   ```bash
   # Create environment file
   echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
   ```

3. **Verify backend connection**:
   ```bash
   # Test that the RAG backend is accessible
   curl http://localhost:8000/health
   ```

## Adding the Chat Component

1. **Import and use the RagChat component**:
   ```jsx
   import { RagChat } from './src/components/RagChat';

   // Add to your Docusaurus page
   <RagChat />
   ```

2. **Configure for all pages** (optional):
   ```js
   // In docusaurus.config.js
   // Add the chat component to the layout or specific pages
   ```

## Running the Application

1. **Start the Docusaurus development server**:
   ```bash
   cd ai_frontend_book
   npm run start
   # or
   yarn start
   ```

2. **Build for production**:
   ```bash
   npm run build
   # or
   yarn build
   ```

3. **Serve the production build**:
   ```bash
   npm run serve
   # or
   yarn serve
   ```

## Using the Chat Interface

1. **Ask a question**:
   - Type your question in the chat input field
   - Press Enter or click Send to submit
   - View the RAG agent's response with citations

2. **Use selected text**:
   - Select text on the page
   - Click on the chat input or use the context menu
   - The selected text will be included in your query
   - Ask a question about the selected text

## API Client Configuration

The frontend uses an API client to communicate with the RAG backend:

```js
// api-client.js
const apiClient = {
  baseUrl: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
};
```

## Component Structure

The chat interface consists of several components:

- **RagChat**: Main container component
- **ChatInput**: Handles user input and selected text
- **ChatMessage**: Displays individual messages
- **SelectedTextHandler**: Manages text selection functionality

## Troubleshooting

- **CORS errors**: Ensure the backend allows requests from the frontend origin
- **API connection issues**: Verify REACT_APP_BACKEND_URL is set correctly
- **Selected text not working**: Check browser permissions and text selection event handling
- **Styles not loading**: Verify CSS modules are properly configured in Docusaurus