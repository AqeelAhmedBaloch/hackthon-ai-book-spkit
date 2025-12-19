from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ValidationConfig(BaseModel):
    """Configuration for validation operations"""

    # Accuracy validation settings
    expected_accuracy_threshold: float = float(os.getenv("EXPECTED_ACCURACY_THRESHOLD", "0.9"))
    accuracy_sample_size: int = int(os.getenv("ACCURACY_SAMPLE_SIZE", "10"))

    # Metadata validation settings
    expected_metadata_preservation_threshold: float = float(os.getenv("METADATA_PRESERVATION_THRESHOLD", "1.0"))

    # Consistency validation settings
    expected_consistency_threshold: float = float(os.getenv("CONSISTENCY_THRESHOLD", "0.95"))
    consistency_test_runs: int = int(os.getenv("CONSISTENCY_TEST_RUNS", "5"))

    # General validation settings
    validation_batch_size: int = int(os.getenv("VALIDATION_BATCH_SIZE", "5"))
    validation_timeout_seconds: int = int(os.getenv("VALIDATION_TIMEOUT_SECONDS", "30"))
    enable_detailed_logging: bool = os.getenv("ENABLE_DETAILED_LOGGING", "false").lower() == "true"

    # Qdrant-specific validation settings
    qdrant_validation_collection: str = os.getenv("QDRANT_VALIDATION_COLLECTION", "validation_tests")

    class Config:
        case_sensitive = True


# Create a singleton instance
validation_config = ValidationConfig()