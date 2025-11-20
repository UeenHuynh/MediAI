# Healthcare ML Platform - Complete Task Breakdown & Implementation Plan

**Version:** 1.0  
**Status:** Active Development  
**Last Updated:** 2025-01-20

---

## DOCUMENT PURPOSE

This document provides a **comprehensive, prioritized task list** with:
- ✅ Task descriptions and acceptance criteria
- 🔗 Dependencies between tasks
- 👤 Owner/Agent assignments
- 📊 Status tracking (Not Started / In Progress / Complete)
- ⏱️ Time estimates
- 🎯 Priority levels (P0-P3)

**Related Documents:**
- Requirements: `REQUIREMENTS.md`
- Architecture: `ARCHITECTURE_DESIGN.md`
- Agent Design: `agents/AGENT_ARCHITECTURE.md`

---

## TASK ORGANIZATION

Tasks are organized by **Project Phases** following the ML lifecycle:

```
Phase 1: Setup & Infrastructure (Week 1)
    ↓
Phase 2: Data Pipeline (Week 1-2)
    ↓
Phase 3: Feature Engineering (Week 2)
    ↓
Phase 4: ML Models (Week 2-3)
    ↓
Phase 5: API & Serving (Week 3)
    ↓
Phase 6: Orchestration (Week 3-4)
    ↓
Phase 7: UI Development (Week 4)
    ↓
Phase 8: Agent Integration (Week 4-5)
    ↓
Phase 9: Testing & Documentation (Week 5-6)
    ↓
Phase 10: Finalization (Week 6)
```

---

## LEGEND

**Status:**
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- ⏸️ Blocked (waiting on dependency)
- ⚠️ At Risk

**Priority:**
- P0: Critical (MVP blocker)
- P1: High (Important for MVP)
- P2: Medium (Nice to have)
- P3: Low (Future enhancement)

**Owner Types:**
- 👤 Human Developer
- 🤖 Agent (automated)
- 🤝 Hybrid (human + agent)

---

## PHASE 1: SETUP & INFRASTRUCTURE

### Task 1.1: Project Repository Setup
**ID:** SETUP-001  
**Priority:** P0  
**Status:** 🟢 Complete  
**Owner:** 👤 Developer  
**Time Estimate:** 2 hours  
**Dependencies:** None

**Description:**
Initialize GitHub repository with proper structure, branch protection, and CI/CD skeleton.

**Subtasks:**
- [x] Create GitHub repository (public)
- [x] Initialize with MIT license
- [x] Create `.gitignore` for Python/Docker/Data
- [x] Setup branch protection (main branch)
- [x] Create initial README.md
- [x] Add CONTRIBUTING.md
- [x] Create project directory structure

**Acceptance Criteria:**
- Repository accessible at github.com/username/healthcare-ml-platform
- Branch protection prevents direct pushes to main
- README has project description

**Implementation Notes:**
```bash
# Directory structure created
healthcare-ml-platform/
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── api/
├── apps/
├── dbt_project/
├── airflow/
├── agents/
├── scripts/
├── tests/
└── docs/
```

---

### Task 1.2: Development Environment Setup
**ID:** SETUP-002  
**Priority:** P0  
**Status:** 🟢 Complete  
**Owner:** 👤 Developer  
**Time Estimate:** 3 hours  
**Dependencies:** SETUP-001

**Description:**
Setup local development environment with Docker, Python, and all required tools.

**Subtasks:**
- [x] Install Docker Desktop (20.10+)
- [x] Install Docker Compose (2.24+)
- [x] Install Python 3.11+
- [x] Create virtual environment
- [x] Create `pyproject.toml` with dependencies
- [x] Create `.env.example`
- [x] Setup pre-commit hooks (black, flake8, mypy)

**Acceptance Criteria:**
- `docker --version` shows 20.10+
- `python --version` shows 3.11+
- Virtual environment activated
- Pre-commit hooks run successfully

**Key Files:**
- `pyproject.toml` (Python dependencies)
- `.env.example` (environment variables template)
- `.pre-commit-config.yaml` (linting hooks)

---

### Task 1.3: Docker Compose Configuration
**ID:** SETUP-003  
**Priority:** P0  
**Status:** 🟡 In Progress  
**Owner:** 🤝 Hybrid (Developer + Infrastructure Agent)  
**Time Estimate:** 4 hours  
**Dependencies:** SETUP-002

**Description:**
Create complete Docker Compose configuration for all services (PostgreSQL, Redis, Airflow, MLflow, API, Streamlit).

**Subtasks:**
- [x] Configure PostgreSQL service (port 5432, 4GB RAM)
- [x] Configure Redis service (port 6379, 512MB RAM)
- [x] Configure Airflow services (webserver, scheduler, worker)
- [ ] Configure MLflow service (port 5000)
- [ ] Configure API service (port 8000)
- [ ] Configure Streamlit service (port 8501)
- [x] Create health checks for all services
- [ ] Setup persistent volumes
- [ ] Test service startup

**Acceptance Criteria:**
- All services start successfully with `docker-compose up -d`
- Health checks pass within 2 minutes
- Services can communicate (network connectivity verified)
- Persistent volumes work (data survives container restart)

**Current Blockers:**
- MLflow backend store configuration needs PostgreSQL to be fully initialized first

**Agent Assignment:**
- Infrastructure Agent handles service configuration
- Developer reviews and validates

---

### Task 1.4: CI/CD Pipeline Setup
**ID:** SETUP-004  
**Priority:** P1  
**Status:** 🔴 Not Started  
**Owner:** 🤖 DevOps Agent  
**Time Estimate:** 3 hours  
**Dependencies:** SETUP-001

**Description:**
Setup GitHub Actions for automated linting, testing, and Docker image building.

**Subtasks:**
- [ ] Create `.github/workflows/ci.yml`
- [ ] Configure linting (flake8, black, mypy)
- [ ] Configure unit tests (pytest)
- [ ] Configure coverage reporting (codecov)
- [ ] Add status badges to README

**Acceptance Criteria:**
- CI runs on every PR
- All checks must pass before merge
- Coverage badge shows ≥70%
- Build time <5 minutes

**Agent Execution:**
```yaml
# Agent task definition
task_id: setup_ci_cd
agent: devops_engineer_agent
tools:
  - github_actions_tool
  - yaml_generator_tool
inputs:
  repo_url: github.com/username/healthcare-ml-platform
  required_checks:
    - linting
    - unit_tests
    - integration_tests
```

---

## PHASE 2: DATA PIPELINE

### Task 2.1: MIMIC-IV Download from Kaggle
**ID:** DATA-001
**Priority:** P0
**Status:** 🔴 Not Started
**Owner:** 👤 Developer
**Time Estimate:** 30 minutes (download time depends on internet speed)
**Dependencies:** None

**Description:**
Download MIMIC-IV dataset from Kaggle using kagglehub (no approval needed).

**Subtasks:**
- [ ] Install kagglehub: `pip install kagglehub`
- [ ] Setup Kaggle credentials (API token from kaggle.com/settings)
- [ ] Download dataset: `python scripts/download_data.py`
- [ ] Verify downloaded files (icustays.csv, chartevents.csv, etc.)
- [ ] Dataset ready at kagglehub cache location

**Acceptance Criteria:**
- Dataset downloaded successfully (~5GB)
- All 6 core CSV files present (icustays, patients, admissions, chartevents, labevents, diagnoses_icd)
- Files verified by download script
- Path saved to `config/data_path.txt`

**Advantages over PhysioNet:**
✅ No approval required (instant access)
✅ Smaller download (5GB vs 15GB)
✅ Pre-cleaned data
✅ Same MIMIC-IV schema and item IDs

**See:** [DATA_SOURCE.md](../DATA_SOURCE.md) for complete documentation.

---

### Task 2.2: Generate Sample Data
**ID:** DATA-002  
**Priority:** P1  
**Status:** 🟢 Complete  
**Owner:** 🤖 Data Ingestion Agent  
**Time Estimate:** 4 hours  
**Dependencies:** SETUP-003

**Description:**
Generate synthetic ICU data for development/testing without waiting for MIMIC-IV access.

**Subtasks:**
- [x] Create synthetic data generator script
- [x] Generate 1000 patient records
- [x] Match MIMIC-IV schema
- [x] Include realistic distributions (age, vitals, labs)
- [x] Save as CSV files
- [x] Create data loading script

**Acceptance Criteria:**
- Sample data matches MIMIC-IV schema exactly
- 1000 patients with complete vitals/labs
- Can be loaded into PostgreSQL
- Useful for development/testing

**Generated Files:**
- `data/sample/icustays.csv` (1000 rows)
- `data/sample/chartevents.csv` (~200K rows)
- `data/sample/labevents.csv` (~100K rows)

**Agent Output:**
```json
{
  "status": "complete",
  "files_generated": 6,
  "total_rows": 301000,
  "schema_validation": "passed"
}
```

---

### Task 2.3: Database Schema Creation
**ID:** DATA-003  
**Priority:** P0  
**Status:** 🟡 In Progress  
**Owner:** 🤖 Data Transformation Agent  
**Time Estimate:** 6 hours  
**Dependencies:** SETUP-003

**Description:**
Create PostgreSQL schemas (raw, staging, analytics) with proper tables, indexes, and constraints.

**Subtasks:**
- [x] Create `raw` schema
- [x] Create `staging` schema
- [x] Create `analytics` schema
- [ ] Define all raw tables (icustays, chartevents, etc.)
- [ ] Add indexes on frequently queried columns
- [ ] Create foreign key constraints
- [ ] Write Alembic migration scripts

**Acceptance Criteria:**
- All schemas created successfully
- Tables match MIMIC-IV specification
- Indexes improve query performance (tested with EXPLAIN ANALYZE)
- Migration scripts work forward and backward

**SQL Generated:**
```sql
-- raw schema (bronze layer)
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.icustays (
    subject_id INTEGER,
    hadm_id INTEGER,
    stay_id INTEGER PRIMARY KEY,
    intime TIMESTAMP,
    outtime TIMESTAMP,
    los NUMERIC
);

CREATE INDEX idx_icustays_subject ON raw.icustays(subject_id);
CREATE INDEX idx_icustays_hadm ON raw.icustays(hadm_id);

-- (similar for other tables)
```

**Agent Assignment:**
- Data Transformation Agent generates DDL
- Data Quality Agent validates schema

---

### Task 2.4: Data Ingestion Implementation
**ID:** DATA-004  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Data Ingestion Agent  
**Time Estimate:** 8 hours  
**Dependencies:** DATA-003, (DATA-001 OR DATA-002)

**Description:**
Implement batch ingestion pipeline to load CSV files into PostgreSQL.

**Subtasks:**
- [ ] Write CSV to PostgreSQL loader (`scripts/ingest_mimic_iv.py`)
- [ ] Implement batch inserts (10K rows at a time)
- [ ] Add progress tracking (tqdm)
- [ ] Handle data type conversions
- [ ] Implement error handling and logging
- [ ] Add data validation (Great Expectations)
- [ ] Create resumable ingestion (checkpoint support)

**Acceptance Criteria:**
- Loads all MIMIC-IV ICU tables successfully
- Handles 15GB of data without memory issues
- Shows progress bar
- Logs errors to `logs/ingestion.log`
- Can resume from checkpoint if interrupted
- Validates data quality (>95% pass rate)

**Performance Targets:**
- Load speed: >10K rows/second
- Memory usage: <2GB
- Total time: <4 hours for full dataset

**Agent Execution:**
```python
# Agent orchestrates ingestion
from agents.roles.data_engineer import DataIngestionAgent

agent = DataIngestionAgent()
result = agent.execute(context={
    'source_directory': '/data/mimic-iv/icu',
    'target_schema': 'raw',
    'batch_size': 10000
})

# Expected output
{
    'status': 'success',
    'tables_loaded': 6,
    'total_rows': 73181,
    'execution_time': '3h 45m'
}
```

---

### Task 2.5: dbt Project Setup
**ID:** DATA-005  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Data Transformation Agent  
**Time Estimate:** 4 hours  
**Dependencies:** DATA-004

**Description:**
Initialize dbt project with PostgreSQL connection and project structure.

**Subtasks:**
- [ ] Initialize dbt project (`dbt init dbt_project`)
- [ ] Configure `profiles.yml` with PostgreSQL connection
- [ ] Setup `dbt_project.yml` (project config)
- [ ] Create directory structure (staging/marts)
- [ ] Configure materialization strategies
- [ ] Setup dbt documentation

**Acceptance Criteria:**
- `dbt debug` passes (connection successful)
- `dbt run` executes without errors (even if no models yet)
- `dbt docs generate` creates documentation site
- Project structure follows best practices

**Directory Structure:**
```
dbt_project/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── schema.yml
│   │   ├── stg_icustays.sql
│   │   ├── stg_chartevents.sql
│   │   └── ...
│   └── marts/
│       ├── schema.yml
│       ├── dim_patients.sql
│       ├── fact_icu_stays.sql
│       └── features_sepsis_6h.sql
├── macros/
├── tests/
└── README.md
```

---

### Task 2.6: dbt Staging Models (Silver Layer)
**ID:** DATA-006  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Data Transformation Agent  
**Time Estimate:** 12 hours  
**Dependencies:** DATA-005

**Description:**
Create dbt staging models to clean and standardize raw data.

**Subtasks:**
- [ ] Create `stg_icustays.sql` (type casting, deduplication)
- [ ] Create `stg_chartevents.sql` (vitals cleaning, outlier removal)
- [ ] Create `stg_labevents.sql` (lab result validation)
- [ ] Create `stg_inputevents.sql` (medication data)
- [ ] Create `stg_patients.sql` (demographics)
- [ ] Add data quality tests (`schema.yml`)
- [ ] Document transformations
- [ ] Optimize query performance

**Acceptance Criteria:**
- All staging models compile and run successfully
- Data quality tests pass (>95% pass rate)
- Queries execute in <5 minutes each
- Null handling documented
- Outlier removal logged

**Example Model:**
```sql
-- dbt_project/models/staging/stg_chartevents.sql

WITH raw_vitals AS (
    SELECT * FROM {{ source('raw', 'chartevents') }}
),

cleaned AS (
    SELECT
        subject_id,
        stay_id,
        charttime,
        itemid,
        CAST(valuenum AS NUMERIC) AS value,
        valueuom AS unit
    FROM raw_vitals
    WHERE valuenum IS NOT NULL
      AND valuenum BETWEEN 0 AND 300  -- Heart rate range
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY stay_id, charttime, itemid 
            ORDER BY charttime DESC
        ) AS rn
    FROM cleaned
)

SELECT * 
FROM deduplicated 
WHERE rn = 1
```

**Agent Assignment:**
- Data Transformation Agent writes SQL models
- Data Quality Agent writes tests

---

### Task 2.7: dbt Mart Models (Gold Layer - Star Schema)
**ID:** DATA-007  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Data Transformation Agent  
**Time Estimate:** 16 hours  
**Dependencies:** DATA-006

**Description:**
Create star schema with dimension and fact tables for analytics.

**Subtasks:**
- [ ] Create `dim_patients.sql`
- [ ] Create `dim_time.sql`
- [ ] Create `dim_diagnoses.sql`
- [ ] Create `fact_icu_stays.sql` (grain: 1 per admission)
- [ ] Create `fact_vitals_hourly.sql` (aggregated vitals)
- [ ] Create `fact_labs_daily.sql` (aggregated labs)
- [ ] Add referential integrity tests
- [ ] Document star schema (ERD)

**Acceptance Criteria:**
- All dimension tables created
- Fact tables have correct grain (no duplicates at grain level)
- Foreign keys validated
- Star schema diagram in dbt docs
- Queries optimized with indexes

**Star Schema Design:**
```
fact_icu_stays (73K rows)
├── → dim_patients (patient_key)
├── → dim_time (admission_date_key)
└── → dim_diagnoses (primary_diagnosis_key)

fact_vitals_hourly (5M+ rows)
├── → fact_icu_stays (stay_key)
└── → dim_time (hour_key)

fact_labs_daily (1M+ rows)
├── → fact_icu_stays (stay_key)
└── → dim_time (date_key)
```

---

### Task 2.8: Data Quality Validation
**ID:** DATA-008  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Data Quality Agent  
**Time Estimate:** 8 hours  
**Dependencies:** DATA-007

**Description:**
Implement comprehensive data quality checks using Great Expectations.

**Subtasks:**
- [ ] Install Great Expectations
- [ ] Create expectation suite for raw data
- [ ] Create expectation suite for staging data
- [ ] Create expectation suite for marts
- [ ] Automate quality checks in Airflow
- [ ] Generate data quality dashboard

**Acceptance Criteria:**
- Quality checks run automatically after each dbt run
- Quality score >95% on all layers
- Alerts triggered on quality drop
- Dashboard shows quality trends

**Expectations Defined:**
```python
# great_expectations/expectations/raw_icustays.json
{
    "expectations": [
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "stay_id"}
        },
        {
            "expectation_type": "expect_column_values_to_be_unique",
            "kwargs": {"column": "stay_id"}
        },
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "los",
                "min_value": 0,
                "max_value": 365
            }
        }
    ]
}
```

---

## PHASE 3: FEATURE ENGINEERING

### Task 3.1: Sepsis Feature Engineering
**ID:** FEAT-001  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Feature Engineering Agent  
**Time Estimate:** 10 hours  
**Dependencies:** DATA-007

**Description:**
Create 42 features for sepsis prediction based on BorgwardtLab/mgp-tcn methodology.

**Subtasks:**
- [ ] Adapt mgp-tcn preprocessing code
- [ ] Extract demographics (3 features)
- [ ] Extract vitals (5 features)
- [ ] Extract labs (20 features)
- [ ] Calculate SOFA scores (6 features)
- [ ] Calculate temporal trends (6 features)
- [ ] Extract time features (2 features)
- [ ] Create feature table: `analytics.features_sepsis_6h`
- [ ] Validate no data leakage

**Acceptance Criteria:**
- Feature table contains 42 columns + metadata
- ~20K rows (training cohort)
- No future information used (temporal split validated)
- Feature distributions stable across train/val/test
- SOFA scores match clinical definitions

**dbt Model:**
```sql
-- dbt_project/models/marts/features_sepsis_6h.sql

WITH demographics AS (
    SELECT
        stay_id,
        age,
        gender,
        bmi
    FROM {{ ref('dim_patients') }}
),

vitals_latest AS (
    SELECT
        stay_id,
        heart_rate,
        sbp,
        dbp,
        temperature,
        respiratory_rate
    FROM {{ ref('fact_vitals_hourly') }}
    WHERE hour_offset = -6  -- 6 hours before prediction time
),

labs_latest AS (
    SELECT
        stay_id,
        wbc,
        lactate,
        creatinine,
        -- ... (20 lab values)
    FROM {{ ref('fact_labs_daily') }}
),

sofa_scores AS (
    SELECT
        stay_id,
        respiratory_sofa,
        cardiovascular_sofa,
        hepatic_sofa,
        coagulation_sofa,
        renal_sofa,
        neurological_sofa
    FROM {{ ref('fact_icu_stays') }}
),

temporal_trends AS (
    SELECT
        stay_id,
        lactate_trend_12h,
        hr_trend_6h,
        -- ... (trend features)
    FROM {{ ref('fact_vitals_hourly') }}
)

SELECT
    d.*,
    v.*,
    l.*,
    s.*,
    t.*,
    -- Target variable
    sepsis_onset_within_6h AS target
FROM demographics d
LEFT JOIN vitals_latest v USING (stay_id)
LEFT JOIN labs_latest l USING (stay_id)
LEFT JOIN sofa_scores s USING (stay_id)
LEFT JOIN temporal_trends t USING (stay_id)
WHERE stay_id IN (SELECT stay_id FROM {{ ref('sepsis_cohort') }})
```

**Agent Tool Usage:**
- `mgptcn_adapter_tool` - Extract features using mgp-tcn logic
- `sofa_calculator_tool` - Calculate SOFA scores
- `temporal_aggregator_tool` - Compute trends

---

### Task 3.2: Mortality Feature Engineering
**ID:** FEAT-002  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Feature Engineering Agent  
**Time Estimate:** 12 hours  
**Dependencies:** DATA-007

**Description:**
Create 65 features for mortality prediction based on healthylaife/MIMIC-IV-Data-Pipeline.

**Subtasks:**
- [ ] Adapt healthylaife preprocessing code
- [ ] Extract SOFA scores (6 features)
- [ ] Extract APACHE-II components (12 features)
- [ ] Extract worst vitals in 24h (8 features)
- [ ] Extract worst labs in 24h (25 features)
- [ ] Extract ICU details (10 features)
- [ ] Extract diagnosis flags (4 features)
- [ ] Create feature table: `analytics.features_mortality_24h`

**Acceptance Criteria:**
- Feature table contains 65 columns
- ~70K rows (full cohort)
- APACHE-II validated against reference implementation
- No temporal leakage

---

### Task 3.3: Feature Validation & Testing
**ID:** FEAT-003  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Feature Validation Agent  
**Time Estimate:** 6 hours  
**Dependencies:** FEAT-001, FEAT-002

**Description:**
Validate all engineered features for quality and absence of data leakage.

**Subtasks:**
- [ ] Check for data leakage (temporal validation)
- [ ] Check for future information
- [ ] Validate feature distributions (train vs test)
- [ ] Check for high cardinality features
- [ ] Check for zero-variance features
- [ ] Generate feature documentation

**Acceptance Criteria:**
- No data leakage detected
- Distribution stability confirmed (KS test p-value >0.05)
- No zero-variance features
- Feature documentation generated

**Validation Tests:**
```python
# tests/test_features.py

def test_no_data_leakage_sepsis():
    """Ensure sepsis features don't contain future information."""
    features = pd.read_sql("SELECT * FROM analytics.features_sepsis_6h", conn)
    
    # Check that feature_extraction_time is before prediction_time
    assert (features['feature_extraction_time'] <= features['prediction_time']).all()

def test_distribution_stability():
    """Ensure train/test distributions are similar."""
    from scipy.stats import ks_2samp
    
    train = features[features['split'] == 'train']['lactate']
    test = features[features['split'] == 'test']['lactate']
    
    statistic, pvalue = ks_2samp(train, test)
    assert pvalue > 0.05, "Distribution drift detected"
```

---

## PHASE 4: ML MODELS

### Task 4.1: MLflow Setup
**ID:** ML-001  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Model Training Agent  
**Time Estimate:** 3 hours  
**Dependencies:** SETUP-003

**Description:**
Configure MLflow tracking server and model registry.

**Subtasks:**
- [ ] Configure MLflow with PostgreSQL backend
- [ ] Setup artifact storage (local filesystem for MVP)
- [ ] Create experiments (sepsis, mortality)
- [ ] Test model logging and loading
- [ ] Configure model registry

**Acceptance Criteria:**
- MLflow UI accessible at http://localhost:5000
- Experiments created successfully
- Can log and retrieve models
- Model versioning works

---

### Task 4.2: Sepsis Model Training
**ID:** ML-002  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Model Training Agent  
**Time Estimate:** 12 hours  
**Dependencies:** FEAT-001, ML-001

**Description:**
Train LightGBM model for sepsis prediction.

**Subtasks:**
- [ ] Create training notebook (`notebooks/02_sepsis_model.ipynb`)
- [ ] Load feature data from `features_sepsis_6h`
- [ ] Train/val/test split (70/15/15)
- [ ] Handle class imbalance (SMOTE)
- [ ] Train LightGBM baseline
- [ ] Hyperparameter tuning (Optuna, 100 trials)
- [ ] 5-fold cross-validation
- [ ] Evaluate on test set
- [ ] Calculate SHAP values
- [ ] Log to MLflow
- [ ] Register model

**Acceptance Criteria:**
- AUROC >0.85 on test set
- Sensitivity >0.80
- Specificity >0.80
- Model logged to MLflow with metrics
- SHAP explainer saved
- Model card completed

**Training Script:**
```python
# notebooks/02_sepsis_model.ipynb

import lightgbm as lgb
from imblearn.over_sampling import SMOTE
import mlflow

# Load data
features = pd.read_sql("SELECT * FROM analytics.features_sepsis_6h", conn)
X = features.drop(['stay_id', 'target'], axis=1)
y = features['target']

# Split
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp)

# Handle imbalance
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Train
params = {
    'objective': 'binary',
    'metric': 'auc',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'n_estimators': 500
}

with mlflow.start_run():
    model = lgb.LGBMClassifier(**params)
    model.fit(X_train_resampled, y_train_resampled)
    
    # Evaluate
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auroc = roc_auc_score(y_test, y_pred_proba)
    
    # Log
    mlflow.log_params(params)
    mlflow.log_metric("auroc", auroc)
    mlflow.lightgbm.log_model(model, "model")
    
    # Register
    mlflow.register_model("runs:/{}/model".format(mlflow.active_run().info.run_id),
                         "sepsis_lightgbm_v1")
```

---

### Task 4.3: Mortality Model Training
**ID:** ML-003  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Model Training Agent  
**Time Estimate:** 12 hours  
**Dependencies:** FEAT-002, ML-001

**Description:**
Train LightGBM model for mortality prediction.

(Similar structure to Task 4.2, adapted for mortality features)

---

### Task 4.4: Model Evaluation & Comparison
**ID:** ML-004  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Model Evaluation Agent  
**Time Estimate:** 6 hours  
**Dependencies:** ML-002, ML-003

**Description:**
Comprehensive evaluation of both models with visualizations.

**Subtasks:**
- [ ] Calculate all metrics (AUROC, precision, recall, F1)
- [ ] Generate confusion matrices
- [ ] Generate ROC curves
- [ ] Generate calibration plots
- [ ] Calculate SHAP feature importance
- [ ] Compare model versions
- [ ] Generate evaluation report

**Acceptance Criteria:**
- Evaluation notebook completed
- All visualizations saved to `reports/`
- Model comparison table generated
- Evaluation report auto-generated

---

## PHASE 5: API & SERVING

### Task 5.1: FastAPI Application Structure
**ID:** API-001  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 🤖 API Development Agent  
**Time Estimate:** 4 hours  
**Dependencies:** SETUP-003

**Description:**
Create FastAPI application skeleton with proper structure.

**Subtasks:**
- [ ] Create `api/main.py` (app initialization)
- [ ] Setup routers (predictions, explanations, health)
- [ ] Create Pydantic schemas
- [ ] Configure CORS
- [ ] Setup logging middleware
- [ ] Create error handlers

**Acceptance Criteria:**
- FastAPI app starts successfully
- OpenAPI docs accessible at `/docs`
- All routes registered
- CORS configured

**Directory Created:**
```
api/
├── main.py
├── routers/
│   ├── predictions.py
│   ├── explanations.py
│   └── health.py
├── models/
│   └── schemas.py
├── services/
│   ├── prediction_service.py
│   └── cache_service.py
└── core/
    ├── config.py
    └── dependencies.py
```

---

### Task 5.2: Prediction Endpoints Implementation
**ID:** API-002  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 API Development Agent  
**Time Estimate:** 8 hours  
**Dependencies:** API-001, ML-002, ML-003

**Description:**
Implement `/predict/sepsis` and `/predict/mortality` endpoints.

**Subtasks:**
- [ ] Implement `/health` endpoint
- [ ] Implement `/predict/sepsis` with request validation
- [ ] Implement `/predict/mortality` with request validation
- [ ] Add model loading from MLflow
- [ ] Add input preprocessing
- [ ] Add response formatting
- [ ] Add error handling

**Acceptance Criteria:**
- All endpoints return 200 for valid requests
- Input validation works (400 for invalid input)
- Latency p95 <200ms
- Error messages are clear

**Implementation:**
```python
# api/routers/predictions.py

from fastapi import APIRouter, HTTPException
from api.models.schemas import SepsisFeatures, SepsisPrediction
from api.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["predictions"])
prediction_service = PredictionService()

@router.post("/sepsis", response_model=SepsisPrediction)
async def predict_sepsis(features: SepsisFeatures):
    """
    Predict sepsis risk for ICU patient.
    
    Returns probability, risk level, and SHAP explanation.
    """
    try:
        prediction = await prediction_service.predict_sepsis(features)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Task 5.3: Redis Caching Integration
**ID:** API-003  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 API Development Agent  
**Time Estimate:** 4 hours  
**Dependencies:** API-002

**Description:**
Implement Redis caching for predictions to reduce latency.

**Subtasks:**
- [ ] Setup Redis connection
- [ ] Implement cache key generation (MD5 hash)
- [ ] Implement cache get/set logic
- [ ] Add cache hit/miss metrics
- [ ] Configure TTL (1 hour)
- [ ] Add cache invalidation on model update

**Acceptance Criteria:**
- Redis integrated with FastAPI
- Cache hit rate >50% (will improve with usage)
- Cache invalidation works
- Metrics logged

---

### Task 5.4: SHAP Explanation Endpoint
**ID:** API-004  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 API Development Agent  
**Time Estimate:** 6 hours  
**Dependencies:** API-002

**Description:**
Implement `/explain/shap` endpoint to return SHAP explanations.

**Subtasks:**
- [ ] Load SHAP explainer from MLflow
- [ ] Implement SHAP value calculation
- [ ] Generate SHAP waterfall plot (matplotlib)
- [ ] Convert plot to base64 image
- [ ] Return JSON with top features + plot
- [ ] Cache SHAP calculations

**Acceptance Criteria:**
- Endpoint returns SHAP values + plot
- Top 10 features with impact
- Computation time <500ms
- SHAP values cached

---

## PHASE 6: ORCHESTRATION

### Task 6.1: Airflow DAGs - Data Ingestion
**ID:** ORCH-001  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Workflow Orchestrator Agent  
**Time Estimate:** 4 hours  
**Dependencies:** DATA-004

**Description:**
Create Airflow DAG for one-time data ingestion.

**Subtasks:**
- [ ] Create `airflow/dags/ingest_mimic_iv_dag.py`
- [ ] Define tasks for each table ingestion
- [ ] Add data validation tasks
- [ ] Configure alerts on failure
- [ ] Test DAG execution

**Acceptance Criteria:**
- DAG visible in Airflow UI
- Can be triggered manually
- Completes successfully
- Logs are comprehensive

---

### Task 6.2: Airflow DAGs - ETL Pipeline
**ID:** ORCH-002  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Workflow Orchestrator Agent  
**Time Estimate:** 6 hours  
**Dependencies:** DATA-007

**Description:**
Create Airflow DAG for daily ETL (dbt run).

**Subtasks:**
- [ ] Create `airflow/dags/etl_pipeline_dag.py`
- [ ] Add dbt run tasks (staging → marts)
- [ ] Add dbt test tasks
- [ ] Add Great Expectations validation
- [ ] Schedule daily at 2 AM
- [ ] Configure email alerts

**Acceptance Criteria:**
- DAG runs on schedule
- dbt models execute successfully
- Tests pass
- Alerts trigger on failure

---

### Task 6.3: Airflow DAGs - Feature Engineering
**ID:** ORCH-003  
**Priority:** P0  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Workflow Orchestrator Agent  
**Time Estimate:** 4 hours  
**Dependencies:** FEAT-003

**Description:**
Create Airflow DAG for weekly feature refresh.

**Subtasks:**
- [ ] Create `airflow/dags/feature_engineering_dag.py`
- [ ] Schedule weekly (Sunday midnight)
- [ ] Add feature validation
- [ ] Configure alerts

**Acceptance Criteria:**
- DAG runs weekly
- Features refreshed successfully
- Validation passes

---

## PHASE 7: UI DEVELOPMENT

### Task 7.1: Streamlit Application Setup
**ID:** UI-001  
**Priority:** P1  
**Status:** 🔴 Not Started  
**Owner:** 👤 Developer  
**Time Estimate:** 3 hours  
**Dependencies:** SETUP-003

**Description:**
Setup Streamlit application structure.

**Subtasks:**
- [ ] Create `apps/streamlit_app.py`
- [ ] Setup page navigation
- [ ] Configure theme
- [ ] Create reusable components
- [ ] Setup API client

**Acceptance Criteria:**
- App loads successfully
- Navigation works
- Theme applied

---

### Task 7.2: Dashboard Page
**ID:** UI-002  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 👤 Developer  
**Time Estimate:** 6 hours  
**Dependencies:** UI-001, API-002

**Description:**
Create main dashboard showing ICU overview.

**Subtasks:**
- [ ] Create patient summary cards
- [ ] Create patient table (searchable)
- [ ] Add risk distribution chart
- [ ] Add recent predictions list
- [ ] Connect to API

**Acceptance Criteria:**
- Dashboard displays live data from API
- All charts render correctly
- Search works

---

### Task 7.3: Prediction Interface
**ID:** UI-003  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 👤 Developer  
**Time Estimate:** 8 hours  
**Dependencies:** UI-001, API-002

**Description:**
Create prediction interface for manual predictions.

**Subtasks:**
- [ ] Create input form (42 fields for sepsis)
- [ ] Add form validation
- [ ] Call API on submit
- [ ] Display prediction results
- [ ] Display SHAP explanation
- [ ] Add model selector (sepsis/mortality)

**Acceptance Criteria:**
- Form works for both models
- Real-time predictions via API
- SHAP plot displays correctly

---

### Task 7.4: Model Performance Page
**ID:** UI-004  
**Priority:** P2  
**Status:** ⏸️ Blocked  
**Owner:** 👤 Developer  
**Time Estimate:** 6 hours  
**Dependencies:** UI-001, ML-004

**Description:**
Create page showing model performance metrics.

**Subtasks:**
- [ ] Display AUROC curves
- [ ] Display confusion matrices
- [ ] Display feature importance
- [ ] Add model version selector
- [ ] Add performance trend charts

**Acceptance Criteria:**
- All charts render
- Model comparison works

---

## PHASE 8: AGENT INTEGRATION

### Task 8.1: Agent Configuration Finalization
**ID:** AGENT-001  
**Priority:** P1  
**Status:** 🟡 In Progress  
**Owner:** 👤 Developer  
**Time Estimate:** 4 hours  
**Dependencies:** All DATA tasks, All ML tasks

**Description:**
Finalize all agent configurations in `agents/config/agents.yaml` and `tasks.yaml`.

**Subtasks:**
- [x] Define all 17 agents in `agents.yaml`
- [ ] Define all 30+ tasks in `tasks.yaml`
- [ ] Map tasks to agents
- [ ] Define task dependencies
- [ ] Validate YAML syntax

**Acceptance Criteria:**
- All agents have complete configs
- All tasks defined with dependencies
- YAML validates successfully

---

### Task 8.2: Agent Implementation - Data Agents
**ID:** AGENT-002  
**Priority:** P1  
**Status:** 🟡 In Progress  
**Owner:** 👤 Developer  
**Time Estimate:** 12 hours  
**Dependencies:** AGENT-001

**Description:**
Implement Data Engineering agents (Ingestion, Transformation, Quality).

**Subtasks:**
- [x] Implement `DataIngestionAgent` (base structure done)
- [ ] Implement `DataTransformationAgent`
- [ ] Implement `DataQualityAgent`
- [ ] Write unit tests for each agent
- [ ] Test agent execution with real data

**Acceptance Criteria:**
- All 3 agents implement `BaseAgent`
- Agents execute tasks successfully
- Unit tests pass

---

### Task 8.3: Agent Implementation - ML Agents
**ID:** AGENT-003  
**Priority:** P1  
**Status:** 🔴 Not Started  
**Owner:** 👤 Developer  
**Time Estimate:** 12 hours  
**Dependencies:** AGENT-001

**Description:**
Implement ML Engineering agents.

**Subtasks:**
- [ ] Implement `FeatureEngineeringAgent`
- [ ] Implement `ModelTrainingAgent`
- [ ] Implement `ModelEvaluationAgent`
- [ ] Write tests

**Acceptance Criteria:**
- Agents execute ML tasks
- Tests pass

---

### Task 8.4: Crew Implementations
**ID:** AGENT-004  
**Priority:** P1  
**Status:** 🟡 In Progress  
**Owner:** 👤 Developer  
**Time Estimate:** 8 hours  
**Dependencies:** AGENT-002, AGENT-003

**Description:**
Implement all 4 crews (DataPipeline, MLDevelopment, Deployment, Monitoring).

**Subtasks:**
- [x] Implement `DataPipelineCrew` (structure done)
- [ ] Implement `MLDevelopmentCrew`
- [ ] Implement `DeploymentCrew`
- [ ] Implement `MonitoringCrew`
- [ ] Test crew execution

**Acceptance Criteria:**
- All crews coordinate agents successfully
- Crews can be kicked off independently
- Execution summary generated

---

### Task 8.5: Workflow Orchestrator
**ID:** AGENT-005  
**Priority:** P1  
**Status:** 🟡 In Progress  
**Owner:** 👤 Developer  
**Time Estimate:** 10 hours  
**Dependencies:** AGENT-004

**Description:**
Implement top-level Workflow Orchestrator to coordinate all crews.

**Subtasks:**
- [x] Implement `WorkflowOrchestrator` (base structure done)
- [ ] Implement dependency management
- [ ] Implement checkpointing
- [ ] Implement failure recovery
- [ ] Add decision engine logic
- [ ] Test full pipeline orchestration

**Acceptance Criteria:**
- Orchestrator coordinates all crews
- Dependency graph respected
- Checkpointing works (resumable)
- Failure recovery works

---

## PHASE 9: TESTING & DOCUMENTATION

### Task 9.1: Unit Tests
**ID:** TEST-001  
**Priority:** P1  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Quality Assurance Agent  
**Time Estimate:** 12 hours  
**Dependencies:** All implementation tasks

**Description:**
Write comprehensive unit tests for all modules.

**Subtasks:**
- [ ] Test data ingestion functions
- [ ] Test feature engineering functions
- [ ] Test model loading/inference
- [ ] Test API endpoints
- [ ] Test agent execution
- [ ] Achieve 70%+ coverage

**Acceptance Criteria:**
- pytest runs successfully
- Coverage ≥70%
- All critical paths tested

---

### Task 9.2: Integration Tests
**ID:** TEST-002  
**Priority:** P1  
**Status:** 🔴 Not Started  
**Owner:** 🤖 Quality Assurance Agent  
**Time Estimate:** 8 hours  
**Dependencies:** TEST-001

**Description:**
Write integration tests for cross-component interactions.

**Subtasks:**
- [ ] Test database ↔ API
- [ ] Test API ↔ UI
- [ ] Test Airflow ↔ dbt
- [ ] Test agent ↔ tools
- [ ] Test end-to-end pipeline

**Acceptance Criteria:**
- Integration tests pass
- All critical flows tested

---

### Task 9.3: Documentation - README
**ID:** DOC-001  
**Priority:** P0  
**Status:** 🟡 In Progress  
**Owner:** 👤 Developer  
**Time Estimate:** 4 hours  
**Dependencies:** All implementation tasks

**Description:**
Write comprehensive README with setup instructions.

**Subtasks:**
- [x] Project description
- [ ] Architecture diagram
- [ ] Setup instructions
- [ ] Usage examples
- [ ] Screenshots
- [ ] Troubleshooting guide

**Acceptance Criteria:**
- README is complete and accurate
- New users can setup from README
- All features documented

---

### Task 9.4: Documentation - Model Cards
**ID:** DOC-002  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 Model Evaluation Agent  
**Time Estimate:** 4 hours  
**Dependencies:** ML-004

**Description:**
Create detailed model cards for both models.

**Subtasks:**
- [ ] Sepsis model card (performance, limitations, ethical considerations)
- [ ] Mortality model card
- [ ] Add to `docs/MODEL_CARDS.md`

**Acceptance Criteria:**
- Model cards follow best practices
- All sections complete

---

### Task 9.5: Documentation - API Docs
**ID:** DOC-003  
**Priority:** P1  
**Status:** ⏸️ Blocked  
**Owner:** 🤖 API Development Agent  
**Time Estimate:** 3 hours  
**Dependencies:** API-004

**Description:**
Enhance FastAPI auto-docs with detailed descriptions and examples.

**Subtasks:**
- [ ] Add docstrings to all endpoints
- [ ] Add request/response examples
- [ ] Add cURL examples to README

**Acceptance Criteria:**
- OpenAPI docs complete
- All endpoints documented
- Examples work

---

## PHASE 10: FINALIZATION

### Task 10.1: Performance Optimization
**ID:** FINAL-001  
**Priority:** P2  
**Status:** 🔴 Not Started  
**Owner:** 👤 Developer  
**Time Estimate:** 8 hours  
**Dependencies:** All implementation tasks

**Description:**
Optimize system performance to meet targets.

**Subtasks:**
- [ ] Profile API endpoints (identify bottlenecks)
- [ ] Optimize database queries (add indexes)
- [ ] Optimize model inference (batch predictions)
- [ ] Optimize Docker images (reduce size)

**Acceptance Criteria:**
- API p95 latency <200ms
- Model inference <100ms
- Database queries <5s

---

### Task 10.2: Security Hardening
**ID:** FINAL-002  
**Priority:** P1  
**Status:** 🔴 Not Started  
**Owner:** 🤖 DevOps Agent  
**Time Estimate:** 6 hours  
**Dependencies:** All implementation tasks

**Description:**
Implement security best practices.

**Subtasks:**
- [ ] Add input sanitization
- [ ] Add rate limiting
- [ ] Add HTTPS (for production)
- [ ] Scan for vulnerabilities (Trivy)
- [ ] Review secrets management

**Acceptance Criteria:**
- No critical vulnerabilities
- Rate limiting works
- Secrets not hardcoded

---

### Task 10.3: Final Testing & Demo Preparation
**ID:** FINAL-003  
**Priority:** P0  
**Status:** 🔴 Not Started  
**Owner:** 👤 Developer  
**Time Estimate:** 6 hours  
**Dependencies:** FINAL-001, FINAL-002

**Description:**
Final system testing and demo preparation.

**Subtasks:**
- [ ] End-to-end system test
- [ ] Prepare demo script
- [ ] Record demo video (5-10 minutes)
- [ ] Create presentation slides
- [ ] Take screenshots for README

**Acceptance Criteria:**
- Full pipeline works end-to-end
- Demo script ready
- Video recorded
- Screenshots captured

---

## SUMMARY STATISTICS

### By Phase
| Phase | Total Tasks | Complete | In Progress | Not Started | Blocked |
|-------|-------------|----------|-------------|-------------|---------|
| 1. Setup | 4 | 2 | 1 | 1 | 0 |
| 2. Data Pipeline | 8 | 1 | 1 | 3 | 3 |
| 3. Feature Engineering | 3 | 0 | 0 | 0 | 3 |
| 4. ML Models | 4 | 0 | 0 | 0 | 4 |
| 5. API & Serving | 4 | 0 | 0 | 1 | 3 |
| 6. Orchestration | 3 | 0 | 0 | 1 | 2 |
| 7. UI Development | 4 | 0 | 0 | 1 | 3 |
| 8. Agent Integration | 5 | 0 | 4 | 1 | 0 |
| 9. Testing & Docs | 5 | 0 | 1 | 4 | 0 |
| 10. Finalization | 3 | 0 | 0 | 3 | 0 |
| **TOTAL** | **43** | **3** | **7** | **15** | **18** |

### By Priority
| Priority | Count | % Complete |
|----------|-------|------------|
| P0 (Critical) | 22 | 9% |
| P1 (High) | 17 | 6% |
| P2 (Medium) | 3 | 0% |
| P3 (Low) | 1 | 0% |

### By Owner Type
| Owner | Count |
|-------|-------|
| 👤 Developer | 15 |
| 🤖 Agent | 23 |
| 🤝 Hybrid | 5 |

---

## CRITICAL PATH

**Longest dependency chain (must complete sequentially):**

```
SETUP-001 → SETUP-002 → SETUP-003 → DATA-001/DATA-002 → DATA-003 → DATA-004 
→ DATA-005 → DATA-006 → DATA-007 → FEAT-001 → ML-001 → ML-002 → API-002 
→ UI-003 → TEST-002 → FINAL-003
```

**Estimated Critical Path Duration:** ~10 weeks (part-time work)

**Parallelizable Work:**
- Feature engineering (FEAT-001, FEAT-002) can run in parallel
- Model training (ML-002, ML-003) can run in parallel
- UI development can start once API-001 is done
- Agent implementation can progress alongside data/ML work

---

## NEXT ACTIONS (Priority Order)

1. ✅ **Complete Task SETUP-003** (Docker Compose) - BLOCKING 15 tasks
2. ✅ **Complete Task DATA-001** (MIMIC-IV access) - Can use DATA-002 (sample data) meanwhile
3. ✅ **Start Task DATA-004** (Data ingestion) - Agents can begin work
4. ✅ **Start Task ML-001** (MLflow setup) - Unblocks model training
5. ✅ **Finalize Task AGENT-001** (Agent configs) - Enables agent automation

---

**Document Version:** 1.0  
**Status:** 🔄 Living Document (Updated as tasks progress)  
**Owner:** Project Lead  
**Review Frequency:** Weekly
