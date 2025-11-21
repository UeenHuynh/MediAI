# 🤖 MediAI Multi-Agent System - Deployment Guide

**Status:** ✅ Ready for Local Deployment
**Version:** 1.0
**Last Updated:** 2025-01-21

---

## 📋 Overview

MediAI sử dụng **multi-agent architecture** với CrewAI để tự động hóa:
- ✅ Data ingestion (DataIngestionAgent)
- ✅ Data transformations (DataTransformationAgent)
- ✅ Quality validation (DataQualityAgent)
- 🔄 ML training (ModelTrainingAgent) - Coming soon
- 🔄 Deployment (DeploymentAgent) - Coming soon

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│       WorkflowOrchestrator                       │
│       (Main coordination layer)                  │
└───────────────┬──────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────┐
│            DataPipelineCrew                       │
│  ┌───────────────────────────────────────────┐   │
│  │  DataIngestionAgent                       │   │
│  │  - Load CSV → PostgreSQL                  │   │
│  │  - Batch processing                       │   │
│  │  - Checkpointing                          │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌───────────────────────────────────────────┐   │
│  │  DataTransformationAgent                  │   │
│  │  - Run dbt models                         │   │
│  │  - Bronze → Silver → Gold                 │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌───────────────────────────────────────────┐   │
│  │  DataQualityAgent                         │   │
│  │  - Completeness checks                    │   │
│  │  - Uniqueness validation                  │   │
│  └───────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │  PostgreSQL   │
        │  + Redis      │
        └───────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

1. **Docker services running:**
```bash
docker-compose up -d postgres redis
```

2. **Sample data generated:**
```bash
python scripts/generate_sample_data.py
```

3. **Python dependencies installed:**
```bash
pip install -r requirements.txt
```

### Run Agent Demo (Recommended)

```bash
# Run complete demo
python run_agent_demo.py

# This will:
# 1. Check for sample data
# 2. Run DataIngestionAgent to load data
# 3. Run DataQualityAgent to validate
# 4. Show execution results
```

**Expected output:**
```
================================================================================
MediAI Multi-Agent System - Demo
================================================================================

[Step 1] Checking sample data...
✓ Found 3 CSV files:
  - patients.csv (0.1 MB)
  - icustays.csv (0.2 MB)
  - chartevents.csv (14.8 MB)

[Step 2] Running data ingestion workflow...
[2025-01-21 10:30:00] INFO - DataIngestionAgent - Starting execution
[2025-01-21 10:30:05] INFO - Ingestion complete: 1000/1000 rows

[Step 3] Execution Results
================================================================================
✓ Status: SUCCESS
✓ Tables ingested: 3
```

---

## 💻 Agent System Usage

### Option 1: Using Orchestrator CLI

```bash
# Ingest specific file
python agents/orchestrator.py ingest \
  --source-file data/sample/patients.csv \
  --target-table raw.patients

# Run transformations only
python agents/orchestrator.py transform

# Run quality checks only
python agents/orchestrator.py quality --target-table raw.patients

# Run full pipeline
python agents/orchestrator.py full-pipeline
```

### Option 2: Using Python API

```python
from agents.orchestrator import WorkflowOrchestrator

# Initialize orchestrator
orchestrator = WorkflowOrchestrator()

# Run data pipeline
result = orchestrator.run_data_pipeline(
    source_file='data/sample/patients.csv',
    target_table='raw.patients',
    run_transformation=True,
    run_quality_check=True
)

print(result['status'])  # 'success' or 'failed'
```

### Option 3: Using Individual Crews

```python
from agents.crews.data_pipeline_crew import DataPipelineCrew

# Initialize crew
crew = DataPipelineCrew()

# Run ingestion only
result = crew.run_ingestion_only(
    source_file='data/sample/patients.csv',
    target_table='raw.patients'
)

# Run transformation only
result = crew.run_transformation_only(models=['staging.*'])

# Run quality check only
result = crew.run_quality_check_only(table_name='raw.patients')
```

---

## 📂 Project Structure

```
agents/
├── core/
│   ├── base_agent.py          # BaseAgent abstract class
│   └── __init__.py
│
├── roles/
│   ├── data_engineer.py       # Data engineering agents
│   ├── ml_engineer.py         # ML agents (coming soon)
│   └── __init__.py
│
├── crews/
│   ├── data_pipeline_crew.py  # Data pipeline coordination
│   └── __init__.py
│
├── tools/
│   ├── database_tool.py       # PostgreSQL operations
│   ├── file_tool.py           # File operations
│   └── __init__.py
│
├── orchestrator.py            # Main workflow orchestrator
└── __init__.py

run_agent_demo.py              # Demo script
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/mimic_iv
DBT_PROJECT_DIR=./dbt_project
LOG_LEVEL=INFO
```

### Agent Configuration

Each agent can be configured via constructor:

```python
# DataIngestionAgent
agent = DataIngestionAgent(
    db_connection_string='postgresql://...'
)
agent.batch_size = 5000  # Rows per batch

# DataTransformationAgent
agent = DataTransformationAgent(
    dbt_project_dir='./dbt_project'
)

# DataQualityAgent
agent = DataQualityAgent(
    db_connection_string='postgresql://...'
)
```

---

## 📊 Monitoring & Logging

### View Agent Logs

```bash
# Real-time logs
tail -f logs/agent_demo.log

# All agent logs
cat logs/agent_demo.log | grep "DataIngestionAgent"
```

### Agent Execution History

```python
from agents.roles.data_engineer import DataIngestionAgent

agent = DataIngestionAgent(db_connection='...')
result = agent.execute(context)

# Get execution history
history = agent.get_execution_history()
for item in history:
    print(f"Status: {item.status}")
    print(f"Output: {item.output}")
    print(f"Errors: {item.errors}")
```

---

## 🐛 Troubleshooting

### Issue: Agent execution fails

**Check logs:**
```bash
tail -50 logs/agent_demo.log
```

**Common causes:**
- Database not running: `docker-compose up -d postgres`
- Sample data missing: `python scripts/generate_sample_data.py`
- Connection string wrong: Check `.env` file

### Issue: Database connection error

```bash
# Test connection
docker-compose exec postgres psql -U postgres -d mimic_iv

# Check if database exists
docker-compose exec postgres psql -U postgres -l
```

### Issue: dbt transformation fails

```bash
# Test dbt manually
cd dbt_project
dbt debug
dbt run --models staging.*
```

---

## ✅ Testing Agents

### Unit Tests

```bash
# Run agent tests
pytest tests/test_agents.py -v

# Test specific agent
pytest tests/test_agents.py::TestDataIngestionAgent -v

# With coverage
pytest tests/test_agents.py --cov=agents --cov-report=html
```

### Integration Tests

```bash
# Test full pipeline
python run_agent_demo.py

# Should complete without errors
```

---

## 📈 Performance Metrics

### Agent Execution Time

```python
import time

start = time.time()
result = agent.execute(context)
duration = time.time() - start

print(f"Execution time: {duration:.2f}s")
```

### Throughput

```python
# DataIngestionAgent
rows_per_second = result.output['rows_ingested'] / duration
print(f"Throughput: {rows_per_second:.0f} rows/second")
```

---

## 🎯 Next Steps

### 1. Add ML Agents

```python
# agents/roles/ml_engineer.py
class ModelTrainingAgent(BaseAgent):
    """Agent for training ML models."""
    pass

class ModelEvaluationAgent(BaseAgent):
    """Agent for evaluating models."""
    pass
```

### 2. Add Deployment Agents

```python
# agents/roles/devops.py
class APIDeploymentAgent(BaseAgent):
    """Agent for deploying API."""
    pass
```

### 3. Add Airflow Integration

```python
# airflow/dags/agent_orchestrated_dag.py
from agents.orchestrator import WorkflowOrchestrator

def run_agent_workflow():
    orchestrator = WorkflowOrchestrator()
    return orchestrator.ingest_sample_data()

agent_task = PythonOperator(
    task_id='run_agents',
    python_callable=run_agent_workflow
)
```

---

## 📚 Resources

**Documentation:**
- [AGENT_IMPLEMENTATION_GUIDE.md](AGENT_IMPLEMENTATION_GUIDE.md) - Complete implementation patterns
- [AGENT_HOOKS_AND_STEERING.md](AGENT_HOOKS_AND_STEERING.md) - Event-driven triggers
- [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) - System architecture

**Examples:**
- [agents/examples/](agents/examples/) - Example implementations

**Related:**
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [README_DEPLOYMENT.md](README_DEPLOYMENT.md) - Full deployment guide

---

**Status:** ✅ Ready for production
**Maintainer:** MediAI Team
**Last Updated:** 2025-01-21
