# Data Model: Backend Entry Points

## Configuration Settings

### Server Settings
- **HOST**: string (server host address, default: "0.0.0.0")
- **PORT**: integer (server port number, default: 8000)
- **DEBUG**: boolean (debug mode enabled, default: false)

### API Settings
- **API_V1_STR**: string (API version prefix, default: "/api/v1")
- **PROJECT_NAME**: string (project name, default: "RAG Chatbot Backend")

### CORS Settings
- **BACKEND_CORS_ORIGINS**: string (CORS allowed origins, default: "*")

### Ingestion Settings
- **INGESTION_TIMEOUT**: integer (request timeout in seconds, default: 30)
- **INGESTION_RATE_LIMIT**: integer (max requests per minute, default: 1000)
- **INGESTION_MAX_RETRIES**: integer (max retry attempts, default: 3)
- **INGESTION_CONCURRENT_WORKERS**: integer (number of concurrent workers, default: 5)

### Content Settings
- **CONTENT_URL_PATTERNS**: string (URL patterns for content, default: "/docs/*,/book/*,/content/*")

### Logging Settings
- **LOG_LEVEL**: string (logging level, default: "INFO")
- **LOG_FORMAT**: string (logging format string)

### API Keys
- **QDRANT_URL**: string (nullable) - Qdrant vector database URL
- **QDRANT_API_KEY**: string (nullable) - Qdrant API key
- **QDRANT_COLLECTION_NAME**: string (collection name, default: "book_content")
- **COHERE_API_KEY**: string (nullable) - Cohere API key
- **OPENAI_API_KEY**: string (nullable) - OpenAI API key
- **ANTHROPIC_API_KEY**: string (nullable) - Anthropic API key

## API Response Models

### HealthCheck
- **status**: string (health status: "healthy", "unhealthy")
- **service**: string (service name)
- **timestamp**: number (timestamp of check)

### IngestionResult
- **sitemap_url**: string (source sitemap URL)
- **urls_found**: integer (number of URLs extracted)
- **urls**: array of strings (extracted URLs)
- **status**: string (status: "success", "error")

### ErrorResult
- **error**: string (error message)
- **status_code**: integer (HTTP status code)

## Service Integration Models

### IngestionService Configuration
- **timeout**: integer (request timeout)
- **rate_limit**: integer (requests per minute)
- **max_retries**: integer (retry attempts)
- **concurrent_workers**: integer (parallel workers)

### AgentWrapper Models
- **command**: string (agent command)
- **parameters**: object (command parameters)
- **result**: object (command result)
- **status**: string (execution status)