# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Healthcare ML Platform** demonstrating end-to-end MLOps for ICU patient risk prediction using MIMIC-IV data from Kaggle. The platform predicts:
- **Sepsis risk** (6-hour early warning, 42 features, LightGBM)
- **ICU mortality risk** (24-hour prediction, 65 features, LightGBM)

**Tech Stack:** Python, FastAPI, PostgreSQL, Redis, Airflow, dbt, MLflow, Streamlit, Docker Compose, CrewAI agents

**Data Source:** Kaggle dataset `akshaybe/updated-mimic-iv` (downloaded via kagglehub)

## Architecture

### Three-Layer Data Architecture (Medallion)
```
Bronze (raw) → Silver (staging) → Gold (analytics)
PostgreSQL schemas: raw, staging, analytics
```

### Service Architecture
```
Streamlit UI (port 8501)
    ↓ HTTP REST
FastAPI Backend (port 8000)
    ↓ SQL/Redis
PostgreSQL (5432) + Redis (6379) + MLflow (5000)
    ↑
Airflow orchestration (webserver: 8080)
    ↑
dbt transformations
```

## Critical Design Principles

### 1. Feature-Schema Alignment
**The database feature tables MUST exactly match the API Pydantic schemas.** Every feature in `analytics.features_sepsis_6h` (42 features) must have a corresponding field in `api/models/schemas.py::SepsisFeatures`.

**Validation:** Run `scripts/validate_schema_alignment.py` after any schema changes.

### 2. No Data Leakage
- Feature extraction time must be BEFORE prediction time
- Sepsis features: extracted at t-6h, predict at t=0
- Mortality features: extracted from first 24h only
- NEVER use future information in feature engineering

### 3. Optimized ML Input Schema
Gold layer uses **denormalized master table** for fast ML queries:
- **Master table:** `analytics.ml_input_master` - One row per ICU stay with ALL 42 features
- **No joins at inference time** - All features pre-computed and indexed
- **Materialized views:** `mv_sofa_scores` for expensive SOFA calculations
- **Helper functions:** `get_patient_features()`, `check_completeness()`

**Critical:** See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for complete schema design optimized for ML input processing.

## Development Commands

### Environment Setup
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps
docker-compose logs -f [service_name]

# Stop services
docker-compose down
```

### Data Download & Ingestion
```bash
# Download MIMIC-IV from Kaggle
python scripts/download_data.py
# This uses kagglehub to download akshaybe/updated-mimic-iv

# Run data ingestion (one-time)
python scripts/ingest_mimic_iv.py --data-path /path/to/kaggle/dataset

# Connect to PostgreSQL
docker exec -it mediai_postgres_1 psql -U postgres -d mimic_iv

# Check schemas
psql -U postgres -d mimic_iv -c "\dn"
psql -U postgres -d mimic_iv -c "\dt analytics.*"
```

### dbt Operations
```bash
cd dbt_project

# Run all models
dbt run

# Run specific layer
dbt run --models staging.*
dbt run --models marts.*

# Run tests
dbt test

# Generate docs
dbt docs generate
dbt docs serve
```

### API Development
```bash
cd api

# Run API locally (development)
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/test_api.py -v

# Check OpenAPI docs
# Navigate to http://localhost:8000/docs
```

### Streamlit UI
```bash
cd apps

# Run Streamlit app
streamlit run streamlit_app.py --server.port 8501
```

### Agent System
```bash
# Run agent workflows
python agents/orchestrator.py

# Run specific crew
python -m agents.crews.data_pipeline_crew
python -m agents.crews.ml_development_crew
```

### Airflow Operations
```bash
# Access Airflow UI: http://localhost:8080
# Default credentials: admin/admin

# Trigger DAG manually
docker exec mediai_airflow_webserver_1 airflow dags trigger ingest_mimic_iv_dag
docker exec mediai_airflow_webserver_1 airflow dags trigger etl_pipeline_dag

# List DAGs
docker exec mediai_airflow_webserver_1 airflow dags list
```

### MLflow Operations
```bash
# Access MLflow UI: http://localhost:5000

# List registered models
mlflow models list

# Load model in Python
import mlflow
model = mlflow.pyfunc.load_model("models:/sepsis_lightgbm_v1/Production")
```

## Code Organization

```
MediAI/
├── api/                      # FastAPI backend
│   ├── main.py              # App entry point
│   ├── routers/             # API endpoints
│   ├── models/schemas.py    # Pydantic schemas (MUST match DB)
│   ├── services/            # Business logic
│   └── core/                # Config, dependencies
├── apps/                     # Streamlit UI
│   ├── streamlit_app.py     # Main entry
│   ├── pages/               # Multi-page app
│   ├── components/          # Reusable UI components
│   └── services/            # API client
├── dbt_project/             # Data transformations
│   ├── models/
│   │   ├── staging/         # Silver layer (cleaning)
│   │   └── marts/           # Gold layer (star schema + features)
│   └── tests/               # Data quality tests
├── airflow/                 # Orchestration
│   └── dags/                # Pipeline definitions
├── agents/                  # CrewAI agent system
│   ├── orchestrator.py      # Workflow orchestrator
│   ├── crews/               # Multi-agent crews
│   └── config/              # Agent configurations
├── scripts/                 # Utility scripts
│   ├── ingest_mimic_iv.py  # Data ingestion
│   └── validate_schema_alignment.py
├── tests/                   # Test suite
├── notebooks/               # Jupyter notebooks
│   ├── 01_eda.ipynb
│   ├── 02_sepsis_model.ipynb
│   └── 03_mortality_model.ipynb
└── docs/                    # Documentation
    ├── ARCHITECTURE_DESIGN.md
    ├── REQUIREMENTS.md
    ├── TASK_BREAKDOWN.md
    └── UI_BACKEND_WIRING.md
```

## Key Files to Know

### Configuration Files
- `docker-compose.yml` - All service definitions
- `.env` - Environment variables (DATABASE_URL, REDIS_URL, MLFLOW_TRACKING_URI)
- `dbt_project/profiles.yml` - Database connections for dbt
- `dbt_project/dbt_project.yml` - dbt project config

### Schema Definitions
- `api/models/schemas.py` - API request/response schemas
- `dbt_project/models/marts/schema.yml` - dbt model schemas
- Database schema DDL in `dbt_project/models/marts/*.sql`

### Feature Engineering
- Sepsis features: `dbt_project/models/marts/features_sepsis_6h.sql`
- Mortality features: `dbt_project/models/marts/features_mortality_24h.sql`
- SOFA score calculation: SQL CTEs in feature models

### Model Training
- Sepsis model: `notebooks/02_sepsis_model.ipynb`
- Mortality model: `notebooks/03_mortality_model.ipynb`
- Model artifacts stored in MLflow registry

## Important Patterns

### 1. API Endpoint Pattern
```python
# api/routers/predictions.py
@router.post("/predict/sepsis", response_model=SepsisPrediction)
async def predict_sepsis(features: SepsisFeatures):
    # 1. Check Redis cache
    # 2. Load model from MLflow (cached in memory)
    # 3. Preprocess features
    # 4. Run inference
    # 5. Calculate SHAP explanation
    # 6. Cache result
    # 7. Store prediction in DB
    # 8. Return response
```

### 2. dbt Model Pattern
```sql
-- dbt_project/models/marts/features_sepsis_6h.sql
WITH demographics AS (
    SELECT stay_id, age, gender, bmi
    FROM {{ ref('dim_patients') }}
),
vitals_latest AS (
    SELECT stay_id, heart_rate, sbp, dbp, temperature, respiratory_rate
    FROM {{ ref('fact_vitals_hourly') }}
    WHERE hour_offset = -6  -- 6 hours before prediction
),
-- ... more CTEs
SELECT
    d.*, v.*, l.*, s.*, t.*,
    sepsis_onset_within_6h AS target
FROM demographics d
LEFT JOIN vitals_latest v USING (stay_id)
-- ... more joins
```

### 3. Agent Execution Pattern
```python
# agents/orchestrator.py
from agents.crews.data_pipeline_crew import DataPipelineCrew

crew = DataPipelineCrew()
result = crew.kickoff()  # Executes all tasks in crew
```

## Data Quality & Testing

### dbt Tests
```yaml
# dbt_project/models/marts/schema.yml
models:
  - name: features_sepsis_6h
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [stay_id]
    columns:
      - name: stay_id
        tests:
          - not_null
          - unique
      - name: age
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 18
              max_value: 120
```

### API Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html

# Run specific test file
pytest tests/test_api.py::test_predict_sepsis -v
```

## Performance Targets

- **API p95 latency:** <200ms
- **Model inference:** <100ms (sepsis), <80ms (mortality)
- **Database queries:** <5 seconds for feature extraction
- **Cache hit rate:** >80% (target)
- **Test coverage:** >70%

## Common Issues & Solutions

### Issue: dbt models fail with "relation does not exist"
**Solution:** Run models in order: `dbt run --models staging.*` then `dbt run --models marts.*`

### Issue: API returns 500 on prediction
**Solution:**
1. Check MLflow model is registered: `mlflow models list`
2. Check database connection: `docker-compose logs postgres`
3. Check feature table exists: `psql -c "\dt analytics.features_*"`

### Issue: Docker services won't start
**Solution:**
1. Check ports not in use: `lsof -i :5432,6379,8000,8080,5000,8501`
2. Restart Docker: `docker-compose down && docker-compose up -d`
3. Check logs: `docker-compose logs -f`

### Issue: Schema mismatch between API and database
**Solution:** Run validation script: `python scripts/validate_schema_alignment.py`

## Agent System Notes

The platform uses CrewAI agents for automation:
- **Data Pipeline Crew:** Ingestion, transformation, quality checks
- **ML Development Crew:** Feature engineering, model training, evaluation
- **Deployment Crew:** API deployment, model serving
- **Monitoring Crew:** Performance monitoring, drift detection

Agents are coordinated by a Workflow Orchestrator that manages dependencies and failure recovery.

## Data Sources

**PRIMARY SOURCE:** Kaggle dataset `akshaybe/updated-mimic-iv`

Key advantages:
- ✅ **No approval required** (public dataset)
- ✅ **Instant access** (download immediately)
- ✅ **Pre-cleaned** (outliers removed, types validated)
- ✅ **Smaller size** (5GB vs 15GB)
- ✅ **Same schema** (compatible with MIMIC-IV item IDs)

Download method:
```python
import kagglehub
path = kagglehub.dataset_download("akshaybe/updated-mimic-iv")
```

Or use provided script: `python scripts/download_data.py`

**COMPLETE DOCUMENTATION:** See [DATA_SOURCE.md](DATA_SOURCE.md)

**Feature extraction** based on:
- BorgwardtLab/mgp-tcn preprocessing (sepsis)
- healthylaife/MIMIC-IV-Data-Pipeline (mortality)

## Model Details

### Sepsis Model (sepsis_lightgbm_v1)
- **Algorithm:** LightGBM binary classifier
- **Features:** 42 (demographics, vitals, labs, SOFA, trends, time)
- **Target:** Sepsis onset within 6 hours (SEPSIS-3 criteria)
- **Performance target:** AUROC >0.85, Sensitivity >0.80, Specificity >0.80
- **Class imbalance:** SMOTE oversampling (6% positive class)

### Mortality Model (mortality_lightgbm_v1)
- **Algorithm:** LightGBM binary classifier
- **Features:** 65 (SOFA, APACHE-II, worst vitals/labs in 24h, ICU details)
- **Target:** Hospital mortality
- **Performance target:** AUROC >0.80, Sensitivity >0.75
- **Training data:** ~70K ICU stays (10% mortality rate)

## Security & Compliance

- **Data:** De-identified MIMIC-IV data only (HIPAA-aware design)
- **Authentication:** Placeholder in MVP (username/password)
- **Input validation:** Pydantic schemas enforce strict validation
- **API security:** Rate limiting, input sanitization
- **No PHI logging:** All logs sanitized

## Environment Variables

Required in `.env`:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/mimic_iv
REDIS_URL=redis://localhost:6379
MLFLOW_TRACKING_URI=http://localhost:5000
API_URL=http://localhost:8000
```

## Deployment Notes

- **Current:** Local deployment via Docker Compose
- **Infrastructure:** Max 12 containers, 16GB RAM minimum, 50GB disk
- **Monitoring:** Placeholder (Prometheus/Grafana not implemented in MVP)
- **Cloud deployment:** Out of scope for MVP

## Documentation References

- **Database schema (IMPORTANT):** See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
- **Full architecture:** See [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)
- **Requirements:** See [REQUIREMENTS.md](REQUIREMENTS.md)
- **Task breakdown:** See [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)
- **API wiring:** See [UI_BACKEND_WIRING.md](UI_BACKEND_WIRING.md)

## Important: What's NOT Implemented Yet

This is an **active development project**. Many components are designed but not implemented:
- Prometheus/Grafana monitoring (placeholder)
- Metabase BI dashboards (SQL written, not deployed)
- Auto-retraining pipeline (manual only)
- Real-time streaming (batch only)
- Cloud deployment (local only)

Check [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) for current implementation status (43 tasks tracked).
