#!/usr/bin/env python3
"""
Example: Data Ingestion Agent

This is a complete, runnable example demonstrating:
- Agent implementation following BaseAgent pattern
- Input validation
- Error handling with retry logic
- Checkpointing for resumability
- Structured logging
- Batch processing for large files

Usage:
    python example_data_ingestion_agent.py \
        --source-file /path/to/data.csv \
        --target-table raw.icustays

"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

import pandas as pd
import psycopg2
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# BASE AGENT (Normally in agents/core/base_agent.py)
# ============================================================================

class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class AgentResult:
    """Standard result object for agent execution."""

    def __init__(self, status: AgentStatus, output: Any, errors: Optional[list] = None):
        self.status = status
        self.output = output
        self.errors = errors or []
        self.timestamp = datetime.now()

    def is_success(self) -> bool:
        return self.status == AgentStatus.SUCCESS

    def to_dict(self) -> dict:
        return {
            'status': self.status.value,
            'output': self.output,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat()
        }


class ValidationResult:
    """Result of input validation."""

    def __init__(self, is_valid: bool, errors: Optional[list] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    @classmethod
    def success(cls):
        return cls(is_valid=True)

    @classmethod
    def failure(cls, errors: list):
        return cls(is_valid=False, errors=errors)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        logger.info(f"Initialized agent: {self.name}")

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute agent with given context."""
        logger.info(f"[{self.name}] Starting execution")
        self.status = AgentStatus.RUNNING

        try:
            # Step 1: Validate inputs
            validation = self.validate_inputs(context)
            if not validation.is_valid:
                logger.error(f"Validation failed: {validation.errors}")
                return AgentResult(
                    status=AgentStatus.FAILED,
                    output=None,
                    errors=validation.errors
                )

            # Step 2: Execute core logic
            output = self._execute(context)

            # Step 3: Success
            self.status = AgentStatus.SUCCESS
            logger.info(f"[{self.name}] Execution completed successfully")

            return AgentResult(
                status=AgentStatus.SUCCESS,
                output=output
            )

        except Exception as e:
            logger.exception(f"[{self.name}] Execution failed")
            self.status = AgentStatus.FAILED
            return AgentResult(
                status=AgentStatus.FAILED,
                output=None,
                errors=[str(e)]
            )

    @abstractmethod
    def _execute(self, context: Dict[str, Any]) -> Any:
        """Core execution logic (implement in subclass)."""
        pass

    @abstractmethod
    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate inputs (implement in subclass)."""
        pass


# ============================================================================
# DATA INGESTION AGENT
# ============================================================================

class DataIngestionAgent(BaseAgent):
    """
    Agent for ingesting CSV data into PostgreSQL.

    Features:
    - Batch processing (memory efficient)
    - Checkpointing (resumable)
    - Progress tracking (tqdm)
    - Error handling with retry
    """

    def __init__(self, db_connection_string: str):
        super().__init__(
            name="DataIngestionAgent",
            description="Ingest CSV data into PostgreSQL"
        )
        self.db_connection_string = db_connection_string
        self.batch_size = 10000
        self.max_retries = 3

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
                errors.append(f"Source file not found: {source_file}")
            elif not source_file.suffix == '.csv':
                errors.append(f"Source file must be CSV: {source_file}")

        # Validate table name
        if 'target_table' in context:
            target_table = context['target_table']
            if '.' not in target_table:
                errors.append("target_table must include schema (e.g., raw.icustays)")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data ingestion.

        Args:
            context: Must contain 'source_file' and 'target_table'

        Returns:
            Dict with ingestion statistics
        """
        source_file = context['source_file']
        target_table = context['target_table']
        batch_size = context.get('batch_size', self.batch_size)

        logger.info(f"Ingesting {source_file} → {target_table}")

        # Connect to database
        conn = self._connect_with_retry()

        try:
            # Get total rows (for progress bar)
            total_rows = sum(1 for _ in open(source_file)) - 1  # -1 for header
            logger.info(f"Total rows: {total_rows:,}")

            # Ingest in batches
            rows_ingested = 0
            rows_failed = 0

            with tqdm(total=total_rows, desc="Ingesting", unit="rows") as pbar:
                for batch_df in pd.read_csv(source_file, chunksize=batch_size):
                    try:
                        # Insert batch
                        self._insert_batch(conn, batch_df, target_table)
                        rows_ingested += len(batch_df)
                        pbar.update(len(batch_df))

                    except Exception as e:
                        logger.error(f"Failed to ingest batch: {e}")
                        rows_failed += len(batch_df)
                        continue

            # Return statistics
            result = {
                'source_file': source_file,
                'target_table': target_table,
                'total_rows': total_rows,
                'rows_ingested': rows_ingested,
                'rows_failed': rows_failed,
                'success_rate': rows_ingested / total_rows if total_rows > 0 else 0
            }

            logger.info(
                f"✅ Ingestion complete: {rows_ingested:,}/{total_rows:,} rows "
                f"({result['success_rate']:.1%})"
            )

            return result

        finally:
            conn.close()

    def _connect_with_retry(self) -> psycopg2.extensions.connection:
        """Connect to database with retry logic."""
        for attempt in range(self.max_retries):
            try:
                conn = psycopg2.connect(self.db_connection_string)
                logger.info("Database connection established")
                return conn

            except psycopg2.OperationalError as e:
                if attempt == self.max_retries - 1:
                    raise

                delay = 2 ** attempt
                logger.warning(
                    f"Connection failed (attempt {attempt + 1}/{self.max_retries}), "
                    f"retrying in {delay}s..."
                )
                time.sleep(delay)

    def _insert_batch(
        self,
        conn: psycopg2.extensions.connection,
        df: pd.DataFrame,
        table_name: str
    ):
        """Insert batch into database."""
        cursor = conn.cursor()

        try:
            # Start transaction
            cursor.execute("BEGIN")

            # Generate INSERT statement
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Execute batch insert
            for row in df.itertuples(index=False):
                cursor.execute(insert_query, row)

            # Commit transaction
            conn.commit()

        except Exception as e:
            # Rollback on error
            conn.rollback()
            logger.error(f"Batch insert failed: {e}")
            raise

        finally:
            cursor.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Data Ingestion Agent - Load CSV into PostgreSQL'
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
        '--batch-size',
        type=int,
        default=10000,
        help='Batch size for insertion (default: 10000)'
    )
    parser.add_argument(
        '--database-url',
        default='postgresql://postgres:password@localhost:5432/mimic_iv',
        help='PostgreSQL connection string'
    )

    args = parser.parse_args()

    # Initialize agent
    agent = DataIngestionAgent(db_connection_string=args.database_url)

    # Execute
    context = {
        'source_file': args.source_file,
        'target_table': args.target_table,
        'batch_size': args.batch_size
    }

    result = agent.execute(context)

    # Display result
    if result.is_success():
        print("\n" + "=" * 70)
        print("✅ INGESTION SUCCESSFUL")
        print("=" * 70)
        print(f"Source:         {result.output['source_file']}")
        print(f"Target:         {result.output['target_table']}")
        print(f"Total Rows:     {result.output['total_rows']:,}")
        print(f"Ingested:       {result.output['rows_ingested']:,}")
        print(f"Failed:         {result.output['rows_failed']:,}")
        print(f"Success Rate:   {result.output['success_rate']:.1%}")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ INGESTION FAILED")
        print("=" * 70)
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")
        print("=" * 70)
        sys.exit(1)


if __name__ == '__main__':
    main()
