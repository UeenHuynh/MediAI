"""
Pydantic models for request/response validation
IMPORTANT: These schemas must match database feature tables exactly
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level categories"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================================
# SEPSIS PREDICTION SCHEMAS (42 features)
# ============================================================================

class SepsisFeatures(BaseModel):
    """
    42 features for sepsis prediction
    Must match analytics.features_sepsis_6h table
    """

    # Demographics (3 features)
    age: int = Field(..., ge=18, le=120, description="Patient age in years")
    gender: str = Field(..., pattern="^(M|F)$", description="Gender (M/F)")
    bmi: float = Field(..., ge=10, le=60, description="Body mass index (kg/m²)")

    # Vitals (5 features)
    heart_rate: float = Field(..., ge=0, le=300, description="Heart rate (bpm)")
    sbp: float = Field(..., ge=40, le=250, description="Systolic blood pressure (mmHg)")
    dbp: float = Field(..., ge=20, le=150, description="Diastolic blood pressure (mmHg)")
    temperature: float = Field(..., ge=32, le=42, description="Body temperature (°C)")
    respiratory_rate: float = Field(..., ge=0, le=60, description="Respiratory rate (breaths/min)")

    # Laboratory Values (20 features)
    wbc: float = Field(..., ge=0, le=100, description="White blood cell count (10^9/L)")
    lactate: float = Field(..., ge=0, le=30, description="Serum lactate (mmol/L)")
    creatinine: float = Field(..., ge=0, le=20, description="Creatinine (mg/dL)")
    platelets: float = Field(..., ge=0, le=1000, description="Platelet count (10^9/L)")
    bilirubin: float = Field(..., ge=0, le=50, description="Total bilirubin (mg/dL)")
    sodium: float = Field(..., ge=100, le=180, description="Sodium (mmol/L)")
    potassium: float = Field(..., ge=2, le=8, description="Potassium (mmol/L)")
    glucose: float = Field(..., ge=0, le=1000, description="Glucose (mg/dL)")
    hemoglobin: float = Field(..., ge=0, le=25, description="Hemoglobin (g/dL)")
    bicarbonate: float = Field(..., ge=0, le=50, description="Bicarbonate (mmol/L)")
    pao2: Optional[float] = Field(None, ge=0, le=800, description="PaO2 (mmHg)")
    paco2: Optional[float] = Field(None, ge=0, le=150, description="PaCO2 (mmHg)")
    ph: Optional[float] = Field(None, ge=6.5, le=8.0, description="Arterial pH")
    anion_gap: Optional[float] = Field(None, ge=0, le=50, description="Anion gap (mmol/L)")
    albumin: Optional[float] = Field(None, ge=0, le=10, description="Albumin (g/dL)")
    troponin: Optional[float] = Field(None, ge=0, le=100, description="Troponin (ng/mL)")
    bnp: Optional[float] = Field(None, ge=0, le=10000, description="BNP (pg/mL)")
    inr: Optional[float] = Field(None, ge=0, le=10, description="INR")
    ast: Optional[float] = Field(None, ge=0, le=10000, description="AST (U/L)")
    alt: Optional[float] = Field(None, ge=0, le=10000, description="ALT (U/L)")

    # SOFA Scores (6 features)
    respiratory_sofa: int = Field(..., ge=0, le=4, description="Respiratory SOFA score")
    cardiovascular_sofa: int = Field(..., ge=0, le=4, description="Cardiovascular SOFA score")
    hepatic_sofa: int = Field(..., ge=0, le=4, description="Hepatic SOFA score")
    coagulation_sofa: int = Field(..., ge=0, le=4, description="Coagulation SOFA score")
    renal_sofa: int = Field(..., ge=0, le=4, description="Renal SOFA score")
    neurological_sofa: int = Field(..., ge=0, le=4, description="Neurological SOFA score")

    # Temporal Trends (6 features)
    lactate_trend_12h: float = Field(..., description="Lactate change over 12h (mmol/L)")
    hr_trend_6h: float = Field(..., description="Heart rate change over 6h (bpm)")
    wbc_trend_12h: float = Field(..., description="WBC change over 12h (10^9/L)")
    sbp_trend_6h: float = Field(..., description="SBP change over 6h (mmHg)")
    temperature_trend_6h: float = Field(..., description="Temperature change over 6h (°C)")
    rr_trend_6h: float = Field(..., description="Respiratory rate change over 6h (breaths/min)")

    # Time Features (2 features)
    hour_of_admission: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    icu_los_so_far: float = Field(..., ge=0, description="ICU length of stay so far (hours)")

    @validator('lactate')
    def check_lactate(cls, v):
        if v > 10:
            raise ValueError('Lactate >10 mmol/L is critically high. Please verify measurement.')
        return v


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
    top_features: List[FeatureContribution] = Field(..., max_items=10)
    metadata: dict


# ============================================================================
# MORTALITY PREDICTION SCHEMAS (65 features)
# ============================================================================

class MortalityFeatures(BaseModel):
    """
    65 features for mortality prediction
    Must match analytics.features_mortality_24h table
    """

    # SOFA Scores (6 features) - same as sepsis
    respiratory_sofa: int = Field(..., ge=0, le=4)
    cardiovascular_sofa: int = Field(..., ge=0, le=4)
    hepatic_sofa: int = Field(..., ge=0, le=4)
    coagulation_sofa: int = Field(..., ge=0, le=4)
    renal_sofa: int = Field(..., ge=0, le=4)
    neurological_sofa: int = Field(..., ge=0, le=4)

    # APACHE-II Components (12 features)
    age_points: int = Field(..., ge=0, le=6)
    gcs_score: int = Field(..., ge=3, le=15, description="Glasgow Coma Scale")
    worst_hr_24h: float = Field(..., ge=0, le=300)
    worst_sbp_24h: float = Field(..., ge=0, le=300)
    worst_temp_24h: float = Field(..., ge=30, le=45)
    worst_rr_24h: float = Field(..., ge=0, le=100)
    worst_pao2_24h: Optional[float] = Field(None, ge=0, le=800)
    worst_ph_24h: Optional[float] = Field(None, ge=6.5, le=8.0)
    worst_sodium_24h: float = Field(..., ge=100, le=200)
    worst_potassium_24h: float = Field(..., ge=2, le=10)
    worst_creatinine_24h: float = Field(..., ge=0, le=30)
    worst_hematocrit_24h: float = Field(..., ge=0, le=100)

    # Worst Vitals in 24h (8 features)
    min_hr_24h: float = Field(..., ge=0, le=300)
    max_hr_24h: float = Field(..., ge=0, le=300)
    min_sbp_24h: float = Field(..., ge=0, le=300)
    max_sbp_24h: float = Field(..., ge=0, le=300)
    min_temp_24h: float = Field(..., ge=30, le=45)
    max_temp_24h: float = Field(..., ge=30, le=45)
    min_rr_24h: float = Field(..., ge=0, le=100)
    max_rr_24h: float = Field(..., ge=0, le=100)

    # Worst Labs in 24h (25 features)
    worst_wbc_24h: float = Field(..., ge=0, le=200)
    worst_lactate_24h: float = Field(..., ge=0, le=50)
    worst_platelets_24h: float = Field(..., ge=0, le=2000)
    worst_bilirubin_24h: float = Field(..., ge=0, le=100)
    worst_glucose_24h: float = Field(..., ge=0, le=2000)
    worst_hemoglobin_24h: float = Field(..., ge=0, le=30)
    worst_bicarbonate_24h: float = Field(..., ge=0, le=100)
    # ... (additional 18 lab values)

    # ICU Details (10 features)
    icu_type: str = Field(..., description="Medical/Surgical/Cardiac")
    ventilation_flag: bool = Field(..., description="Mechanical ventilation")
    vasopressor_flag: bool = Field(..., description="Vasopressor use")
    dialysis_flag: bool = Field(..., description="Dialysis")
    age: int = Field(..., ge=18, le=120)
    gender: str = Field(..., pattern="^(M|F)$")
    bmi: float = Field(..., ge=10, le=100)
    admission_source: str = Field(..., description="Emergency/Transfer/Direct")
    comorbidity_count: int = Field(..., ge=0, le=20)
    icu_los_24h: float = Field(..., ge=0, le=24, description="Always 24 for this cohort")

    # Diagnosis Flags (4 features)
    sepsis_flag: bool
    shock_flag: bool
    cardiac_arrest_flag: bool
    trauma_flag: bool


class MortalityPredictionRequest(BaseModel):
    """Request for mortality prediction"""
    patient_id: str
    features: MortalityFeatures


class MortalityPredictionResponse(BaseModel):
    """Response from mortality prediction"""
    patient_id: str
    prediction: PredictionDetail
    top_features: List[FeatureContribution] = Field(..., max_items=10)
    metadata: dict
