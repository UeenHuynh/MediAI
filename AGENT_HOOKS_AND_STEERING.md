# Agent Hooks & Steering Design
**Healthcare ML Platform - Agent Orchestration & Control**

**Version:** 1.0  
**Status:** Design Approved  
**Last Updated:** 2025-01-20

---

## DOCUMENT PURPOSE

This document defines **agent hooks** (event-driven triggers) and **steering policies** (decision-making rules) for the CrewAI-based agent architecture.

**Related Documents:**
- Agent Architecture: `agents/AGENT_ARCHITECTURE.md`
- Agent Configuration: `agents/config/agents.yaml`
- Task Breakdown: `TASK_BREAKDOWN.md`

---

## 1. AGENT HOOKS (EVENT-DRIVEN TRIGGERS)

### 1.1 Hook Philosophy

**Hooks enable reactive workflows:**
- Agents react to system events (data ingested, model trained, etc.)
- No manual intervention needed for routine tasks
- Loose coupling between components

**Hook Pattern:**
```python
@hook('on_new_data_ingested')
def trigger_etl_pipeline(context):
    """Automatically run ETL when new data arrives."""
    etl_crew = DataPipelineCrew()
    etl_crew.kickoff(inputs={'trigger': 'new_data'})
```

---

### 1.2 Core System Hooks

#### HOOK-DATA-001: on_new_data_ingested

**Trigger Event:** New CSV file successfully loaded into `raw` schema

**Emitted By:** Data Ingestion Agent

**Payload:**
```python
{
    'table_name': 'raw.icustays',
    'rows_loaded': 73181,
    'timestamp': '2025-01-20T10:30:00Z',
    'checksum': 'a1b2c3d4...',
    'source_file': '/data/mimic-iv/icu/icustays.csv'
}
```

**Subscribed Agents:**
- Data Transformation Agent → Triggers dbt run
- Data Quality Agent → Triggers validation suite
- Workflow Orchestrator → Updates pipeline status

**Action Taken:**
```python
# airflow/dags/reactive_etl_dag.py
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_ingestion = ExternalTaskSensor(
    task_id='wait_for_data_ingestion',
    external_dag_id='ingest_mimic_iv',
    external_task_id='ingest_complete',
    mode='reschedule'
)

run_dbt = BashOperator(
    task_id='run_dbt_staging',
    bash_command='dbt run --models staging.*'
)

wait_for_ingestion >> run_dbt
```

**Steering Policy:**
- **IF** ingestion failed → Do NOT trigger ETL, alert human
- **IF** data quality score <90% → Trigger investigation, pause ETL
- **IF** ingestion successful → Proceed with ETL

---

#### HOOK-DATA-002: on_feature_table_updated

**Trigger Event:** Feature tables refreshed in `analytics` schema

**Emitted By:** Feature Engineering Agent

**Payload:**
```python
{
    'feature_table': 'analytics.features_sepsis_6h',
    'rows_updated': 20000,
    'new_features_added': [],
    'feature_schema_hash': 'e5f6g7h8...',
    'timestamp': '2025-01-20T12:00:00Z'
}
```

**Subscribed Agents:**
- Model Training Agent → Checks if retraining needed
- Model Evaluation Agent → Validates feature distributions
- Decision Engine Agent → Decides whether to auto-retrain

**Action Taken:**
```python
# agents/hooks/feature_update_hook.py

@hook('on_feature_table_updated')
def check_retraining_needed(payload):
    """Decide if model retraining is needed."""
    
    # Check 1: Has schema changed?
    current_hash = payload['feature_schema_hash']
    model_metadata = mlflow.get_model_metadata("sepsis_lightgbm_v1")
    trained_on_hash = model_metadata.tags.get('feature_schema_hash')
    
    if current_hash != trained_on_hash:
        logger.warning("Feature schema changed, retraining required")
        return DecisionEngine.recommend_action('RETRAIN_URGENCY_HIGH')
    
    # Check 2: Distribution shift?
    drift_detected = DataDriftDetectionAgent.check_drift(
        reference_data=model_metadata.artifacts['training_data'],
        current_data=payload['feature_table']
    )
    
    if drift_detected:
        logger.warning("Feature drift detected")
        return DecisionEngine.recommend_action('RETRAIN_URGENCY_MEDIUM')
    
    # Check 3: Scheduled retraining?
    days_since_training = (datetime.now() - model_metadata.created_at).days
    if days_since_training > 30:
        logger.info("Scheduled retraining due (30 days)")
        return DecisionEngine.recommend_action('RETRAIN_URGENCY_LOW')
    
    return DecisionEngine.recommend_action('NO_ACTION')
```

**Steering Policy:**
- **IF** feature schema changed → MUST retrain (blocking)
- **IF** drift detected (PSI >0.2) → SHOULD retrain (high priority)
- **IF** >30 days since training → MAY retrain (low priority)
- **IF** none of above → Skip retraining

---

#### HOOK-ML-001: on_model_registered

**Trigger Event:** New model version registered in MLflow registry

**Emitted By:** Model Training Agent

**Payload:**
```python
{
    'model_name': 'sepsis_lightgbm_v1',
    'version': 2,
    'run_id': 'abc123...',
    'metrics': {
        'auroc': 0.89,
        'sensitivity': 0.87,
        'specificity': 0.85
    },
    'stage': 'Staging',  # Not yet Production
    'timestamp': '2025-01-20T14:00:00Z'
}
```

**Subscribed Agents:**
- Model Evaluation Agent → Runs comprehensive evaluation
- Deployment Agent → Prepares deployment artifacts
- Alert Management Agent → Notifies team

**Action Taken:**
```python
@hook('on_model_registered')
def evaluate_and_deploy(payload):
    """Evaluate new model and decide if production-ready."""
    
    # Step 1: Run evaluation suite
    eval_results = ModelEvaluationAgent.comprehensive_eval(
        model_name=payload['model_name'],
        version=payload['version']
    )
    
    # Step 2: Compare with current production model
    production_version = mlflow.get_latest_versions(
        payload['model_name'], stages=['Production']
    )[0]
    
    comparison = compare_models(
        challenger=payload,
        champion=production_version
    )
    
    # Step 3: Decision logic
    if comparison['auroc_improvement'] > 0.03:  # 3% improvement
        logger.info("New model significantly better, promoting to Production")
        promote_to_production(payload)
    elif comparison['auroc_improvement'] > 0.01:  # 1-3% improvement
        logger.info("New model better, requesting human approval")
        request_human_approval(payload, comparison)
    else:
        logger.info("New model not better, keeping in Staging")
        keep_in_staging(payload)
```

**Steering Policy:**
- **IF** new AUROC > old AUROC + 0.03 → Auto-promote to Production
- **IF** new AUROC > old AUROC + 0.01 → Request human approval
- **IF** new AUROC ≤ old AUROC + 0.01 → Keep in Staging
- **IF** new AUROC < old AUROC → Alert, do NOT promote

---

#### HOOK-ML-002: on_model_approved

**Trigger Event:** Model promoted to Production stage in MLflow

**Emitted By:** Decision Engine Agent OR Human Operator

**Payload:**
```python
{
    'model_name': 'sepsis_lightgbm_v1',
    'version': 2,
    'stage': 'Production',
    'approved_by': 'decision_engine' | 'human:john@example.com',
    'timestamp': '2025-01-20T15:00:00Z'
}
```

**Subscribed Agents:**
- API Development Agent → Updates model in FastAPI
- Infrastructure Agent → Deploys to production environment
- Monitoring Agent → Sets up drift detection

**Action Taken:**
```python
@hook('on_model_approved')
def deploy_to_production(payload):
    """Deploy newly approved model to production API."""
    
    # Step 1: Update API to load new model version
    api_service = APIService()
    api_service.reload_model(
        model_name=payload['model_name'],
        version=payload['version']
    )
    
    # Step 2: Clear Redis cache (old predictions invalid)
    cache_service = CacheService()
    cache_service.invalidate_all(model_name=payload['model_name'])
    
    # Step 3: Enable monitoring
    monitoring_agent = PerformanceMonitorAgent()
    monitoring_agent.setup_alerts(
        model_name=payload['model_name'],
        version=payload['version'],
        alert_thresholds={
            'latency_p95_ms': 200,
            'error_rate': 0.05,
            'auroc_drop': 0.03
        }
    )
    
    # Step 4: Notify stakeholders
    alert_management_agent = AlertManagementAgent()
    alert_management_agent.send_notification(
        channel='slack',
        message=f"Model {payload['model_name']} v{payload['version']} deployed to Production"
    )
```

**Steering Policy:**
- **ALWAYS** reload API model
- **ALWAYS** clear cache
- **ALWAYS** enable monitoring
- **IF** deployment fails → Rollback to previous version

---

#### HOOK-MONITOR-001: on_drift_detected

**Trigger Event:** Statistical drift detected in input features or predictions

**Emitted By:** Data Drift Detection Agent

**Payload:**
```python
{
    'model_name': 'sepsis_lightgbm_v1',
    'drift_type': 'covariate_shift' | 'concept_drift',
    'features_drifted': ['lactate', 'heart_rate'],
    'psi_scores': {
        'lactate': 0.25,  # PSI > 0.2 indicates drift
        'heart_rate': 0.18
    },
    'severity': 'HIGH' | 'MEDIUM' | 'LOW',
    'timestamp': '2025-01-20T16:00:00Z'
}
```

**Subscribed Agents:**
- Model Training Agent → Prepares retraining
- Alert Management Agent → Notifies team
- Decision Engine Agent → Decides action

**Action Taken:**
```python
@hook('on_drift_detected')
def handle_drift(payload):
    """Handle detected data drift."""
    
    severity = payload['severity']
    
    if severity == 'HIGH':
        # Critical drift - immediate action
        logger.critical("High severity drift detected")
        
        # Alert humans
        AlertManagementAgent.send_alert(
            severity='critical',
            message=f"High drift in {payload['features_drifted']}",
            channels=['slack', 'email', 'pagerduty']
        )
        
        # Initiate emergency retraining
        ModelTrainingAgent.emergency_retrain(
            model_name=payload['model_name'],
            priority='HIGH'
        )
    
    elif severity == 'MEDIUM':
        # Moderate drift - schedule retraining
        logger.warning("Medium severity drift detected")
        
        AlertManagementAgent.send_alert(
            severity='warning',
            message=f"Moderate drift in {payload['features_drifted']}",
            channels=['slack']
        )
        
        # Schedule retraining within 48 hours
        schedule_retraining(
            model_name=payload['model_name'],
            deadline='48h'
        )
    
    else:  # LOW
        # Minor drift - log and monitor
        logger.info("Low severity drift detected")
        
        # Just log, no immediate action
        drift_log = {
            'timestamp': payload['timestamp'],
            'features': payload['features_drifted'],
            'psi_scores': payload['psi_scores']
        }
        
        store_drift_log(drift_log)
```

**Steering Policy:**
- **IF** drift severity HIGH → Alert humans + emergency retrain
- **IF** drift severity MEDIUM → Alert + schedule retrain (48h)
- **IF** drift severity LOW → Log + monitor
- **IF** consecutive drift (3 times) → Escalate severity

---

#### HOOK-MONITOR-002: on_performance_degradation

**Trigger Event:** Model performance drops below acceptable threshold

**Emitted By:** Performance Monitor Agent

**Payload:**
```python
{
    'model_name': 'sepsis_lightgbm_v1',
    'metric': 'auroc',
    'current_value': 0.82,
    'expected_value': 0.87,
    'degradation_pct': -5.7,
    'threshold': 0.85,
    'timestamp': '2025-01-20T17:00:00Z'
}
```

**Subscribed Agents:**
- Model Evaluation Agent → Investigates cause
- Decision Engine Agent → Decides rollback or retrain
- Alert Management Agent → Notifies team

**Action Taken:**
```python
@hook('on_performance_degradation')
def handle_performance_drop(payload):
    """Handle model performance degradation."""
    
    degradation_pct = abs(payload['degradation_pct'])
    
    if degradation_pct > 5:  # >5% drop
        logger.critical("Critical performance degradation")
        
        # Alert immediately
        AlertManagementAgent.page_oncall(
            message=f"URGENT: {payload['model_name']} AUROC dropped to {payload['current_value']}"
        )
        
        # Investigate cause
        investigation = ModelEvaluationAgent.investigate_degradation(
            model_name=payload['model_name']
        )
        
        if investigation['cause'] == 'data_drift':
            # Drift is the issue - retrain
            logger.info("Cause: data drift - initiating retrain")
            ModelTrainingAgent.emergency_retrain()
        
        elif investigation['cause'] == 'data_quality':
            # Bad data - pause predictions
            logger.critical("Cause: data quality - pausing predictions")
            APIService.pause_predictions(payload['model_name'])
            AlertManagementAgent.alert_data_team()
        
        else:
            # Unknown cause - rollback
            logger.warning("Unknown cause - rolling back to previous version")
            rollback_to_previous_version(payload['model_name'])
    
    elif degradation_pct > 3:  # 3-5% drop
        logger.warning("Moderate performance degradation")
        
        # Alert but don't act immediately
        AlertManagementAgent.send_alert(
            severity='warning',
            message=f"{payload['model_name']} performance dropped by {degradation_pct}%"
        )
        
        # Schedule investigation
        schedule_investigation(payload['model_name'])
```

**Steering Policy:**
- **IF** degradation >5% → Page on-call + immediate action
- **IF** degradation 3-5% → Alert + schedule investigation
- **IF** degradation <3% → Log + monitor
- **IF** degradation due to data quality → Pause predictions

---

## 2. AGENT STEERING POLICIES

### 2.1 Steering Philosophy

**Steering = Decision-making rules for agents**

**Key Principles:**
1. **Autonomy with Guardrails:** Agents can act autonomously within defined boundaries
2. **Human-in-the-Loop:** Critical decisions require human approval
3. **Fail-Safe Defaults:** When uncertain, err on the side of caution
4. **Transparent Decisions:** All decisions logged with reasoning

---

### 2.2 Data Pipeline Steering

#### POLICY-DATA-001: When to Trigger ETL

**Decision Logic:**
```python
def should_trigger_etl(context):
    """Decide if ETL should run."""
    
    # Check 1: Is new data available?
    new_data_available = check_new_data()
    if not new_data_available:
        return Decision.SKIP(reason="No new data")
    
    # Check 2: Is data quality acceptable?
    quality_score = DataQualityAgent.check_quality()
    if quality_score < 0.90:
        return Decision.BLOCK(reason=f"Quality too low: {quality_score}")
    
    # Check 3: Is there enough time before next scheduled run?
    time_until_next_run = get_time_until_next_scheduled_run()
    estimated_etl_time = estimate_etl_duration()
    
    if time_until_next_run < estimated_etl_time * 1.2:
        return Decision.DEFER(reason="Not enough time, wait for scheduled run")
    
    # All checks passed
    return Decision.PROCEED(reason="All checks passed")
```

**Steering Rules:**
- ✅ **PROCEED** if: New data + quality >90% + sufficient time
- ⏸️ **SKIP** if: No new data
- 🚫 **BLOCK** if: Quality <90%
- ⏰ **DEFER** if: Insufficient time

---

#### POLICY-DATA-002: Data Quality Failure Handling

**Decision Tree:**
```
Data Quality Check
    ├─ Score ≥ 95% → PASS (proceed)
    ├─ Score 90-95% → WARN (proceed with caution)
    ├─ Score 80-90% → INVESTIGATE (pause, notify data team)
    └─ Score < 80% → FAIL (block pipeline, alert on-call)
```

**Steering Rules:**
```python
def handle_quality_failure(quality_score, issues):
    """Handle data quality failures."""
    
    if quality_score >= 0.95:
        return Action.PROCEED
    
    elif quality_score >= 0.90:
        logger.warning(f"Quality marginal: {quality_score}")
        AlertManagementAgent.send_alert(
            severity='warning',
            message="Data quality below optimal"
        )
        return Action.PROCEED_WITH_CAUTION
    
    elif quality_score >= 0.80:
        logger.error(f"Quality low: {quality_score}")
        AlertManagementAgent.notify_data_team(issues)
        return Action.PAUSE_PIPELINE
    
    else:  # < 80%
        logger.critical(f"Quality unacceptable: {quality_score}")
        AlertManagementAgent.page_oncall()
        return Action.BLOCK_PIPELINE
```

---

### 2.3 ML Model Steering

#### POLICY-ML-001: Model Promotion Decision

**Promotion Criteria Matrix:**

| Condition | Action | Approval Required |
|-----------|--------|-------------------|
| New AUROC > Old + 0.05 | Auto-promote | No |
| New AUROC > Old + 0.03 | Promote with notification | No |
| New AUROC > Old + 0.01 | Request approval | Yes |
| New AUROC ≈ Old (±0.01) | Keep in staging | N/A |
| New AUROC < Old | Keep in staging, investigate | N/A |

**Implementation:**
```python
class ModelPromotionPolicy:
    """Policy for model promotion decisions."""
    
    AUROC_THRESHOLD_AUTO = 0.05
    AUROC_THRESHOLD_NOTIFY = 0.03
    AUROC_THRESHOLD_APPROVAL = 0.01
    
    @staticmethod
    def decide(new_model_metrics, old_model_metrics):
        """Decide if new model should be promoted."""
        
        new_auroc = new_model_metrics['auroc']
        old_auroc = old_model_metrics['auroc']
        improvement = new_auroc - old_auroc
        
        if improvement >= ModelPromotionPolicy.AUROC_THRESHOLD_AUTO:
            return Decision(
                action='PROMOTE',
                approval_required=False,
                reason=f"Significant improvement: {improvement:.3f}"
            )
        
        elif improvement >= ModelPromotionPolicy.AUROC_THRESHOLD_NOTIFY:
            return Decision(
                action='PROMOTE',
                approval_required=False,
                reason=f"Notable improvement: {improvement:.3f}",
                notification_required=True
            )
        
        elif improvement >= ModelPromotionPolicy.AUROC_THRESHOLD_APPROVAL:
            return Decision(
                action='REQUEST_APPROVAL',
                approval_required=True,
                reason=f"Minor improvement: {improvement:.3f}"
            )
        
        else:
            return Decision(
                action='KEEP_IN_STAGING',
                approval_required=False,
                reason=f"Insufficient improvement: {improvement:.3f}"
            )
```

---

#### POLICY-ML-002: Retraining Trigger Policy

**Retraining Decision Matrix:**

| Trigger | Urgency | Action | Timeline |
|---------|---------|--------|----------|
| Feature schema changed | HIGH | Emergency retrain | Immediate |
| High drift (PSI >0.3) | HIGH | Scheduled retrain | <24h |
| Medium drift (PSI 0.2-0.3) | MEDIUM | Scheduled retrain | <48h |
| Low drift (PSI 0.1-0.2) | LOW | Consider retrain | <7 days |
| Performance drop >5% | CRITICAL | Emergency retrain + investigate | Immediate |
| Performance drop 3-5% | HIGH | Scheduled retrain | <24h |
| >30 days since training | LOW | Routine retrain | <7 days |

**Implementation:**
```python
class RetrainingPolicy:
    """Policy for deciding when to retrain models."""
    
    @staticmethod
    def evaluate_need(context):
        """Evaluate if retraining is needed."""
        
        urgency_scores = []
        
        # Check 1: Feature schema
        if context['feature_schema_changed']:
            urgency_scores.append(('CRITICAL', 'Feature schema changed'))
        
        # Check 2: Data drift
        max_psi = max(context['psi_scores'].values())
        if max_psi > 0.3:
            urgency_scores.append(('HIGH', f'High drift: PSI={max_psi:.2f}'))
        elif max_psi > 0.2:
            urgency_scores.append(('MEDIUM', f'Medium drift: PSI={max_psi:.2f}'))
        elif max_psi > 0.1:
            urgency_scores.append(('LOW', f'Low drift: PSI={max_psi:.2f}'))
        
        # Check 3: Performance degradation
        performance_drop = context['performance_drop_pct']
        if performance_drop > 5:
            urgency_scores.append(('CRITICAL', f'Performance drop: {performance_drop}%'))
        elif performance_drop > 3:
            urgency_scores.append(('HIGH', f'Performance drop: {performance_drop}%'))
        
        # Check 4: Age
        days_since_training = context['days_since_last_training']
        if days_since_training > 30:
            urgency_scores.append(('LOW', f'Model age: {days_since_training} days'))
        
        # Determine overall urgency (highest urgency wins)
        if not urgency_scores:
            return RetrainingDecision(urgency='NONE', reasons=[])
        
        urgency_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        max_urgency = min(urgency_scores, key=lambda x: urgency_order.index(x[0]))
        
        return RetrainingDecision(
            urgency=max_urgency[0],
            reasons=[reason for _, reason in urgency_scores],
            timeline=RetrainingPolicy.get_timeline(max_urgency[0])
        )
    
    @staticmethod
    def get_timeline(urgency):
        """Get retraining timeline based on urgency."""
        timelines = {
            'CRITICAL': 'IMMEDIATE',
            'HIGH': '<24h',
            'MEDIUM': '<48h',
            'LOW': '<7days'
        }
        return timelines.get(urgency, 'NONE')
```

---

### 2.4 Deployment Steering

#### POLICY-DEPLOY-001: Production Deployment Approval

**Approval Requirements:**

| Change Type | Approval Required | Approvers |
|-------------|-------------------|-----------|
| Model update (auto-promoted) | No | N/A |
| Model update (manual-approved) | Yes | ML Lead |
| Infrastructure change | Yes | DevOps + ML Lead |
| Breaking API change | Yes | DevOps + ML Lead + Product |
| Data schema change | Yes | Data Eng + ML Lead |

**Implementation:**
```python
class DeploymentApprovalPolicy:
    """Policy for deployment approvals."""
    
    @staticmethod
    def get_required_approvers(change_type):
        """Get required approvers for a change."""
        
        approvers_map = {
            'model_update_auto': [],
            'model_update_manual': ['ml_lead'],
            'infrastructure': ['devops', 'ml_lead'],
            'api_breaking': ['devops', 'ml_lead', 'product'],
            'data_schema': ['data_eng', 'ml_lead']
        }
        
        return approvers_map.get(change_type, ['ml_lead', 'devops'])
    
    @staticmethod
    def request_approval(change_description, change_type):
        """Request approval for a deployment."""
        
        approvers = DeploymentApprovalPolicy.get_required_approvers(change_type)
        
        if not approvers:
            # No approval needed
            return ApprovalDecision(
                approved=True,
                reason='No approval required for this change type'
            )
        
        # Send approval request
        approval_request = {
            'change_description': change_description,
            'change_type': change_type,
            'approvers': approvers,
            'created_at': datetime.now()
        }
        
        # Store request and wait for approvals
        request_id = store_approval_request(approval_request)
        
        return ApprovalDecision(
            approved=False,
            pending=True,
            request_id=request_id,
            approvers=approvers
        )
```

---

#### POLICY-DEPLOY-002: Rollback Decision

**Rollback Triggers:**

| Condition | Action | Automatic? |
|-----------|--------|------------|
| Deployment fails (error) | Rollback immediately | Yes |
| API error rate >10% | Rollback immediately | Yes |
| API latency p95 >500ms | Rollback immediately | Yes |
| Model error rate >5% | Rollback immediately | Yes |
| Performance drop >10% | Rollback + investigate | Yes |
| Performance drop 5-10% | Alert + manual decision | No |

**Implementation:**
```python
class RollbackPolicy:
    """Policy for deployment rollbacks."""
    
    # Thresholds
    API_ERROR_RATE_THRESHOLD = 0.10
    API_LATENCY_P95_THRESHOLD_MS = 500
    MODEL_ERROR_RATE_THRESHOLD = 0.05
    PERFORMANCE_DROP_AUTO_ROLLBACK = 0.10
    PERFORMANCE_DROP_MANUAL_DECISION = 0.05
    
    @staticmethod
    def should_rollback(metrics):
        """Decide if rollback is needed."""
        
        # Check API health
        if metrics['api_error_rate'] > RollbackPolicy.API_ERROR_RATE_THRESHOLD:
            return RollbackDecision(
                should_rollback=True,
                automatic=True,
                reason=f"API error rate too high: {metrics['api_error_rate']:.2%}"
            )
        
        if metrics['api_latency_p95_ms'] > RollbackPolicy.API_LATENCY_P95_THRESHOLD_MS:
            return RollbackDecision(
                should_rollback=True,
                automatic=True,
                reason=f"API latency too high: {metrics['api_latency_p95_ms']}ms"
            )
        
        # Check model health
        if metrics['model_error_rate'] > RollbackPolicy.MODEL_ERROR_RATE_THRESHOLD:
            return RollbackDecision(
                should_rollback=True,
                automatic=True,
                reason=f"Model error rate too high: {metrics['model_error_rate']:.2%}"
            )
        
        # Check performance degradation
        perf_drop = metrics['performance_drop_pct']
        if perf_drop > RollbackPolicy.PERFORMANCE_DROP_AUTO_ROLLBACK:
            return RollbackDecision(
                should_rollback=True,
                automatic=True,
                reason=f"Severe performance drop: {perf_drop:.1%}"
            )
        elif perf_drop > RollbackPolicy.PERFORMANCE_DROP_MANUAL_DECISION:
            return RollbackDecision(
                should_rollback=False,
                automatic=False,
                reason=f"Moderate performance drop: {perf_drop:.1%}",
                requires_manual_decision=True
            )
        
        # All good
        return RollbackDecision(
            should_rollback=False,
            automatic=False,
            reason="All metrics within acceptable range"
        )
```

---

## 3. DECISION ENGINE

### 3.1 Central Decision Engine Agent

**Purpose:** Make intelligent routing decisions for complex scenarios

**Responsibilities:**
- Aggregate signals from multiple agents
- Apply policies
- Make final decisions
- Log reasoning

**Example Decision:**
```python
class DecisionEngine:
    """Central decision-making agent."""
    
    def decide_action(self, context):
        """Make a decision based on context."""
        
        # Gather inputs
        data_quality = DataQualityAgent.get_score()
        drift_status = DataDriftAgent.get_status()
        performance = PerformanceMonitorAgent.get_metrics()
        
        # Apply policies
        data_policy_result = DataPipelinePolicy.evaluate(data_quality)
        ml_policy_result = MLPolicy.evaluate(drift_status, performance)
        
        # Combine results
        if data_policy_result.action == 'BLOCK':
            # Data quality issue takes precedence
            return Decision(
                action='PAUSE_PIPELINE',
                reason='Data quality below threshold',
                confidence=1.0
            )
        
        elif ml_policy_result.urgency == 'CRITICAL':
            # Critical ML issue
            return Decision(
                action='EMERGENCY_RETRAIN',
                reason=ml_policy_result.reason,
                confidence=0.95
            )
        
        elif ml_policy_result.urgency == 'HIGH':
            return Decision(
                action='SCHEDULE_RETRAIN',
                reason=ml_policy_result.reason,
                timeline='24h',
                confidence=0.85
            )
        
        else:
            return Decision(
                action='CONTINUE_MONITORING',
                reason='All systems normal',
                confidence=0.90
            )
```

---

## 4. HOOK IMPLEMENTATION

### 4.1 Hook Registry Pattern

```python
# agents/core/hook_registry.py

class HookRegistry:
    """Registry for managing hooks and subscribers."""
    
    def __init__(self):
        self._hooks = {}
        self._subscribers = defaultdict(list)
    
    def register_hook(self, hook_name):
        """Register a new hook."""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = Hook(hook_name)
    
    def subscribe(self, hook_name, callback):
        """Subscribe to a hook."""
        self._subscribers[hook_name].append(callback)
    
    def emit(self, hook_name, payload):
        """Emit a hook event."""
        logger.info(f"Hook emitted: {hook_name}")
        
        for callback in self._subscribers[hook_name]:
            try:
                callback(payload)
            except Exception as e:
                logger.error(f"Hook callback failed: {e}")

# Global registry
hook_registry = HookRegistry()

# Decorator for subscribing to hooks
def hook(hook_name):
    """Decorator for subscribing to a hook."""
    def decorator(func):
        hook_registry.subscribe(hook_name, func)
        return func
    return decorator
```

### 4.2 Usage Example

```python
# Register hooks
hook_registry.register_hook('on_new_data_ingested')
hook_registry.register_hook('on_model_registered')

# Subscribe to hooks
@hook('on_new_data_ingested')
def trigger_etl(payload):
    logger.info(f"New data ingested: {payload['table_name']}")
    # Trigger ETL
    
@hook('on_model_registered')
def evaluate_model(payload):
    logger.info(f"New model registered: {payload['model_name']} v{payload['version']}")
    # Run evaluation

# Emit hook
DataIngestionAgent.execute()
hook_registry.emit('on_new_data_ingested', {
    'table_name': 'raw.icustays',
    'rows_loaded': 73181
})
```

---

## 5. MONITORING & OBSERVABILITY

### 5.1 Logging All Decisions

**Every decision MUST be logged:**
```python
class DecisionLogger:
    """Log all agent decisions for audit trail."""
    
    @staticmethod
    def log_decision(agent_name, decision, context):
        """Log a decision with full context."""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'decision': decision.action,
            'reason': decision.reason,
            'confidence': decision.confidence,
            'context': context,
            'approval_required': decision.approval_required
        }
        
        # Store in database
        store_decision_log(log_entry)
        
        # Also log to file
        logger.info(f"Decision: {decision.action} | Reason: {decision.reason}")
```

### 5.2 Decision Audit Trail

**Query decision history:**
```sql
-- Decision audit trail
SELECT
    timestamp,
    agent,
    decision,
    reason,
    confidence
FROM decision_logs
WHERE agent = 'model_training_agent'
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
```

---

**Document Version:** 1.0  
**Status:** ✅ APPROVED - Implementation Ready  
**Next Steps:** Implement hooks in agent code
