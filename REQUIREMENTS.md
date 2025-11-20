# Healthcare ML Platform - Requirements Specification

**Version:** 1.0  
**Status:** Approved for Implementation  
**Last Updated:** 2025-01-20

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Purpose
Build a **production-ready, portfolio-quality** healthcare ML platform demonstrating end-to-end MLOps capabilities using real-world ICU data (MIMIC-IV).

### 1.2 Core Objectives
1. **Data Engineering:** Implement medallion architecture (bronze/silver/gold) for MIMIC-IV
2. **ML Engineering:** Deploy 2 production models (Sepsis + Mortality prediction)
3. **MLOps:** Full lifecycle management (training, serving, monitoring, retraining)
4. **Platform Engineering:** Orchestration, APIs, UI, containerization
5. **Agent Architecture:** CrewAI-based workflow automation

### 1.3 Success Criteria
- ✅ End-to-end pipeline operational (data → models → predictions → UI)
- ✅ Models meet performance targets (AUROC >0.85 sepsis, >0.80 mortality)
- ✅ API latency p95 <200ms
- ✅ 70%+ test coverage
- ✅ Complete documentation
- ✅ Agent orchestration functional

---

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 Data Management

#### FR-DATA-001: MIMIC-IV Ingestion
**Requirement:** System SHALL ingest MIMIC-IV ICU data (~5GB) into PostgreSQL

**Details:**
- **Source:** Kaggle dataset `akshaybe/updated-mimic-iv` (downloaded via kagglehub)
- **Tables:** icustays, patients, admissions, chartevents, labevents, diagnoses_icd
- **Volume:** ~73K ICU stays, ~200M chart events
- **Format:** CSV → PostgreSQL raw schema
- **Validation:** Row count verification, schema inference, data quality checks

**Note:** See [DATA_SOURCE.md](DATA_SOURCE.md) for complete data source documentation.

**Acceptance Criteria:**
- All CSV files loaded without data loss
- Raw schema matches MIMIC-IV specification
- Data quality checks pass (>95% completeness)
- Ingestion resumable from checkpoint

**Dependencies:** None
**Priority:** P0 (Critical)

---

#### FR-DATA-002: Medallion Architecture
**Requirement:** System SHALL implement bronze/silver/gold data layers using dbt

**Details:**
- **Bronze (Raw):** Exact copy of source data
- **Silver (Staging):** Cleaned, deduplicated, type-casted
- **Gold (Analytics):** Star schema with fact/dimension tables

**Tables Required:**

**Silver Layer:**
- `stg_icustays` - Cleaned ICU stays
- `stg_chartevents` - Validated vitals/measurements
- `stg_labevents` - Cleaned lab results
- `stg_patients` - Patient demographics

**Gold Layer (Star Schema):**
- `dim_patients` - Patient dimension (age, gender, demographics)
- `dim_time` - Time dimension (date, hour, day_of_week)
- `dim_diagnoses` - Diagnosis dimension (ICD-10 codes)
- `fact_icu_stays` - ICU stay fact (1 row per admission)
- `fact_vitals_hourly` - Aggregated vitals per hour
- `fact_labs_daily` - Aggregated labs per day

**Acceptance Criteria:**
- All dbt models compile and run successfully
- Data lineage traceable (raw → staging → marts)
- dbt tests pass (referential integrity, not_null, unique)
- Documentation generated via dbt docs

**Dependencies:** FR-DATA-001
**Priority:** P0 (Critical)

---

#### FR-DATA-003: Data Quality Monitoring
**Requirement:** System SHALL implement automated data quality checks

**Quality Checks:**
1. **Completeness:** Missing value rate <5% for critical fields
2. **Validity:** Vitals within physiological ranges (HR: 0-300, Temp: 32-42°C)
3. **Consistency:** Referential integrity between tables
4. **Timeliness:** Data freshness <24 hours
5. **Uniqueness:** No duplicate ICU stays

**Tools:**
- Great Expectations test suites
- dbt data tests
- Custom validation rules

**Acceptance Criteria:**
- Quality checks run automatically after each ETL
- Alerts triggered on quality score <95%
- Quality dashboard shows metrics over time

**Dependencies:** FR-DATA-002
**Priority:** P1 (High)

---

### 2.2 Feature Engineering

#### FR-FEAT-001: Sepsis Features
**Requirement:** System SHALL create 42 features for sepsis prediction

**Feature Categories:**

1. **Demographics (3 features):**
   - `age` - Patient age in years
   - `gender` - M/F
   - `bmi` - Body mass index (calculated from height/weight)

2. **Vitals (5 features):**
   - `heart_rate` - Most recent HR (bpm)
   - `sbp` - Systolic blood pressure (mmHg)
   - `dbp` - Diastolic blood pressure (mmHg)
   - `temperature` - Body temperature (°C)
   - `respiratory_rate` - Breaths per minute

3. **Laboratory Values (20 features):**
   - `wbc` - White blood cell count
   - `lactate` - Serum lactate (mmol/L)
   - `creatinine` - Serum creatinine (mg/dL)
   - `platelets` - Platelet count
   - `bilirubin` - Total bilirubin
   - ... (full list in MODEL_CARDS.md)

4. **SOFA Scores (6 features):**
   - `respiratory_sofa` - Respiratory component (0-4)
   - `cardiovascular_sofa` - Cardiovascular component (0-4)
   - `hepatic_sofa` - Hepatic component (0-4)
   - `coagulation_sofa` - Coagulation component (0-4)
   - `renal_sofa` - Renal component (0-4)
   - `neurological_sofa` - Neurological component (0-4)

5. **Temporal Trends (6 features):**
   - `lactate_trend_12h` - Lactate change over 12 hours
   - `hr_trend_6h` - Heart rate trend over 6 hours
   - `wbc_trend_12h` - WBC trend over 12 hours
   - `sbp_trend_6h` - Blood pressure trend
   - `temperature_trend_6h` - Temperature trend
   - `rr_trend_6h` - Respiratory rate trend

6. **Time Features (2 features):**
   - `hour_of_admission` - Hour of day (0-23)
   - `icu_los_so_far` - Hours in ICU so far

**Reference Implementation:** Adapted from BorgwardtLab/mgp-tcn preprocessing

**Feature Table:** `analytics.features_sepsis_6h`

**Acceptance Criteria:**
- Feature table contains 42 columns + metadata
- No data leakage (features extracted from t-6h, target at t=0)
- No future information used
- Feature distributions stable across train/val/test

**Dependencies:** FR-DATA-002
**Priority:** P0 (Critical)

---

#### FR-FEAT-002: Mortality Features
**Requirement:** System SHALL create 65 features for mortality prediction

**Feature Categories:**

1. **SOFA Scores (6 features):** Same as sepsis
2. **APACHE-II Components (12 features):**
   - Age points
   - Worst vitals in first 24h
   - Worst labs in first 24h
   - GCS score
3. **Vitals Summary (8 features):** Worst values in first 24h
4. **Labs Summary (25 features):** Worst values in first 24h
5. **ICU Details (10 features):**
   - `icu_type` - Medical/Surgical/Cardiac
   - `ventilation_flag` - Mechanical ventilation
   - `vasopressor_flag` - Vasopressor use
   - ... (full list in MODEL_CARDS.md)
6. **Diagnoses (4 features):**
   - `sepsis_flag` - Sepsis diagnosis
   - `shock_flag` - Shock diagnosis
   - `cardiac_arrest_flag` - Cardiac arrest
   - `trauma_flag` - Trauma admission

**Reference Implementation:** Adapted from healthylaife/MIMIC-IV-Data-Pipeline

**Feature Table:** `analytics.features_mortality_24h`

**Acceptance Criteria:**
- Feature table contains 65 columns + metadata
- APACHE-II calculation validated against reference
- SOFA scores match clinical definitions
- No temporal leakage

**Dependencies:** FR-DATA-002
**Priority:** P0 (Critical)

---

### 2.3 Machine Learning Models

#### FR-ML-001: Sepsis Early Warning Model
**Requirement:** System SHALL train and deploy sepsis prediction model

**Model Specification:**
```yaml
model_name: sepsis_lightgbm_v1
algorithm: LightGBM Classifier
task: Binary Classification
target: sepsis_onset_within_6h

training_data:
  cohort_definition: SEPSIS-3 criteria (microsoft/mimic_sepsis)
  total_samples: 20000
  positive_class: 1200 (6%)
  negative_class: 18800 (94%)
  class_imbalance_handling: SMOTE oversampling
  split_ratio: 70/15/15 (train/val/test)

features: 42 (defined in FR-FEAT-001)

hyperparameters:
  num_leaves: 31
  learning_rate: 0.05
  n_estimators: 500
  max_depth: 6
  min_child_samples: 20
  subsample: 0.8
  colsample_bytree: 0.8
  class_weight: balanced

performance_targets:
  AUROC: >0.85
  Sensitivity: >0.80
  Specificity: >0.80
  PPV: >0.35
  NPV: >0.95

inference:
  latency_target: <100ms (p95)
  batch_size: 1 (real-time)
  output_format: probability + risk_level + explanation
```

**Model Artifacts:**
- Trained model: `models/sepsis_lightgbm_v1/model.pkl`
- Preprocessing: `models/sepsis_lightgbm_v1/preprocessing.pkl`
- SHAP explainer: `models/sepsis_lightgbm_v1/shap_explainer.pkl`
- Model card: `models/sepsis_lightgbm_v1/model_card.md`

**Acceptance Criteria:**
- Model meets all performance targets on test set
- Model registered in MLflow registry
- Model card completed (performance, limitations, ethical considerations)
- SHAP explainer generates feature importance for every prediction

**Dependencies:** FR-FEAT-001
**Priority:** P0 (Critical)

---

#### FR-ML-002: ICU Mortality Prediction Model
**Requirement:** System SHALL train and deploy mortality prediction model

**Model Specification:**
```yaml
model_name: mortality_lightgbm_v1
algorithm: LightGBM Classifier
task: Binary Classification
target: hospital_expire_flag

training_data:
  total_samples: 70000
  positive_class: 7000 (10%)
  negative_class: 63000 (90%)
  class_imbalance_handling: class_weight='balanced'
  split_ratio: 70/15/15

features: 65 (defined in FR-FEAT-002)

hyperparameters:
  num_leaves: 31
  learning_rate: 0.03
  n_estimators: 800
  max_depth: 8
  min_child_samples: 20
  subsample: 0.85
  colsample_bytree: 0.85

performance_targets:
  AUROC: >0.80
  Sensitivity: >0.75
  Specificity: >0.85

inference:
  latency_target: <80ms (p95)
```

**Acceptance Criteria:**
- Model meets performance targets
- Model registered in MLflow
- Complete model documentation

**Dependencies:** FR-FEAT-002
**Priority:** P0 (Critical)

---

### 2.4 API & Serving

#### FR-API-001: Prediction Endpoints
**Requirement:** System SHALL expose REST API for model predictions

**Endpoints:**

1. **Health Check**
```http
GET /health
Response: {"status": "healthy", "version": "1.0.0"}
```

2. **Sepsis Prediction**
```http
POST /predict/sepsis
Content-Type: application/json

Request:
{
  "patient_id": "P-100234",
  "features": {
    "age": 65,
    "heart_rate": 110,
    "lactate": 3.5,
    ... (42 features)
  }
}

Response:
{
  "prediction": {
    "risk_score": 0.78,
    "risk_level": "HIGH",
    "recommendation": "Consider sepsis protocol"
  },
  "explanation": {
    "top_features": [
      {"feature": "lactate", "importance": 0.23, "value": 3.5},
      ...
    ]
  },
  "metadata": {
    "model_version": "sepsis_lightgbm_v1",
    "prediction_time_ms": 45
  }
}
```

3. **Mortality Prediction**
```http
POST /predict/mortality
(Similar structure)
```

4. **SHAP Explanation**
```http
POST /explain/shap
Request: Same as prediction
Response: Base64-encoded SHAP waterfall plot
```

**Acceptance Criteria:**
- All endpoints return 200 for valid requests
- Input validation via Pydantic schemas
- Error handling (400 for invalid input, 500 for server errors)
- API documentation auto-generated (FastAPI /docs)
- Latency targets met (p95 <200ms)

**Dependencies:** FR-ML-001, FR-ML-002
**Priority:** P0 (Critical)

---

#### FR-API-002: Caching Layer
**Requirement:** System SHALL implement Redis caching for predictions

**Caching Strategy:**
- Cache key: MD5(model_version + feature_hash)
- TTL: 1 hour
- Cache hit rate target: >80%
- Eviction policy: LRU

**Acceptance Criteria:**
- Redis integrated with FastAPI
- Cache hit rate logged and monitored
- Cache invalidation on model update

**Dependencies:** FR-API-001
**Priority:** P1 (High)

---

### 2.5 Orchestration

#### FR-ORCH-001: Airflow DAGs
**Requirement:** System SHALL orchestrate workflows using Apache Airflow

**DAGs Required:**

1. **Data Ingestion DAG** (`ingest_mimic_iv_dag.py`)
   - Schedule: Once (manual trigger)
   - Tasks: Ingest all MIMIC-IV tables
   - Dependencies: None
   - Success criteria: All tables loaded

2. **ETL Pipeline DAG** (`etl_pipeline_dag.py`)
   - Schedule: Daily at 2 AM
   - Tasks: dbt run (bronze → silver → gold)
   - Dependencies: Data ingestion complete
   - Success criteria: dbt tests pass

3. **Feature Engineering DAG** (`feature_engineering_dag.py`)
   - Schedule: Weekly (Sunday midnight)
   - Tasks: Create sepsis + mortality features
   - Dependencies: ETL complete
   - Success criteria: Feature tables updated

4. **Data Quality DAG** (`data_quality_dag.py`)
   - Schedule: Daily at 3 AM
   - Tasks: Run Great Expectations suites
   - Dependencies: ETL complete
   - Success criteria: Quality score >95%

**Acceptance Criteria:**
- All DAGs visible in Airflow UI
- DAGs execute on schedule
- Email alerts on failure
- Execution time logged

**Dependencies:** FR-DATA-002
**Priority:** P0 (Critical)

---

### 2.6 User Interface

#### FR-UI-001: Streamlit Dashboard
**Requirement:** System SHALL provide web-based dashboard for model interaction

**Pages Required:**

1. **Home / Overview**
   - Total ICU patients
   - High-risk patient count
   - Model performance summary
   - Recent predictions

2. **Patient Management**
   - Patient list table (searchable)
   - Patient detail view (vitals, labs, predictions)
   - Risk scores displayed

3. **Prediction Interface**
   - Input form for manual predictions
   - Model selector (sepsis / mortality)
   - Real-time prediction via API
   - SHAP explanation display

4. **Model Performance**
   - AUROC curves
   - Confusion matrices
   - Feature importance charts
   - Model version info

**Acceptance Criteria:**
- All pages load without errors
- API integration works
- Charts render correctly
- Responsive design (mobile-friendly)

**Dependencies:** FR-API-001
**Priority:** P1 (High)

---

### 2.7 Agent Architecture

#### FR-AGENT-001: CrewAI Agent System
**Requirement:** System SHALL implement agent-based workflow automation

**Agent Roles Defined:**

1. **Data Engineering Agents:**
   - Data Ingestion Agent
   - Data Transformation Agent
   - Data Quality Agent

2. **ML Engineering Agents:**
   - Feature Discovery Agent
   - Feature Engineering Agent
   - Model Training Agent
   - Model Evaluation Agent

3. **DevOps Agents:**
   - API Development Agent
   - Container Orchestration Agent
   - Infrastructure Agent

4. **Monitoring Agents:**
   - Performance Monitor Agent
   - Data Drift Detection Agent
   - Alert Management Agent

5. **Orchestration Agents:**
   - Workflow Orchestrator Agent
   - Decision Engine Agent

**Agent Capabilities:**
- Execute tasks autonomously
- Delegate to other agents
- Use tools (database, API, MLflow)
- Report results and metrics

**Acceptance Criteria:**
- All agents defined in `agents/config/agents.yaml`
- Agent implementations inherit from `BaseAgent`
- Crews orchestrate multi-agent workflows
- Workflow Orchestrator coordinates all crews

**Dependencies:** All other FRs
**Priority:** P1 (High)

---

## 3. NON-FUNCTIONAL REQUIREMENTS

### 3.1 Performance

#### NFR-PERF-001: API Latency
- **Requirement:** API p95 latency SHALL be <200ms
- **Measurement:** Prometheus metrics
- **Acceptance:** 95th percentile consistently under threshold

#### NFR-PERF-002: Database Query Performance
- **Requirement:** Feature extraction queries SHALL complete in <5 seconds
- **Implementation:** Proper indexing on frequently queried columns
- **Acceptance:** EXPLAIN ANALYZE shows efficient execution plans

#### NFR-PERF-003: Model Inference Speed
- **Requirement:** Sepsis model inference SHALL be <100ms (p95)
- **Requirement:** Mortality model inference SHALL be <80ms (p95)
- **Acceptance:** Latency measured via MLflow autolog

---

### 3.2 Scalability

#### NFR-SCALE-001: Data Volume
- **Requirement:** System SHALL handle up to 100K ICU stays
- **Requirement:** System SHALL handle up to 500M chart events
- **Implementation:** Batch processing, streaming where needed

#### NFR-SCALE-002: Prediction Throughput
- **Requirement:** System SHALL handle 100 predictions/second
- **Implementation:** FastAPI async endpoints, Redis caching

---

### 3.3 Reliability

#### NFR-REL-001: System Uptime
- **Requirement:** System SHALL have 99% uptime (local demo)
- **Implementation:** Docker health checks, Airflow retries

#### NFR-REL-002: Data Durability
- **Requirement:** Data SHALL be persisted across container restarts
- **Implementation:** Docker volumes for PostgreSQL, Redis

#### NFR-REL-003: Failure Recovery
- **Requirement:** ETL pipeline SHALL be resumable from checkpoint
- **Implementation:** Airflow checkpointing, idempotent DAGs

---

### 3.4 Security & Compliance

#### NFR-SEC-001: Data Privacy
- **Requirement:** System SHALL use de-identified data only (MIMIC-IV)
- **Requirement:** No PHI SHALL be logged or displayed
- **Compliance:** HIPAA-aware design

#### NFR-SEC-002: Authentication
- **Requirement:** UI SHALL require login (placeholder in MVP)
- **Implementation:** Simple auth (username/password)

#### NFR-SEC-003: API Security
- **Requirement:** API SHALL validate all inputs
- **Implementation:** Pydantic schemas, rate limiting

---

### 3.5 Maintainability

#### NFR-MAINT-001: Code Quality
- **Requirement:** Code SHALL pass linting (flake8, black)
- **Requirement:** Code SHALL have type hints
- **Requirement:** Code SHALL have docstrings
- **Acceptance:** CI checks pass

#### NFR-MAINT-002: Test Coverage
- **Requirement:** Unit test coverage SHALL be >70%
- **Requirement:** Integration tests SHALL cover critical paths
- **Acceptance:** pytest coverage report

#### NFR-MAINT-003: Documentation
- **Requirement:** All modules SHALL have README
- **Requirement:** API SHALL have OpenAPI docs
- **Requirement:** Models SHALL have model cards
- **Acceptance:** Documentation complete and accurate

---

### 3.6 Usability

#### NFR-USE-001: UI Responsiveness
- **Requirement:** UI SHALL load in <3 seconds
- **Requirement:** UI SHALL work on mobile devices

#### NFR-USE-002: Error Messages
- **Requirement:** Error messages SHALL be clear and actionable
- **Example:** "Heart rate must be between 0 and 300 bpm" (not "Invalid input")

---

## 4. CONSTRAINTS

### 4.1 Technical Constraints
- **Dataset:** MIMIC-IV ICU-only (15GB, not full 100GB)
- **Algorithm:** LightGBM only (consistency)
- **Models:** Exactly 2 in v1 (Sepsis + Mortality)
- **Infrastructure:** Local deployment via Docker Compose
- **Budget:** $0 (no cloud resources)

### 4.2 Time Constraints
- **Timeline:** 4-6 weeks (part-time)
- **MVP Focus:** Core functionality, defer vision features

### 4.3 Resource Constraints
- **Hardware:** 16GB RAM minimum, 50GB disk
- **Services:** Max 12 Docker containers concurrently

---

## 5. OUT OF SCOPE (VISION FEATURES)

The following are **documented but NOT implemented** in v1:

- ❌ Prometheus + Grafana monitoring (placeholder only)
- ❌ Metabase BI dashboards (SQL queries written, not deployed)
- ❌ Readmission prediction model (future)
- ❌ Length of stay prediction (future)
- ❌ NLP on clinical notes (research)
- ❌ Reinforcement learning policies (research)
- ❌ Auto-retraining pipeline (manual retraining only)
- ❌ Cloud deployment (local only)
- ❌ Real-time streaming (batch only)
- ❌ Mobile app (web only)

See `IMPLEMENTED_VS_VISION.md` for details.

---

## 6. ACCEPTANCE CRITERIA SUMMARY

### 6.1 Data Pipeline
- ✅ All MIMIC-IV tables loaded
- ✅ dbt models compile and run
- ✅ Data quality checks pass
- ✅ Airflow DAGs scheduled

### 6.2 ML Models
- ✅ Sepsis model AUROC >0.85
- ✅ Mortality model AUROC >0.80
- ✅ Models in MLflow registry
- ✅ SHAP explainers functional

### 6.3 API & Serving
- ✅ All endpoints return 200
- ✅ Latency p95 <200ms
- ✅ Input validation works
- ✅ Redis caching >80% hit rate

### 6.4 UI
- ✅ All pages load
- ✅ Predictions via API work
- ✅ Charts render correctly

### 6.5 Testing
- ✅ Unit tests >70% coverage
- ✅ Integration tests pass
- ✅ CI/CD pipeline passes

### 6.6 Documentation
- ✅ README complete
- ✅ API docs auto-generated
- ✅ Model cards written
- ✅ Architecture documented

---

## 7. TRACEABILITY MATRIX

| Requirement ID | Description | Implementation | Test Coverage |
|----------------|-------------|----------------|---------------|
| FR-DATA-001 | MIMIC-IV Ingestion | `scripts/ingest_mimic_iv.py` | `test_ingestion.py` |
| FR-DATA-002 | Medallion Architecture | `dbt_project/models/` | `dbt test` |
| FR-DATA-003 | Data Quality | `great_expectations/` | `test_data_quality.py` |
| FR-FEAT-001 | Sepsis Features | `dbt_project/models/marts/features_sepsis_6h.sql` | `test_features.py` |
| FR-FEAT-002 | Mortality Features | `dbt_project/models/marts/features_mortality_24h.sql` | `test_features.py` |
| FR-ML-001 | Sepsis Model | `notebooks/02_sepsis_model.ipynb` | `test_models.py` |
| FR-ML-002 | Mortality Model | `notebooks/03_mortality_model.ipynb` | `test_models.py` |
| FR-API-001 | Prediction Endpoints | `api/routers/predictions.py` | `test_api.py` |
| FR-API-002 | Caching | `api/services/cache_service.py` | `test_cache.py` |
| FR-ORCH-001 | Airflow DAGs | `airflow/dags/` | Manual testing |
| FR-UI-001 | Streamlit Dashboard | `apps/streamlit_app.py` | Manual testing |
| FR-AGENT-001 | Agent System | `agents/` | `test_agents.py` |

---

**Document Version:** 1.0  
**Approval Status:** ✅ APPROVED  
**Next Steps:** See TASK_BREAKDOWN.md for implementation plan
