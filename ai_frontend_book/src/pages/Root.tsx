import React from 'react';
import ChatbotWidget from '../components/ChatbotWidget';

const Root = ({children}: {children: React.ReactNode}) => {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
};

export default Root;