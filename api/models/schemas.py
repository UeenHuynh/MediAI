"""
Pydantic models for request/response validation
IMPORTANT: These schemas EXACTLY match the Kaggle CSV column names
Updated: December 2024 - Aligned with data/sample_kaggle/ CSV files
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level categories"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================================
# SEPSIS PREDICTION SCHEMAS (42 features from features_sepsis_6h.csv)
# ============================================================================
# CSV columns: subject_id, hadm_id, stay_id (IDs) + 42 feature columns + sepsis_label
# Total: 46 columns, 42 features for prediction


class SepsisFeatures(BaseModel):
    """
    42 features for sepsis prediction
    EXACTLY matches features_sepsis_6h.csv column names
    """

    # Demographics (3 features)
    age: int = Field(..., ge=18, le=120, description="Patient age in years")
    gender: int = Field(..., ge=0, le=1, description="Gender (0=F, 1=M)")
    bmi: float = Field(..., ge=10, le=80, description="Body mass index (kg/m²)")

    # Vitals (5 features)
    heart_rate: float = Field(..., ge=0, le=300, description="Heart rate (bpm)")
    sbp: float = Field(..., ge=40, le=250, description="Systolic blood pressure (mmHg)")
    dbp: float = Field(
        ..., ge=20, le=200, description="Diastolic blood pressure (mmHg)"
    )
    temperature: float = Field(..., ge=32, le=45, description="Body temperature (°C)")
    respiratory_rate: float = Field(
        ..., ge=0, le=80, description="Respiratory rate (breaths/min)"
    )

    # Laboratory Values (20 features)
    wbc: float = Field(..., ge=0, le=200, description="White blood cell count (10^9/L)")
    lactate: float = Field(..., ge=0, le=30, description="Serum lactate (mmol/L)")
    creatinine: float = Field(..., ge=0, le=30, description="Creatinine (mg/dL)")
    platelets: float = Field(..., ge=0, le=2000, description="Platelet count (10^9/L)")
    bilirubin: float = Field(..., ge=0, le=100, description="Total bilirubin (mg/dL)")
    sodium: float = Field(..., ge=100, le=200, description="Sodium (mmol/L)")
    potassium: float = Field(..., ge=2, le=10, description="Potassium (mmol/L)")
    glucose: float = Field(..., ge=0, le=2000, description="Glucose (mg/dL)")
    hemoglobin: float = Field(..., ge=0, le=30, description="Hemoglobin (g/dL)")
    bicarbonate: float = Field(..., ge=0, le=100, description="Bicarbonate (mmol/L)")
    pao2: float = Field(..., ge=0, le=800, description="PaO2 (mmHg)")
    paco2: float = Field(..., ge=0, le=200, description="PaCO2 (mmHg)")
    ph: float = Field(..., ge=6.5, le=8.0, description="Arterial pH")
    anion_gap: float = Field(..., ge=0, le=50, description="Anion gap (mmol/L)")
    albumin: float = Field(..., ge=0, le=10, description="Albumin (g/dL)")
    troponin: float = Field(..., ge=0, le=100, description="Troponin (ng/mL)")
    bnp: float = Field(..., ge=0, le=50000, description="BNP (pg/mL)")
    inr: float = Field(..., ge=0, le=20, description="INR")
    ast: float = Field(..., ge=0, le=10000, description="AST (U/L)")
    alt: float = Field(..., ge=0, le=10000, description="ALT (U/L)")

    # SOFA Scores (6 features)
    respiratory_sofa: int = Field(..., ge=0, le=4, description="Respiratory SOFA score")
    cardiovascular_sofa: int = Field(
        ..., ge=0, le=4, description="Cardiovascular SOFA score"
    )
    hepatic_sofa: int = Field(..., ge=0, le=4, description="Hepatic SOFA score")
    coagulation_sofa: int = Field(..., ge=0, le=4, description="Coagulation SOFA score")
    renal_sofa: int = Field(..., ge=0, le=4, description="Renal SOFA score")
    neurological_sofa: int = Field(
        ..., ge=0, le=4, description="Neurological SOFA score"
    )

    # Temporal Trends (6 features)
    lactate_trend_12h: float = Field(
        ..., description="Lactate change over 12h (mmol/L)"
    )
    hr_trend_6h: float = Field(..., description="Heart rate change over 6h (bpm)")
    wbc_trend_12h: float = Field(..., description="WBC change over 12h (10^9/L)")
    sbp_trend_6h: float = Field(..., description="SBP change over 6h (mmHg)")
    temperature_trend_6h: float = Field(
        ..., description="Temperature change over 6h (°C)"
    )
    rr_trend_6h: float = Field(
        ..., description="Respiratory rate change over 6h (breaths/min)"
    )

    # Time Features (2 features)
    hour_of_admission: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    icu_los_so_far: float = Field(
        ..., ge=0, description="ICU length of stay so far (hours)"
    )


class SepsisPredictionRequest(BaseModel):
    """Request for sepsis prediction"""

    patient_id: str = Field(..., description="Patient identifier")
    features: SepsisFeatures


class FeatureContribution(BaseModel):
    """Individual feature contribution to prediction"""

    feature: str
    value: float
    importance: float = Field(..., description="SHAP value (contribution to risk)")


class PredictionDetail(BaseModel):
    """Prediction result details"""

    risk_score: float = Field(..., ge=0, le=1, description="Probability (0-1)")
    risk_level: RiskLevel
    recommendation: str


class SepsisPredictionResponse(BaseModel):
    """Response from sepsis prediction"""

    patient_id: str
    prediction: PredictionDetail
    top_features: List[FeatureContribution] = Field(..., max_length=10)
    metadata: dict


# ============================================================================
# MORTALITY PREDICTION SCHEMAS (61 features from features_mortality_24h.csv)
# ============================================================================
# CSV columns: subject_id, hadm_id, stay_id (IDs) + 61 feature columns + mortality_label
# Total: 65 columns, 61 features for prediction


class MortalityFeatures(BaseModel):
    """
    61 features for mortality prediction
    EXACTLY matches features_mortality_24h.csv column names
    """

    # SOFA Scores (6 features)
    respiratory_sofa: int = Field(..., ge=0, le=4)
    cardiovascular_sofa: int = Field(..., ge=0, le=4)
    hepatic_sofa: int = Field(..., ge=0, le=4)
    coagulation_sofa: int = Field(..., ge=0, le=4)
    renal_sofa: int = Field(..., ge=0, le=4)
    neurological_sofa: int = Field(..., ge=0, le=4)

    # APACHE-II Components (2 features)
    age_points: int = Field(..., ge=0, le=6)
    gcs_score: float = Field(..., ge=3, le=15, description="Glasgow Coma Scale")

    # Worst values in 24h (20 features)
    worst_hr_24h: float = Field(..., ge=0, le=300)
    worst_sbp_24h: float = Field(..., ge=0, le=300)
    worst_temp_24h: float = Field(..., ge=30, le=45)
    worst_rr_24h: float = Field(..., ge=0, le=100)
    worst_pao2_24h: float = Field(..., ge=0, le=800)
    worst_ph_24h: float = Field(..., ge=6.5, le=8.0)
    worst_sodium_24h: float = Field(..., ge=100, le=200)
    worst_potassium_24h: float = Field(..., ge=2, le=10)
    worst_creatinine_24h: float = Field(..., ge=0, le=30)
    worst_hematocrit_24h: float = Field(..., ge=0, le=100)
    worst_wbc_24h: float = Field(..., ge=0, le=200)
    worst_lactate_24h: float = Field(..., ge=0, le=50)
    worst_platelets_24h: float = Field(..., ge=0, le=2000)
    worst_bilirubin_24h: float = Field(..., ge=0, le=100)
    worst_glucose_24h: float = Field(..., ge=0, le=2000)
    worst_hemoglobin_24h: float = Field(..., ge=0, le=30)
    worst_bicarbonate_24h: float = Field(..., ge=0, le=100)
    worst_albumin_24h: float = Field(..., ge=0, le=10)
    worst_ast_24h: float = Field(..., ge=0, le=10000)
    worst_alt_24h: float = Field(..., ge=0, le=10000)

    # Additional worst labs (10 features)
    worst_bun_24h: float = Field(..., ge=0, le=300)
    worst_chloride_24h: float = Field(..., ge=80, le=150)
    worst_inr_24h: float = Field(..., ge=0, le=20)
    worst_ptt_24h: float = Field(..., ge=0, le=200)
    worst_troponin_24h: float = Field(..., ge=0, le=100)
    worst_bnp_24h: float = Field(..., ge=0, le=50000)
    worst_anion_gap_24h: float = Field(..., ge=0, le=50)
    worst_paco2_24h: float = Field(..., ge=0, le=200)
    worst_map_24h: float = Field(..., ge=0, le=200)
    worst_spo2_24h: float = Field(..., ge=0, le=100)

    # Min/Max Vitals in 24h (8 features)
    min_hr_24h: float = Field(..., ge=0, le=300)
    max_hr_24h: float = Field(..., ge=0, le=300)
    min_sbp_24h: float = Field(..., ge=0, le=300)
    max_sbp_24h: float = Field(..., ge=0, le=300)
    min_temp_24h: float = Field(..., ge=30, le=45)
    max_temp_24h: float = Field(..., ge=30, le=45)
    min_rr_24h: float = Field(..., ge=0, le=100)
    max_rr_24h: float = Field(..., ge=0, le=100)

    # Additional lab (1 feature)
    worst_fio2_24h: float = Field(..., ge=21, le=100)

    # ICU Details (6 features)
    icu_type: int = Field(..., ge=0, le=10, description="ICU type code")
    ventilation_flag: int = Field(..., ge=0, le=1, description="Mechanical ventilation")
    vasopressor_flag: int = Field(..., ge=0, le=1, description="Vasopressor use")
    dialysis_flag: int = Field(..., ge=0, le=1, description="Dialysis")
    age: int = Field(..., ge=18, le=120)
    gender: int = Field(..., ge=0, le=1, description="Gender (0=F, 1=M)")

    # Patient info (3 features)
    bmi: float = Field(..., ge=10, le=100)
    admission_source: int = Field(..., ge=0, le=10, description="Admission source code")
    comorbidity_count: int = Field(..., ge=0, le=30)

    # Time (1 feature)
    icu_los_24h: float = Field(
        ..., ge=0, le=24, description="ICU length of stay (hours)"
    )

    # Diagnosis Flags (4 features)
    sepsis_flag: int = Field(..., ge=0, le=1)
    shock_flag: int = Field(..., ge=0, le=1)
    cardiac_arrest_flag: int = Field(..., ge=0, le=1)
    trauma_flag: int = Field(..., ge=0, le=1)


class MortalityPredictionRequest(BaseModel):
    """Request for mortality prediction"""

    patient_id: str
    features: MortalityFeatures


class MortalityPredictionResponse(BaseModel):
    """Response from mortality prediction"""

    patient_id: str
    prediction: PredictionDetail
    top_features: List[FeatureContribution] = Field(..., max_length=10)
    metadata: dict
