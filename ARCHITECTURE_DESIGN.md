# Healthcare ML Platform - Architecture Design Document

**Version:** 1.0  
**Status:** Design Approved  
**Last Updated:** 2025-01-20

---

## DOCUMENT PURPOSE

This document provides **detailed technical design** for all system components. It serves as the single source of truth for implementation and ensures consistency across:
- Data pipeline architecture
- ML model architecture
- API design
- Agent architecture
- UI/UX design
- Integration patterns

**Related Documents:**
- Requirements: `REQUIREMENTS.md`
- Task Breakdown: `TASK_BREAKDOWN.md`
- Agent Design: `agents/AGENT_ARCHITECTURE.md`
- Model Cards: `docs/MODEL_CARDS.md`

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### 1.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Streamlit  │  │  FastAPI     │  │   Metabase   │        │
│  │   Dashboard  │  │   /docs      │  │  (Future)    │        │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘        │
└─────────┼──────────────────┼──────────────────────────────────┘
          │                  │
          │ HTTP             │ HTTP/REST
          ▼                  ▼
┌────────────────────────────────────────────────────────────────┐
│                      API & SERVING LAYER                        │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  FastAPI Application                                  │     │
│  │  ├─ /predict/sepsis                                  │     │
│  │  ├─ /predict/mortality                               │     │
│  │  ├─ /explain/shap                                    │     │
│  │  └─ /health                                          │     │
│  └──────────────────────────────────────────────────────┘     │
│                           │                                     │
│                           │ Load models                         │
│                           ▼                                     │
│  ┌─────────────────────────────────────┐  ┌────────────────┐ │
│  │   MLflow Model Registry              │  │  Redis Cache   │ │
│  │   └─ sepsis_lightgbm_v1             │  │  (Features)    │ │
│  │   └─ mortality_lightgbm_v1          │  └────────────────┘ │
│  └─────────────────────────────────────┘                      │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ Query features
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER (Airflow)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Ingest DAG  │  │  ETL DAG     │  │  Feature DAG │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                │
│                            │                                    │
│                            │ Trigger                            │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              dbt Transformations                     │      │
│  │  Bronze → Silver → Gold                              │      │
│  └─────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ Read/Write
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                           │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              PostgreSQL Database                     │      │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │      │
│  │  │   Raw      │  │  Staging   │  │ Analytics  │    │      │
│  │  │  (Bronze)  │→ │  (Silver)  │→ │  (Gold)    │    │      │
│  │  └────────────┘  └────────────┘  └────────────┘    │      │
│  └─────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ Source data
                            ▼
                   ┌──────────────────┐
                   │   MIMIC-IV CSV   │
                   │   (15GB, ICU)    │
                   └──────────────────┘
```

### 1.2 Component Interaction Flow

**End-to-End Flow for Prediction:**

```
1. User inputs patient data in Streamlit UI
2. UI sends POST request to FastAPI /predict/sepsis
3. FastAPI checks Redis cache for prediction
4. If cache miss:
   a. Load LightGBM model from MLflow registry
   b. Extract features from PostgreSQL (analytics.features_sepsis_6h)
   c. Run model inference
   d. Calculate SHAP explanation
   e. Cache result in Redis
5. Return prediction + explanation to UI
6. UI displays risk score + SHAP waterfall plot
```

---

## 2. DATA ARCHITECTURE

### 2.1 Medallion Architecture Design

**Philosophy:** Layered data transformation (Bronze → Silver → Gold)

```
┌─────────────────────────────────────────────────────────────────┐
│                         BRONZE LAYER                             │
│                        (Raw, Immutable)                          │
├─────────────────────────────────────────────────────────────────┤
│  Schema: raw                                                     │
│  Purpose: Exact copy of source data                             │
│  Transformations: None                                           │
│                                                                  │
│  Tables:                                                         │
│  ├─ raw.icustays          (73K rows)                           │
│  ├─ raw.chartevents       (200M+ rows)                         │
│  ├─ raw.labevents         (100M+ rows)                         │
│  ├─ raw.inputevents       (50M rows)                           │
│  ├─ raw.outputevents      (30M rows)                           │
│  └─ raw.procedureevents   (10M rows)                           │
│                                                                  │
│  Data Quality: As-is from source                                │
│  Retention: Permanent                                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ dbt run (staging models)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SILVER LAYER                              │
│                   (Cleaned, Standardized)                        │
├─────────────────────────────────────────────────────────────────┤
│  Schema: staging                                                 │
│  Purpose: Data cleaning, type casting, deduplication            │
│                                                                  │
│  Transformations:                                                │
│  ├─ Type casting (string → numeric, timestamp)                 │
│  ├─ Deduplication (ROW_NUMBER() window functions)              │
│  ├─ Outlier removal (vitals within physiological ranges)       │
│  ├─ Unit conversion (Fahrenheit → Celsius)                     │
│  └─ Null handling (explicit NULL vs missing)                    │
│                                                                  │
│  Tables:                                                         │
│  ├─ staging.stg_icustays                                        │
│  ├─ staging.stg_chartevents                                     │
│  ├─ staging.stg_labevents                                       │
│  ├─ staging.stg_patients                                        │
│  └─ staging.stg_diagnoses                                       │
│                                                                  │
│  Data Quality Tests (dbt):                                       │
│  ├─ not_null: subject_id, hadm_id, stay_id                     │
│  ├─ unique: stay_id                                             │
│  ├─ relationships: referential integrity                        │
│  └─ accepted_values: gender in ('M', 'F')                       │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ dbt run (mart models)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GOLD LAYER                               │
│                   (Star Schema, Analytics)                       │
├─────────────────────────────────────────────────────────────────┤
│  Schema: analytics                                               │
│  Purpose: Business-ready data, optimized for queries            │
│                                                                  │
│  Star Schema:                                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              FACT TABLES                              │      │
│  ├──────────────────────────────────────────────────────┤      │
│  │  fact_icu_stays                                       │      │
│  │  ├─ stay_id (PK)                                     │      │
│  │  ├─ patient_key (FK → dim_patients)                  │      │
│  │  ├─ admission_date_key (FK → dim_time)               │      │
│  │  ├─ diagnosis_key (FK → dim_diagnoses)               │      │
│  │  ├─ length_of_stay_hours                             │      │
│  │  ├─ discharge_disposition                             │      │
│  │  └─ mortality_flag                                    │      │
│  │                                                        │      │
│  │  fact_vitals_hourly                                   │      │
│  │  ├─ stay_id (FK)                                     │      │
│  │  ├─ hour_key (FK → dim_time)                         │      │
│  │  ├─ heart_rate_mean, heart_rate_min, heart_rate_max │      │
│  │  ├─ blood_pressure_systolic_mean                     │      │
│  │  └─ ... (aggregated vitals)                          │      │
│  │                                                        │      │
│  │  fact_labs_daily                                      │      │
│  │  ├─ stay_id (FK)                                     │      │
│  │  ├─ date_key (FK → dim_time)                         │      │
│  │  ├─ wbc_latest, wbc_mean                             │      │
│  │  ├─ lactate_latest                                    │      │
│  │  └─ ... (aggregated labs)                            │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │             DIMENSION TABLES                          │      │
│  ├──────────────────────────────────────────────────────┤      │
│  │  dim_patients                                         │      │
│  │  ├─ patient_key (PK)                                 │      │
│  │  ├─ subject_id (natural key)                         │      │
│  │  ├─ age                                               │      │
│  │  ├─ gender                                            │      │
│  │  └─ ethnicity                                         │      │
│  │                                                        │      │
│  │  dim_time                                             │      │
│  │  ├─ date_key (PK)                                    │      │
│  │  ├─ date                                              │      │
│  │  ├─ year, month, day, hour, day_of_week             │      │
│  │  └─ is_weekend, is_holiday                           │      │
│  │                                                        │      │
│  │  dim_diagnoses                                        │      │
│  │  ├─ diagnosis_key (PK)                               │      │
│  │  ├─ icd10_code                                        │      │
│  │  ├─ diagnosis_description                             │      │
│  │  └─ diagnosis_category                                │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │             FEATURE TABLES                            │      │
│  ├──────────────────────────────────────────────────────┤      │
│  │  features_sepsis_6h                                   │      │
│  │  ├─ stay_id (PK)                                     │      │
│  │  ├─ feature_extraction_time                          │      │
│  │  ├─ Demographics (3): age, gender, bmi               │      │
│  │  ├─ Vitals (5): hr, sbp, dbp, temp, rr              │      │
│  │  ├─ Labs (20): wbc, lactate, creatinine, ...        │      │
│  │  ├─ SOFA (6): respiratory_sofa, ...                  │      │
│  │  ├─ Trends (6): lactate_trend_12h, ...              │      │
│  │  ├─ Time (2): hour_of_admission, los_so_far         │      │
│  │  └─ target (label): sepsis_onset_within_6h          │      │
│  │                                                        │      │
│  │  features_mortality_24h                               │      │
│  │  ├─ stay_id (PK)                                     │      │
│  │  ├─ (65 features total)                              │      │
│  │  └─ target: hospital_expire_flag                     │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Lineage & Dependencies

**dbt DAG:**
```
raw.icustays
    ↓
staging.stg_icustays
    ↓
    ├─→ analytics.dim_patients
    ├─→ analytics.fact_icu_stays
    └─→ analytics.features_sepsis_6h
    
raw.chartevents
    ↓
staging.stg_chartevents
    ↓
    ├─→ analytics.fact_vitals_hourly
    └─→ analytics.features_sepsis_6h (vitals)
    
raw.labevents
    ↓
staging.stg_labevents
    ↓
    ├─→ analytics.fact_labs_daily
    └─→ analytics.features_sepsis_6h (labs)
```

**Critical Path:**
1. Raw data must be loaded first
2. Staging models depend on raw tables
3. Fact/dimension tables depend on staging
4. Feature tables depend on fact/dimension tables
5. Models train on feature tables

---

## 3. ML MODEL ARCHITECTURE

### 3.1 Model Pipeline Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     MODEL TRAINING PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Data Extraction                                             │
│     ├─ Query: SELECT * FROM analytics.features_sepsis_6h       │
│     └─ Output: DataFrame (20K rows × 42 features)              │
│                                                                  │
│  2. Train/Val/Test Split                                        │
│     ├─ Stratified split (maintain class balance)               │
│     ├─ Train: 70% (14K samples)                                │
│     ├─ Val: 15% (3K samples)                                   │
│     └─ Test: 15% (3K samples)                                  │
│                                                                  │
│  3. Preprocessing                                                │
│     ├─ Handle missing values (KNN imputation)                  │
│     ├─ Scale features (StandardScaler)                         │
│     ├─ Handle class imbalance (SMOTE on training set only)     │
│     └─ Save preprocessor: preprocessing.pkl                     │
│                                                                  │
│  4. Model Training (LightGBM)                                   │
│     ├─ Hyperparameters from config                             │
│     ├─ 5-fold cross-validation on training set                │
│     ├─ Early stopping on validation set                        │
│     └─ Save model: model.pkl                                    │
│                                                                  │
│  5. Model Evaluation                                             │
│     ├─ Metrics: AUROC, Sensitivity, Specificity, PPV, NPV      │
│     ├─ Confusion matrix                                         │
│     ├─ Calibration curve                                        │
│     └─ Performance on test set (not touched until now)          │
│                                                                  │
│  6. SHAP Explainer                                              │
│     ├─ TreeExplainer for LightGBM                              │
│     ├─ Calculate SHAP values for test set                      │
│     └─ Save explainer: shap_explainer.pkl                       │
│                                                                  │
│  7. MLflow Logging                                              │
│     ├─ Log parameters (hyperparameters)                        │
│     ├─ Log metrics (AUROC, sensitivity, etc.)                  │
│     ├─ Log artifacts (model, preprocessor, explainer)          │
│     ├─ Log feature names and importance                        │
│     └─ Register model: sepsis_lightgbm_v1                      │
│                                                                  │
│  8. Model Card Generation                                        │
│     └─ Automated template with performance metrics              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Model Architecture Details

#### Sepsis Model (LightGBM)

**Architecture:**
```
Input Features (42)
    ↓
Gradient Boosting Decision Trees
    ├─ num_leaves: 31
    ├─ max_depth: 6
    ├─ n_estimators: 500
    └─ learning_rate: 0.05
    ↓
Tree Ensemble (500 trees)
    ↓
Logistic Link Function
    ↓
Output: Probability [0, 1]
```

**Training Strategy:**
- **Loss Function:** Binary cross-entropy with class weights
- **Regularization:** L1 (lambda_l1=0.1), L2 (lambda_l2=0.1)
- **Early Stopping:** Patience 50 rounds on validation AUROC
- **Feature Importance:** Gain-based (built-in LightGBM)

**Inference Pipeline:**
```python
# Load model from MLflow
model_uri = "models:/sepsis_lightgbm_v1/Production"
model = mlflow.pyfunc.load_model(model_uri)

# Preprocessing
features_raw = extract_features(patient_id)
features_processed = preprocessor.transform(features_raw)

# Predict
probability = model.predict_proba(features_processed)[:, 1]

# Explain
shap_values = shap_explainer.shap_values(features_processed)

# Return
return {
    'probability': probability,
    'risk_level': categorize_risk(probability),
    'shap_values': shap_values
}
```

---

## 4. API ARCHITECTURE

### 4.1 FastAPI Application Structure

```
api/
├── main.py                    # FastAPI app initialization
├── routers/
│   ├── predictions.py         # /predict/* endpoints
│   ├── explanations.py        # /explain/* endpoints
│   └── health.py              # /health endpoint
├── models/
│   ├── schemas.py             # Pydantic request/response models
│   └── ml_models.py           # Model loading logic
├── services/
│   ├── prediction_service.py  # Business logic for predictions
│   ├── cache_service.py       # Redis caching logic
│   └── feature_service.py     # Feature extraction from DB
├── core/
│   ├── config.py              # Settings (env vars)
│   ├── dependencies.py        # Dependency injection
│   └── exceptions.py          # Custom exceptions
└── utils/
    ├── logging.py             # Structured logging
    └── validators.py          # Input validators
```

### 4.2 Request/Response Flow

**Prediction Request Flow:**

```
1. Client sends POST /predict/sepsis
   {
     "patient_id": "P-100234",
     "features": { ... }
   }
   
2. FastAPI validates request (Pydantic)
   ├─ Check all required fields present
   ├─ Validate types (age: int, lactate: float)
   ├─ Validate ranges (age: 18-120, HR: 0-300)
   └─ If invalid → 400 Bad Request
   
3. PredictionService.predict_sepsis()
   │
   ├─ Check Redis cache
   │  └─ Key: md5(model_version + feature_hash)
   │  └─ If hit → return cached prediction
   │
   ├─ If cache miss:
   │  ├─ Load model from MLflow (cached in memory)
   │  ├─ Extract/validate features
   │  ├─ Run preprocessing
   │  ├─ Run model inference
   │  ├─ Calculate SHAP explanation
   │  ├─ Cache result (TTL: 1 hour)
   │  └─ Return prediction
   │
   └─ Log metrics (latency, cache hit/miss)
   
4. FastAPI returns response
   {
     "prediction": {
       "risk_score": 0.78,
       "risk_level": "HIGH"
     },
     "explanation": { ... },
     "metadata": {
       "model_version": "sepsis_lightgbm_v1",
       "prediction_time_ms": 45
     }
   }
```

### 4.3 API Schemas (Pydantic)

```python
# api/models/schemas.py

from pydantic import BaseModel, Field, validator

class SepsisFeatures(BaseModel):
    """Input features for sepsis prediction."""
    
    # Demographics
    age: int = Field(..., ge=18, le=120, description="Patient age in years")
    gender: str = Field(..., pattern="^(M|F)$", description="Gender (M/F)")
    bmi: float = Field(..., ge=10, le=60, description="Body mass index")
    
    # Vitals
    heart_rate: float = Field(..., ge=0, le=300, description="Heart rate (bpm)")
    sbp: float = Field(..., ge=40, le=250, description="Systolic BP (mmHg)")
    dbp: float = Field(..., ge=20, le=150, description="Diastolic BP (mmHg)")
    temperature: float = Field(..., ge=32, le=42, description="Temperature (°C)")
    respiratory_rate: float = Field(..., ge=0, le=60, description="Resp rate (bpm)")
    
    # Labs (20 fields)
    wbc: float = Field(..., ge=0, le=100, description="WBC count")
    lactate: float = Field(..., ge=0, le=30, description="Lactate (mmol/L)")
    # ... (remaining lab values)
    
    # SOFA scores (6 fields)
    respiratory_sofa: int = Field(..., ge=0, le=4)
    cardiovascular_sofa: int = Field(..., ge=0, le=4)
    # ... (remaining SOFA components)
    
    # Temporal trends (6 fields)
    lactate_trend_12h: float = Field(..., description="Lactate change (mmol/L)")
    # ... (remaining trends)
    
    # Time features (2 fields)
    hour_of_admission: int = Field(..., ge=0, le=23)
    icu_los_so_far: float = Field(..., ge=0, description="Hours in ICU")
    
    @validator('lactate')
    def lactate_range(cls, v):
        if v > 10:
            raise ValueError('Lactate >10 mmol/L is critically high, please verify')
        return v

class SepsisPrediction(BaseModel):
    """Sepsis prediction response."""
    
    class PredictionDetail(BaseModel):
        risk_score: float = Field(..., ge=0, le=1, description="Probability [0-1]")
        risk_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
        recommendation: str = Field(..., description="Clinical recommendation")
    
    class Explanation(BaseModel):
        class FeatureContribution(BaseModel):
            feature: str
            importance: float
            value: float
            effect: str  # e.g., "+0.15" (increases risk by 0.15)
        
        top_features: List[FeatureContribution] = Field(..., max_items=10)
        shap_plot_base64: Optional[str] = None
    
    class Metadata(BaseModel):
        model_version: str
        prediction_time_ms: float
        cached: bool
        timestamp: datetime
    
    prediction: PredictionDetail
    explanation: Explanation
    metadata: Metadata
```

---

## 5. AGENT ARCHITECTURE

### 5.1 Agent System Design

**See `agents/AGENT_ARCHITECTURE.md` for full details.**

**High-Level Agent Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                  WORKFLOW ORCHESTRATOR                           │
│  (Top-level coordinator for entire ML lifecycle)                │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ Delegates to Crews
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          CREWS                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Data Pipeline│  │  ML Dev Crew │  │ Deployment   │         │
│  │    Crew      │  │              │  │    Crew      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │ Assigns tasks    │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INDIVIDUAL AGENTS                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ Data Ingestion │  │ Feature Eng    │  │ API Development│   │
│  │    Agent       │  │    Agent       │  │    Agent       │   │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘   │
│           │                    │                    │            │
│           │ Uses tools         │                    │            │
│           ▼                    ▼                    ▼            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                     TOOLS LAYER                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │ Postgres │  │   dbt    │  │  MLflow  │            │    │
│  │  │  Tool    │  │  Tool    │  │   Tool   │            │    │
│  │  └──────────┘  └──────────┘  └──────────┘            │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Agent Steering & Hooks

**Steering Mechanisms:**
1. **Task Dependencies:** Agents wait for upstream tasks to complete
2. **Validation Gates:** Agents check preconditions before execution
3. **Failure Policies:** Retry, skip, or abort on failure
4. **Decision Engine:** Workflow Orchestrator makes intelligent routing decisions

**Agent Hooks (Event-Driven):**
- `on_new_data_ingested` → Trigger ETL DAG
- `on_feature_table_updated` → Trigger model retraining
- `on_model_registered` → Deploy to staging
- `on_model_approved` → Promote to production
- `on_drift_detected` → Alert + initiate retraining

**See `agents/AGENT_STEERING.md` for detailed policies.**

---

## 6. UI/UX ARCHITECTURE

### 6.1 Streamlit Application Structure

```
apps/
├── streamlit_app.py           # Main entry point
├── pages/
│   ├── 01_dashboard.py        # Overview dashboard
│   ├── 02_patients.py         # Patient management
│   ├── 03_predictions.py      # Prediction interface
│   └── 04_model_perf.py       # Model performance
├── components/
│   ├── patient_table.py       # Reusable table component
│   ├── risk_gauge.py          # Risk score visualization
│   ├── shap_plot.py           # SHAP explanation charts
│   └── metric_card.py         # Metric display card
├── services/
│   └── api_client.py          # FastAPI client wrapper
└── utils/
    └── formatters.py          # Data formatting utilities
```

### 6.2 UI Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Action: "Predict Sepsis for Patient P-100234"            │
│        │                                                         │
│        ▼                                                         │
│  ┌──────────────────────────────────────────────────┐          │
│  │  pages/03_predictions.py                          │          │
│  │  ├─ Render input form (42 fields)               │          │
│  │  ├─ Validate inputs client-side                  │          │
│  │  └─ On submit → call api_client.predict_sepsis() │          │
│  └──────────────────┬───────────────────────────────┘          │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────┐          │
│  │  services/api_client.py                           │          │
│  │  def predict_sepsis(features):                    │          │
│  │      response = requests.post(                    │          │
│  │          "http://localhost:8000/predict/sepsis",  │          │
│  │          json=features                             │          │
│  │      )                                             │          │
│  │      return response.json()                        │          │
│  └──────────────────┬───────────────────────────────┘          │
└────────────────────┼────────────────────────────────────────────┘
                      │
                      │ HTTP POST
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│  POST /predict/sepsis                                           │
│  └─→ Return prediction JSON                                     │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   │ Response
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI                                │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Display Results                                  │          │
│  │  ├─ Risk Score: 78% (HIGH)                       │          │
│  │  ├─ components/risk_gauge.py (circular gauge)    │          │
│  │  ├─ Recommendation: "Consider sepsis protocol"   │          │
│  │  └─ SHAP Plot: components/shap_plot.py           │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 UI Component Specifications

**See `ui/UI_COMPONENTS.md` for detailed component designs.**

**Key Components:**
- `RiskGauge`: Circular gauge showing risk score (0-100%)
- `PatientTable`: Sortable, filterable table of ICU patients
- `ShapWaterfallPlot`: SHAP waterfall chart for feature contributions
- `MetricCard`: Card displaying key metrics (AUROC, Sensitivity, etc.)
- `PredictionForm`: Auto-generated form from Pydantic schema

---

## 7. INTEGRATION PATTERNS

### 7.1 Database ↔ dbt ↔ Airflow

```python
# airflow/dags/etl_pipeline_dag.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@example.com'],
    'retries': 3
}

with DAG(
    'etl_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2025, 1, 1),
    catchup=False
) as dag:
    
    # Task 1: Check data freshness
    check_data_freshness = PostgresOperator(
        task_id='check_data_freshness',
        postgres_conn_id='mimic_postgres',
        sql='''
            SELECT MAX(charttime) AS latest_data
            FROM raw.chartevents;
        '''
    )
    
    # Task 2: Run dbt staging models
    dbt_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command='cd /opt/dbt_project && dbt run --models staging.*'
    )
    
    # Task 3: Run dbt tests on staging
    dbt_test_staging = BashOperator(
        task_id='dbt_test_staging',
        bash_command='cd /opt/dbt_project && dbt test --models staging.*'
    )
    
    # Task 4: Run dbt marts
    dbt_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /opt/dbt_project && dbt run --models marts.*'
    )
    
    # Task 5: Run dbt tests on marts
    dbt_test_marts = BashOperator(
        task_id='dbt_test_marts',
        bash_command='cd /opt/dbt_project && dbt test --models marts.*'
    )
    
    # Task 6: Generate dbt docs
    dbt_docs = BashOperator(
        task_id='dbt_generate_docs',
        bash_command='cd /opt/dbt_project && dbt docs generate'
    )
    
    # Dependencies
    check_data_freshness >> dbt_staging >> dbt_test_staging >> dbt_marts >> dbt_test_marts >> dbt_docs
```

### 7.2 MLflow ↔ FastAPI Integration

```python
# api/models/ml_models.py

import mlflow.pyfunc
from functools import lru_cache

class ModelLoader:
    """Singleton pattern for model loading."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._models = {}
        return cls._instance
    
    @lru_cache(maxsize=10)
    def load_model(self, model_name: str, stage: str = "Production"):
        """
        Load model from MLflow registry.
        Uses LRU cache to avoid reloading on every request.
        """
        if model_name not in self._models:
            model_uri = f"models:/{model_name}/{stage}"
            self._models[model_name] = mlflow.pyfunc.load_model(model_uri)
        
        return self._models[model_name]

# Usage in FastAPI endpoint
from api.models.ml_models import ModelLoader

@app.post("/predict/sepsis")
async def predict_sepsis(features: SepsisFeatures):
    model_loader = ModelLoader()
    model = model_loader.load_model("sepsis_lightgbm_v1")
    
    # Convert Pydantic model to DataFrame
    features_df = pd.DataFrame([features.dict()])
    
    # Predict
    prediction = model.predict(features_df)
    
    return {"risk_score": float(prediction[0])}
```

### 7.3 Agent ↔ System Integration

```python
# agents/crews/data_pipeline_crew.py

from crewai import Crew, Task
from agents.roles.data_engineer import DataIngestionAgent

class DataPipelineCrew:
    def __init__(self):
        self.agents = self._init_agents()
        self.tasks = self._init_tasks()
    
    def _init_agents(self):
        return {
            'ingestion': DataIngestionAgent(
                db_connection=os.getenv('DATABASE_URL')
            )
        }
    
    def _init_tasks(self):
        return [
            Task(
                description="Ingest MIMIC-IV icustays table",
                agent=self.agents['ingestion'],
                expected_output="73K rows loaded into raw.icustays",
                context={
                    'source_file': '/data/mimic-iv/icu/icustays.csv',
                    'target_table': 'raw.icustays'
                }
            )
        ]
    
    def kickoff(self):
        """Execute crew workflow."""
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process='sequential'
        )
        return crew.kickoff()

# Integration with Airflow
from agents.crews.data_pipeline_crew import DataPipelineCrew

def run_data_pipeline_crew():
    crew = DataPipelineCrew()
    result = crew.kickoff()
    return result

# airflow/dags/agent_orchestrated_pipeline.py
agent_task = PythonOperator(
    task_id='run_agent_crew',
    python_callable=run_data_pipeline_crew
)
```

---

## 8. DEPLOYMENT ARCHITECTURE

### 8.1 Docker Compose Services

```yaml
# docker-compose.yml

version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: mimic_iv
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
  
  airflow-init:
    image: apache/airflow:2.8.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    command: >
      bash -c "
        airflow db init &&
        airflow users create \
          --username admin \
          --password admin \
          --firstname Admin \
          --lastname User \
          --role Admin \
          --email admin@example.com
      "
    depends_on:
      postgres:
        condition: service_healthy
  
  airflow-webserver:
    image: apache/airflow:2.8.0
    depends_on:
      - airflow-init
      - postgres
    ports:
      - "8080:8080"
    command: airflow webserver
  
  airflow-scheduler:
    image: apache/airflow:2.8.0
    depends_on:
      - airflow-init
      - postgres
    command: airflow scheduler
  
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.10.0
    ports:
      - "5000:5000"
    command: >
      mlflow server 
      --backend-store-uri postgresql://mlflow:mlflow@postgres/mlflow
      --default-artifact-root /mlflow/artifacts
      --host 0.0.0.0
    depends_on:
      postgres:
        condition: service_healthy
  
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/mimic_iv
      - REDIS_URL=redis://redis:6379
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      - postgres
      - redis
      - mlflow
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
  
  streamlit:
    build: ./apps
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

---

## 9. CONSISTENCY CHECKPOINTS

### 9.1 Cross-Component Consistency

| Component | Reference | Must Align With |
|-----------|-----------|-----------------|
| dbt feature table schemas | `dbt_project/models/marts/` | `api/models/schemas.py` (Pydantic) |
| Model feature names | `models/*/feature_names.json` | dbt SQL SELECT columns |
| API endpoint paths | `api/routers/*.py` | `apps/services/api_client.py` |
| Agent task names | `agents/config/tasks.yaml` | `agents/crews/*.py` (Task creation) |
| Database table names | `dbt_project/models/` | Agent tool SQL queries |

### 9.2 Validation Scripts

```bash
# scripts/validate_consistency.sh

#!/bin/bash

echo "Running consistency checks..."

# Check 1: dbt feature columns match Pydantic schema
python scripts/check_feature_schema_alignment.py

# Check 2: API endpoints match UI client calls
python scripts/check_api_ui_alignment.py

# Check 3: Agent configs valid YAML
python scripts/validate_agent_configs.py

# Check 4: Model artifacts exist in expected paths
python scripts/check_model_artifacts.py

echo "Consistency checks complete!"
```

---

**Document Version:** 1.0  
**Status:** ✅ APPROVED - Implementation Ready  
**Next Steps:** See TASK_BREAKDOWN.md for work items
