# Agent Examples - Working Demos

This directory contains **runnable examples** demonstrating how to implement and use agents in the Healthcare ML Platform.

## Available Examples

1. **`example_data_ingestion_agent.py`** - Complete data ingestion agent with error handling
2. **`example_data_pipeline_crew.py`** - Multi-agent crew orchestrating data pipeline
3. **`example_orchestrator.py`** - Top-level workflow orchestrator coordinating multiple crews

---

## Prerequisites

```bash
# Install dependencies
pip install crewai psycopg2-binary pandas tqdm mlflow lightgbm

# Set environment variables
export DATABASE_URL="postgresql://postgres:password@localhost:5432/mimic_iv"
export MLFLOW_TRACKING_URI="http://localhost:5000"
```

---

## Example 1: Data Ingestion Agent

### Description
Demonstrates a complete data ingestion agent that:
- Validates inputs
- Loads CSV data in batches
- Handles errors with retry logic
- Saves checkpoints for resumability
- Logs structured errors

### Run
```bash
python agents/examples/example_data_ingestion_agent.py \
    --source-file /path/to/icustays.csv \
    --target-table raw.icustays
```

### Expected Output
```
[DataIngestionAgent] Starting execution
[DataIngestionAgent] Executing core logic
Ingesting: 100%|██████████| 73181/73181 [01:23<00:00, 875.32 rows/s]
[DataIngestionAgent] Execution completed successfully
✅ Ingestion successful: 73181 rows
```

---

## Example 2: Data Pipeline Crew

### Description
Demonstrates a multi-agent crew that orchestrates:
1. Data ingestion (DataIngestionAgent)
2. dbt transformation (DataTransformationAgent)
3. Data quality validation (DataQualityAgent)

### Run
```bash
python agents/examples/example_data_pipeline_crew.py
```

### Expected Output
```
[DataPipelineCrew] Starting crew execution
[Task 1/3] Data Ingestion
  ✅ Ingested 73181 rows
[Task 2/3] dbt Transformation
  ✅ Ran 15 models successfully
[Task 3/3] Data Quality
  ✅ Quality score: 96.5%
[DataPipelineCrew] All tasks completed successfully
```

---

## Example 3: Workflow Orchestrator

### Description
Demonstrates top-level orchestrator that:
- Coordinates multiple crews (Data Pipeline, ML Development, Deployment)
- Manages dependencies between crews
- Implements decision engine logic
- Handles failures with recovery

### Run
```bash
python agents/examples/example_orchestrator.py
```

### Expected Output
```
[WorkflowOrchestrator] Starting workflow
[Crew 1/3] Data Pipeline Crew
  ✅ Complete
[Crew 2/3] ML Development Crew
  ✅ Model trained (AUROC: 0.89)
[Crew 3/3] Deployment Crew
  ✅ Model deployed to production
[WorkflowOrchestrator] Workflow completed successfully
```

---

## Running All Examples

```bash
# Run sequentially
./run_all_examples.sh

# Or individually
python agents/examples/example_data_ingestion_agent.py
python agents/examples/example_data_pipeline_crew.py
python agents/examples/example_orchestrator.py
```

---

## Testing Examples

```bash
# Run unit tests for example agents
pytest agents/examples/test_examples.py -v

# Run with coverage
pytest agents/examples/test_examples.py --cov=agents --cov-report=html
```

---

## Customization

### Modify Agent Behavior

Edit the agent classes in each example file:

```python
# example_data_ingestion_agent.py

class DataIngestionAgent(BaseAgent):
    def __init__(self, db_connection_string: str):
        super().__init__(...)
        self.batch_size = 5000  # Change batch size
        self.checkpoint_enabled = True  # Enable/disable checkpoints
```

### Add New Agents

Follow the pattern in `AGENT_IMPLEMENTATION_GUIDE.md`:

```python
from agents.core.base_agent import BaseAgent, ValidationResult

class MyCustomAgent(BaseAgent):
    def validate_inputs(self, context):
        # Validation logic
        return ValidationResult.success()

    def _execute(self, context):
        # Core logic
        return result
```

---

## Troubleshooting

### Problem: Database connection refused
**Solution:** Ensure PostgreSQL is running:
```bash
docker-compose up -d postgres
docker-compose ps postgres
```

### Problem: MLflow connection refused
**Solution:** Ensure MLflow server is running:
```bash
docker-compose up -d mlflow
docker-compose ps mlflow
```

### Problem: Agent execution fails
**Solution:** Check logs:
```bash
tail -f logs/agents.log
```

---

## Next Steps

After understanding these examples:
1. Read `AGENT_IMPLEMENTATION_GUIDE.md` for detailed patterns
2. Read `ERROR_HANDLING_POLICY.md` for error handling strategies
3. Implement your own agents following the `BaseAgent` pattern
4. Add tests following `test_examples.py` pattern

---

**Questions?** See [AGENT_ARCHITECTURE.md](../AGENT_ARCHITECTURE.md)
