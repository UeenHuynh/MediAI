# UI ↔ Backend ↔ Data Wiring Design
**Healthcare ML Platform - Complete Integration Map**

**Version:** 1.0  
**Status:** Design Approved  
**Last Updated:** 2025-01-20

---

## DOCUMENT PURPOSE

This document provides **complete wiring specification** for how the UI, backend API, and data layer integrate. It ensures every component knows exactly where to get data and how to communicate.

**Related Documents:**
- Architecture: `ARCHITECTURE_DESIGN.md`
- Requirements: `REQUIREMENTS.md`
- API Spec: `docs/API_SPEC.md`

---

## 1. SYSTEM INTEGRATION OVERVIEW

### 1.1 Three-Tier Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      PRESENTATION TIER                          │
│                      (Streamlit UI)                             │
│  - User interactions                                            │
│  - Data visualization                                           │
│  - Form inputs                                                  │
└────────────────┬───────────────────────────────────────────────┘
                 │ HTTP REST
                 │ (JSON payloads)
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                      APPLICATION TIER                           │
│                      (FastAPI Backend)                          │
│  - Business logic                                               │
│  - Model serving                                                │
│  - Caching                                                      │
│  - Authentication                                               │
└────────────────┬───────────────────────────────────────────────┘
                 │ SQL / Redis
                 │ (Database queries, cache operations)
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                         DATA TIER                               │
│  ┌─────────────────┐  ┌─────────────┐  ┌────────────────┐    │
│  │   PostgreSQL    │  │    Redis    │  │     MLflow     │    │
│  │  (Features,     │  │   (Cache)   │  │  (Models)      │    │
│  │   Predictions)  │  │             │  │                │    │
│  └─────────────────┘  └─────────────┘  └────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. COMPLETE API SPECIFICATION

### 2.1 All Endpoints

#### Health & Status
```
GET /health
GET /metrics
```

#### Patients
```
GET    /patients              # List all patients
GET    /patients/{stay_id}    # Get patient details
POST   /patients/search       # Search patients
```

#### Predictions
```
POST   /predict/sepsis        # Predict sepsis risk
POST   /predict/mortality     # Predict mortality risk
GET    /predictions/{stay_id} # Get past predictions
```

#### Explanations
```
POST   /explain/shap          # Get SHAP explanation
GET    /explain/features      # Get feature importance
```

#### Model Management
```
GET    /models                # List available models
GET    /models/{model_name}   # Get model info
POST   /models/reload         # Reload model (admin)
```

---

### 2.2 Detailed Endpoint Specs

#### POST /predict/sepsis

**Request:**
```json
{
  "patient_id": "P-100234",
  "features": {
    "age": 65,
    "gender": "M",
    "bmi": 28.5,
    "heart_rate": 110.0,
    "sbp": 90.0,
    "dbp": 60.0,
    "temperature": 38.5,
    "respiratory_rate": 24.0,
    "spo2": 92.0,
    "wbc": 15.2,
    "lactate": 3.5,
    "creatinine": 1.8,
    "bilirubin": 2.1,
    "platelets": 120.0,
    "inr": 1.5,
    "glucose": 180.0,
    "potassium": 4.2,
    "sodium": 138.0,
    "chloride": 102.0,
    "bicarbonate": 22.0,
    "bun": 28.0,
    "hemoglobin": 11.5,
    "hematocrit": 34.0,
    "rdw": 14.5,
    "mcv": 88.0,
    "mch": 30.0,
    "mchc": 34.0,
    "bands": 12.0,
    "respiratory_sofa": 2,
    "cardiovascular_sofa": 1,
    "hepatic_sofa": 1,
    "coagulation_sofa": 1,
    "renal_sofa": 1,
    "neurological_sofa": 0,
    "lactate_trend_12h": 0.8,
    "hr_trend_6h": 10.0,
    "sbp_trend_6h": -15.0,
    "temp_trend_6h": 1.2,
    "wbc_trend_24h": 3.5,
    "lactate_trend_6h": 0.5,
    "hour_of_admission": 14,
    "icu_los_so_far": 18.5
  }
}
```

**Response (200 OK):**
```json
{
  "prediction": {
    "risk_score": 0.78,
    "risk_level": "HIGH",
    "confidence": 0.92,
    "recommendation": "Consider initiating sepsis protocol. Monitor lactate and hemodynamics closely."
  },
  "explanation": {
    "top_features": [
      {
        "feature": "lactate",
        "importance": 0.23,
        "value": 3.5,
        "effect": "+0.18",
        "normal_range": "0.5-2.2 mmol/L",
        "interpretation": "Elevated lactate indicates tissue hypoperfusion"
      },
      {
        "feature": "heart_rate",
        "importance": 0.18,
        "value": 110.0,
        "effect": "+0.14",
        "normal_range": "60-100 bpm",
        "interpretation": "Tachycardia suggests systemic response"
      },
      {
        "feature": "wbc",
        "importance": 0.15,
        "value": 15.2,
        "effect": "+0.12",
        "normal_range": "4-11 K/μL",
        "interpretation": "Leukocytosis indicates infection/inflammation"
      },
      {
        "feature": "temperature",
        "importance": 0.12,
        "value": 38.5,
        "effect": "+0.09",
        "normal_range": "36.5-37.5 °C",
        "interpretation": "Fever suggests infectious process"
      },
      {
        "feature": "respiratory_sofa",
        "importance": 0.10,
        "value": 2,
        "effect": "+0.08",
        "normal_range": "0",
        "interpretation": "Respiratory dysfunction present"
      }
    ],
    "shap_waterfall_plot": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..." 
  },
  "metadata": {
    "model_name": "sepsis_lightgbm_v1",
    "model_version": "2",
    "prediction_time_ms": 45,
    "cached": false,
    "timestamp": "2025-01-20T10:30:15.234Z",
    "request_id": "req_abc123xyz"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "detail": [
    {
      "loc": ["body", "features", "lactate"],
      "msg": "ensure this value is less than or equal to 30",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Model inference failed",
  "error_id": "err_xyz789",
  "timestamp": "2025-01-20T10:30:15.234Z"
}
```

---

#### GET /patients

**Request:**
```
GET /patients?limit=100&offset=0&sort_by=admission_date&order=desc&risk_filter=high
```

**Query Parameters:**
- `limit`: int (default: 100, max: 1000)
- `offset`: int (default: 0)
- `sort_by`: string (admission_date, sepsis_risk, mortality_risk, age)
- `order`: string (asc, desc)
- `risk_filter`: string (all, low, medium, high, critical)

**Response (200 OK):**
```json
{
  "patients": [
    {
      "stay_id": "P-100234",
      "patient_key": 12345,
      "age": 65,
      "gender": "M",
      "admission_date": "2025-01-19T08:30:00Z",
      "discharge_date": null,
      "diagnosis": "Pneumonia",
      "sepsis_risk": 0.89,
      "sepsis_level": "HIGH",
      "mortality_risk": 0.45,
      "mortality_level": "MEDIUM",
      "last_updated": "2025-01-20T10:00:00Z"
    },
    {
      "stay_id": "P-100235",
      "patient_key": 12346,
      "age": 72,
      "gender": "F",
      "admission_date": "2025-01-18T14:15:00Z",
      "discharge_date": null,
      "diagnosis": "Septic shock",
      "sepsis_risk": 0.95,
      "sepsis_level": "CRITICAL",
      "mortality_risk": 0.78,
      "mortality_level": "HIGH",
      "last_updated": "2025-01-20T10:00:00Z"
    }
  ],
  "total": 142,
  "page": 1,
  "per_page": 100,
  "pages": 2
}
```

---

#### GET /patients/{stay_id}

**Request:**
```
GET /patients/P-100234
```

**Response (200 OK):**
```json
{
  "stay_id": "P-100234",
  "patient_key": 12345,
  "demographics": {
    "age": 65,
    "gender": "M",
    "bmi": 28.5,
    "ethnicity": "Caucasian"
  },
  "admission": {
    "admission_date": "2025-01-19T08:30:00Z",
    "admission_type": "Emergency",
    "admission_location": "Emergency Department"
  },
  "diagnosis": {
    "primary": "Pneumonia",
    "secondary": ["Diabetes Type 2", "Hypertension"],
    "icd10_codes": ["J18.9", "E11.9", "I10"]
  },
  "current_vitals": {
    "heart_rate": 110.0,
    "sbp": 90.0,
    "dbp": 60.0,
    "temperature": 38.5,
    "respiratory_rate": 24.0,
    "spo2": 92.0,
    "measured_at": "2025-01-20T10:25:00Z"
  },
  "latest_labs": {
    "wbc": 15.2,
    "lactate": 3.5,
    "creatinine": 1.8,
    "measured_at": "2025-01-20T09:00:00Z"
  },
  "predictions": {
    "sepsis": {
      "risk_score": 0.89,
      "risk_level": "HIGH",
      "predicted_at": "2025-01-20T10:00:00Z",
      "trend": "+0.15 (last 6h)"
    },
    "mortality": {
      "risk_score": 0.45,
      "risk_level": "MEDIUM",
      "predicted_at": "2025-01-20T10:00:00Z",
      "trend": "+0.08 (last 24h)"
    }
  },
  "icu_stay": {
    "length_of_stay_hours": 18.5,
    "vent_status": "Mechanical ventilation",
    "vasopressor_status": "Norepinephrine 0.1 mcg/kg/min"
  }
}
```

---

## 3. DATA FLOW: PREDICTION REQUEST (DETAILED)

### 3.1 Complete Sequence Diagram

```
User          Streamlit         FastAPI         Redis         PostgreSQL      MLflow
  │               │                │              │                │             │
  │─────(1)────>│                │              │                │             │
  │ Click        │                │              │                │             │
  │ "Predict"    │                │              │                │             │
  │               │                │              │                │             │
  │               │─────(2)────>│              │                │             │
  │               │ POST          │              │                │             │
  │               │ /predict      │              │                │             │
  │               │ /sepsis       │              │                │             │
  │               │                │              │                │             │
  │               │                │─────(3)───>│                │             │
  │               │                │ Check cache │                │             │
  │               │                │              │                │             │
  │               │                │<────(4)────│                │             │
  │               │                │ Cache MISS  │                │             │
  │               │                │              │                │             │
  │               │                │──────────────────────(5)───>│             │
  │               │                │              │    Load model│             │
  │               │                │              │                │             │
  │               │                │<─────────────────────(6)────│             │
  │               │                │              │  Model loaded│             │
  │               │                │              │                │             │
  │               │                │─────(7)───────────────────────────>│
  │               │                │              │                │ Get features│
  │               │                │              │                │             │
  │               │                │<────(8)───────────────────────────│
  │               │                │              │     Features data   │
  │               │                │              │                │             │
  │               │                │ [Preprocessing]              │             │
  │               │                │ [Inference]                  │             │
  │               │                │ [SHAP calc]                  │             │
  │               │                │              │                │             │
  │               │                │─────(9)───>│                │             │
  │               │                │ Store cache │                │             │
  │               │                │              │                │             │
  │               │                │─────(10)────────────────>│             │
  │               │                │              │ Store prediction  │
  │               │                │              │                │             │
  │               │<────(11)───────│              │                │             │
  │               │ JSON response  │              │                │             │
  │               │                │              │                │             │
  │<────(12)──│                │              │                │             │
  │ Display      │                │              │                │             │
  │ results      │                │              │                │             │
```

**Timing Breakdown:**
1. User interaction: 0ms
2. API request (network): 5-10ms
3. Cache check: 2-5ms
4. Cache miss: 0ms
5. Model load (first time): 100-200ms, (subsequent): 0ms (cached)
6. Model loaded: 0ms
7. Feature extraction: 10-20ms
8. Features retrieved: 0ms
9. Preprocessing + Inference: 30-50ms
10. SHAP calculation: 50-100ms
11. Cache storage: 5ms
12. Store prediction: 10-20ms
13. Return response: 5-10ms
14. UI rendering: 50-100ms

**Total end-to-end:** 150-250ms (p50), 200-400ms (p95)

---

## 4. DATABASE SCHEMA & MAPPINGS

### 4.1 Complete Schema Diagram

```sql
-- DIMENSION TABLES

CREATE TABLE analytics.dim_patients (
    patient_key SERIAL PRIMARY KEY,
    subject_id INTEGER UNIQUE NOT NULL,
    gender VARCHAR(1),
    anchor_age INTEGER,
    anchor_year INTEGER,
    dod TIMESTAMP
);

CREATE TABLE analytics.dim_time (
    date_key SERIAL PRIMARY KEY,
    date_actual DATE UNIQUE NOT NULL,
    day_of_week INTEGER,
    day_of_month INTEGER,
    day_of_year INTEGER,
    week_of_year INTEGER,
    month_number INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

CREATE TABLE analytics.dim_diagnoses (
    diagnosis_key SERIAL PRIMARY KEY,
    icd_code VARCHAR(10),
    icd_version INTEGER,
    diagnosis_description TEXT
);

-- FACT TABLES

CREATE TABLE analytics.fact_icu_stays (
    stay_id VARCHAR PRIMARY KEY,
    patient_key INTEGER REFERENCES analytics.dim_patients(patient_key),
    admission_date_key INTEGER REFERENCES analytics.dim_time(date_key),
    discharge_date_key INTEGER REFERENCES analytics.dim_time(date_key),
    diagnosis_key INTEGER REFERENCES analytics.dim_diagnoses(diagnosis_key),
    
    -- Stay details
    hadm_id INTEGER,
    intime TIMESTAMP,
    outtime TIMESTAMP,
    los_hours NUMERIC,
    
    -- Admission details
    admission_type VARCHAR(50),
    admission_location VARCHAR(50),
    discharge_location VARCHAR(50),
    
    -- ICU details
    first_careunit VARCHAR(50),
    last_careunit VARCHAR(50)
);

CREATE TABLE analytics.fact_vitals_hourly (
    vital_id SERIAL PRIMARY KEY,
    stay_id VARCHAR REFERENCES analytics.fact_icu_stays(stay_id),
    hour_key INTEGER REFERENCES analytics.dim_time(date_key),
    charttime TIMESTAMP,
    
    -- Vital signs
    heart_rate NUMERIC,
    sbp NUMERIC,
    dbp NUMERIC,
    mbp NUMERIC,
    temperature NUMERIC,
    respiratory_rate NUMERIC,
    spo2 NUMERIC,
    
    -- Derived
    shock_index NUMERIC,  -- HR / SBP
    pulse_pressure NUMERIC  -- SBP - DBP
);

CREATE TABLE analytics.fact_labs_daily (
    lab_id SERIAL PRIMARY KEY,
    stay_id VARCHAR REFERENCES analytics.fact_icu_stays(stay_id),
    date_key INTEGER REFERENCES analytics.dim_time(date_key),
    charttime TIMESTAMP,
    
    -- Hematology
    wbc NUMERIC,
    hemoglobin NUMERIC,
    hematocrit NUMERIC,
    platelets NUMERIC,
    
    -- Chemistry
    sodium NUMERIC,
    potassium NUMERIC,
    chloride NUMERIC,
    bicarbonate NUMERIC,
    bun NUMERIC,
    creatinine NUMERIC,
    glucose NUMERIC,
    
    -- Liver
    bilirubin NUMERIC,
    ast NUMERIC,
    alt NUMERIC,
    alp NUMERIC,
    
    -- Coagulation
    inr NUMERIC,
    pt NUMERIC,
    ptt NUMERIC,
    
    -- Other
    lactate NUMERIC,
    ph NUMERIC,
    pao2 NUMERIC,
    paco2 NUMERIC
);

-- FEATURE TABLES

CREATE TABLE analytics.features_sepsis_6h (
    stay_id VARCHAR PRIMARY KEY REFERENCES analytics.fact_icu_stays(stay_id),
    feature_computed_at TIMESTAMP DEFAULT NOW(),
    
    -- Demographics (3 features)
    age INTEGER,
    gender VARCHAR(1),
    bmi NUMERIC,
    
    -- Vitals (6 features)
    heart_rate NUMERIC,
    sbp NUMERIC,
    dbp NUMERIC,
    temperature NUMERIC,
    respiratory_rate NUMERIC,
    spo2 NUMERIC,
    
    -- Labs (20 features)
    wbc NUMERIC,
    hemoglobin NUMERIC,
    hematocrit NUMERIC,
    platelets NUMERIC,
    sodium NUMERIC,
    potassium NUMERIC,
    chloride NUMERIC,
    bicarbonate NUMERIC,
    bun NUMERIC,
    creatinine NUMERIC,
    glucose NUMERIC,
    bilirubin NUMERIC,
    lactate NUMERIC,
    inr NUMERIC,
    pt NUMERIC,
    rdw NUMERIC,
    mcv NUMERIC,
    mch NUMERIC,
    mchc NUMERIC,
    bands NUMERIC,
    
    -- SOFA scores (6 features)
    respiratory_sofa INTEGER,
    cardiovascular_sofa INTEGER,
    hepatic_sofa INTEGER,
    coagulation_sofa INTEGER,
    renal_sofa INTEGER,
    neurological_sofa INTEGER,
    
    -- Temporal trends (6 features)
    lactate_trend_12h NUMERIC,
    lactate_trend_6h NUMERIC,
    hr_trend_6h NUMERIC,
    sbp_trend_6h NUMERIC,
    temp_trend_6h NUMERIC,
    wbc_trend_24h NUMERIC,
    
    -- Time features (2 features)
    hour_of_admission INTEGER,
    icu_los_so_far NUMERIC,
    
    -- Target (NOT a feature - for training only)
    sepsis_onset_within_6h BOOLEAN
);

CREATE INDEX idx_features_sepsis_stay_id ON analytics.features_sepsis_6h(stay_id);
CREATE INDEX idx_features_sepsis_computed_at ON analytics.features_sepsis_6h(feature_computed_at);

-- PREDICTION TABLES

CREATE TABLE analytics.predictions_sepsis (
    prediction_id SERIAL PRIMARY KEY,
    stay_id VARCHAR REFERENCES analytics.fact_icu_stays(stay_id),
    predicted_at TIMESTAMP DEFAULT NOW(),
    
    -- Prediction
    risk_score NUMERIC(5,4) CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_level VARCHAR(10) CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    confidence NUMERIC(4,3),
    
    -- Model metadata
    model_name VARCHAR NOT NULL,
    model_version VARCHAR NOT NULL,
    
    -- Input features (stored as JSONB for flexibility)
    features_json JSONB NOT NULL,
    
    -- Explanation
    shap_values JSONB,
    top_features JSONB,
    
    -- Performance metadata
    prediction_time_ms INTEGER,
    cached BOOLEAN DEFAULT FALSE,
    request_id VARCHAR,
    
    -- Outcome tracking (filled in later)
    actual_outcome BOOLEAN,
    outcome_timestamp TIMESTAMP
);

CREATE INDEX idx_predictions_sepsis_stay_id ON analytics.predictions_sepsis(stay_id);
CREATE INDEX idx_predictions_sepsis_predicted_at ON analytics.predictions_sepsis(predicted_at DESC);
CREATE INDEX idx_predictions_sepsis_risk_level ON analytics.predictions_sepsis(risk_level);

-- Similar table for mortality predictions
CREATE TABLE analytics.predictions_mortality (
    -- Same structure as predictions_sepsis
    ...
);
```

### 4.2 Feature Table → API Schema Mapping

**Complete 1:1 Mapping:**

```python
# api/models/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class SepsisFeatures(BaseModel):
    """Exact mapping to analytics.features_sepsis_6h table."""
    
    # Demographics (3)
    age: int = Field(..., ge=18, le=120, description="Patient age in years")
    gender: str = Field(..., pattern="^(M|F)$", description="Patient gender")
    bmi: float = Field(..., ge=10, le=60, description="Body Mass Index")
    
    # Vitals (6)
    heart_rate: float = Field(..., ge=0, le=300, description="Heart rate (bpm)")
    sbp: float = Field(..., ge=40, le=250, description="Systolic BP (mmHg)")
    dbp: float = Field(..., ge=20, le=200, description="Diastolic BP (mmHg)")
    temperature: float = Field(..., ge=32, le=42, description="Temperature (°C)")
    respiratory_rate: float = Field(..., ge=0, le=60, description="Respiratory rate (breaths/min)")
    spo2: float = Field(..., ge=50, le=100, description="Oxygen saturation (%)")
    
    # Labs (20)
    wbc: float = Field(..., ge=0, le=100, description="White blood cell count (K/μL)")
    hemoglobin: float = Field(..., ge=3, le=20, description="Hemoglobin (g/dL)")
    hematocrit: float = Field(..., ge=10, le=70, description="Hematocrit (%)")
    platelets: float = Field(..., ge=10, le=1000, description="Platelet count (K/μL)")
    sodium: float = Field(..., ge=100, le=180, description="Sodium (mEq/L)")
    potassium: float = Field(..., ge=2, le=8, description="Potassium (mEq/L)")
    chloride: float = Field(..., ge=70, le=130, description="Chloride (mEq/L)")
    bicarbonate: float = Field(..., ge=5, le=45, description="Bicarbonate (mEq/L)")
    bun: float = Field(..., ge=1, le=200, description="Blood urea nitrogen (mg/dL)")
    creatinine: float = Field(..., ge=0.1, le=20, description="Creatinine (mg/dL)")
    glucose: float = Field(..., ge=20, le=1000, description="Glucose (mg/dL)")
    bilirubin: float = Field(..., ge=0, le=50, description="Bilirubin (mg/dL)")
    lactate: float = Field(..., ge=0, le=30, description="Lactate (mmol/L)")
    inr: float = Field(..., ge=0.5, le=10, description="INR")
    pt: float = Field(..., ge=5, le=100, description="Prothrombin time (sec)")
    rdw: float = Field(..., ge=10, le=30, description="RDW (%)")
    mcv: float = Field(..., ge=60, le=120, description="MCV (fL)")
    mch: float = Field(..., ge=20, le=40, description="MCH (pg)")
    mchc: float = Field(..., ge=25, le=40, description="MCHC (g/dL)")
    bands: float = Field(..., ge=0, le=50, description="Band neutrophils (%)")
    
    # SOFA scores (6)
    respiratory_sofa: int = Field(..., ge=0, le=4, description="Respiratory SOFA")
    cardiovascular_sofa: int = Field(..., ge=0, le=4, description="Cardiovascular SOFA")
    hepatic_sofa: int = Field(..., ge=0, le=4, description="Hepatic SOFA")
    coagulation_sofa: int = Field(..., ge=0, le=4, description="Coagulation SOFA")
    renal_sofa: int = Field(..., ge=0, le=4, description="Renal SOFA")
    neurological_sofa: int = Field(..., ge=0, le=4, description="Neurological SOFA")
    
    # Temporal trends (6)
    lactate_trend_12h: float = Field(..., description="Lactate change over 12h")
    lactate_trend_6h: float = Field(..., description="Lactate change over 6h")
    hr_trend_6h: float = Field(..., description="Heart rate change over 6h")
    sbp_trend_6h: float = Field(..., description="SBP change over 6h")
    temp_trend_6h: float = Field(..., description="Temperature change over 6h")
    wbc_trend_24h: float = Field(..., description="WBC change over 24h")
    
    # Time features (2)
    hour_of_admission: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    icu_los_so_far: float = Field(..., ge=0, description="ICU length of stay so far (hours)")
    
    class Config:
        schema_extra = {
            "example": {
                "age": 65,
                "gender": "M",
                "bmi": 28.5,
                "heart_rate": 110.0,
                "sbp": 90.0,
                "dbp": 60.0,
                "temperature": 38.5,
                "respiratory_rate": 24.0,
                "spo2": 92.0,
                "wbc": 15.2,
                "hemoglobin": 11.5,
                "hematocrit": 34.0,
                "platelets": 120.0,
                "sodium": 138.0,
                "potassium": 4.2,
                "chloride": 102.0,
                "bicarbonate": 22.0,
                "bun": 28.0,
                "creatinine": 1.8,
                "glucose": 180.0,
                "bilirubin": 2.1,
                "lactate": 3.5,
                "inr": 1.5,
                "pt": 15.0,
                "rdw": 14.5,
                "mcv": 88.0,
                "mch": 30.0,
                "mchc": 34.0,
                "bands": 12.0,
                "respiratory_sofa": 2,
                "cardiovascular_sofa": 1,
                "hepatic_sofa": 1,
                "coagulation_sofa": 1,
                "renal_sofa": 1,
                "neurological_sofa": 0,
                "lactate_trend_12h": 0.8,
                "lactate_trend_6h": 0.5,
                "hr_trend_6h": 10.0,
                "sbp_trend_6h": -15.0,
                "temp_trend_6h": 1.2,
                "wbc_trend_24h": 3.5,
                "hour_of_admission": 14,
                "icu_los_so_far": 18.5
            }
        }
```

**Validation Script:**
```python
# scripts/validate_schema_alignment.py

import psycopg2
from api.models.schemas import SepsisFeatures

def validate_schema_alignment():
    """Ensure database and API schemas match."""
    
    # Get DB columns
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'analytics'
          AND table_name = 'features_sepsis_6h'
          AND column_name NOT IN ('stay_id', 'feature_computed_at', 'sepsis_onset_within_6h')
        ORDER BY ordinal_position;
    """)
    db_columns = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Get Pydantic fields
    pydantic_fields = set(SepsisFeatures.__fields__.keys())
    
    # Compare
    db_cols = set(db_columns.keys())
    missing_in_api = db_cols - pydantic_fields
    missing_in_db = pydantic_fields - db_cols
    
    if missing_in_api:
        raise ValueError(f"❌ Columns in DB but not in API: {missing_in_api}")
    
    if missing_in_db:
        raise ValueError(f"❌ Fields in API but not in DB: {missing_in_db}")
    
    print("✅ Schema alignment validated: All 42 features match!")
    print(f"   Database columns: {len(db_cols)}")
    print(f"   API fields: {len(pydantic_fields)}")
    
    return True

if __name__ == "__main__":
    validate_schema_alignment()
```

---

## 5. UI COMPONENTS DETAILED WIRING

### 5.1 Patient Table Component

**File:** `apps/components/patient_table.py`

```python
import streamlit as st
import pandas as pd
from apps.services.api_client import api_client

def patient_table(filters=None, page=1, per_page=50):
    """
    Display paginated patient table with real-time data.
    
    Args:
        filters: Dict of filter criteria
        page: Current page number
        per_page: Patients per page
    
    Returns:
        Selected patient (if any)
    """
    
    # Fetch data from API
    try:
        response = api_client.get_patients(
            limit=per_page,
            offset=(page - 1) * per_page,
            sort_by='admission_date',
            order='desc',
            risk_filter=filters.get('risk_level', 'all') if filters else 'all'
        )
        
        patients_df = pd.DataFrame(response['patients'])
        total_patients = response['total']
        total_pages = response['pages']
        
    except Exception as e:
        st.error(f"Failed to load patients: {str(e)}")
        return None
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", total_patients)
    
    with col2:
        high_risk_count = len(patients_df[patients_df['sepsis_level'] == 'HIGH'])
        st.metric("High Risk", high_risk_count, delta=f"{high_risk_count/len(patients_df)*100:.1f}%")
    
    with col3:
        critical_count = len(patients_df[patients_df['sepsis_level'] == 'CRITICAL'])
        st.metric("Critical", critical_count, delta=f"{critical_count/len(patients_df)*100:.1f}%")
    
    with col4:
        avg_mortality = patients_df['mortality_risk'].mean()
        st.metric("Avg Mortality Risk", f"{avg_mortality*100:.1f}%")
    
    # Configure table columns
    column_config = {
        "stay_id": st.column_config.TextColumn(
            "Patient ID",
            width="small"
        ),
        "age": st.column_config.NumberColumn(
            "Age",
            format="%d",
            width="small"
        ),
        "gender": st.column_config.TextColumn(
            "Gender",
            width="small"
        ),
        "admission_date": st.column_config.DatetimeColumn(
            "Admitted",
            format="DD MMM HH:mm",
            width="medium"
        ),
        "diagnosis": st.column_config.TextColumn(
            "Diagnosis",
            width="medium"
        ),
        "sepsis_risk": st.column_config.ProgressColumn(
            "Sepsis Risk",
            format="%.0f%%",
            min_value=0,
            max_value=1,
            width="small"
        ),
        "sepsis_level": st.column_config.TextColumn(
            "Level",
            width="small"
        ),
        "mortality_risk": st.column_config.ProgressColumn(
            "Mortality Risk",
            format="%.0f%%",
            min_value=0,
            max_value=1,
            width="small"
        )
    }
    
    # Color-code risk levels
    def color_risk_level(val):
        if val == 'CRITICAL':
            return 'background-color: #ff4444; color: white; font-weight: bold'
        elif val == 'HIGH':
            return 'background-color: #ff9800; color: white'
        elif val == 'MEDIUM':
            return 'background-color: #ffeb3b'
        else:
            return 'background-color: #4caf50; color: white'
    
    # Display table
    st.subheader(f"Patients (Page {page} of {total_pages})")
    
    event = st.dataframe(
        patients_df.style.applymap(color_risk_level, subset=['sepsis_level']),
        use_container_width=True,
        column_config=column_config,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Pagination
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if page > 1:
            if st.button("← Previous"):
                st.session_state.page = page - 1
                st.rerun()
    
    with col_page:
        st.write(f"Page {page} of {total_pages}")
    
    with col_next:
        if page < total_pages:
            if st.button("Next →"):
                st.session_state.page = page + 1
                st.rerun()
    
    # Handle selection
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        selected_patient = patients_df.iloc[selected_idx]
        return selected_patient
    
    return None
```

---

### 5.2 Prediction Form Component

**File:** `apps/components/prediction_form.py`

```python
import streamlit as st
from api.models.schemas import SepsisFeatures

def prediction_form():
    """
    Display form for sepsis prediction with 42 input fields.
    Returns features dict if form submitted, None otherwise.
    """
    
    st.subheader("Enter Patient Data")
    
    with st.form("prediction_form"):
        # Demographics
        st.write("**Demographics**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("Age (years)", min_value=18, max_value=120, value=65)
        with col2:
            gender = st.selectbox("Gender", options=["M", "F"])
        with col3:
            bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=28.5)
        
        # Vitals
        st.write("**Vital Signs**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            heart_rate = st.number_input("Heart Rate (bpm)", min_value=0.0, max_value=300.0, value=110.0)
            sbp = st.number_input("Systolic BP (mmHg)", min_value=40.0, max_value=250.0, value=90.0)
        
        with col2:
            dbp = st.number_input("Diastolic BP (mmHg)", min_value=20.0, max_value=200.0, value=60.0)
            temperature = st.number_input("Temperature (°C)", min_value=32.0, max_value=42.0, value=38.5)
        
        with col3:
            respiratory_rate = st.number_input("Respiratory Rate", min_value=0.0, max_value=60.0, value=24.0)
            spo2 = st.number_input("SpO2 (%)", min_value=50.0, max_value=100.0, value=92.0)
        
        # Labs
        st.write("**Laboratory Values**")
        
        # Hematology
        st.write("*Hematology*")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            wbc = st.number_input("WBC (K/μL)", min_value=0.0, max_value=100.0, value=15.2)
            hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=3.0, max_value=20.0, value=11.5)
        
        with col2:
            hematocrit = st.number_input("Hematocrit (%)", min_value=10.0, max_value=70.0, value=34.0)
            platelets = st.number_input("Platelets (K/μL)", min_value=10.0, max_value=1000.0, value=120.0)
        
        with col3:
            rdw = st.number_input("RDW (%)", min_value=10.0, max_value=30.0, value=14.5)
            mcv = st.number_input("MCV (fL)", min_value=60.0, max_value=120.0, value=88.0)
        
        with col4:
            mch = st.number_input("MCH (pg)", min_value=20.0, max_value=40.0, value=30.0)
            mchc = st.number_input("MCHC (g/dL)", min_value=25.0, max_value=40.0, value=34.0)
        
        # Chemistry
        st.write("*Chemistry*")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sodium = st.number_input("Sodium (mEq/L)", min_value=100.0, max_value=180.0, value=138.0)
            potassium = st.number_input("Potassium (mEq/L)", min_value=2.0, max_value=8.0, value=4.2)
        
        with col2:
            chloride = st.number_input("Chloride (mEq/L)", min_value=70.0, max_value=130.0, value=102.0)
            bicarbonate = st.number_input("Bicarbonate (mEq/L)", min_value=5.0, max_value=45.0, value=22.0)
        
        with col3:
            bun = st.number_input("BUN (mg/dL)", min_value=1.0, max_value=200.0, value=28.0)
            creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.1, max_value=20.0, value=1.8)
        
        with col4:
            glucose = st.number_input("Glucose (mg/dL)", min_value=20.0, max_value=1000.0, value=180.0)
            bilirubin = st.number_input("Bilirubin (mg/dL)", min_value=0.0, max_value=50.0, value=2.1)
        
        # Other labs
        st.write("*Other Labs*")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            lactate = st.number_input("Lactate (mmol/L)", min_value=0.0, max_value=30.0, value=3.5)
        
        with col2:
            inr = st.number_input("INR", min_value=0.5, max_value=10.0, value=1.5)
        
        with col3:
            pt = st.number_input("PT (sec)", min_value=5.0, max_value=100.0, value=15.0)
        
        with col4:
            bands = st.number_input("Bands (%)", min_value=0.0, max_value=50.0, value=12.0)
        
        # SOFA scores
        st.write("**SOFA Scores**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            respiratory_sofa = st.number_input("Respiratory", min_value=0, max_value=4, value=2)
            cardiovascular_sofa = st.number_input("Cardiovascular", min_value=0, max_value=4, value=1)
        
        with col2:
            hepatic_sofa = st.number_input("Hepatic", min_value=0, max_value=4, value=1)
            coagulation_sofa = st.number_input("Coagulation", min_value=0, max_value=4, value=1)
        
        with col3:
            renal_sofa = st.number_input("Renal", min_value=0, max_value=4, value=1)
            neurological_sofa = st.number_input("Neurological", min_value=0, max_value=4, value=0)
        
        # Temporal trends
        st.write("**Temporal Trends**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lactate_trend_12h = st.number_input("Lactate Δ 12h", value=0.8)
            lactate_trend_6h = st.number_input("Lactate Δ 6h", value=0.5)
        
        with col2:
            hr_trend_6h = st.number_input("HR Δ 6h", value=10.0)
            sbp_trend_6h = st.number_input("SBP Δ 6h", value=-15.0)
        
        with col3:
            temp_trend_6h = st.number_input("Temp Δ 6h", value=1.2)
            wbc_trend_24h = st.number_input("WBC Δ 24h", value=3.5)
        
        # Time features
        st.write("**Time Context**")
        col1, col2 = st.columns(2)
        
        with col1:
            hour_of_admission = st.number_input("Hour of Admission (0-23)", min_value=0, max_value=23, value=14)
        
        with col2:
            icu_los_so_far = st.number_input("ICU LOS So Far (hours)", min_value=0.0, value=18.5)
        
        # Submit button
        submitted = st.form_submit_button("🔮 Predict Risk", type="primary")
        
        if submitted:
            # Construct features dict
            features = {
                "age": age,
                "gender": gender,
                "bmi": bmi,
                "heart_rate": heart_rate,
                "sbp": sbp,
                "dbp": dbp,
                "temperature": temperature,
                "respiratory_rate": respiratory_rate,
                "spo2": spo2,
                "wbc": wbc,
                "hemoglobin": hemoglobin,
                "hematocrit": hematocrit,
                "platelets": platelets,
                "sodium": sodium,
                "potassium": potassium,
                "chloride": chloride,
                "bicarbonate": bicarbonate,
                "bun": bun,
                "creatinine": creatinine,
                "glucose": glucose,
                "bilirubin": bilirubin,
                "lactate": lactate,
                "inr": inr,
                "pt": pt,
                "rdw": rdw,
                "mcv": mcv,
                "mch": mch,
                "mchc": mchc,
                "bands": bands,
                "respiratory_sofa": respiratory_sofa,
                "cardiovascular_sofa": cardiovascular_sofa,
                "hepatic_sofa": hepatic_sofa,
                "coagulation_sofa": coagulation_sofa,
                "renal_sofa": renal_sofa,
                "neurological_sofa": neurological_sofa,
                "lactate_trend_12h": lactate_trend_12h,
                "lactate_trend_6h": lactate_trend_6h,
                "hr_trend_6h": hr_trend_6h,
                "sbp_trend_6h": sbp_trend_6h,
                "temp_trend_6h": temp_trend_6h,
                "wbc_trend_24h": wbc_trend_24h,
                "hour_of_admission": hour_of_admission,
                "icu_los_so_far": icu_los_so_far
            }
            
            return features
    
    return None
```

---

### 5.3 API Client Service

**File:** `apps/services/api_client.py`

```python
"""API client for communicating with FastAPI backend."""

import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """
    Client for communicating with FastAPI backend.

    Features:
    - Connection pooling
    - Automatic retry with exponential backoff
    - Request/response logging
    - Error handling
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.

        Args:
            base_url: Base URL of FastAPI backend
        """
        self.base_url = base_url
        self.session = requests.Session()

        # Configure session
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def get_patients(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = 'admission_date',
        order: str = 'desc',
        risk_filter: str = 'all'
    ) -> Dict[str, Any]:
        """
        Get paginated list of patients.

        Args:
            limit: Number of patients per page
            offset: Offset for pagination
            sort_by: Column to sort by
            order: Sort order (asc/desc)
            risk_filter: Filter by risk level

        Returns:
            Dict with patients list and pagination info
        """
        params = {
            'limit': limit,
            'offset': offset,
            'sort_by': sort_by,
            'order': order,
            'risk_filter': risk_filter
        }

        response = self._request('GET', '/patients', params=params)
        return response.json()

    def get_patient(self, stay_id: str) -> Dict[str, Any]:
        """
        Get details for specific patient.

        Args:
            stay_id: Patient stay ID

        Returns:
            Patient details
        """
        response = self._request('GET', f'/patients/{stay_id}')
        return response.json()

    def predict_sepsis(
        self,
        patient_id: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Request sepsis prediction.

        Args:
            patient_id: Patient identifier
            features: Dict with 42 features

        Returns:
            Prediction result with risk score and explanation
        """
        payload = {
            'patient_id': patient_id,
            'features': features
        }

        response = self._request('POST', '/predict/sepsis', json=payload)
        return response.json()

    def predict_mortality(
        self,
        patient_id: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request mortality prediction."""
        payload = {
            'patient_id': patient_id,
            'features': features
        }

        response = self._request('POST', '/predict/mortality', json=payload)
        return response.json()

    def _request(
        self,
        method: str,
        endpoint: str,
        max_retries: int = 3,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            max_retries: Maximum retry attempts
            **kwargs: Additional request arguments

        Returns:
            Response object

        Raises:
            APIError if request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    # Retry on server errors
                    delay = 2 ** attempt
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s")
                    import time
                    time.sleep(delay)
                    continue
                else:
                    raise APIError(f"API request failed: {e}")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s")
                    import time
                    time.sleep(delay)
                    continue
                else:
                    raise APIError(f"API request failed: {e}")


class APIError(Exception):
    """API request error."""
    pass


# Global client instance
api_client = APIClient()
```

---

### 5.4 Result Display Component

**File:** `apps/components/result_display.py`

```python
"""Display prediction results with SHAP explanation."""

import streamlit as st
import pandas as pd
from typing import Dict, Any
import base64
from io import BytesIO


def display_prediction_result(result: Dict[str, Any], model_type: str = "sepsis"):
    """
    Display prediction result with visualization.

    Args:
        result: Prediction result from API
        model_type: Type of model (sepsis/mortality)
    """
    prediction = result['prediction']
    explanation = result['explanation']
    metadata = result['metadata']

    # Main result card
    st.subheader("Prediction Result")

    col1, col2, col3 = st.columns(3)

    with col1:
        risk_score = prediction['risk_score']
        st.metric(
            "Risk Score",
            f"{risk_score:.1%}",
            delta=None,
            delta_color="inverse"
        )

    with col2:
        risk_level = prediction['risk_level']
        color = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠',
            'CRITICAL': '🔴'
        }.get(risk_level, '⚪')

        st.metric("Risk Level", f"{color} {risk_level}")

    with col3:
        confidence = prediction['confidence']
        st.metric("Confidence", f"{confidence:.1%}")

    # Recommendation
    st.info(f"**Recommendation:** {prediction['recommendation']}")

    # Feature Importance
    st.subheader("Key Contributing Factors")

    top_features = explanation['top_features']

    # Create dataframe for table
    features_df = pd.DataFrame(top_features)

    # Display as styled table
    st.dataframe(
        features_df[['feature', 'importance', 'value', 'interpretation']],
        use_container_width=True,
        hide_index=True
    )

    # SHAP Waterfall Plot
    if 'shap_waterfall_plot' in explanation:
        st.subheader("SHAP Explanation")

        # Decode base64 image
        image_data = base64.b64decode(
            explanation['shap_waterfall_plot'].split(',')[1]
        )

        st.image(image_data, caption="SHAP Waterfall Plot")

    # Metadata
    with st.expander("Prediction Metadata"):
        st.json(metadata)
```

---

## 6. CACHE STRATEGY

### 6.1 Redis Caching Layer

**Purpose:** Reduce API latency by caching prediction results

**File:** `api/services/cache_service.py`

```python
"""Redis cache service for predictions."""

import redis
import hashlib
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize cache service."""
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour

    def get_prediction(
        self,
        model_name: str,
        features: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached prediction.

        Args:
            model_name: Name of model
            features: Input features

        Returns:
            Cached prediction or None
        """
        cache_key = self._generate_key(model_name, features)

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache miss: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def store_prediction(
        self,
        model_name: str,
        features: Dict[str, Any],
        prediction: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """
        Store prediction in cache.

        Args:
            model_name: Name of model
            features: Input features
            prediction: Prediction result
            ttl: Time to live in seconds
        """
        cache_key = self._generate_key(model_name, features)
        ttl = ttl or self.default_ttl

        try:
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(prediction)
            )
            logger.info(f"Cached prediction: {cache_key} (TTL: {ttl}s)")

        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def invalidate_model(self, model_name: str):
        """Invalidate all cache entries for a model."""
        pattern = f"prediction:{model_name}:*"

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for {model_name}")

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")

    def _generate_key(self, model_name: str, features: Dict[str, Any]) -> str:
        """Generate cache key from model name and features."""
        # Sort features for consistent hashing
        features_str = json.dumps(features, sort_keys=True)
        features_hash = hashlib.md5(features_str.encode()).hexdigest()

        return f"prediction:{model_name}:{features_hash}"
```

**Cache Invalidation Policy:**
- TTL: 1 hour (predictions valid for short time)
- On model update: Invalidate all entries for that model
- On patient data update: Invalidate specific patient predictions

---

## 7. ERROR HANDLING IN UI

### 7.1 Error Display Patterns

**File:** `apps/utils/error_handler.py`

```python
"""Error handling utilities for Streamlit UI."""

import streamlit as st
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator for handling API errors in Streamlit.

    Usage:
        @handle_api_errors
        def my_function():
            # API call that might fail
            result = api_client.get_patients()
            return result
    """
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)

        except APIError as e:
            st.error(f"API Error: {e}")
            logger.error(f"API error in {func.__name__}: {e}")
            return None

        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            logger.error(f"Timeout in {func.__name__}")
            return None

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to API. Please ensure the backend is running."
            )
            logger.error(f"Connection error in {func.__name__}")
            return None

        except Exception as e:
            st.error(f"Unexpected error: {e}")
            logger.exception(f"Unexpected error in {func.__name__}")
            return None

    return wrapper


def show_error_message(error_type: str, message: str):
    """Display formatted error message."""
    error_styles = {
        'api': '🔌',
        'validation': '⚠️',
        'data': '📊',
        'model': '🤖',
        'unknown': '❌'
    }

    icon = error_styles.get(error_type, '❌')
    st.error(f"{icon} **{error_type.upper()} Error**: {message}")
```

---

## 8. TESTING STRATEGIES

### 8.1 API Integration Tests

**File:** `tests/test_integration.py`

```python
"""Integration tests for UI ↔ API wiring."""

import pytest
from apps.services.api_client import APIClient


class TestAPIIntegration:
    """Test API integration."""

    @pytest.fixture
    def api_client(self):
        """Create API client for testing."""
        return APIClient(base_url="http://localhost:8000")

    def test_get_patients(self, api_client):
        """Test GET /patients endpoint."""
        response = api_client.get_patients(limit=10)

        assert 'patients' in response
        assert 'total' in response
        assert len(response['patients']) <= 10

    def test_predict_sepsis(self, api_client):
        """Test POST /predict/sepsis endpoint."""
        features = {
            'age': 65,
            'gender': 'M',
            'bmi': 28.5,
            'heart_rate': 110.0,
            # ... all 42 features
        }

        response = api_client.predict_sepsis(
            patient_id='test_patient',
            features=features
        )

        assert 'prediction' in response
        assert 'risk_score' in response['prediction']
        assert 0 <= response['prediction']['risk_score'] <= 1
```

### 8.2 UI Component Tests

**File:** `tests/test_components.py`

```python
"""Unit tests for Streamlit components."""

import pytest
from unittest.mock import Mock, patch

from apps.components.patient_table import patient_table


class TestPatientTable:
    """Test patient table component."""

    @patch('apps.services.api_client.api_client.get_patients')
    def test_patient_table_renders(self, mock_get_patients):
        """Test patient table renders correctly."""
        mock_get_patients.return_value = {
            'patients': [
                {
                    'stay_id': 'P-001',
                    'age': 65,
                    'gender': 'M',
                    'sepsis_risk': 0.75
                }
            ],
            'total': 1,
            'pages': 1
        }

        # Render component (in test environment)
        result = patient_table(page=1, per_page=10)

        # Verify mock was called
        mock_get_patients.assert_called_once()
```

---

## 9. MONITORING & OBSERVABILITY

### 9.1 Logging Strategy

**All components log to centralized logger:**

```python
# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log key events
logger.info("User requested prediction for patient P-001")
logger.info("API request: POST /predict/sepsis (45ms)")
logger.error("API request failed: Connection timeout")
```

### 9.2 Metrics Tracking

**Track key metrics:**
- API request latency (p50, p95, p99)
- Cache hit rate
- Prediction counts
- Error rates
- User interactions

**Implementation:**
```python
from prometheus_client import Counter, Histogram

# Define metrics
prediction_requests = Counter(
    'prediction_requests_total',
    'Total prediction requests',
    ['model_type', 'risk_level']
)

api_latency = Histogram(
    'api_request_duration_seconds',
    'API request duration'
)

# Track metrics
with api_latency.time():
    result = api_client.predict_sepsis(patient_id, features)

prediction_requests.labels(
    model_type='sepsis',
    risk_level=result['prediction']['risk_level']
).inc()
```

---

## 10. DEPLOYMENT CHECKLIST

### Before Deploying UI + API:

**Infrastructure:**
- [ ] PostgreSQL running and accessible
- [ ] Redis running and accessible
- [ ] MLflow server running with registered models
- [ ] All environment variables set correctly

**Database:**
- [ ] All schemas created (raw, staging, analytics)
- [ ] Feature tables populated
- [ ] Indexes created on frequently queried columns

**API:**
- [ ] FastAPI server starts without errors
- [ ] Health check endpoint returns 200
- [ ] OpenAPI docs accessible at /docs
- [ ] Models load successfully from MLflow
- [ ] Redis cache working

**UI:**
- [ ] Streamlit app starts without errors
- [ ] API client connects to backend
- [ ] All pages render correctly
- [ ] Forms validate inputs
- [ ] Predictions work end-to-end

**Testing:**
- [ ] Unit tests pass (>70% coverage)
- [ ] Integration tests pass
- [ ] End-to-end test completes successfully
- [ ] Load test (100 requests/sec) passes

**Monitoring:**
- [ ] Logging configured
- [ ] Metrics collection enabled
- [ ] Alerts configured for errors

**Documentation:**
- [ ] API documentation complete
- [ ] User guide written
- [ ] Troubleshooting guide available

---

## 11. COMPLETE WIRING SUMMARY

### Data Flow (Complete Path)

```
1. User clicks "Predict" in Streamlit
   ↓
2. Streamlit calls api_client.predict_sepsis(features)
   ↓
3. API client sends POST /predict/sepsis
   ↓
4. FastAPI endpoint receives request
   ↓
5. Pydantic validates 42 features
   ↓
6. Check Redis cache (key: model_name + feature_hash)
   ↓ (if miss)
7. Load model from MLflow (cached in memory)
   ↓
8. Query database for patient features (single query, no joins)
   ↓
9. Preprocess features
   ↓
10. Run model inference (<100ms)
    ↓
11. Calculate SHAP explanation
    ↓
12. Store prediction in database
    ↓
13. Store result in Redis cache (TTL: 1h)
    ↓
14. Return JSON response
    ↓
15. Streamlit displays result with visualization
```

**Total latency target:** <200ms (p95)

---

## 12. TROUBLESHOOTING GUIDE

### Issue: UI cannot connect to API
**Solution:**
```bash
# Check API is running
curl http://localhost:8000/health

# Check Streamlit config
# apps/.streamlit/config.toml
[server]
port = 8501

[client]
serverAddress = "localhost"
```

### Issue: Predictions are slow
**Solutions:**
1. Check Redis cache hit rate (should be >80%)
2. Check database query time (should be <5s)
3. Check model inference time (should be <100ms)

### Issue: Feature validation fails
**Solution:**
Run schema alignment validator:
```bash
python scripts/validate_schema_alignment.py
```

---

**Document Version:** 1.0
**Status:** ✅ COMPLETE - Implementation Ready
**Next Steps:** Implement UI components and test end-to-end