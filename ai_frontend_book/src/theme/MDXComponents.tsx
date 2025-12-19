import React from 'react';
import MDXComponents from '@theme-original/MDXComponents';
import RagChat from '../components/RagChat/RagChat';

type MDXComponentMap = typeof MDXComponents;

const CustomMDXComponents: MDXComponentMap = {
  ...MDXComponents,
  // Add RagChat as an MDX component that can be used in markdown files
  RagChat,
};

export default CustomMDXComponents;