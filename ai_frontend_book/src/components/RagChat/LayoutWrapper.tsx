import React from 'react';
import Layout from '@theme/Layout';
import RagChat from './RagChat';

interface LayoutWrapperProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  backendUrl?: string;
}

const LayoutWrapper: React.FC<LayoutWrapperProps> = ({
  children,
  title,
  description,
  backendUrl = 'http://localhost:8000'
}) => {
  return (
    <Layout title={title} description={description}>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <main style={{ flex: 1, position: 'relative' }}>
          {children}
        </main>

        {/* RagChat component positioned at the bottom */}
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '400px',
          height: '500px',
          zIndex: 1000
        }}>
          <RagChat backendUrl={backendUrl} />
        </div>
      </div>
    </Layout>
  );
};

export default LayoutWrapper;