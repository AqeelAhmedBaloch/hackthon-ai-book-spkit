# Quickstart: Retrieval Validation

## Prerequisites

- Python 3.11+
- Access to Qdrant instance with existing embeddings from Spec-1
- Required Python packages (see requirements.txt)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Qdrant connection**:
   ```bash
   # Set environment variables
   export QDRANT_URL="your-qdrant-url"
   export QDRANT_API_KEY="your-api-key"  # if required
   export QDRANT_COLLECTION="your-collection-name"
   ```

3. **Verify connection**:
   ```bash
   python -c "from backend.src.retrieval_validation.client import QdrantClientWrapper; client = QdrantClientWrapper(); print('Connection successful' if client.health_check() else 'Connection failed')"
   ```

## Running Validation

1. **Run basic validation**:
   ```bash
   python backend/src/retrieval_validation/main.py validate
   ```

2. **Run validation with custom config**:
   ```bash
   python backend/src/retrieval_validation/main.py validate --config-path path/to/config.json
   ```

3. **Run specific validation type**:
   ```bash
   python backend/src/retrieval_validation/main.py validate --validation-type accuracy
   ```

## Configuration

Create a config file to customize validation behavior:

```json
{
  "top_k": 5,
  "similarity_threshold": 0.7,
  "consistency_runs": 5,
  "test_queries": [
    "What is the main concept discussed in chapter 1?",
    "Explain the implementation details of the system",
    "How does the retrieval mechanism work?"
  ],
  "expected_accuracy_threshold": 0.9,
  "metadata_preservation_threshold": 1.0,
  "consistency_threshold": 0.95
}
```

## Output Format

The validation will output results in JSON format:

```json
{
  "id": "validation_123",
  "timestamp": "2023-12-19T10:00:00Z",
  "summary": {
    "accuracy_score": 0.95,
    "metadata_preservation_rate": 1.0,
    "consistency_score": 0.98,
    "retrieval_time_ms": 125.3,
    "status": "PASS"
  },
  "details": {
    "accuracy_validation": {
      "passed": true,
      "expected": 0.9,
      "actual": 0.95
    },
    "metadata_validation": {
      "passed": true,
      "expected": 1.0,
      "actual": 1.0
    },
    "consistency_validation": {
      "passed": true,
      "expected": 0.95,
      "actual": 0.98
    }
  }
}
```

## Troubleshooting

- **Connection issues**: Verify QDRANT_URL and API key are correctly set
- **No results returned**: Check that the collection name is correct and contains embeddings
- **Poor accuracy**: Verify that test queries are relevant to the embedded content