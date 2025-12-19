import asyncio
import argparse
import sys
import logging
from typing import List, Optional
from datetime import datetime

from ..shared.models import ContentChunk
from .validator import RetrievalValidator
from .models import ValidationConfig, ValidationType, ValidationRequest, ValidationSummary
from ..shared.qdrant_client import QdrantClientWrapper
from ..shared.config import config


class ValidationService:
    """
    Main service class for retrieval validation
    """

    def __init__(self):
        self.validator = RetrievalValidator()
        self.qdrant_client = QdrantClientWrapper()
        self.logger = logging.getLogger(__name__)

    async def run_validation(self, request: ValidationRequest) -> ValidationSummary:
        """
        Run validation based on the request configuration
        """
        # Set up default test queries if none provided
        if not request.test_queries:
            # Try to get some sample queries from the collection
            sample_chunks = self.qdrant_client.search_similar([0.1] * 1536, top_k=3)
            request.test_queries = [chunk.content[:100] + "..." for chunk in sample_chunks if len(chunk.content) > 20]

            # If still no queries, use some default test queries
            if not request.test_queries:
                request.test_queries = [
                    "What is the main topic of this book?",
                    "Explain the key concepts discussed in this content",
                    "Summarize the important points from this text"
                ]

        # Run the validation suite
        summary = self.validator.run_validation_suite(
            test_queries=request.test_queries,
            config=request.config,
            expected_results=request.expected_results
        )

        return summary

    def validate_retrieval_pipeline(self, validation_type: ValidationType = ValidationType.ALL,
                                  top_k: int = 5,
                                  similarity_threshold: float = 0.7,
                                  consistency_runs: int = 5,
                                  test_queries: Optional[List[str]] = None) -> ValidationSummary:
        """
        Convenience method to run validation with common parameters
        """
        config = ValidationConfig(
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            consistency_runs=consistency_runs,
            validation_type=validation_type
        )

        request = ValidationRequest(
            validation_type=validation_type,
            config=config,
            test_queries=test_queries
        )

        # Since run_validation is async, we need to run it in an event loop
        try:
            summary = asyncio.run(self.run_validation(request))
            return summary
        except Exception as e:
            self.logger.error(f"Error running validation: {e}")
            raise


def main():
    """
    Command-line interface for retrieval validation
    """
    parser = argparse.ArgumentParser(description="Retrieval Validation for RAG System")
    parser.add_argument("--type", choices=["accuracy", "metadata", "consistency", "all"],
                       default="all", help="Type of validation to perform")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top results to retrieve")
    parser.add_argument("--similarity-threshold", type=float, default=0.7, help="Similarity threshold")
    parser.add_argument("--consistency-runs", type=int, default=5, help="Number of runs for consistency check")
    parser.add_argument("--query", action="append", dest="queries", help="Test query (can be used multiple times)")
    parser.add_argument("--collection", help="Qdrant collection to validate (default from config)")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Set up validation service
    service = ValidationService()

    # Set validation type
    validation_type = ValidationType(args.type)

    # Use provided queries or default ones
    test_queries = args.queries or [
        "What is the main topic of this content?",
        "Explain the key concepts discussed here",
    ]

    try:
        summary = service.validate_retrieval_pipeline(
            validation_type=validation_type,
            top_k=args.top_k,
            similarity_threshold=args.similarity_threshold,
            consistency_runs=args.consistency_runs,
            test_queries=test_queries
        )

        print(f"\nValidation Summary:")
        print(f"  Status: {summary.status}")
        print(f"  Total validations: {summary.total_validations}")
        print(f"  Passed: {summary.passed_validations}")
        print(f"  Failed: {summary.failed_validations}")

        if summary.accuracy_score is not None:
            print(f"  Accuracy Score: {summary.accuracy_score:.2f}")
        if summary.metadata_preservation_rate is not None:
            print(f"  Metadata Preservation: {summary.metadata_preservation_rate:.2f}")
        print(f"  Avg Retrieval Time: {summary.average_retrieval_time_ms:.2f}ms")

        # Exit with error code if validation failed
        if summary.status == "FAIL":
            sys.exit(1)
        elif summary.status == "WARNING":
            sys.exit(2)  # Use different exit code for warnings

    except Exception as e:
        print(f"Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()