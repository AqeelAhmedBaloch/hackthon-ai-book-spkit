from typing import List, Dict, Optional, Tuple
import time
import logging
from collections import Counter
from ..shared.models import ContentChunk
from ..shared.qdrant_client import QdrantClientWrapper
from .models import (
    ValidationResult, ValidationConfig, ValidationType,
    ValidationSummary, ValidationDetail, QueryValidationResult
)
from ..shared.utils import calculate_similarity, get_logger


class RetrievalValidator:
    """
    Class to validate the retrieval pipeline for accuracy, metadata preservation, and consistency
    """

    def __init__(self):
        self.qdrant_client = QdrantClientWrapper()
        self.logger = get_logger(__name__)

    def validate_accuracy(self, query: str, expected_chunks: Optional[List[ContentChunk]] = None) -> Tuple[float, List[ValidationDetail]]:
        """
        Validate the accuracy of retrieval results
        """
        details = []

        # Retrieve chunks for the query
        # Note: This is a simplified implementation. In a real system, you'd need to:
        # 1. Convert the query to an embedding
        # 2. Search in Qdrant
        # 3. Compare results with expected chunks

        # For now, we'll use a mock implementation
        retrieved_chunks = self.qdrant_client.search_similar([0.1] * 1536, top_k=5)  # Mock embedding

        if expected_chunks is None or not expected_chunks:
            # If no expected chunks provided, we can't validate accuracy
            accuracy_score = 0.0
            details.append(ValidationDetail(
                validation_type="accuracy",
                passed=False,
                expected="specific chunks",
                actual="no expected chunks provided",
                threshold="N/A",
                details="Cannot validate accuracy without expected results"
            ))
        else:
            # Calculate accuracy based on overlap between expected and retrieved chunks
            expected_ids = {chunk.id for chunk in expected_chunks}
            retrieved_ids = {chunk.id for chunk in retrieved_chunks}

            if expected_ids:
                intersection = expected_ids.intersection(retrieved_ids)
                accuracy_score = len(intersection) / len(expected_ids)

                details.append(ValidationDetail(
                    validation_type="accuracy",
                    passed=accuracy_score >= 0.5,  # Basic threshold
                    expected=f"{len(expected_ids)} expected chunks",
                    actual=f"{len(intersection)} matching chunks",
                    threshold="0.5",
                    details=f"Accuracy: {accuracy_score:.2f}"
                ))
            else:
                accuracy_score = 0.0
                details.append(ValidationDetail(
                    validation_type="accuracy",
                    passed=False,
                    expected="specific chunks",
                    actual="no expected chunks",
                    threshold="0.5",
                    details="No expected chunks to compare against"
                ))

        return accuracy_score, details

    def validate_metadata_preservation(self, retrieved_chunks: List[ContentChunk],
                                     expected_chunks: Optional[List[ContentChunk]] = None) -> Tuple[float, List[ValidationDetail]]:
        """
        Validate that metadata is preserved correctly during retrieval
        """
        details = []

        if not retrieved_chunks:
            metadata_preservation_rate = 0.0
            details.append(ValidationDetail(
                validation_type="metadata",
                passed=False,
                expected="metadata preserved",
                actual="no chunks retrieved",
                threshold="1.0",
                details="No chunks to validate metadata for"
            ))
            return metadata_preservation_rate, details

        # Count chunks with preserved metadata
        chunks_with_metadata = 0
        total_chunks = len(retrieved_chunks)

        for chunk in retrieved_chunks:
            if chunk.metadata and len(chunk.metadata) > 0:
                chunks_with_metadata += 1

        metadata_preservation_rate = chunks_with_metadata / total_chunks if total_chunks > 0 else 0.0

        details.append(ValidationDetail(
            validation_type="metadata",
            passed=metadata_preservation_rate >= 0.9,  # 90% threshold
            expected="metadata preserved in 90% of chunks",
            actual=f"metadata preserved in {chunks_with_metadata}/{total_chunks} chunks",
            threshold="0.9",
            details=f"Metadata preservation rate: {metadata_preservation_rate:.2f}"
        ))

        return metadata_preservation_rate, details

    def validate_consistency(self, query: str, num_runs: int = 5) -> Tuple[float, List[ValidationDetail]]:
        """
        Validate that retrieval results are consistent across multiple runs
        """
        details = []

        if num_runs < 2:
            consistency_score = 1.0
            details.append(ValidationDetail(
                validation_type="consistency",
                passed=True,
                expected="consistent results",
                actual="only one run performed",
                threshold="N/A",
                details="Consistency validation requires multiple runs"
            ))
            return consistency_score, details

        # Perform multiple retrieval runs
        all_results = []
        for i in range(num_runs):
            # Mock implementation - in reality, you'd convert query to embedding and search
            run_results = self.qdrant_client.search_similar([0.1 + i * 0.01] * 1536, top_k=5)
            all_results.append([chunk.id for chunk in run_results])

        # Calculate consistency based on how many runs returned the same top results
        if not all_results:
            consistency_score = 0.0
            details.append(ValidationDetail(
                validation_type="consistency",
                passed=False,
                expected="consistent results across runs",
                actual="no results from any runs",
                threshold="0.95",
                details="No results to validate consistency"
            ))
            return consistency_score, details

        # Find the most common result set
        result_sets = [tuple(sorted(run)) for run in all_results]
        result_counts = Counter(result_sets)
        most_common_count = result_counts.most_common(1)[0][1] if result_counts else 0

        consistency_score = most_common_count / num_runs

        details.append(ValidationDetail(
            validation_type="consistency",
            passed=consistency_score >= 0.8,  # 80% threshold
            expected="same results across 80% of runs",
            actual=f"same results in {most_common_count}/{num_runs} runs",
            threshold="0.8",
            details=f"Consistency score: {consistency_score:.2f}"
        ))

        return consistency_score, details

    def validate_retrieval(self, query: str, config: ValidationConfig,
                          expected_chunks: Optional[List[ContentChunk]] = None) -> QueryValidationResult:
        """
        Perform comprehensive validation of retrieval for a single query
        """
        start_time = time.time()

        # Initialize result
        result = QueryValidationResult(
            query=query,
            retrieved_chunks=[],
            expected_chunks=expected_chunks,
            retrieval_time_ms=0.0,
            status="",
            validation_details=[]
        )

        # Perform different types of validation based on config
        all_details = []

        # Accuracy validation
        if config.validation_type in [ValidationType.ACCURACY, ValidationType.ALL]:
            accuracy_score, accuracy_details = self.validate_accuracy(query, expected_chunks)
            result.accuracy_score = accuracy_score
            all_details.extend(accuracy_details)

        # Metadata validation
        if config.validation_type in [ValidationType.METADATA, ValidationType.ALL]:
            metadata_rate, metadata_details = self.validate_metadata_preservation(result.retrieved_chunks, expected_chunks)
            result.metadata_preservation_rate = metadata_rate
            all_details.extend(metadata_details)

        # Consistency validation (only makes sense if we're testing the same query multiple times)
        if config.validation_type in [ValidationType.CONSISTENCY, ValidationType.ALL]:
            consistency_score, consistency_details = self.validate_consistency(query, config.consistency_runs)
            # Note: This is a simplified approach - in practice, consistency would be tested separately
            all_details.extend(consistency_details)

        # Calculate final status
        passed_count = sum(1 for detail in all_details if detail.passed)
        total_count = len(all_details)

        if total_count == 0:
            result.status = "WARNING"
        elif passed_count == total_count:
            result.status = "PASS"
        elif passed_count == 0:
            result.status = "FAIL"
        else:
            result.status = "WARNING"

        result.validation_details = all_details
        result.retrieval_time_ms = (time.time() - start_time) * 1000

        return result

    def run_validation_suite(self, test_queries: List[str], config: ValidationConfig,
                           expected_results: Optional[Dict[str, List[ContentChunk]]] = None) -> ValidationSummary:
        """
        Run a complete validation suite on multiple queries
        """
        start_time = time.time()

        results = []
        for query in test_queries:
            expected = expected_results.get(query) if expected_results else None
            result = self.validate_retrieval(query, config, expected)
            results.append(result)

        # Calculate summary statistics
        total_validations = len(results)
        passed_validations = sum(1 for r in results if r.status == "PASS")
        failed_validations = sum(1 for r in results if r.status == "FAIL")

        # Calculate average metrics
        accuracy_scores = [r.accuracy_score for r in results if r.accuracy_score is not None]
        accuracy_avg = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else None

        metadata_rates = [r.metadata_preservation_rate for r in results if r.metadata_preservation_rate is not None]
        metadata_avg = sum(metadata_rates) / len(metadata_rates) if metadata_rates else None

        avg_retrieval_time = sum(r.retrieval_time_ms for r in results) / len(results) if results else 0

        # Determine overall status
        if passed_validations == total_validations:
            overall_status = "PASS"
        elif failed_validations == total_validations:
            overall_status = "FAIL"
        else:
            overall_status = "WARNING"

        summary = ValidationSummary(
            total_validations=total_validations,
            passed_validations=passed_validations,
            failed_validations=failed_validations,
            accuracy_score=accuracy_avg,
            metadata_preservation_rate=metadata_avg,
            average_retrieval_time_ms=avg_retrieval_time,
            status=overall_status
        )

        self.logger.info(f"Validation suite completed: {summary.passed_validations}/{summary.total_validations} passed")
        return summary