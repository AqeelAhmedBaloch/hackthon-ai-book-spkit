import React from 'react';
import './RagChat.module.css';

interface SelectedTextHandlerProps {
  selectedText: string;
  onClear: () => void;
}

const SelectedTextHandler: React.FC<SelectedTextHandlerProps> = ({
  selectedText,
  onClear
}) => {
  return (
    <div className="selected-text-handler">
      <div className="selected-text-preview">
        <strong>Selected text:</strong>
        <p>"{selectedText.length > 100 ? selectedText.substring(0, 100) + '...' : selectedText}"</p>
      </div>
      <button
        onClick={onClear}
        className="clear-selection-button"
        title="Clear selection"
      >
        ×
      </button>
    </div>
  );
};

export default SelectedTextHandler;