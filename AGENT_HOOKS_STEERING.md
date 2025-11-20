# Agent Hooks & Steering Policies
**Healthcare ML Platform - Agent Event System & Decision Framework**

**Version:** 1.0  
**Status:** Design Approved  
**Last Updated:** 2025-01-20

---

## DOCUMENT PURPOSE

This document defines:
1. **Agent Hooks** - Event-driven triggers that activate agents
2. **Steering Policies** - Rules for agent decision-making and workflow control
3. **Event System** - How agents communicate via events
4. **Failure Handling** - Retry policies, fallbacks, circuit breakers
5. **Human-in-the-Loop** - When to request human intervention

**Related Documents:**
- Agent Architecture: `agents/AGENT_ARCHITECTURE.md`
- Task Breakdown: `TASK_BREAKDOWN.md`
- Requirements: `REQUIREMENTS.md`

---

## 1. AGENT HOOKS (EVENT-DRIVEN SYSTEM)

### 1.1 Hook Architecture

**Philosophy:** Agents react to **events** rather than being manually triggered.

```
┌─────────────────────────────────────────────────────────────┐
│                    EVENT BUS (Redis Pub/Sub)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Agent A      │ │  Agent B      │ │  Agent C      │
│  (subscribed  │ │  (subscribed  │ │  (subscribed  │
│   to event X) │ │   to event Y) │ │   to event Z) │
└───────────────┘ └───────────────┘ └───────────────┘
```

**Event Flow Example:**
```
1. Data Ingestion Agent finishes loading raw.icustays
2. Agent publishes event: "data.ingested.icustays"
3. ETL Agent (subscribed to "data.ingested.*") receives event
4. ETL Agent triggers dbt run
5. ETL Agent publishes event: "etl.complete.staging"
6. Feature Engineering Agent (subscribed) receives event
7. ... (chain continues)
```

---

### 1.2 Hook Definitions

#### Hook 1: `on_data_ingested`
**Event Name:** `data.ingested.{table_name}`

**Trigger:** When Data Ingestion Agent completes loading a table

**Example Event Payload:**
```json
{
  "event_type": "data.ingested.icustays",
  "timestamp": "2025-01-20T10:30:00Z",
  "agent": "data_ingestion_agent",
  "data": {
    "table_name": "raw.icustays",
    "rows_loaded": 73181,
    "execution_time_seconds": 120,
    "checksum": "a1b2c3d4e5f6",
    "quality_score": 0.98
  }
}
```

**Subscribed Agents:**
- ETL Agent (Data Transformation)
- Data Quality Agent

**Actions Triggered:**
- ETL Agent: Start dbt run for staging models
- Data Quality Agent: Run Great Expectations validation

**Implementation:**
```python
# agents/core/event_bus.py

import redis
import json

class EventBus:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
    
    def publish(self, event_type: str, data: dict):
        """Publish event to all subscribers."""
        event = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.redis.publish(event_type, json.dumps(event))
    
    def subscribe(self, pattern: str, callback):
        """Subscribe to events matching pattern."""
        self.pubsub.psubscribe(**{pattern: callback})
        thread = self.pubsub.run_in_thread(sleep_time=0.1)
        return thread

# Usage in Data Ingestion Agent
from agents.core.event_bus import EventBus

class DataIngestionAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.event_bus = EventBus()
    
    def execute(self, context):
        # ... (ingestion logic)
        
        # Publish event when done
        self.event_bus.publish(
            f"data.ingested.{table_name}",
            {
                'table_name': table_name,
                'rows_loaded': rows_loaded,
                'checksum': checksum
            }
        )

# ETL Agent subscribes
class ETLAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.event_bus = EventBus()
        
        # Subscribe to all data.ingested.* events
        self.event_bus.subscribe(
            'data.ingested.*',
            self.handle_data_ingested
        )
    
    def handle_data_ingested(self, message):
        event = json.loads(message['data'])
        logger.info(f"Received event: {event['event_type']}")
        
        # Trigger dbt run
        self.run_dbt_staging()
```

---

#### Hook 2: `on_etl_complete`
**Event Name:** `etl.complete.{layer}`

**Trigger:** When ETL Agent completes a dbt run (staging/marts)

**Example Event Payload:**
```json
{
  "event_type": "etl.complete.staging",
  "timestamp": "2025-01-20T10:35:00Z",
  "agent": "data_transformation_agent",
  "data": {
    "layer": "staging",
    "models_run": 6,
    "tests_passed": 45,
    "tests_failed": 0,
    "execution_time_seconds": 180
  }
}
```

**Subscribed Agents:**
- Data Quality Agent
- Feature Engineering Agent (if layer == 'marts')

**Actions Triggered:**
- Data Quality Agent: Run comprehensive quality checks
- Feature Engineering Agent: Start feature creation

---

#### Hook 3: `on_feature_table_updated`
**Event Name:** `features.updated.{model_name}`

**Trigger:** When Feature Engineering Agent completes feature table

**Example Event Payload:**
```json
{
  "event_type": "features.updated.sepsis",
  "timestamp": "2025-01-20T11:00:00Z",
  "agent": "feature_engineering_agent",
  "data": {
    "feature_table": "analytics.features_sepsis_6h",
    "num_features": 42,
    "num_samples": 20000,
    "feature_hash": "abc123def456"
  }
}
```

**Subscribed Agents:**
- Model Training Agent

**Actions Triggered:**
- Model Training Agent: Initiate model retraining

---

#### Hook 4: `on_model_registered`
**Event Name:** `model.registered.{model_name}`

**Trigger:** When Model Training Agent registers model in MLflow

**Example Event Payload:**
```json
{
  "event_type": "model.registered.sepsis_lightgbm_v1",
  "timestamp": "2025-01-20T13:00:00Z",
  "agent": "model_training_agent",
  "data": {
    "model_name": "sepsis_lightgbm_v1",
    "model_version": 2,
    "stage": "Staging",
    "metrics": {
      "auroc": 0.87,
      "sensitivity": 0.84,
      "specificity": 0.83
    }
  }
}
```

**Subscribed Agents:**
- Model Evaluation Agent
- API Development Agent (if metrics meet threshold)

**Actions Triggered:**
- Model Evaluation Agent: Generate comprehensive evaluation report
- API Development Agent: Update model in API (if approved)

---

#### Hook 5: `on_model_approved`
**Event Name:** `model.approved.{model_name}`

**Trigger:** When Decision Engine approves model for production

**Example Event Payload:**
```json
{
  "event_type": "model.approved.sepsis_lightgbm_v1",
  "timestamp": "2025-01-20T14:00:00Z",
  "agent": "decision_engine_agent",
  "data": {
    "model_name": "sepsis_lightgbm_v1",
    "model_version": 2,
    "approval_reason": "Metrics exceed thresholds (AUROC: 0.87 > 0.85)",
    "approved_by": "automated_system"
  }
}
```

**Subscribed Agents:**
- Deployment Agent

**Actions Triggered:**
- Deployment Agent: Promote model to Production stage in MLflow
- Deployment Agent: Update FastAPI to load new model version
- Deployment Agent: Invalidate Redis cache

---

#### Hook 6: `on_drift_detected`
**Event Name:** `monitoring.drift_detected.{feature}`

**Trigger:** When Data Drift Detection Agent detects distribution shift

**Example Event Payload:**
```json
{
  "event_type": "monitoring.drift_detected.lactate",
  "timestamp": "2025-01-20T16:00:00Z",
  "agent": "data_drift_detection_agent",
  "data": {
    "feature_name": "lactate",
    "drift_score": 0.15,
    "threshold": 0.10,
    "recommendation": "Retrain model or investigate data quality issue"
  }
}
```

**Subscribed Agents:**
- Alert Management Agent
- Decision Engine Agent

**Actions Triggered:**
- Alert Management Agent: Send Slack notification to team
- Decision Engine Agent: Evaluate if retraining is needed

---

#### Hook 7: `on_api_error_spike`
**Event Name:** `monitoring.api_error_spike`

**Trigger:** When Performance Monitor Agent detects error rate spike

**Example Event Payload:**
```json
{
  "event_type": "monitoring.api_error_spike",
  "timestamp": "2025-01-20T17:00:00Z",
  "agent": "performance_monitor_agent",
  "data": {
    "error_rate": 0.08,
    "threshold": 0.05,
    "time_window": "5m",
    "error_types": {
      "500_internal_server_error": 45,
      "422_validation_error": 15
    }
  }
}
```

**Subscribed Agents:**
- Alert Management Agent
- Decision Engine Agent

**Actions Triggered:**
- Alert Management Agent: Page on-call engineer
- Decision Engine Agent: Evaluate if rollback is needed

---

### 1.3 Hook Registry

**All hooks registered in `agents/config/hooks.yaml`:**

```yaml
hooks:
  data.ingested.*:
    description: "Triggered when data ingestion completes"
    publishers:
      - data_ingestion_agent
    subscribers:
      - data_transformation_agent
      - data_quality_agent
    priority: high
    
  etl.complete.*:
    description: "Triggered when ETL layer completes"
    publishers:
      - data_transformation_agent
    subscribers:
      - data_quality_agent
      - feature_engineering_agent
    priority: high
    
  features.updated.*:
    description: "Triggered when feature table updated"
    publishers:
      - feature_engineering_agent
    subscribers:
      - model_training_agent
    priority: high
    
  model.registered.*:
    description: "Triggered when model registered in MLflow"
    publishers:
      - model_training_agent
    subscribers:
      - model_evaluation_agent
      - api_development_agent
    priority: critical
    
  model.approved.*:
    description: "Triggered when model approved for production"
    publishers:
      - decision_engine_agent
    subscribers:
      - deployment_agent
    priority: critical
    
  monitoring.drift_detected.*:
    description: "Triggered when data drift detected"
    publishers:
      - data_drift_detection_agent
    subscribers:
      - alert_management_agent
      - decision_engine_agent
    priority: medium
    
  monitoring.api_error_spike:
    description: "Triggered when API error rate spikes"
    publishers:
      - performance_monitor_agent
    subscribers:
      - alert_management_agent
      - decision_engine_agent
    priority: critical
```

---

## 2. STEERING POLICIES

### 2.1 Decision Framework

**Agents make decisions based on:**
1. **Rules** (hard-coded conditions)
2. **Thresholds** (configurable metrics)
3. **Context** (current system state)
4. **History** (past events)

```
┌─────────────────────────────────────────────────────────────┐
│                    DECISION ENGINE AGENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: Event + Context                                     │
│     ↓                                                        │
│  Step 1: Check Rules                                        │
│     ↓                                                        │
│  Step 2: Evaluate Thresholds                                │
│     ↓                                                        │
│  Step 3: Consult History                                    │
│     ↓                                                        │
│  Step 4: Calculate Confidence                               │
│     ↓                                                        │
│  Decision: ✅ Auto-proceed / ⏸️ Request Human / ❌ Abort    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.2 Policy: Model Approval for Production

**Trigger:** Model registered in MLflow (Staging stage)

**Decision Logic:**
```python
def should_approve_model_for_production(model_metrics, current_production_metrics):
    """
    Decide whether to approve model for production.
    
    Returns:
        - "auto_approve": Metrics clearly better, auto-promote
        - "request_human": Close call, need human review
        - "reject": Metrics worse, do not promote
    """
    
    # Rule 1: Minimum thresholds (hard requirements)
    if model_metrics['auroc'] < 0.85:
        return "reject", "AUROC below minimum threshold (0.85)"
    
    if model_metrics['sensitivity'] < 0.80:
        return "reject", "Sensitivity below minimum threshold (0.80)"
    
    # Rule 2: Improvement over current production model
    auroc_improvement = model_metrics['auroc'] - current_production_metrics['auroc']
    
    if auroc_improvement >= 0.03:  # 3% improvement
        return "auto_approve", "Significant AUROC improvement (≥3%)"
    
    elif auroc_improvement >= 0.01:  # 1-3% improvement
        return "request_human", "Moderate improvement, recommend human review"
    
    else:  # <1% improvement or worse
        # Check if other metrics improved
        sens_improvement = model_metrics['sensitivity'] - current_production_metrics['sensitivity']
        spec_improvement = model_metrics['specificity'] - current_production_metrics['specificity']
        
        if sens_improvement > 0.05 or spec_improvement > 0.05:
            return "request_human", "AUROC similar but sensitivity/specificity improved"
        else:
            return "reject", "No significant improvement over current production model"
    
    # Rule 3: Check for regressions in secondary metrics
    if model_metrics['sensitivity'] < current_production_metrics['sensitivity'] - 0.05:
        return "request_human", "WARNING: Sensitivity dropped by >5%"
    
    # Default: request human review if logic unclear
    return "request_human", "Unusual case, recommend manual review"
```

**Configuration:**
```yaml
# agents/config/policies.yaml

model_approval_policy:
  minimum_thresholds:
    auroc: 0.85
    sensitivity: 0.80
    specificity: 0.80
  
  auto_approve_conditions:
    - auroc_improvement >= 0.03  # 3% better
  
  request_human_conditions:
    - auroc_improvement between [0.01, 0.03]
    - sensitivity_drop > 0.05
    - specificity_drop > 0.05
  
  reject_conditions:
    - auroc < minimum_thresholds.auroc
    - auroc_improvement < 0.01
```

---

### 2.3 Policy: ETL Failure Handling

**Trigger:** dbt run fails (e.g., SQL error in staging model)

**Decision Logic:**
```python
def handle_etl_failure(failure_info):
    """
    Decide how to handle ETL failure.
    
    Returns:
        - "retry": Transient error, retry immediately
        - "rollback": Critical error, rollback to last good state
        - "alert_human": Unknown error, need investigation
    """
    
    error_type = failure_info['error_type']
    error_count = failure_info['consecutive_failures']
    
    # Rule 1: Transient errors (network, timeout)
    if error_type in ['ConnectionError', 'TimeoutError']:
        if error_count < 3:
            return "retry", "Transient error, retry with exponential backoff"
        else:
            return "alert_human", "Persistent connection issues, need investigation"
    
    # Rule 2: SQL syntax errors (code bug)
    if error_type == 'SQLSyntaxError':
        return "alert_human", "SQL syntax error detected, code fix required"
    
    # Rule 3: Data quality failures
    if error_type == 'DataQualityError':
        if failure_info['quality_score'] > 0.90:  # Borderline
            return "retry", "Quality score 90-95%, retry with more lenient thresholds"
        else:
            return "alert_human", "Severe data quality issues, manual review required"
    
    # Rule 4: Dependency errors (upstream table missing)
    if error_type == 'DependencyError':
        # Check if upstream agent is still running
        if is_upstream_agent_running(failure_info['missing_table']):
            return "retry", "Upstream agent in progress, retry in 5 minutes"
        else:
            return "alert_human", "Upstream dependency failed, need to fix root cause"
    
    # Default: alert human for unknown errors
    return "alert_human", f"Unknown error type: {error_type}"
```

---

### 2.4 Policy: Data Drift Response

**Trigger:** Drift detected in input features

**Decision Logic:**
```python
def handle_data_drift(drift_info):
    """
    Decide how to respond to data drift.
    
    Returns:
        - "ignore": Minor drift, acceptable
        - "alert": Moderate drift, inform team but continue
        - "retrain": Significant drift, initiate model retraining
        - "rollback": Severe drift, rollback to previous model
    """
    
    drift_score = drift_info['drift_score']
    consecutive_drift_days = drift_info['consecutive_drift_days']
    feature_name = drift_info['feature_name']
    
    # Rule 1: Minor drift (acceptable variation)
    if drift_score < 0.10:
        return "ignore", "Drift within acceptable range"
    
    # Rule 2: Moderate drift (monitor)
    elif drift_score < 0.15:
        if consecutive_drift_days < 3:
            return "alert", "Moderate drift detected, monitoring"
        else:
            return "retrain", "Persistent drift for 3+ days, recommend retraining"
    
    # Rule 3: Significant drift (action required)
    elif drift_score < 0.25:
        return "retrain", "Significant drift, initiate model retraining"
    
    # Rule 4: Severe drift (potential data quality issue)
    else:
        # Check if it's a critical feature
        if feature_name in ['lactate', 'heart_rate', 'wbc']:
            return "rollback", "CRITICAL: Severe drift in key feature, rollback model"
        else:
            return "alert", "Severe drift in non-critical feature, investigate data quality"
```

---

### 2.5 Policy: API Rate Limiting & Circuit Breaking

**Trigger:** High request volume or error rate

**Decision Logic:**
```python
def handle_api_load(load_info):
    """
    Decide whether to apply rate limiting or circuit breaking.
    
    Returns:
        - "normal": No action needed
        - "rate_limit": Apply rate limiting
        - "circuit_break": Open circuit breaker, reject requests
    """
    
    requests_per_second = load_info['requests_per_second']
    error_rate = load_info['error_rate']
    p95_latency_ms = load_info['p95_latency_ms']
    
    # Rule 1: Check capacity
    if requests_per_second > 500:  # Max capacity
        return "rate_limit", "Request volume exceeds capacity (500 req/s)"
    
    # Rule 2: Check error rate
    if error_rate > 0.10:  # 10% error rate
        if error_rate > 0.50:  # 50% error rate
            return "circuit_break", "CRITICAL: Error rate >50%, opening circuit breaker"
        else:
            return "rate_limit", "High error rate (>10%), applying rate limiting"
    
    # Rule 3: Check latency
    if p95_latency_ms > 500:  # p95 > 500ms
        return "rate_limit", "High latency detected, reducing load"
    
    return "normal", "System operating normally"
```

---

## 3. FAILURE HANDLING STRATEGIES

### 3.1 Retry Policies

**Exponential Backoff with Jitter:**

```python
# agents/core/retry_policy.py

import time
import random

class RetryPolicy:
    """Configurable retry policy with exponential backoff."""
    
    def __init__(self, max_retries=3, base_delay=1, max_delay=60):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def calculate_delay(self, attempt):
        """Calculate delay for given attempt."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = random.uniform(0, delay * 0.1)  # Add 10% jitter
        return delay + jitter
    
    def should_retry(self, error):
        """Determine if error is retryable."""
        retryable_errors = [
            'ConnectionError',
            'TimeoutError',
            'TemporaryFailure'
        ]
        return error.__class__.__name__ in retryable_errors

# Usage in agent
class DataIngestionAgent(BaseAgent):
    def execute_with_retry(self, context):
        policy = RetryPolicy(max_retries=3)
        
        for attempt in range(policy.max_retries):
            try:
                return self.execute(context)
            except Exception as e:
                if policy.should_retry(e) and attempt < policy.max_retries - 1:
                    delay = policy.calculate_delay(attempt)
                    logger.warning(f"Attempt {attempt+1} failed, retrying in {delay:.2f}s")
                    time.sleep(delay)
                else:
                    raise
```

---

### 3.2 Circuit Breaker Pattern

**Prevent cascading failures:**

```python
# agents/core/circuit_breaker.py

from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""
    
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        
        # Check if circuit should transition to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN, rejecting request")
        
        try:
            result = func(*args, **kwargs)
            
            # Success: reset counter or close circuit
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker CLOSED after successful request")
            
            self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
            
            raise

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

def call_external_api():
    response = requests.get("https://external-api.com/data")
    return response.json()

# Protected call
try:
    result = circuit_breaker.call(call_external_api)
except Exception as e:
    logger.error(f"Call failed or circuit open: {e}")
```

---

### 3.3 Fallback Strategies

**Graceful degradation when primary method fails:**

```python
# agents/core/fallback.py

class FallbackStrategy:
    """Execute fallback logic when primary method fails."""
    
    def execute_with_fallback(self, primary_func, fallback_func, *args, **kwargs):
        """Try primary function, fall back if it fails."""
        
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary function failed: {e}, using fallback")
            return fallback_func(*args, **kwargs)

# Example: Model prediction with fallback
def predict_with_latest_model(features):
    """Use latest model version."""
    model = mlflow.pyfunc.load_model("models:/sepsis_lightgbm_v1/Production")
    return model.predict(features)

def predict_with_baseline_model(features):
    """Fallback to stable baseline model."""
    model = mlflow.pyfunc.load_model("models:/sepsis_lightgbm_v1/1")  # Version 1
    return model.predict(features)

fallback = FallbackStrategy()
prediction = fallback.execute_with_fallback(
    predict_with_latest_model,
    predict_with_baseline_model,
    features
)
```

---

## 4. HUMAN-IN-THE-LOOP POLICIES

### 4.1 When to Request Human Intervention

**Automatic approval thresholds:**
- Model AUROC improvement ≥3% → Auto-approve
- Model AUROC improvement 1-3% → Request human
- Model AUROC < minimum threshold → Auto-reject

**Request human for:**
1. **Ambiguous decisions** (metrics borderline)
2. **Critical changes** (production deployment)
3. **Unexpected errors** (unknown error types)
4. **High-risk operations** (data deletion, schema changes)
5. **Security concerns** (unusual access patterns)

---

### 4.2 Human Approval Workflow

```python
# agents/core/human_approval.py

class HumanApprovalRequest:
    """Request human approval for agent action."""
    
    def __init__(self, slack_webhook_url):
        self.slack_webhook = slack_webhook_url
    
    def request_approval(self, decision_context):
        """
        Send approval request to Slack, wait for response.
        
        Returns:
            - "approved": Human approved action
            - "rejected": Human rejected action
            - "timeout": No response within timeout
        """
        
        # Send Slack message
        message = self._format_approval_message(decision_context)
        self._send_slack_message(message)
        
        # Wait for response (via webhook callback)
        response = self._wait_for_response(timeout_seconds=3600)  # 1 hour
        
        return response
    
    def _format_approval_message(self, context):
        return {
            "text": f"🤖 Agent Approval Request",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Agent:* {context['agent_name']}\n*Action:* {context['action']}\n*Reason:* {context['reason']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Confidence:* {context['confidence']:.0%}\n*Recommendation:* {context['recommendation']}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✅ Approve"},
                            "style": "primary",
                            "value": "approve"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "❌ Reject"},
                            "style": "danger",
                            "value": "reject"
                        }
                    ]
                }
            ]
        }
```

---

## 5. STEERING CONFIGURATION

**All policies defined in `agents/config/steering_policies.yaml`:**

```yaml
# agents/config/steering_policies.yaml

steering_policies:
  model_approval:
    minimum_thresholds:
      auroc: 0.85
      sensitivity: 0.80
      specificity: 0.80
    
    auto_approve_if:
      - auroc_improvement >= 0.03
    
    request_human_if:
      - auroc_improvement between [0.01, 0.03]
      - sensitivity_drop > 0.05
    
    auto_reject_if:
      - auroc < 0.85
      - auroc_improvement < 0.01
  
  etl_failure:
    retry_transient_errors: true
    max_retries: 3
    backoff_multiplier: 2
    
    retryable_errors:
      - ConnectionError
      - TimeoutError
      - TemporaryFailure
    
    alert_human_errors:
      - SQLSyntaxError
      - DataQualityError (if quality_score < 0.90)
  
  data_drift:
    acceptable_drift: 0.10
    moderate_drift: 0.15
    severe_drift: 0.25
    
    actions:
      - drift < 0.10: ignore
      - drift 0.10-0.15: alert
      - drift 0.15-0.25: retrain
      - drift > 0.25: rollback (if critical feature)
  
  api_rate_limiting:
    max_requests_per_second: 500
    error_rate_threshold: 0.10
    critical_error_rate: 0.50
    latency_threshold_ms: 500
    
    actions:
      - error_rate > 0.50: circuit_break
      - error_rate > 0.10: rate_limit
      - latency > 500ms: rate_limit
  
  human_approval:
    required_for:
      - production_deployment
      - data_deletion
      - schema_changes
      - ambiguous_decisions (confidence < 0.80)
    
    approval_timeout: 3600  # 1 hour
    approval_channels:
      - slack_webhook_url: "https://hooks.slack.com/..."
      - email: "team@example.com"
```

---

## SUMMARY

✅ **Agent Hooks:** 7 core event types defined  
✅ **Steering Policies:** 5 decision frameworks implemented  
✅ **Failure Handling:** Retry, circuit breaker, fallback strategies  
✅ **Human-in-the-Loop:** Clear escalation policies  
✅ **Configuration:** All policies in YAML for easy tuning

**Next Steps:** See `agents/` directory for implementations

---

**Document Version:** 1.0  
**Status:** ✅ APPROVED - Implementation Ready  
**Owner:** Agent Architect
