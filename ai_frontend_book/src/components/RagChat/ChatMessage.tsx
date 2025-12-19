import React from 'react';
import './RagChat.module.css';

interface Citation {
  source_document: string;
  page_number?: number;
  section?: string;
  text_snippet: string;
  similarity_score?: number;
}

interface ChatMessageProps {
  message: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  citations?: Citation[];
  status?: 'sent' | 'pending' | 'received' | 'error';
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  sender,
  timestamp,
  citations,
  status = 'received'
}) => {
  const isUser = sender === 'user';
  const isError = status === 'error';
  const isPending = status === 'pending';

  // Format timestamp
  const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'} ${status}`}>
      <div className="message-header">
        <span className="sender-name">{isUser ? 'You' : 'Assistant'}</span>
        <span className="timestamp">{formattedTime}</span>
      </div>

      <div className="message-content">
        {isPending ? (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        ) : (
          <>
            <p>{message}</p>

            {citations && citations.length > 0 && (
              <div className="citations">
                <h4>Sources:</h4>
                <ul>
                  {citations.map((citation, index) => (
                    <li key={index} className="citation-item">
                      <div className="citation-source">
                        <strong>{citation.source_document}</strong>
                        {citation.page_number && <span>, Page {citation.page_number}</span>}
                        {citation.section && <span>, Section: {citation.section}</span>}
                      </div>
                      <div className="citation-text">"{citation.text_snippet}"</div>
                      {citation.similarity_score && (
                        <div className="similarity-score">
                          Relevance: {(citation.similarity_score * 100).toFixed(1)}%
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>

      {isError && (
        <div className="error-message">
          An error occurred. Please try again.
        </div>
      )}
    </div>
  );
};

export default ChatMessage;