"""Data pipeline crew - orchestrates data ingestion, transformation, and quality checks."""

from typing import Dict, Any, List
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.roles.data_engineer import (
    DataIngestionAgent,
    DataTransformationAgent,
    DataQualityAgent
)

logger = logging.getLogger(__name__)


class DataPipelineCrew:
    """
    Crew for data pipeline operations.

    Coordinates:
    - Data ingestion
    - dbt transformations
    - Data quality validation
    """

    def __init__(self):
        """Initialize data pipeline crew."""
        self.db_connection = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/mimic_iv')
        self.dbt_project_dir = os.getenv('DBT_PROJECT_DIR', './dbt_project')

        # Initialize agents
        logger.info("Initializing Data Pipeline Crew...")
        self.ingestion_agent = DataIngestionAgent(self.db_connection)
        self.transformation_agent = DataTransformationAgent(self.dbt_project_dir)
        self.quality_agent = DataQualityAgent(self.db_connection)
        logger.info("Data Pipeline Crew initialized")

    def kickoff(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data pipeline crew.

        Args:
            context: Execution context with inputs
                Format:
                {
                    'ingestion': {
                        'source_file': '/path/to/data.csv',
                        'target_table': 'raw.icustays'
                    },
                    'transformation': {
                        'command': 'run',
                        'models': ['staging.*']
                    },
                    'quality': {
                        'table_name': 'raw.icustays',
                        'checks': ['completeness', 'uniqueness']
                    }
                }

        Returns:
            Dict with execution results
        """
        logger.info("=" * 60)
        logger.info("DATA PIPELINE CREW - Starting execution")
        logger.info("=" * 60)

        results = {}

        # Task 1: Data Ingestion
        if 'ingestion' in context:
            logger.info("\n[Task 1/3] Data Ingestion")
            logger.info("-" * 60)
            ingestion_result = self.ingestion_agent.execute(context['ingestion'])
            results['ingestion'] = ingestion_result.to_dict()

            if not ingestion_result.is_success():
                logger.error("Data ingestion failed, aborting pipeline")
                return {'status': 'failed', 'results': results, 'failed_at': 'ingestion'}

            logger.info(f"✓ Ingestion complete: {ingestion_result.output['rows_ingested']} rows")

        # Task 2: dbt Transformation
        if 'transformation' in context:
            logger.info("\n[Task 2/3] dbt Transformation")
            logger.info("-" * 60)
            transformation_result = self.transformation_agent.execute(context['transformation'])
            results['transformation'] = transformation_result.to_dict()

            if not transformation_result.is_success():
                logger.error("dbt transformation failed, aborting pipeline")
                return {'status': 'failed', 'results': results, 'failed_at': 'transformation'}

            logger.info("✓ Transformation complete")

        # Task 3: Data Quality
        if 'quality' in context:
            logger.info("\n[Task 3/3] Data Quality Validation")
            logger.info("-" * 60)
            quality_result = self.quality_agent.execute(context['quality'])
            results['quality'] = quality_result.to_dict()

            if not quality_result.is_success():
                logger.warning("Data quality checks failed")
                return {'status': 'failed', 'results': results, 'failed_at': 'quality'}

            quality_score = quality_result.output.get('overall_score', 0)
            logger.info(f"✓ Quality check complete: {quality_score:.1%} score")

        logger.info("\n" + "=" * 60)
        logger.info("DATA PIPELINE CREW - Execution complete")
        logger.info("=" * 60)

        return {'status': 'success', 'results': results}

    def run_ingestion_only(self, source_file: str, target_table: str) -> Dict[str, Any]:
        """
        Run ingestion task only.

        Args:
            source_file: Path to CSV file
            target_table: Target table (schema.table)

        Returns:
            Execution result
        """
        context = {
            'ingestion': {
                'source_file': source_file,
                'target_table': target_table
            }
        }
        return self.kickoff(context)

    def run_transformation_only(self, models: List[str] = None) -> Dict[str, Any]:
        """
        Run dbt transformation only.

        Args:
            models: List of models to run (e.g., ['staging.*'])

        Returns:
            Execution result
        """
        context = {
            'transformation': {
                'command': 'run',
                'models': models or []
            }
        }
        return self.kickoff(context)

    def run_quality_check_only(self, table_name: str) -> Dict[str, Any]:
        """
        Run quality checks only.

        Args:
            table_name: Table to validate

        Returns:
            Execution result
        """
        context = {
            'quality': {
                'table_name': table_name,
                'checks': ['completeness', 'uniqueness']
            }
        }
        return self.kickoff(context)
