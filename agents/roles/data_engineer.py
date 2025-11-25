"""Data engineering agents."""

import psycopg2
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
from tqdm import tqdm
import logging
import subprocess

from agents.core.base_agent import BaseAgent, AgentResult, ValidationResult, AgentStatus
from agents.tools.database_tool import DatabaseTool
from agents.tools.file_tool import FileTool

logger = logging.getLogger(__name__)


class DataIngestionAgent(BaseAgent):
    """
    Agent responsible for ingesting CSV data into PostgreSQL.

    Capabilities:
    - Load CSV files in batches
    - Handle large files (>1GB)
    - Validate data quality
    - Resume from checkpoint
    """

    def __init__(self, db_connection_string: str):
        """
        Initialize data ingestion agent.

        Args:
            db_connection_string: PostgreSQL connection string
        """
        super().__init__(
            name="DataIngestionAgent",
            description="Ingest CSV data into PostgreSQL",
            tools=[DatabaseTool(db_connection_string), FileTool()]
        )
        self.db_tool = self.tools[0]
        self.file_tool = self.tools[1]
        self.batch_size = 10000  # Rows per batch

    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate ingestion inputs."""
        errors = []

        # Check required fields
        if 'source_file' not in context:
            errors.append("Missing required field: source_file")

        if 'target_table' not in context:
            errors.append("Missing required field: target_table")

        # Validate file exists
        if 'source_file' in context:
            source_file = Path(context['source_file'])
            if not source_file.exists():
                errors.append(f"Source file does not exist: {source_file}")

        # Validate table name format
        if 'target_table' in context:
            target_table = context['target_table']
            if '.' not in target_table:
                errors.append("target_table must include schema (e.g., raw.icustays)")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute data ingestion.

        Context structure:
        {
            'source_file': '/path/to/data.csv',
            'target_table': 'raw.icustays',
            'checkpoint_file': '/path/to/checkpoint.json' (optional),
            'batch_size': 10000 (optional)
        }

        Returns:
            Dict with ingestion statistics
        """
        source_file = context['source_file']
        target_table = context['target_table']
        checkpoint_file = context.get('checkpoint_file')
        batch_size = context.get('batch_size', self.batch_size)

        logger.info(f"Starting ingestion: {source_file} → {target_table}")

        # Load checkpoint if exists
        start_row = 0
        if checkpoint_file and Path(checkpoint_file).exists():
            checkpoint = self.file_tool.load_json(checkpoint_file)
            start_row = checkpoint.get('last_row', 0)
            logger.info(f"Resuming from row {start_row}")

        # Count total rows (for progress bar)
        total_rows = self.file_tool.count_csv_rows(source_file)
        logger.info(f"Total rows to ingest: {total_rows}")

        # Ingest in batches
        rows_ingested = 0
        rows_failed = 0

        with tqdm(total=total_rows, initial=start_row, desc="Ingesting") as pbar:
            for batch_df in pd.read_csv(source_file, chunksize=batch_size, skiprows=range(1, start_row + 1)):
                try:
                    # Insert batch
                    self.db_tool.insert_dataframe(
                        df=batch_df,
                        table_name=target_table,
                        if_exists='append'
                    )

                    rows_ingested += len(batch_df)
                    pbar.update(len(batch_df))

                    # Update checkpoint
                    if checkpoint_file:
                        self.file_tool.save_json(
                            checkpoint_file,
                            {'last_row': start_row + rows_ingested}
                        )

                except Exception as e:
                    logger.error(f"Failed to ingest batch: {e}")
                    rows_failed += len(batch_df)
                    continue

        # Return statistics
        result = {
            'source_file': source_file,
            'target_table': target_table,
            'rows_ingested': rows_ingested,
            'rows_failed': rows_failed,
            'total_rows': total_rows,
            'success_rate': rows_ingested / total_rows if total_rows > 0 else 0
        }

        logger.info(f"Ingestion complete: {rows_ingested}/{total_rows} rows")
        return result


class DataTransformationAgent(BaseAgent):
    """
    Agent responsible for running dbt transformations.

    Capabilities:
    - Run dbt models
    - Run dbt tests
    - Generate dbt documentation
    """

    def __init__(self, dbt_project_dir: str):
        """
        Initialize data transformation agent.

        Args:
            dbt_project_dir: Path to dbt project directory
        """
        super().__init__(
            name="DataTransformationAgent",
            description="Run dbt transformations",
            tools=[]
        )
        self.dbt_project_dir = Path(dbt_project_dir)

    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate transformation inputs."""
        errors = []

        # Check dbt project exists
        if not self.dbt_project_dir.exists():
            errors.append(f"dbt project directory not found: {self.dbt_project_dir}")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute dbt transformation.

        Context structure:
        {
            'command': 'run' | 'test' | 'docs generate',
            'models': ['staging.*'] (optional),
            'vars': {'key': 'value'} (optional)
        }

        Returns:
            Dict with dbt execution results
        """
        command = context.get('command', 'run')
        models = context.get('models', [])
        vars_dict = context.get('vars', {})

        # Build dbt command
        dbt_cmd = ['dbt', command]

        if models:
            dbt_cmd.extend(['--models', ' '.join(models)])

        if vars_dict:
            import json
            dbt_cmd.extend(['--vars', json.dumps(vars_dict)])

        logger.info(f"Running dbt: {' '.join(dbt_cmd)}")

        # Execute dbt
        result = subprocess.run(
            dbt_cmd,
            cwd=self.dbt_project_dir,
            capture_output=True,
            text=True
        )

        # Parse result
        success = result.returncode == 0

        output = {
            'command': ' '.join(dbt_cmd),
            'success': success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }

        if not success:
            logger.error(f"dbt failed: {result.stderr}")
            raise Exception(f"dbt command failed: {result.stderr}")

        logger.info("dbt execution successful")
        return output


class DataQualityAgent(BaseAgent):
    """
    Agent responsible for data quality validation.

    Capabilities:
    - Run Great Expectations validation suites
    - Check data completeness
    - Detect anomalies
    """

    def __init__(self, db_connection_string: str):
        super().__init__(
            name="DataQualityAgent",
            description="Validate data quality",
            tools=[DatabaseTool(db_connection_string)]
        )
        self.db_tool = self.tools[0]

    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate quality check inputs."""
        errors = []

        if 'table_name' not in context:
            errors.append("Missing required field: table_name")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute data quality checks.

        Context structure:
        {
            'table_name': 'raw.icustays',
            'checks': ['completeness', 'uniqueness', 'validity']
        }

        Returns:
            Dict with quality check results
        """
        table_name = context['table_name']
        checks = context.get('checks', ['completeness', 'uniqueness'])

        logger.info(f"Running quality checks on {table_name}")

        results = {}

        # Completeness check
        if 'completeness' in checks:
            completeness = self._check_completeness(table_name)
            results['completeness'] = completeness

        # Uniqueness check
        if 'uniqueness' in checks:
            uniqueness = self._check_uniqueness(table_name)
            results['uniqueness'] = uniqueness

        # Calculate overall quality score
        scores = [r['score'] for r in results.values()]
        overall_score = sum(scores) / len(scores) if scores else 0

        results['overall_score'] = overall_score
        results['passed'] = overall_score >= 0.90

        logger.info(f"Quality score: {overall_score:.2%}")
        return results

    def _check_completeness(self, table_name: str) -> Dict[str, Any]:
        """Check data completeness (non-null rate)."""
        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (WHERE stay_id IS NOT NULL) AS non_null_stay_id,
                COUNT(*) FILTER (WHERE subject_id IS NOT NULL) AS non_null_subject_id
            FROM {table_name}
        """

        result = self.db_tool.execute_query(query)
        row = result[0]

        completeness_rate = (
            (row['non_null_stay_id'] + row['non_null_subject_id']) /
            (2 * row['total_rows'])
        )

        return {
            'check': 'completeness',
            'score': completeness_rate,
            'details': row
        }

    def _check_uniqueness(self, table_name: str) -> Dict[str, Any]:
        """Check uniqueness of primary key."""
        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT stay_id) AS unique_stay_ids
            FROM {table_name}
        """

        result = self.db_tool.execute_query(query)
        row = result[0]

        uniqueness_rate = row['unique_stay_ids'] / row['total_rows'] if row['total_rows'] > 0 else 0

        return {
            'check': 'uniqueness',
            'score': uniqueness_rate,
            'details': row
        }
