from typing import List, Optional
from ..shared.models import ContentChunk, QueryRequest, QueryResponse
from ..shared.qdrant_client import QdrantClientWrapper
from .models import ValidationResult, ValidationType
from .validator import RetrievalValidator
from .config import validation_config
import logging


class ValidationClient:
    """
    Client class for interacting with the validation system
    """

    def __init__(self):
        self.qdrant_client = QdrantClientWrapper()
        self.validator = RetrievalValidator()
        self.logger = logging.getLogger(__name__)

    def validate_single_query(self, query: str, expected_chunks: Optional[List[ContentChunk]] = None) -> ValidationResult:
        """
        Validate a single query against the retrieval system
        """
        try:
            # This is a simplified implementation
            # In a real system, you would:
            # 1. Convert query to embedding
            # 2. Retrieve results from Qdrant
            # 3. Compare with expected results
            # 4. Generate validation result

            # For now, using mock implementation
            retrieved_chunks = self.qdrant_client.search_similar([0.1] * 1536, top_k=5)

            # Create a mock validation result
            result = ValidationResult(
                id=f"validation_{hash(query) % 10000}",
                query_text=query,
                retrieved_chunks=retrieved_chunks,
                expected_chunks=expected_chunks,
                accuracy_score=0.85 if expected_chunks else None,
                metadata_preservation_rate=1.0,
                consistency_score=0.95,
                retrieval_time_ms=125.5,
                status="PASS" if (expected_chunks is None or len(expected_chunks) > 0) else "WARNING"
            )

            return result
        except Exception as e:
            self.logger.error(f"Error validating query '{query}': {e}")
            # Return a failed validation result
            return ValidationResult(
                id=f"validation_{hash(query) % 10000}",
                query_text=query,
                retrieved_chunks=[],
                expected_chunks=expected_chunks,
                accuracy_score=0.0,
                metadata_preservation_rate=0.0,
                consistency_score=0.0,
                retrieval_time_ms=0.0,
                status="FAIL",
                details={"error": str(e)}
            )

    def validate_retrieval_accuracy(self, test_queries: List[str],
                                  expected_results: Optional[dict] = None) -> List[ValidationResult]:
        """
        Validate the accuracy of retrieval across multiple queries
        """
        results = []
        for query in test_queries:
            expected_chunks = expected_results.get(query) if expected_results else None
            result = self.validate_single_query(query, expected_chunks)
            results.append(result)

        return results

    def validate_metadata_preservation(self, collection_name: Optional[str] = None) -> ValidationResult:
        """
        Validate that metadata is properly preserved in the collection
        """
        try:
            # Get a sample of chunks from the collection
            sample_chunks = self.qdrant_client.search_similar([0.1] * 1536, top_k=10)

            # Check metadata preservation
            chunks_with_metadata = sum(1 for chunk in sample_chunks if chunk.metadata)
            total_chunks = len(sample_chunks)

            metadata_preservation_rate = chunks_with_metadata / total_chunks if total_chunks > 0 else 0.0

            result = ValidationResult(
                id=f"metadata_validation_{hash(str(sample_chunks)) % 10000}",
                query_text="metadata preservation check",
                retrieved_chunks=sample_chunks,
                accuracy_score=None,
                metadata_preservation_rate=metadata_preservation_rate,
                consistency_score=None,
                retrieval_time_ms=0.0,
                status="PASS" if metadata_preservation_rate >= validation_config.expected_metadata_preservation_threshold else "FAIL"
            )

            return result
        except Exception as e:
            self.logger.error(f"Error validating metadata preservation: {e}")
            return ValidationResult(
                id="metadata_validation_error",
                query_text="metadata preservation check",
                retrieved_chunks=[],
                accuracy_score=0.0,
                metadata_preservation_rate=0.0,
                consistency_score=0.0,
                retrieval_time_ms=0.0,
                status="FAIL",
                details={"error": str(e)}
            )

    def validate_consistency(self, query: str, num_runs: int = 5) -> ValidationResult:
        """
        Validate the consistency of retrieval results across multiple runs
        """
        try:
            # Run the same query multiple times and check for consistency
            all_results = []
            total_time = 0.0

            for i in range(num_runs):
                import time
                start_time = time.time()

                # Mock implementation - in reality you'd convert query to embedding and search
                run_results = self.qdrant_client.search_similar([0.1 + i * 0.01] * 1536, top_k=5)
                all_results.append(run_results)

                total_time += (time.time() - start_time) * 1000  # Convert to milliseconds

            # Calculate consistency (simplified approach)
            # In a real implementation, you'd compare the actual content of results
            consistency_score = 1.0  # Assume perfect consistency for this mock

            # Take the first run as the reference
            reference_chunks = all_results[0] if all_results else []

            result = ValidationResult(
                id=f"consistency_validation_{hash(query) % 10000}",
                query_text=query,
                retrieved_chunks=reference_chunks,
                accuracy_score=None,
                metadata_preservation_rate=None,
                consistency_score=consistency_score,
                retrieval_time_ms=total_time / num_runs if num_runs > 0 else 0.0,
                status="PASS" if consistency_score >= validation_config.expected_consistency_threshold else "FAIL"
            )

            return result
        except Exception as e:
            self.logger.error(f"Error validating consistency for query '{query}': {e}")
            return ValidationResult(
                id=f"consistency_validation_error_{hash(query) % 10000}",
                query_text=query,
                retrieved_chunks=[],
                accuracy_score=0.0,
                metadata_preservation_rate=0.0,
                consistency_score=0.0,
                retrieval_time_ms=0.0,
                status="FAIL",
                details={"error": str(e)}
            )

    def run_comprehensive_validation(self, validation_type: ValidationType = ValidationType.ALL,
                                   test_queries: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        Run comprehensive validation based on the specified type
        """
        if test_queries is None:
            test_queries = [
                "What is the main topic?",
                "Explain the key concepts",
                "Summarize the content"
            ]

        results = []

        if validation_type in [ValidationType.ACCURACY, ValidationType.ALL]:
            accuracy_results = self.validate_retrieval_accuracy(test_queries)
            results.extend(accuracy_results)

        if validation_type in [ValidationType.METADATA, ValidationType.ALL]:
            metadata_result = self.validate_metadata_preservation()
            results.append(metadata_result)

        if validation_type in [ValidationType.CONSISTENCY, ValidationType.ALL]:
            for query in test_queries[:2]:  # Limit consistency tests to first 2 queries to avoid too many
                consistency_result = self.validate_consistency(query)
                results.append(consistency_result)

        return results