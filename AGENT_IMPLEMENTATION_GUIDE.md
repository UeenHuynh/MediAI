# Agent Implementation Guide
**Healthcare ML Platform - Complete Agent Development Reference**

**Version:** 1.0
**Status:** Implementation Ready
**Last Updated:** 2025-01-21

---

## DOCUMENT PURPOSE

This guide provides **complete implementation patterns** for creating CrewAI agents in the Healthcare ML Platform. Every agent follows these patterns to ensure consistency and maintainability.

**Related Documents:**
- Agent Architecture: `agents/AGENT_ARCHITECTURE.md`
- Agent Hooks: `AGENT_HOOKS_AND_STEERING.md`
- Task Breakdown: `TASK_BREAKDOWN.md`

---

## 1. AGENT ARCHITECTURE OVERVIEW

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT HIERARCHY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BaseAgent (Abstract)                                           │
│      ├── Data Engineering Agents                                │
│      │   ├── DataIngestionAgent                                │
│      │   ├── DataTransformationAgent                           │
│      │   └── DataQualityAgent                                  │
│      │                                                           │
│      ├── ML Engineering Agents                                  │
│      │   ├── FeatureEngineeringAgent                           │
│      │   ├── ModelTrainingAgent                                │
│      │   └── ModelEvaluationAgent                              │
│      │                                                           │
│      ├── DevOps Agents                                          │
│      │   ├── APIDeploymentAgent                                │
│      │   └── InfrastructureAgent                               │
│      │                                                           │
│      └── Orchestration Agents                                   │
│          ├── WorkflowOrchestrator                               │
│          └── DecisionEngine                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. BASE AGENT PATTERN

### 2.1 BaseAgent Abstract Class

**File:** `agents/core/base_agent.py`

```python
"""Base agent class for all agents in the system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


class AgentResult:
    """Standard result object for agent execution."""

    def __init__(
        self,
        status: AgentStatus,
        output: Any,
        metrics: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.output = output
        self.metrics = metrics or {}
        self.errors = errors or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'status': self.status.value,
            'output': self.output,
            'metrics': self.metrics,
            'errors': self.errors,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == AgentStatus.SUCCESS


class BaseAgent(ABC):
    """
    Base class for all agents.

    All agents must inherit from this class and implement:
    - _execute(): Core execution logic
    - validate_inputs(): Input validation
    """

    def __init__(
        self,
        name: str,
        description: str,
        tools: Optional[List[Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            tools: List of tools available to agent
            config: Agent configuration
        """
        self.name = name
        self.description = description
        self.tools = tools or []
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.execution_history: List[AgentResult] = []

        logger.info(f"Initialized agent: {self.name}")

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute agent with given context.

        Args:
            context: Execution context with inputs

        Returns:
            AgentResult with status and output
        """
        logger.info(f"[{self.name}] Starting execution")
        self.status = AgentStatus.RUNNING

        try:
            # Step 1: Validate inputs
            validation_result = self.validate_inputs(context)
            if not validation_result.is_valid:
                logger.error(f"[{self.name}] Input validation failed: {validation_result.errors}")
                result = AgentResult(
                    status=AgentStatus.FAILED,
                    output=None,
                    errors=validation_result.errors
                )
                self.status = AgentStatus.FAILED
                self.execution_history.append(result)
                return result

            # Step 2: Execute core logic
            logger.info(f"[{self.name}] Executing core logic")
            output = self._execute(context)

            # Step 3: Create success result
            result = AgentResult(
                status=AgentStatus.SUCCESS,
                output=output,
                metadata={
                    'agent_name': self.name,
                    'context': context
                }
            )
            self.status = AgentStatus.SUCCESS
            logger.info(f"[{self.name}] Execution completed successfully")

        except Exception as e:
            logger.exception(f"[{self.name}] Execution failed: {str(e)}")
            result = AgentResult(
                status=AgentStatus.FAILED,
                output=None,
                errors=[str(e)]
            )
            self.status = AgentStatus.FAILED

        # Store result in history
        self.execution_history.append(result)
        return result

    @abstractmethod
    def _execute(self, context: Dict[str, Any]) -> Any:
        """
        Core execution logic (must be implemented by subclass).

        Args:
            context: Execution context

        Returns:
            Execution output
        """
        pass

    @abstractmethod
    def validate_inputs(self, context: Dict[str, Any]) -> 'ValidationResult':
        """
        Validate input context (must be implemented by subclass).

        Args:
            context: Input context to validate

        Returns:
            ValidationResult object
        """
        pass

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status

    def get_execution_history(self) -> List[AgentResult]:
        """Get execution history."""
        return self.execution_history

    def reset(self):
        """Reset agent to initial state."""
        self.status = AgentStatus.IDLE
        self.execution_history = []
        logger.info(f"[{self.name}] Reset to initial state")


class ValidationResult:
    """Result of input validation."""

    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    @classmethod
    def success(cls) -> 'ValidationResult':
        """Create successful validation result."""
        return cls(is_valid=True)

    @classmethod
    def failure(cls, errors: List[str]) -> 'ValidationResult':
        """Create failed validation result."""
        return cls(is_valid=False, errors=errors)
```

---

## 3. DATA ENGINEERING AGENTS

### 3.1 Data Ingestion Agent

**File:** `agents/roles/data_engineer.py`

```python
"""Data engineering agents."""

import psycopg2
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
from tqdm import tqdm

from agents.core.base_agent import BaseAgent, AgentResult, ValidationResult, AgentStatus
from agents.tools.database_tool import DatabaseTool
from agents.tools.file_tool import FileTool


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

        # Check required files
        required_files = ['dbt_project.yml', 'profiles.yml']
        for file in required_files:
            if not (self.dbt_project_dir / file).exists():
                errors.append(f"Required file not found: {file}")

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
        import subprocess

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

        uniqueness_rate = row['unique_stay_ids'] / row['total_rows']

        return {
            'check': 'uniqueness',
            'score': uniqueness_rate,
            'details': row
        }
```

---

## 4. ML ENGINEERING AGENTS

### 4.1 Model Training Agent

**File:** `agents/roles/ml_engineer.py`

```python
"""ML engineering agents."""

import mlflow
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from typing import Dict, Any

from agents.core.base_agent import BaseAgent, ValidationResult
from agents.tools.database_tool import DatabaseTool
from agents.tools.mlflow_tool import MLflowTool


class ModelTrainingAgent(BaseAgent):
    """
    Agent responsible for training ML models.

    Capabilities:
    - Train LightGBM models
    - Handle class imbalance (SMOTE)
    - Log to MLflow
    - Register models
    """

    def __init__(self, db_connection_string: str, mlflow_tracking_uri: str):
        super().__init__(
            name="ModelTrainingAgent",
            description="Train ML models",
            tools=[
                DatabaseTool(db_connection_string),
                MLflowTool(mlflow_tracking_uri)
            ]
        )
        self.db_tool = self.tools[0]
        self.mlflow_tool = self.tools[1]

    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate training inputs."""
        errors = []

        required_fields = ['model_name', 'feature_table', 'target_column']
        for field in required_fields:
            if field not in context:
                errors.append(f"Missing required field: {field}")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success()

    def _execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute model training.

        Context structure:
        {
            'model_name': 'sepsis_lightgbm_v1',
            'feature_table': 'analytics.features_sepsis_6h',
            'target_column': 'sepsis_onset_within_6h',
            'hyperparameters': {...},
            'use_smote': True
        }

        Returns:
            Dict with training results
        """
        model_name = context['model_name']
        feature_table = context['feature_table']
        target_column = context['target_column']
        hyperparameters = context.get('hyperparameters', self._default_hyperparameters())
        use_smote = context.get('use_smote', True)

        logger.info(f"Training model: {model_name}")

        # Step 1: Load data
        logger.info("Loading training data...")
        query = f"SELECT * FROM {feature_table}"
        df = self.db_tool.query_to_dataframe(query)

        # Separate features and target
        X = df.drop(columns=['stay_id', target_column])
        y = df[target_column]

        logger.info(f"Loaded {len(df)} samples with {len(X.columns)} features")

        # Step 2: Train/val/test split
        logger.info("Splitting data...")
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, stratify=y, random_state=42
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
        )

        # Step 3: Handle class imbalance
        if use_smote:
            logger.info("Applying SMOTE...")
            smote = SMOTE(random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)

        # Step 4: Train model
        logger.info("Training LightGBM model...")
        with mlflow.start_run(run_name=model_name):
            # Log parameters
            mlflow.log_params(hyperparameters)

            # Train
            model = lgb.LGBMClassifier(**hyperparameters)
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                eval_metric='auc',
                callbacks=[lgb.early_stopping(stopping_rounds=50)]
            )

            # Evaluate
            from sklearn.metrics import roc_auc_score, classification_report

            y_pred_proba = model.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_pred_proba)

            logger.info(f"Test AUROC: {auroc:.4f}")

            # Log metrics
            mlflow.log_metric("auroc", auroc)
            mlflow.log_metric("train_samples", len(X_train))
            mlflow.log_metric("test_samples", len(X_test))

            # Log model
            mlflow.lightgbm.log_model(model, "model")

            # Register model
            run_id = mlflow.active_run().info.run_id
            model_uri = f"runs:/{run_id}/model"
            mlflow.register_model(model_uri, model_name)

            logger.info(f"Model registered: {model_name}")

        return {
            'model_name': model_name,
            'run_id': run_id,
            'auroc': auroc,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

    def _default_hyperparameters(self) -> Dict[str, Any]:
        """Get default LightGBM hyperparameters."""
        return {
            'objective': 'binary',
            'metric': 'auc',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'n_estimators': 500,
            'max_depth': 6,
            'min_child_samples': 20,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'class_weight': 'balanced',
            'random_state': 42
        }
```

---

## 5. CREW IMPLEMENTATION

### 5.1 Data Pipeline Crew

**File:** `agents/crews/data_pipeline_crew.py`

```python
"""Data pipeline crew - orchestrates data ingestion, transformation, and quality checks."""

from crewai import Crew, Task, Agent
from typing import Dict, Any, List
import os

from agents.roles.data_engineer import (
    DataIngestionAgent,
    DataTransformationAgent,
    DataQualityAgent
)


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
        self.db_connection = os.getenv('DATABASE_URL')
        self.dbt_project_dir = os.getenv('DBT_PROJECT_DIR', './dbt_project')

        # Initialize agents
        self.ingestion_agent = DataIngestionAgent(self.db_connection)
        self.transformation_agent = DataTransformationAgent(self.dbt_project_dir)
        self.quality_agent = DataQualityAgent(self.db_connection)

    def kickoff(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data pipeline crew.

        Args:
            context: Execution context with inputs

        Returns:
            Dict with execution results
        """
        results = {}

        # Task 1: Data Ingestion
        if 'ingestion' in context:
            ingestion_result = self.ingestion_agent.execute(context['ingestion'])
            results['ingestion'] = ingestion_result.to_dict()

            if not ingestion_result.is_success():
                return {'status': 'failed', 'results': results}

        # Task 2: dbt Transformation
        if 'transformation' in context:
            transformation_result = self.transformation_agent.execute(context['transformation'])
            results['transformation'] = transformation_result.to_dict()

            if not transformation_result.is_success():
                return {'status': 'failed', 'results': results}

        # Task 3: Data Quality
        if 'quality' in context:
            quality_result = self.quality_agent.execute(context['quality'])
            results['quality'] = quality_result.to_dict()

            if not quality_result.is_success():
                return {'status': 'failed', 'results': results}

        return {'status': 'success', 'results': results}
```

---

## 6. BEST PRACTICES

### 6.1 Error Handling

```python
def _execute(self, context: Dict[str, Any]) -> Any:
    """Execute with proper error handling."""

    try:
        # Main logic
        result = self._do_work(context)
        return result

    except psycopg2.DatabaseError as e:
        # Database errors - may be retryable
        logger.error(f"Database error: {e}")
        raise RetryableError(str(e))

    except FileNotFoundError as e:
        # File errors - not retryable
        logger.error(f"File not found: {e}")
        raise FatalError(str(e))

    except Exception as e:
        # Unknown errors - log and re-raise
        logger.exception(f"Unexpected error: {e}")
        raise
```

### 6.2 Logging

```python
# Always log key events
logger.info(f"[{self.name}] Starting execution")
logger.info(f"Loaded {len(df)} rows")
logger.info(f"Model AUROC: {auroc:.4f}")
logger.error(f"Failed to connect: {e}")
```

### 6.3 Metrics & Observability

```python
# Track execution time
import time

start_time = time.time()
result = self._execute(context)
execution_time = time.time() - start_time

result.metrics['execution_time_seconds'] = execution_time
```

---

## 7. TESTING AGENTS

### 7.1 Unit Test Example

**File:** `tests/test_agents.py`

```python
"""Unit tests for agents."""

import pytest
from unittest.mock import Mock, patch

from agents.roles.data_engineer import DataIngestionAgent


class TestDataIngestionAgent:
    """Test DataIngestionAgent."""

    def test_validate_inputs_success(self):
        """Test input validation with valid inputs."""
        agent = DataIngestionAgent(db_connection_string="fake")

        context = {
            'source_file': '/tmp/test.csv',
            'target_table': 'raw.test'
        }

        # Mock file existence check
        with patch('pathlib.Path.exists', return_value=True):
            result = agent.validate_inputs(context)
            assert result.is_valid

    def test_validate_inputs_missing_field(self):
        """Test input validation with missing field."""
        agent = DataIngestionAgent(db_connection_string="fake")

        context = {'source_file': '/tmp/test.csv'}

        result = agent.validate_inputs(context)
        assert not result.is_valid
        assert 'target_table' in str(result.errors)

    @patch('agents.roles.data_engineer.pd.read_csv')
    @patch('agents.tools.database_tool.DatabaseTool.insert_dataframe')
    def test_execute_ingestion(self, mock_insert, mock_read_csv):
        """Test data ingestion execution."""
        # Setup mocks
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=100)
        mock_read_csv.return_value = [mock_df]

        agent = DataIngestionAgent(db_connection_string="fake")

        context = {
            'source_file': '/tmp/test.csv',
            'target_table': 'raw.test',
            'batch_size': 100
        }

        # Execute
        with patch('pathlib.Path.exists', return_value=True):
            result = agent.execute(context)

        # Verify
        assert result.is_success()
        assert result.output['rows_ingested'] == 100
```

---

## 8. DEPLOYMENT CHECKLIST

### Before Deploying Agent:

- [ ] Inherits from BaseAgent
- [ ] Implements _execute() method
- [ ] Implements validate_inputs() method
- [ ] Has comprehensive error handling
- [ ] Logs all key events
- [ ] Tracks execution metrics
- [ ] Has unit tests (>70% coverage)
- [ ] Documented with docstrings
- [ ] Configuration externalized (no hardcoded values)
- [ ] Tested with real data

---

**Document Version:** 1.0
**Status:** ✅ Implementation Ready
**Next Steps:** Implement agents following these patterns
