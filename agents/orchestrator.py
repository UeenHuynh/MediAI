"""
Workflow Orchestrator - Coordinates all agent crews

This is the main entry point for agent-based automation.
"""

import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.crews.data_pipeline_crew import DataPipelineCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Top-level orchestrator for all agent workflows.

    Manages:
    - Data Pipeline Crew
    - ML Development Crew
    - Deployment Crew
    - Monitoring Crew
    """

    def __init__(self):
        """Initialize workflow orchestrator."""
        logger.info("Initializing Workflow Orchestrator...")

        # Initialize crews
        self.data_pipeline_crew = DataPipelineCrew()

        logger.info("Workflow Orchestrator ready")

    def run_data_pipeline(
        self,
        source_file: Optional[str] = None,
        target_table: Optional[str] = None,
        run_transformation: bool = True,
        run_quality_check: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete data pipeline workflow.

        Args:
            source_file: CSV file to ingest
            target_table: Target database table
            run_transformation: Run dbt transformations
            run_quality_check: Run quality validation

        Returns:
            Workflow execution results
        """
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW: Data Pipeline")
        logger.info("=" * 80)

        context = {}

        # Ingestion task
        if source_file and target_table:
            context['ingestion'] = {
                'source_file': source_file,
                'target_table': target_table
            }

        # Transformation task
        if run_transformation:
            context['transformation'] = {
                'command': 'run',
                'models': ['staging.*']
            }

        # Quality check task
        if run_quality_check and target_table:
            context['quality'] = {
                'table_name': target_table,
                'checks': ['completeness', 'uniqueness']
            }

        # Execute crew
        result = self.data_pipeline_crew.kickoff(context)

        logger.info("\n" + "=" * 80)
        logger.info(f"WORKFLOW RESULT: {result['status'].upper()}")
        logger.info("=" * 80)

        return result

    def ingest_sample_data(self) -> Dict[str, Any]:
        """
        Ingest sample data (patients, icustays, chartevents).

        This is a convenience method for quick setup.

        Returns:
            Ingestion results
        """
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW: Ingest Sample Data")
        logger.info("=" * 80)

        data_dir = Path(__file__).parent.parent / 'data' / 'sample'

        # Check if sample data exists
        if not data_dir.exists():
            logger.error(f"Sample data directory not found: {data_dir}")
            logger.info("Run: python scripts/generate_sample_data.py")
            return {'status': 'failed', 'error': 'Sample data not found'}

        tables = [
            ('patients.csv', 'raw.patients'),
            ('icustays.csv', 'raw.icustays'),
            ('chartevents.csv', 'raw.chartevents')
        ]

        results = {}

        for csv_file, table_name in tables:
            source_file = data_dir / csv_file

            if not source_file.exists():
                logger.warning(f"File not found: {source_file}")
                continue

            logger.info(f"\nIngesting {csv_file}...")

            result = self.data_pipeline_crew.run_ingestion_only(
                source_file=str(source_file),
                target_table=table_name
            )

            results[table_name] = result

        return {
            'status': 'success',
            'tables_ingested': len(results),
            'results': results
        }


def main():
    """Main entry point for orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description="MediAI Agent Orchestrator")

    parser.add_argument(
        'workflow',
        choices=['ingest', 'transform', 'quality', 'full-pipeline'],
        help='Workflow to execute'
    )

    parser.add_argument(
        '--source-file',
        help='Source CSV file for ingestion'
    )

    parser.add_argument(
        '--target-table',
        help='Target table (schema.table)'
    )

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()

    # Execute workflow
    if args.workflow == 'ingest':
        if not args.source_file or not args.target_table:
            logger.error("--source-file and --target-table required for ingestion")
            sys.exit(1)

        result = orchestrator.run_data_pipeline(
            source_file=args.source_file,
            target_table=args.target_table,
            run_transformation=False,
            run_quality_check=False
        )

    elif args.workflow == 'transform':
        result = orchestrator.data_pipeline_crew.run_transformation_only(
            models=['staging.*']
        )

    elif args.workflow == 'quality':
        if not args.target_table:
            logger.error("--target-table required for quality check")
            sys.exit(1)

        result = orchestrator.data_pipeline_crew.run_quality_check_only(
            table_name=args.target_table
        )

    elif args.workflow == 'full-pipeline':
        result = orchestrator.ingest_sample_data()

    # Print result
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    import json
    print(json.dumps(result, indent=2, default=str))

    # Exit code
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == "__main__":
    main()
