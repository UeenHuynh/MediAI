# Error Handling & Recovery Policy
**Healthcare ML Platform - Comprehensive Error Management**

**Version:** 1.0
**Status:** Policy Approved
**Last Updated:** 2025-01-21

---

## DOCUMENT PURPOSE

This document defines **error handling strategies**, **retry policies**, and **recovery procedures** for all agents and services in the Healthcare ML Platform.

**Related Documents:**
- Agent Implementation: `AGENT_IMPLEMENTATION_GUIDE.md`
- Agent Hooks: `AGENT_HOOKS_AND_STEERING.md`
- Architecture: `ARCHITECTURE_DESIGN.md`

---

## 1. ERROR HANDLING PHILOSOPHY

### 1.1 Core Principles

1. **Fail Fast**: Detect errors immediately, don't let them propagate
2. **Fail Safe**: When uncertain, choose the safer option
3. **Fail Loudly**: Log all errors comprehensively
4. **Fail Gracefully**: Provide meaningful error messages to users
5. **Fail Forward**: Implement automatic recovery when possible

### 1.2 Error Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| **CRITICAL** | System unusable, data loss risk | Immediate (page on-call) | Database connection lost |
| **HIGH** | Major feature broken | <1 hour | Model serving failed |
| **MEDIUM** | Degraded performance | <4 hours | Cache unavailable |
| **LOW** | Minor issue | <24 hours | Slow query |
| **INFO** | Not an error, informational | N/A | Rate limit warning |

---

## 2. ERROR CLASSIFICATION

### 2.1 Retriable Errors

**Definition:** Errors that may succeed if retried (transient failures)

**Examples:**
- Network timeouts
- Database connection pool exhausted
- API rate limit exceeded
- Temporary file system full
- Redis connection refused

**Handling:**
```python
class RetryableError(Exception):
    """Error that can be retried."""
    pass

# Examples
raise RetryableError("Database connection timeout")
raise RetryableError("API rate limit exceeded, retry after 60s")
```

---

### 2.2 Fatal Errors

**Definition:** Errors that will not succeed if retried (permanent failures)

**Examples:**
- File not found
- Invalid credentials
- Schema mismatch
- Data validation failure
- Programming errors (TypeError, AttributeError)

**Handling:**
```python
class FatalError(Exception):
    """Error that cannot be retried."""
    pass

# Examples
raise FatalError("Source file does not exist: /path/to/data.csv")
raise FatalError("Feature schema mismatch: expected 42 features, got 35")
```

---

### 2.3 Business Logic Errors

**Definition:** Errors related to business rules or data quality

**Examples:**
- Data quality score <90%
- Model AUROC <0.75
- Feature completeness <70%
- Prediction confidence <0.5

**Handling:**
```python
class BusinessLogicError(Exception):
    """Error due to business rule violation."""
    pass

# Examples
raise BusinessLogicError("Data quality too low: 85% (threshold: 90%)")
raise BusinessLogicError("Model performance below acceptable: AUROC=0.73")
```

---

## 3. RETRY STRATEGIES

### 3.1 Exponential Backoff

**Use When:** Network errors, API rate limits, database connection issues

**Implementation:**
```python
import time
import random
from typing import Callable, Any, Type

def retry_with_exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retriable_exceptions: tuple = (RetryableError,)
) -> Any:
    """
    Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd
        retriable_exceptions: Tuple of exceptions to retry on

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    for attempt in range(max_retries + 1):
        try:
            return func()

        except retriable_exceptions as e:
            if attempt == max_retries:
                logger.error(f"All {max_retries} retries exhausted")
                raise

            # Calculate delay
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter
            if jitter:
                delay = delay * (0.5 + random.random())

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)

        except Exception as e:
            # Non-retriable error
            logger.error(f"Non-retriable error: {e}")
            raise


# Usage example
def fetch_data_from_api():
    """Fetch data from external API."""
    response = requests.get('https://api.example.com/data', timeout=10)
    if response.status_code == 429:
        raise RetryableError("Rate limit exceeded")
    response.raise_for_status()
    return response.json()

# Retry automatically
data = retry_with_exponential_backoff(
    fetch_data_from_api,
    max_retries=3,
    base_delay=2.0
)
```

---

### 3.2 Fixed Delay Retry

**Use When:** Predictable recovery time (e.g., waiting for lock release)

**Implementation:**
```python
def retry_with_fixed_delay(
    func: Callable,
    max_retries: int = 3,
    delay: float = 5.0
) -> Any:
    """Retry with fixed delay between attempts."""

    for attempt in range(max_retries + 1):
        try:
            return func()

        except RetryableError as e:
            if attempt == max_retries:
                raise

            logger.warning(f"Attempt {attempt + 1} failed, waiting {delay}s...")
            time.sleep(delay)


# Usage: Database lock
def acquire_database_lock():
    """Try to acquire database lock."""
    result = db.execute("SELECT pg_try_advisory_lock(12345)")
    if not result.fetchone()[0]:
        raise RetryableError("Lock not available")
    return True

lock_acquired = retry_with_fixed_delay(acquire_database_lock, delay=5.0)
```

---

### 3.3 Circuit Breaker Pattern

**Use When:** Preventing cascading failures from unhealthy dependencies

**Implementation:**
```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"    # Normal operation
    OPEN = "open"        # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing recovery, limited requests allowed
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError if circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker CLOSED (recovered)")

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker OPEN ({self.failure_count} failures)"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Usage example
mlflow_circuit = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    expected_exception=requests.exceptions.RequestException
)

def load_model_from_mlflow(model_name: str):
    """Load model with circuit breaker protection."""
    return mlflow_circuit.call(
        mlflow.pyfunc.load_model,
        f"models:/{model_name}/Production"
    )
```

---

## 4. ROLLBACK PROCEDURES

### 4.1 Database Transaction Rollback

**Policy:** All database operations MUST use transactions

**Implementation:**
```python
import psycopg2

def execute_with_rollback(db_connection, operations: list):
    """
    Execute operations with automatic rollback on failure.

    Args:
        db_connection: Database connection
        operations: List of SQL operations to execute

    Returns:
        True if successful, False otherwise
    """
    cursor = db_connection.cursor()

    try:
        # Start transaction
        cursor.execute("BEGIN")

        # Execute all operations
        for operation in operations:
            logger.info(f"Executing: {operation[:100]}...")
            cursor.execute(operation)

        # Commit if all succeeded
        db_connection.commit()
        logger.info("All operations committed successfully")
        return True

    except Exception as e:
        # Rollback on any error
        db_connection.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        return False

    finally:
        cursor.close()


# Usage
operations = [
    "INSERT INTO raw.icustays VALUES (...)",
    "UPDATE analytics.ml_input_master SET ...",
    "DELETE FROM temp_table WHERE ..."
]

success = execute_with_rollback(db_connection, operations)
```

---

### 4.2 Model Deployment Rollback

**Policy:** Always keep previous model version for rollback

**Implementation:**
```python
def deploy_model_with_rollback(model_name: str, new_version: int):
    """
    Deploy new model version with automatic rollback on failure.

    Args:
        model_name: Name of model
        new_version: New version to deploy

    Returns:
        Deployment result
    """
    # Get current production version (for rollback)
    current_version = mlflow.get_latest_versions(
        model_name, stages=['Production']
    )[0].version

    logger.info(f"Current version: {current_version}, New version: {new_version}")

    try:
        # Step 1: Promote new version to Production
        mlflow.transition_model_version_stage(
            name=model_name,
            version=new_version,
            stage='Production'
        )

        # Step 2: Archive old version
        mlflow.transition_model_version_stage(
            name=model_name,
            version=current_version,
            stage='Archived'
        )

        # Step 3: Health check
        health_check_passed = run_model_health_check(model_name, new_version)

        if not health_check_passed:
            raise HealthCheckFailed("Model health check failed")

        logger.info(f"Successfully deployed v{new_version}")
        return {'status': 'success', 'version': new_version}

    except Exception as e:
        logger.error(f"Deployment failed, rolling back: {e}")

        # Rollback: Restore old version
        mlflow.transition_model_version_stage(
            name=model_name,
            version=current_version,
            stage='Production'
        )

        mlflow.transition_model_version_stage(
            name=model_name,
            version=new_version,
            stage='Staging'
        )

        logger.info(f"Rolled back to v{current_version}")
        return {'status': 'rolled_back', 'version': current_version, 'error': str(e)}


class HealthCheckFailed(Exception):
    """Model health check failed."""
    pass


def run_model_health_check(model_name: str, version: int) -> bool:
    """
    Run health checks on newly deployed model.

    Checks:
    - Model loads successfully
    - Prediction latency <200ms
    - Sample predictions return valid results

    Returns:
        True if all checks pass
    """
    try:
        # Check 1: Model loads
        model = mlflow.pyfunc.load_model(f"models:/{model_name}/Production")

        # Check 2: Latency check
        import time
        sample_input = get_sample_input()

        start = time.time()
        prediction = model.predict(sample_input)
        latency = (time.time() - start) * 1000

        if latency > 200:
            logger.error(f"Latency too high: {latency:.2f}ms")
            return False

        # Check 3: Valid output
        if prediction is None or len(prediction) == 0:
            logger.error("Invalid prediction output")
            return False

        logger.info("Health check passed")
        return True

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```

---

### 4.3 Data Pipeline Rollback

**Policy:** Create checkpoints before each major operation

**Implementation:**
```python
import json
from pathlib import Path

class CheckpointManager:
    """Manage checkpoints for data pipeline operations."""

    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def save_checkpoint(self, operation_id: str, state: dict):
        """
        Save checkpoint state.

        Args:
            operation_id: Unique operation identifier
            state: State to save
        """
        checkpoint_file = self.checkpoint_dir / f"{operation_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Checkpoint saved: {checkpoint_file}")

    def load_checkpoint(self, operation_id: str) -> dict:
        """
        Load checkpoint state.

        Args:
            operation_id: Unique operation identifier

        Returns:
            Checkpoint state or None if not found
        """
        checkpoint_file = self.checkpoint_dir / f"{operation_id}.json"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, 'r') as f:
            state = json.load(f)

        logger.info(f"Checkpoint loaded: {checkpoint_file}")
        return state

    def delete_checkpoint(self, operation_id: str):
        """Delete checkpoint after successful completion."""
        checkpoint_file = self.checkpoint_dir / f"{operation_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.info(f"Checkpoint deleted: {checkpoint_file}")


# Usage in data ingestion
def ingest_data_with_checkpoint(source_file: str, target_table: str):
    """Ingest data with checkpoint support for resumability."""

    checkpoint_mgr = CheckpointManager()
    operation_id = f"ingest_{Path(source_file).stem}"

    # Try to resume from checkpoint
    checkpoint = checkpoint_mgr.load_checkpoint(operation_id)
    start_row = checkpoint['last_row'] if checkpoint else 0

    logger.info(f"Starting ingestion from row {start_row}")

    try:
        rows_processed = 0

        for batch_df in pd.read_csv(source_file, chunksize=10000, skiprows=range(1, start_row + 1)):
            # Insert batch
            insert_batch(batch_df, target_table)

            rows_processed += len(batch_df)

            # Save checkpoint
            checkpoint_mgr.save_checkpoint(operation_id, {
                'source_file': source_file,
                'target_table': target_table,
                'last_row': start_row + rows_processed,
                'timestamp': datetime.now().isoformat()
            })

        # Success - delete checkpoint
        checkpoint_mgr.delete_checkpoint(operation_id)
        logger.info(f"Ingestion complete: {rows_processed} rows")

    except Exception as e:
        logger.error(f"Ingestion failed at row {start_row + rows_processed}: {e}")
        logger.info("Checkpoint saved. Run again to resume.")
        raise
```

---

## 5. ERROR LOGGING & ALERTING

### 5.1 Structured Error Logging

**Policy:** All errors MUST be logged with structured context

**Implementation:**
```python
import logging
import json
from datetime import datetime

class StructuredErrorLogger:
    """Logger with structured error context."""

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def log_error(
        self,
        error: Exception,
        context: dict,
        severity: str = "HIGH"
    ):
        """
        Log error with structured context.

        Args:
            error: Exception that occurred
            context: Contextual information
            severity: Error severity level
        """
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'stack_trace': traceback.format_exc()
        }

        # Log as JSON for easy parsing
        self.logger.error(json.dumps(error_log, indent=2))

        # Also trigger alert if high severity
        if severity in ['CRITICAL', 'HIGH']:
            self._trigger_alert(error_log)

    def _trigger_alert(self, error_log: dict):
        """Trigger alert for high-severity errors."""
        # Send to alerting system (Slack, PagerDuty, etc.)
        alert_message = (
            f"🚨 {error_log['severity']} ERROR\n"
            f"Type: {error_log['error_type']}\n"
            f"Message: {error_log['error_message']}\n"
            f"Context: {error_log['context']}"
        )

        # Send alert (implementation depends on alerting system)
        send_slack_alert(alert_message)


# Usage
error_logger = StructuredErrorLogger('data_pipeline')

try:
    ingest_data(source_file, target_table)
except Exception as e:
    error_logger.log_error(
        error=e,
        context={
            'operation': 'data_ingestion',
            'source_file': source_file,
            'target_table': target_table,
            'agent': 'DataIngestionAgent'
        },
        severity='HIGH'
    )
    raise
```

---

### 5.2 Alert Routing

**Policy:** Route alerts based on severity and component

| Severity | Component | Alert Channel | Response Time |
|----------|-----------|---------------|---------------|
| CRITICAL | Database | PagerDuty + Slack | Immediate |
| CRITICAL | ML Model | PagerDuty + Slack | Immediate |
| HIGH | Data Pipeline | Slack + Email | <1 hour |
| HIGH | API | Slack | <1 hour |
| MEDIUM | Performance | Slack | <4 hours |
| LOW | Monitoring | Email | <24 hours |

**Implementation:**
```python
class AlertRouter:
    """Route alerts to appropriate channels."""

    ROUTING_RULES = {
        ('CRITICAL', 'database'): ['pagerduty', 'slack'],
        ('CRITICAL', 'ml_model'): ['pagerduty', 'slack'],
        ('HIGH', 'data_pipeline'): ['slack', 'email'],
        ('HIGH', 'api'): ['slack'],
        ('MEDIUM', 'performance'): ['slack'],
        ('LOW', 'monitoring'): ['email']
    }

    def route_alert(self, severity: str, component: str, message: str):
        """Route alert to appropriate channels."""
        channels = self.ROUTING_RULES.get((severity, component), ['email'])

        for channel in channels:
            self._send_to_channel(channel, severity, component, message)

    def _send_to_channel(self, channel: str, severity: str, component: str, message: str):
        """Send alert to specific channel."""
        if channel == 'pagerduty':
            send_pagerduty_alert(severity, component, message)
        elif channel == 'slack':
            send_slack_alert(f"[{severity}] {component}: {message}")
        elif channel == 'email':
            send_email_alert(severity, component, message)
```

---

## 6. RECOVERY PROCEDURES

### 6.1 Database Recovery

**Scenario:** Database connection lost

**Procedure:**
1. Detect connection loss
2. Wait 5 seconds
3. Attempt reconnection (max 3 tries with exponential backoff)
4. If fails, alert on-call and pause operations
5. Once reconnected, resume from checkpoint

```python
def recover_database_connection(db_config: dict, max_retries: int = 3) -> bool:
    """
    Attempt to recover database connection.

    Returns:
        True if recovered, False otherwise
    """
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**db_config)
            conn.cursor().execute("SELECT 1")
            logger.info("Database connection recovered")
            return True

        except psycopg2.OperationalError as e:
            delay = 2 ** attempt
            logger.warning(f"Reconnection attempt {attempt + 1} failed, waiting {delay}s")
            time.sleep(delay)

    logger.error("Failed to recover database connection")
    return False
```

---

### 6.2 Model Serving Recovery

**Scenario:** Model serving fails

**Procedure:**
1. Detect model serving failure
2. Check if model file exists
3. Try reloading model
4. If fails, rollback to previous version
5. If rollback fails, serve fallback predictions (rule-based)

```python
def recover_model_serving(model_name: str) -> bool:
    """
    Attempt to recover model serving.

    Recovery steps:
    1. Reload current model
    2. Rollback to previous version
    3. Use fallback predictions

    Returns:
        True if recovered
    """
    try:
        # Step 1: Try reloading current model
        logger.info("Attempting to reload current model...")
        model = mlflow.pyfunc.load_model(f"models:/{model_name}/Production")
        return True

    except Exception as e:
        logger.error(f"Failed to reload model: {e}")

        try:
            # Step 2: Rollback to previous version
            logger.info("Attempting rollback to previous version...")
            versions = mlflow.search_model_versions(f"name='{model_name}'")
            archived_versions = [v for v in versions if v.current_stage == 'Archived']

            if archived_versions:
                previous_version = archived_versions[-1].version
                mlflow.transition_model_version_stage(
                    name=model_name,
                    version=previous_version,
                    stage='Production'
                )
                logger.info(f"Rolled back to version {previous_version}")
                return True

        except Exception as e2:
            logger.error(f"Rollback failed: {e2}")

            # Step 3: Use fallback predictions
            logger.warning("Using fallback prediction mode")
            enable_fallback_predictions()
            return False


def enable_fallback_predictions():
    """Enable rule-based fallback predictions."""
    global USE_FALLBACK
    USE_FALLBACK = True
    logger.warning("FALLBACK MODE ENABLED - using rule-based predictions")
```

---

## 7. ERROR HANDLING CHECKLIST

### Before Deploying Code:

- [ ] All external calls wrapped in try-except
- [ ] Retriable errors use exponential backoff
- [ ] Database operations use transactions
- [ ] Checkpoints saved before major operations
- [ ] Errors logged with structured context
- [ ] High-severity errors trigger alerts
- [ ] Rollback procedures tested
- [ ] Circuit breakers configured for external services
- [ ] Error messages are actionable
- [ ] Recovery procedures documented

---

## 8. TESTING ERROR SCENARIOS

### 8.1 Chaos Engineering Tests

**Test:** Simulate database connection loss

```python
def test_database_connection_loss():
    """Test recovery from database connection loss."""

    # Start ingestion
    agent = DataIngestionAgent(db_connection_string)

    # Simulate connection loss after 100 rows
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.side_effect = [
            MagicMock(),  # First connection succeeds
            psycopg2.OperationalError("Connection lost"),  # Second fails
            MagicMock()   # Third succeeds (recovered)
        ]

        result = agent.execute({
            'source_file': 'test.csv',
            'target_table': 'raw.test'
        })

        # Verify recovery
        assert result.is_success()
        assert 'recovered_from_error' in result.metadata
```

---

**Document Version:** 1.0
**Status:** ✅ Policy Approved
**Next Steps:** Implement error handling in all agents
