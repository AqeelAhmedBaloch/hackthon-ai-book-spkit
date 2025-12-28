import React, { useState, useEffect, useRef } from 'react';
import './ChatbotWidget.css';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Source[];
}

interface Source {
  url: string;
  title?: string;
  score?: number;
}

const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Function to get selected text from the page
  useEffect(() => {
    const handleSelectionChange = () => {
      const selectedText = window.getSelection()?.toString().trim();
      setSelectedText(selectedText || null);
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Prepare the request body with selected text if available
      const requestBody = {
        query: inputText,
        selected_text: selectedText || null
      };

      // Call the backend API
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        citations: data.sources,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error calling chat API:', error);

      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-widget">
      {/* Floating icon */}
      {!isOpen && (
        <button
          className="chatbot-icon"
          onClick={() => setIsOpen(true)}
          aria-label="Open chatbot"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>AI Textbook Assistant</h3>
            <button
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chatbot"
            >
              ×
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="chatbot-welcome">
                <p>Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics book.</p>
                <p>{selectedText ? "I can answer questions about the selected text." : "Ask me anything about the book content!"}</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`chatbot-message chatbot-message-${message.type}`}
                >
                  <div className="chatbot-message-content">
                    {message.content}
                    {message.citations && message.citations.length > 0 && (
                      <div className="chatbot-citations">
                        <strong>Sources:</strong>
                        <ul>
                          {message.citations.map((source: any, idx: number) => (
                            <li key={idx}>
                              <a href={source.url} target="_blank" rel="noopener noreferrer">
                                {source.title || source.url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <div className="chatbot-message-timestamp">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="chatbot-message chatbot-message-assistant">
                <div className="chatbot-message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-form" onSubmit={handleSubmit}>
            {selectedText && (
              <div className="selected-text-indicator">
                Context: Answering from selected text
              </div>
            )}
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={selectedText ? "Ask about the selected text..." : "Ask a question about the book..."}
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !inputText.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatbotWidget;