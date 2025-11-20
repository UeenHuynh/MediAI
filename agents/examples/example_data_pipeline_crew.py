#!/usr/bin/env python3
"""
Example: Data Pipeline Crew

This demonstrates multi-agent coordination:
1. DataIngestionAgent - Load CSV data
2. DataTransformationAgent - Run dbt models
3. DataQualityAgent - Validate data quality

The crew orchestrates these agents in sequence, handling
dependencies and failures.

Usage:
    python example_data_pipeline_crew.py \
        --source-file /path/to/icustays.csv \
        --target-table raw.icustays

"""

import argparse
import logging
import sys
from typing import Dict, Any
from datetime import datetime

# Reuse base classes from previous example
from example_data_ingestion_agent import (
    BaseAgent,
    AgentResult,
    AgentStatus,
    ValidationResult
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ADDITIONAL AGENTS FOR CREW
# ============================================================================

class DataTransformationAgent(BaseAgent):
    """Agent for running dbt transformations."""

    def __init__(self, dbt_project_dir: str):
        super().__init__(
            name="DataTransformationAgent",
            description="Run dbt transformations"
        )
        self.dbt_project_dir = dbt_project_dir

    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate transformation inputs."""
        errors = []

        if 'models' not in context:
            errors.append("Missing required field: models")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute dbt transformation.

        In real implementation, this would run:
            subprocess.run(['dbt', 'run', '--models', models])

        For this example, we simulate success.
        """
        models = context['models']

        logger.info(f"Running dbt models: {models}")

        # Simulate dbt execution
        import time
        time.sleep(2)  # Simulate processing time

        # Return mock result
        result = {
            'command': f'dbt run --models {models}',
            'models_run': 15,
            'tests_passed': 12,
            'success': True
        }

        logger.info(f"✅ dbt execution complete: {result['models_run']} models run")

        return result


class DataQualityAgent(BaseAgent):
    """Agent for data quality validation."""

    def __init__(self, db_connection_string: str):
        super().__init__(
            name="DataQualityAgent",
            description="Validate data quality"
        )
        self.db_connection_string = db_connection_string

    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate quality check inputs."""
        errors = []

        if 'table_name' not in context:
            errors.append("Missing required field: table_name")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data quality checks.

        In real implementation, this would:
        - Query database for null counts
        - Check uniqueness constraints
        - Validate data ranges

        For this example, we simulate checks.
        """
        table_name = context['table_name']

        logger.info(f"Running quality checks on {table_name}")

        # Simulate quality checks
        import time
        time.sleep(1)

        # Mock quality results
        result = {
            'table_name': table_name,
            'checks_run': 8,
            'checks_passed': 8,
            'completeness_score': 0.985,
            'uniqueness_score': 1.0,
            'validity_score': 0.945,
            'overall_score': 0.965
        }

        logger.info(
            f"✅ Quality checks complete: {result['overall_score']:.1%} overall score"
        )

        return result


# ============================================================================
# DATA PIPELINE CREW
# ============================================================================

class DataPipelineCrew:
    """
    Crew for coordinating data pipeline operations.

    Workflow:
    1. Ingest raw data (DataIngestionAgent)
    2. Transform data (DataTransformationAgent)
    3. Validate quality (DataQualityAgent)

    Features:
    - Sequential execution with dependency management
    - Failure handling (stop on first failure)
    - Execution summary
    """

    def __init__(
        self,
        db_connection_string: str,
        dbt_project_dir: str = './dbt_project'
    ):
        """Initialize crew with agents."""
        self.db_connection_string = db_connection_string
        self.dbt_project_dir = dbt_project_dir

        # Initialize agents (using simplified version for demo)
        from example_data_ingestion_agent import DataIngestionAgent

        self.agents = {
            'ingestion': DataIngestionAgent(db_connection_string),
            'transformation': DataTransformationAgent(dbt_project_dir),
            'quality': DataQualityAgent(db_connection_string)
        }

        logger.info("DataPipelineCrew initialized")

    def kickoff(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute crew workflow.

        Args:
            context: Execution context with inputs for each agent

        Returns:
            Dict with execution summary and results
        """
        logger.info("=" * 70)
        logger.info("DATA PIPELINE CREW - Starting Execution")
        logger.info("=" * 70)

        start_time = datetime.now()
        results = {}

        try:
            # Task 1: Data Ingestion
            if 'ingestion' in context:
                logger.info("\n[Task 1/3] Data Ingestion")
                logger.info("-" * 70)

                ingestion_result = self.agents['ingestion'].execute(
                    context['ingestion']
                )
                results['ingestion'] = ingestion_result.to_dict()

                if not ingestion_result.is_success():
                    return self._failure_result(
                        "Data ingestion failed",
                        results,
                        start_time
                    )

                logger.info(
                    f"✅ Ingested {ingestion_result.output['rows_ingested']:,} rows"
                )

            # Task 2: dbt Transformation
            if 'transformation' in context:
                logger.info("\n[Task 2/3] dbt Transformation")
                logger.info("-" * 70)

                transformation_result = self.agents['transformation'].execute(
                    context['transformation']
                )
                results['transformation'] = transformation_result.to_dict()

                if not transformation_result.is_success():
                    return self._failure_result(
                        "Transformation failed",
                        results,
                        start_time
                    )

                logger.info(
                    f"✅ Ran {transformation_result.output['models_run']} models"
                )

            # Task 3: Data Quality
            if 'quality' in context:
                logger.info("\n[Task 3/3] Data Quality Validation")
                logger.info("-" * 70)

                quality_result = self.agents['quality'].execute(
                    context['quality']
                )
                results['quality'] = quality_result.to_dict()

                if not quality_result.is_success():
                    return self._failure_result(
                        "Quality validation failed",
                        results,
                        start_time
                    )

                quality_score = quality_result.output['overall_score']
                logger.info(f"✅ Quality score: {quality_score:.1%}")

                # Check if quality meets threshold
                if quality_score < 0.90:
                    return self._failure_result(
                        f"Quality score too low: {quality_score:.1%} (threshold: 90%)",
                        results,
                        start_time
                    )

            # Success
            return self._success_result(results, start_time)

        except Exception as e:
            logger.exception("Unexpected error in crew execution")
            return self._failure_result(
                f"Unexpected error: {str(e)}",
                results,
                start_time
            )

    def _success_result(
        self,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Create success result."""
        execution_time = (datetime.now() - start_time).total_seconds()

        logger.info("\n" + "=" * 70)
        logger.info("✅ DATA PIPELINE CREW - EXECUTION SUCCESSFUL")
        logger.info("=" * 70)
        logger.info(f"Execution time: {execution_time:.2f}s")
        logger.info("=" * 70)

        return {
            'status': 'success',
            'results': results,
            'execution_time_seconds': execution_time,
            'timestamp': datetime.now().isoformat()
        }

    def _failure_result(
        self,
        reason: str,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Create failure result."""
        execution_time = (datetime.now() - start_time).total_seconds()

        logger.error("\n" + "=" * 70)
        logger.error("❌ DATA PIPELINE CREW - EXECUTION FAILED")
        logger.error("=" * 70)
        logger.error(f"Reason: {reason}")
        logger.error(f"Execution time: {execution_time:.2f}s")
        logger.error("=" * 70)

        return {
            'status': 'failed',
            'reason': reason,
            'results': results,
            'execution_time_seconds': execution_time,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Data Pipeline Crew - Orchestrate multi-agent workflow'
    )
    parser.add_argument(
        '--source-file',
        required=True,
        help='Path to source CSV file'
    )
    parser.add_argument(
        '--target-table',
        required=True,
        help='Target table (e.g., raw.icustays)'
    )
    parser.add_argument(
        '--database-url',
        default='postgresql://postgres:password@localhost:5432/mimic_iv',
        help='PostgreSQL connection string'
    )
    parser.add_argument(
        '--dbt-project-dir',
        default='./dbt_project',
        help='Path to dbt project directory'
    )

    args = parser.parse_args()

    # Initialize crew
    crew = DataPipelineCrew(
        db_connection_string=args.database_url,
        dbt_project_dir=args.dbt_project_dir
    )

    # Execute crew
    context = {
        'ingestion': {
            'source_file': args.source_file,
            'target_table': args.target_table
        },
        'transformation': {
            'models': ['staging.*', 'marts.*']
        },
        'quality': {
            'table_name': args.target_table
        }
    }

    result = crew.kickoff(context)

    # Exit with appropriate code
    if result['status'] == 'success':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
