// API Configuration
const API_CONFIG = {
  // Default backend URL - will be overridden by environment variables
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',

  // Alternative URLs for different environments
  DEVELOPMENT_URL: process.env.REACT_APP_DEV_API_URL || 'http://localhost:8000',
  PRODUCTION_URL: process.env.REACT_APP_PROD_API_URL || 'https://your-backend-deployment-url.com',

  // API endpoints
  ENDPOINTS: {
    QUERY: '/query',
    HEALTH: '/health',
  },

  // Request timeout in milliseconds
  TIMEOUT: 30000, // 30 seconds

  // Default headers
  HEADERS: {
    'Content-Type': 'application/json',
  },
};

export default API_CONFIG;