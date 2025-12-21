# Quickstart Guide: Retrieval Validation

**Feature**: 6-retrieval-validation
**Created**: 2025-12-21

## Prerequisites

- Completion of Spec-1 (Content Ingestion & Embeddings)
- Qdrant Cloud with stored embeddings from Spec-1
- Access to Cohere embeddings for validation
- Python 3.11 or higher
- UV package manager

## Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Add Validation Dependencies
```bash
# Add validation-specific dependencies to existing project
uv add numpy pytest python-dotenv
```

### 3. Update Environment Variables
Ensure the following variables from Spec-1 are set in your `.env` file:
```bash
# From Spec-1
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
ENVIRONMENT=development
LOG_LEVEL=info
```

## Project Structure

```
backend/
├── validation/
│   ├── __init__.py
│   ├── config.py                 # Validation configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── query_request.py      # Query request data model
│   │   ├── retrieval_result.py   # Retrieval result model
│   │   └── validation_report.py  # Validation report model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── qdrant_connector.py   # Qdrant connection service
│   │   ├── similarity_engine.py  # Similarity calculation service
│   │   ├── validation_engine.py  # Main validation orchestration
│   │   ├── metadata_validator.py # Metadata validation service
│   │   └── consistency_checker.py # Consistency validation service
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── run_retrieval_validation.py # Main validation script
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_similarity.py    # Similarity validation tests
│   │   ├── test_metadata.py      # Metadata validation tests
│   │   └── test_consistency.py   # Consistency validation tests
│   └── utils/
│       ├── __init__.py
│       ├── metrics_calculator.py # Metrics calculation utilities
│       └── validators.py         # Validation utilities
├── .env
├── pyproject.toml
└── main.py
```

## Core Implementation

### 1. Validation Configuration (`validation/config.py`)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class ValidationSettings(BaseSettings):
    qdrant_url: str
    qdrant_api_key: str
    similarity_threshold: float = 0.5
    top_k: int = 5
    consistency_iterations: int = 100
    validation_timeout: int = 300  # 5 minutes
    log_level: str = "info"

    class Config:
        env_file = ".env"

validation_settings = ValidationSettings()
```

### 2. Main Validation Script (`validation/scripts/run_retrieval_validation.py`)
```python
import asyncio
from validation.services.validation_engine import ValidationEngine
from validation.config import validation_settings

async def run_validation():
    """Main function to run retrieval validation tests"""
    engine = ValidationEngine()

    # Define test queries for validation
    test_queries = [
        "What is ROS 2?",
        "Explain humanoid robotics",
        "How to use Docusaurus",
        "What are vector embeddings?",
        "Explain Qdrant database"
    ]

    # Run comprehensive validation
    report = await engine.run_comprehensive_validation(
        test_queries=test_queries,
        similarity_threshold=validation_settings.similarity_threshold,
        top_k=validation_settings.top_k,
        consistency_iterations=validation_settings.consistency_iterations
    )

    # Print validation results
    print(f"Validation completed with ID: {report.id}")
    print(f"Top-3 accuracy: {report.top_k_accuracy['top_3']:.2f}%")
    print(f"Metadata accuracy: {report.metadata_accuracy:.2f}%")
    print(f"Consistency score: {report.consistency_score:.2f}%")
    print(f"Relevance percentage: {report.relevance_percentage:.2f}%")

    # Check success criteria
    criteria = report.passed_criteria
    print(f"\nSuccess Criteria Results:")
    print(f"SC-001 (Top-3 accuracy ≥90%): {'PASS' if criteria['sc_001_top_3_accuracy'] else 'FAIL'}")
    print(f"SC-002 (Metadata accuracy 100%): {'PASS' if criteria['sc_002_metadata_accuracy'] else 'FAIL'}")
    print(f"SC-003 (Consistency ≥95%): {'PASS' if criteria['sc_003_consistency'] else 'FAIL'}")
    print(f"SC-004 (Scale test ≥10,000): {'PASS' if criteria['sc_004_scale_test'] else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(run_validation())
```

## Running Validation Tests

### Execute Full Validation
```bash
# Run the main validation script
uv run python -m validation.scripts.run_retrieval_validation
```

### Run Specific Validation Tests
```bash
# Run similarity validation only
uv run pytest validation/tests/test_similarity.py -v

# Run metadata validation only
uv run pytest validation/tests/test_metadata.py -v

# Run consistency validation only
uv run pytest validation/tests/test_consistency.py -v
```

## API Usage Example

### Start Validation Run
```bash
curl -X POST http://localhost:8000/api/v1/validation/run \
  -H "Content-Type: application/json" \
  -d '{
    "test_queries": ["What is ROS 2?", "Explain humanoid robotics"],
    "similarity_threshold": 0.5,
    "top_k": 5,
    "validation_type": "comprehensive",
    "consistency_iterations": 100
  }'
```

### Check Validation Results
```bash
curl -X GET http://localhost:8000/api/v1/validation/{validation_id}
```

## Testing

### Run All Validation Tests
```bash
# Install test dependencies if not already installed
uv add pytest pytest-asyncio httpx

# Run all validation tests
uv run pytest validation/tests/ -v
```

### Run Specific Validation Scenarios
```bash
# Test metadata preservation
uv run pytest validation/tests/test_metadata.py::test_metadata_preservation -v

# Test consistency across queries
uv run pytest validation/tests/test_consistency.py::test_query_consistency -v

# Test top-k accuracy
uv run pytest validation/tests/test_similarity.py::test_top_k_accuracy -v
```

## Configuration Options

### Validation Parameters
- `similarity_threshold`: Minimum similarity score (0.0-1.0, default 0.5)
- `top_k`: Number of results to validate (default 5)
- `consistency_iterations`: Number of times to repeat queries for consistency (default 100)
- `validation_timeout`: Maximum time to wait for validation completion (default 300 seconds)

## Next Steps

1. Implement the Qdrant connector service
2. Build the similarity engine for relevance calculations
3. Create the validation engine for orchestrating tests
4. Develop metadata and consistency validation services
5. Add comprehensive error handling and logging
6. Implement the API endpoints as defined in the contract