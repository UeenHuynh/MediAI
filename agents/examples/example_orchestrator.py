#!/usr/bin/env python3
"""
Example: Workflow Orchestrator

This demonstrates top-level orchestration coordinating multiple crews:
1. Data Pipeline Crew (ingestion → transformation → quality)
2. ML Development Crew (feature engineering → training → evaluation)
3. Deployment Crew (model deployment → monitoring setup)

Features:
- Manages dependencies between crews
- Decision engine logic
- Failure recovery
- Execution summary

Usage:
    python example_orchestrator.py --full-pipeline

"""

import argparse
import logging
import sys
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ORCHESTRATOR CORE
# ============================================================================

class CrewStatus(Enum):
    """Status of crew execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class CrewResult:
    """Result of crew execution."""

    def __init__(
        self,
        crew_name: str,
        status: CrewStatus,
        output: Any = None,
        error: str = None,
        execution_time: float = 0.0
    ):
        self.crew_name = crew_name
        self.status = status
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            'crew_name': self.crew_name,
            'status': self.status.value,
            'output': self.output,
            'error': self.error,
            'execution_time_seconds': self.execution_time,
            'timestamp': self.timestamp.isoformat()
        }


class WorkflowOrchestrator:
    """
    Top-level orchestrator coordinating multiple crews.

    Responsibilities:
    - Execute crews in dependency order
    - Make routing decisions based on outputs
    - Handle failures with recovery strategies
    - Generate execution summary
    """

    def __init__(self):
        """Initialize orchestrator."""
        self.execution_history: List[CrewResult] = []
        logger.info("WorkflowOrchestrator initialized")

    def execute_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete workflow.

        Args:
            config: Workflow configuration

        Returns:
            Workflow execution summary
        """
        logger.info("=" * 80)
        logger.info("WORKFLOW ORCHESTRATOR - Starting Full Pipeline")
        logger.info("=" * 80)

        start_time = datetime.now()
        workflow_status = "success"

        # Crew 1: Data Pipeline
        logger.info("\n[Crew 1/3] Data Pipeline Crew")
        logger.info("-" * 80)

        data_pipeline_result = self._execute_data_pipeline_crew(config)
        self.execution_history.append(data_pipeline_result)

        if data_pipeline_result.status != CrewStatus.SUCCESS:
            logger.error("Data pipeline failed, aborting workflow")
            return self._generate_summary(start_time, "failed")

        # Decision: Check data quality before proceeding
        quality_score = data_pipeline_result.output.get('quality_score', 0)
        if quality_score < 0.90:
            logger.warning(
                f"Data quality below threshold: {quality_score:.1%}. "
                "Skipping ML development."
            )
            return self._generate_summary(start_time, "partial_success")

        # Crew 2: ML Development
        logger.info("\n[Crew 2/3] ML Development Crew")
        logger.info("-" * 80)

        ml_dev_result = self._execute_ml_development_crew(
            config,
            data_pipeline_result.output
        )
        self.execution_history.append(ml_dev_result)

        if ml_dev_result.status != CrewStatus.SUCCESS:
            logger.error("ML development failed, aborting workflow")
            return self._generate_summary(start_time, "failed")

        # Decision: Check model performance before deployment
        model_auroc = ml_dev_result.output.get('auroc', 0)
        if model_auroc < 0.80:
            logger.warning(
                f"Model AUROC below threshold: {model_auroc:.3f}. "
                "Skipping deployment."
            )
            return self._generate_summary(start_time, "partial_success")

        # Crew 3: Deployment
        logger.info("\n[Crew 3/3] Deployment Crew")
        logger.info("-" * 80)

        deployment_result = self._execute_deployment_crew(
            config,
            ml_dev_result.output
        )
        self.execution_history.append(deployment_result)

        if deployment_result.status != CrewStatus.SUCCESS:
            logger.error("Deployment failed")
            workflow_status = "failed"

        # Generate summary
        return self._generate_summary(start_time, workflow_status)

    def _execute_data_pipeline_crew(
        self,
        config: Dict[str, Any]
    ) -> CrewResult:
        """
        Execute Data Pipeline Crew.

        In real implementation, this would call:
            DataPipelineCrew().kickoff(context)

        For this example, we simulate execution.
        """
        import time

        logger.info("Starting data pipeline crew...")

        start = time.time()

        try:
            # Simulate crew execution
            time.sleep(2)

            # Mock successful result
            output = {
                'rows_ingested': 73181,
                'models_run': 15,
                'quality_score': 0.965
            }

            execution_time = time.time() - start

            logger.info(
                f"✅ Data pipeline complete: "
                f"{output['rows_ingested']:,} rows ingested, "
                f"{output['models_run']} models run, "
                f"quality: {output['quality_score']:.1%}"
            )

            return CrewResult(
                crew_name="DataPipelineCrew",
                status=CrewStatus.SUCCESS,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            logger.exception("Data pipeline crew failed")
            return CrewResult(
                crew_name="DataPipelineCrew",
                status=CrewStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start
            )

    def _execute_ml_development_crew(
        self,
        config: Dict[str, Any],
        data_pipeline_output: Dict[str, Any]
    ) -> CrewResult:
        """
        Execute ML Development Crew.

        Depends on successful data pipeline execution.
        """
        import time

        logger.info("Starting ML development crew...")

        start = time.time()

        try:
            # Simulate crew execution
            time.sleep(3)

            # Mock successful training
            output = {
                'model_name': 'sepsis_lightgbm_v1',
                'version': 2,
                'auroc': 0.892,
                'sensitivity': 0.875,
                'specificity': 0.883,
                'training_samples': 14000,
                'test_samples': 3000
            }

            execution_time = time.time() - start

            logger.info(
                f"✅ ML development complete: "
                f"Model {output['model_name']} v{output['version']} trained, "
                f"AUROC: {output['auroc']:.3f}"
            )

            return CrewResult(
                crew_name="MLDevelopmentCrew",
                status=CrewStatus.SUCCESS,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            logger.exception("ML development crew failed")
            return CrewResult(
                crew_name="MLDevelopmentCrew",
                status=CrewStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start
            )

    def _execute_deployment_crew(
        self,
        config: Dict[str, Any],
        ml_dev_output: Dict[str, Any]
    ) -> CrewResult:
        """
        Execute Deployment Crew.

        Depends on successful ML development.
        """
        import time

        logger.info("Starting deployment crew...")

        start = time.time()

        try:
            # Simulate deployment
            time.sleep(2)

            model_name = ml_dev_output['model_name']
            version = ml_dev_output['version']

            output = {
                'model_name': model_name,
                'version': version,
                'deployed_to': 'Production',
                'api_updated': True,
                'monitoring_enabled': True
            }

            execution_time = time.time() - start

            logger.info(
                f"✅ Deployment complete: "
                f"{model_name} v{version} deployed to Production"
            )

            return CrewResult(
                crew_name="DeploymentCrew",
                status=CrewStatus.SUCCESS,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            logger.exception("Deployment crew failed")
            return CrewResult(
                crew_name="DeploymentCrew",
                status=CrewStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start
            )

    def _generate_summary(
        self,
        start_time: datetime,
        status: str
    ) -> Dict[str, Any]:
        """Generate workflow execution summary."""
        total_execution_time = (datetime.now() - start_time).total_seconds()

        summary = {
            'workflow_status': status,
            'total_execution_time_seconds': total_execution_time,
            'crews_executed': len(self.execution_history),
            'crews_succeeded': sum(
                1 for r in self.execution_history
                if r.status == CrewStatus.SUCCESS
            ),
            'crews_failed': sum(
                1 for r in self.execution_history
                if r.status == CrewStatus.FAILED
            ),
            'crew_results': [r.to_dict() for r in self.execution_history],
            'timestamp': datetime.now().isoformat()
        }

        # Log summary
        logger.info("\n" + "=" * 80)
        if status == "success":
            logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        elif status == "partial_success":
            logger.info("⚠️  WORKFLOW PARTIALLY COMPLETED")
        else:
            logger.info("❌ WORKFLOW FAILED")
        logger.info("=" * 80)
        logger.info(f"Total execution time: {total_execution_time:.2f}s")
        logger.info(f"Crews executed: {summary['crews_executed']}")
        logger.info(f"Crews succeeded: {summary['crews_succeeded']}")
        logger.info(f"Crews failed: {summary['crews_failed']}")
        logger.info("=" * 80)

        # Display crew details
        logger.info("\nCrew Execution Details:")
        logger.info("-" * 80)
        for result in self.execution_history:
            status_emoji = "✅" if result.status == CrewStatus.SUCCESS else "❌"
            logger.info(
                f"{status_emoji} {result.crew_name:25} "
                f"[{result.status.value:8}] "
                f"({result.execution_time:.2f}s)"
            )
        logger.info("=" * 80)

        return summary


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Workflow Orchestrator - Coordinate multi-crew ML pipeline'
    )
    parser.add_argument(
        '--full-pipeline',
        action='store_true',
        help='Run complete pipeline (data → ML → deployment)'
    )
    parser.add_argument(
        '--data-only',
        action='store_true',
        help='Run only data pipeline'
    )
    parser.add_argument(
        '--ml-only',
        action='store_true',
        help='Run only ML development'
    )

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()

    # Configure workflow
    config = {
        'database_url': 'postgresql://postgres:password@localhost:5432/mimic_iv',
        'mlflow_uri': 'http://localhost:5000',
        'dbt_project_dir': './dbt_project'
    }

    # Execute workflow
    if args.full_pipeline or (not args.data_only and not args.ml_only):
        result = orchestrator.execute_workflow(config)
    elif args.data_only:
        logger.info("Running data pipeline only...")
        result = {
            'workflow_status': 'partial',
            'message': 'Data-only mode not fully implemented in example'
        }
    elif args.ml_only:
        logger.info("Running ML development only...")
        result = {
            'workflow_status': 'partial',
            'message': 'ML-only mode not fully implemented in example'
        }

    # Exit with appropriate code
    if result['workflow_status'] == 'success':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
