from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from ..shared.models import ContentChunk, Citation


class ValidationType(str, Enum):
    """Types of validation that can be performed"""
    ACCURACY = "accuracy"
    METADATA = "metadata"
    CONSISTENCY = "consistency"
    ALL = "all"


class ValidationConfig(BaseModel):
    """Configuration for validation"""
    top_k: int = 5
    similarity_threshold: float = 0.7
    consistency_runs: int = 5
    expected_accuracy_threshold: float = 0.9
    metadata_preservation_threshold: float = 1.0
    consistency_threshold: float = 0.95
    validation_type: ValidationType = ValidationType.ALL


class ValidationResult(BaseModel):
    """Result of a single validation"""
    id: str
    timestamp: datetime = datetime.now()
    query_text: str
    retrieved_chunks: List[ContentChunk]
    expected_chunks: Optional[List[ContentChunk]] = None
    accuracy_score: Optional[float] = None
    metadata_preservation_rate: Optional[float] = None
    consistency_score: Optional[float] = None
    retrieval_time_ms: Optional[float] = None
    status: str  # 'PASS', 'FAIL', 'WARNING'
    details: Optional[Dict[str, Any]] = None


class ValidationRequest(BaseModel):
    """Request for validation"""
    validation_type: ValidationType = ValidationType.ALL
    config: ValidationConfig = ValidationConfig()
    test_queries: Optional[List[str]] = None
    expected_results: Optional[Dict[str, List[ContentChunk]]] = None  # For accuracy testing


class ValidationSummary(BaseModel):
    """Summary of validation results"""
    total_validations: int
    passed_validations: int
    failed_validations: int
    accuracy_score: Optional[float] = None
    metadata_preservation_rate: Optional[float] = None
    consistency_score: Optional[float] = None
    average_retrieval_time_ms: Optional[float] = None
    status: str  # 'PASS', 'FAIL', 'WARNING'


class ValidationDetail(BaseModel):
    """Detailed information about a specific validation"""
    validation_type: str  # 'accuracy', 'metadata', 'consistency'
    passed: bool
    expected: Any
    actual: Any
    threshold: Any
    details: str


class QueryValidationResult(BaseModel):
    """Result for a single query validation"""
    query: str
    retrieved_chunks: List[ContentChunk]
    expected_chunks: Optional[List[ContentChunk]] = None
    citations: List[Citation] = []
    accuracy_score: Optional[float] = None
    metadata_preservation_rate: Optional[float] = None
    retrieval_time_ms: float = 0.0
    status: str  # 'PASS', 'FAIL', 'WARNING'
    validation_details: List[ValidationDetail] = []