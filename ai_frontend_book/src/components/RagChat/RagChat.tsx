import React, { useState, useEffect, useRef } from 'react';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import SelectedTextHandler from './SelectedTextHandler';
import './RagChat.module.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  citations?: any[];
  status?: 'sent' | 'pending' | 'received' | 'error';
}

interface RagChatProps {
  backendUrl?: string;
}

const RagChat: React.FC<RagChatProps> = ({ backendUrl = 'http://localhost:8000' }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [connectionError, setConnectionError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      const selectedText = window.getSelection()?.toString().trim() || '';
      setSelectedText(selectedText);
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch(`${backendUrl}/health`);
      const data = await response.json();
      setConnectionError(!data.qdrant_connected || !data.openai_connected);
      return data.qdrant_connected && data.openai_connected;
    } catch (error) {
      setConnectionError(true);
      return false;
    }
  };

  const handleSubmit = async (query: string) => {
    // Check connection before submitting
    const isConnected = await checkConnection();
    if (!isConnected) {
      // Add connection error message
      const errorMessage: Message = {
        id: `connection_error_${Date.now()}`,
        content: 'Unable to connect to the backend service. Please check your connection and try again.',
        sender: 'assistant',
        timestamp: new Date(),
        status: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: selectedText ? `Based on this text: "${selectedText}". ${query}` : query,
      sender: 'user',
      timestamp: new Date(),
      status: 'sent'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch(`${backendUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          selected_text: selectedText || undefined,
          page_url: window.location.href,
          session_id: 'session_' + Date.now()
        }),
      });

      if (!response.ok) {
        // Try to get error details from response
        let errorMessage = `API request failed with status ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (e) {
          // If we can't parse the error, use the default message
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        content: data.response,
        sender: 'assistant',
        timestamp: new Date(),
        citations: data.citations || [],
        status: 'received'
      };

      setMessages(prev => [...prev, assistantMessage]);
      setRetryCount(0); // Reset retry count on success
    } catch (error: any) {
      console.error('Error submitting query:', error);

      // Add error message with user-friendly text
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        content: error.message || 'Sorry, there was an error processing your request. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        status: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);

      // Increment retry count for potential backoff strategy
      setRetryCount(prev => prev + 1);
    } finally {
      setIsLoading(false);
      setSelectedText(''); // Clear selected text after submission
    }
  };

  return (
    <div className="rag-chat-container">
      <div className="rag-chat-header">
        <h3>Ask about this book</h3>
        {connectionError && (
          <div className="connection-error">
            ⚠️ Service may be unavailable. Some features might not work properly.
          </div>
        )}
      </div>

      <div className="rag-chat-messages">
        {messages.length === 0 ? (
          <div className="rag-chat-welcome">
            <p>Ask me anything about this book! Select text and ask a question about it, or ask a general question.</p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message.content}
              sender={message.sender}
              timestamp={message.timestamp}
              citations={message.citations}
              status={message.status}
            />
          ))
        )}
        {isLoading && (
          <ChatMessage
            message="Thinking..."
            sender="assistant"
            timestamp={new Date()}
            status="pending"
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="rag-chat-input-area">
        {selectedText && (
          <SelectedTextHandler
            selectedText={selectedText}
            onClear={() => setSelectedText('')}
          />
        )}
        <ChatInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          placeholder={selectedText ? "Ask about the selected text..." : "Ask a question about the book..."}
        />
      </div>
    </div>
  );
};

export default RagChat;