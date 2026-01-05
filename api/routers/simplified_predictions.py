"""
Simplified prediction endpoints for web UI
Requires only basic vitals, uses smart feature imputation
"""
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional

from core.rbac import require_permission, UserWithRole
from services.feature_imputation import FeatureImputer
from services.prediction_service import PredictionService
from models.schemas import (
    SepsisPredictionRequest,
    SepsisFeatures,
    MortalityPredictionRequest,
    MortalityFeatures,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict/simple", tags=["simplified-predictions"])

# Initialize services
imputer = FeatureImputer()
prediction_service = PredictionService()


class SimplifiedSepsisRequest(BaseModel):
    """Simplified sepsis prediction - only basic vitals needed"""
    patient_id: Optional[str] = None
    age: int = Field(..., ge=18, le=120)
    heart_rate: float = Field(..., ge=0, le=300)
    temperature: float = Field(..., ge=30, le=45)
    respiratory_rate: float = Field(..., ge=0, le=60)
    systolic_bp: float = Field(..., ge=0, le=300)
    diastolic_bp: float = Field(..., ge=0, le=200)
    spo2: float = Field(..., ge=0, le=100, description="Oxygen saturation")
    wbc: Optional[float] = Field(None, ge=0, description="White blood cell count")
    lactate: Optional[float] = Field(None, ge=0, description="Lactate level")
    creatinine: Optional[float] = Field(None, ge=0, description="Creatinine level")


class SimplifiedMortalityRequest(BaseModel):
    """Simplified mortality prediction"""
    patient_id: Optional[str] = None
    age: int = Field(..., ge=18, le=120)
    gender: str = Field(..., description="M or F")
    sofa_score: int = Field(..., ge=0, le=24, description="Total SOFA score")
    los_hours: float = Field(..., ge=0, description="ICU length of stay in hours")
    mechanical_ventilation: bool = False
    vasopressor_use: bool = False
    charlson_index: int = Field(0, ge=0, le=30)


@router.post("/sepsis")
async def predict_sepsis_simplified(
    request: SimplifiedSepsisRequest,
    user: UserWithRole = Depends(require_permission("predictions:write")),
):
    """
    Simplified sepsis prediction endpoint
    
    Requires only basic vitals - backend will impute missing features
    """
    import time
    from datetime import datetime
    
    patient_id = request.patient_id or f"WEB_{int(time.time())}"
    
    # Convert to dict for imputation
    vital_signs = {
        "age": request.age,
        "heart_rate": request.heart_rate,
        "temperature": request.temperature,
        "respiratory_rate": request.respiratory_rate,
        "systolic_bp": request.systolic_bp,
        "diastolic_bp": request.diastolic_bp,
        "spo2": request.spo2,
        "wbc": request.wbc,
        "lactate": request.lactate,
        "creatinine": request.creatinine,
    }
    
    # Impute full 42 features
    full_features = imputer.impute_sepsis_features(vital_signs)
    
    # Create full prediction request
    sepsis_request = SepsisPredictionRequest(
        patient_id=patient_id,
        features=SepsisFeatures(**full_features)
    )
    
    # Call prediction service
    result = await prediction_service.predict_sepsis(sepsis_request, None)
    
    return result


@router.post("/mortality")
async def predict_mortality_simplified(
    request: SimplifiedMortalityRequest,
    user: UserWithRole = Depends(require_permission("predictions:write")),
):
    """
    Simplified mortality prediction endpoint
    """
    import time
    
    patient_id = request.patient_id or f"WEB_{int(time.time())}"
    
    # Calculate features from SOFA and other inputs
    # SOFA components (distributed evenly for simplicity)
    sofa_per_organ = request.sofa_score / 6
    
    # Create full 61 features with realistic defaults
    full_features = {
        # SOFA scores
        "respiratory_sofa": min(4, int(sofa_per_organ)),
        "cardiovascular_sofa": min(4, int(sofa_per_organ)),
        "hepatic_sofa": min(4, int(sofa_per_organ)),
        "coagulation_sofa": min(4, int(sofa_per_organ)),
        "renal_sofa": min(4, int(sofa_per_organ)),
        "neurological_sofa": min(4, int(sofa_per_organ)),
        # APACHE-II
        "age_points": 0 if request.age < 45 else (2 if request.age < 55 else (3 if request.age < 65 else (5 if request.age < 75 else 6))),
        "gcs_score": 15.0 - (request.sofa_score / 4),  # Approximate from SOFA
        # Worst values - use median values from training data
        "worst_hr_24h": 90.0 + (request.sofa_score * 3),
        "worst_sbp_24h": 120.0 - (request.sofa_score * 2),
        "worst_temp_24h": 37.0 + (request.sofa_score * 0.2),
        "worst_rr_24h": 18.0 + (request.sofa_score * 1),
        "worst_pao2_24h": 90.0 - (request.sofa_score * 2),
        "worst_ph_24h": 7.4 - (request.sofa_score * 0.01),
        "worst_sodium_24h": 140.0,
        "worst_potassium_24h": 4.0,
        "worst_creatinine_24h": 1.0 + (request.sofa_score * 0.2),
        "worst_hematocrit_24h": 40.0,
        "worst_wbc_24h": 7.5 + (request.sofa_score * 1.5),
        "worst_lactate_24h": 1.5 + (request.sofa_score * 0.3),
        "worst_platelets_24h": 200.0 - (request.sofa_score * 10),
        "worst_bilirubin_24h": 1.0 + (request.sofa_score * 0.15),
        "worst_glucose_24h": 100.0 + (request.sofa_score * 10),
        "worst_hemoglobin_24h": 12.0 - (request.sofa_score * 0.3),
        "worst_bicarbonate_24h": 24.0 - (request.sofa_score * 0.5),
        "worst_albumin_24h": 3.5 - (request.sofa_score * 0.1),
        "worst_ast_24h": 30.0 + (request.sofa_score * 15),
        "worst_alt_24h": 30.0 + (request.sofa_score * 10),
        # Additional labs
        "worst_bun_24h": 20.0 + (request.sofa_score * 5),
        "worst_chloride_24h": 100.0,
        "worst_inr_24h": 1.0 + (request.sofa_score * 0.1),
        "worst_ptt_24h": 30.0,
        "worst_troponin_24h": 0.01,
        "worst_bnp_24h": 100.0,
        "worst_anion_gap_24h": 12.0,
        "worst_paco2_24h": 40.0,
        "worst_map_24h": 90.0 - (request.sofa_score * 2),
        "worst_spo2_24h": 96.0 - (request.sofa_score * 1.5),
        # Min/Max vitals
        "min_hr_24h": 60.0,
        "max_hr_24h": 100.0 + (request.sofa_score * 5),
        "min_sbp_24h": 100.0 - (request.sofa_score * 3),
        "max_sbp_24h": 140.0,
        "min_temp_24h": 36.5,
        "max_temp_24h": 37.5 + (request.sofa_score * 0.2),
        "min_rr_24h": 12.0,
        "max_rr_24h": 20.0 + (request.sofa_score * 2),
        # Additional
        "worst_fio2_24h": 21.0 + (request.sofa_score * 5),
        # ICU details
        "icu_type": 1,
        "ventilation_flag": 1 if request.mechanical_ventilation else 0,
        "vasopressor_flag": 1 if request.vasopressor_use else 0,
        "dialysis_flag": 1 if request.sofa_score > 12 else 0,
        "age": request.age,
        "gender": 1 if request.gender == "M" else 0,
        # Patient info
        "bmi": 25.0,
        "admission_source": 1,
        "comorbidity_count": request.charlson_index,
        # Time
        "icu_los_24h": min(24.0, request.los_hours),
        # Flags
        "sepsis_flag": 1 if request.sofa_score > 6 else 0,
        "shock_flag": 1 if request.vasopressor_use else 0,
        "cardiac_arrest_flag": 0,
        "trauma_flag": 0,
    }
    
    # Create full prediction request
    mortality_request = MortalityPredictionRequest(
        patient_id=patient_id,
        features=MortalityFeatures(**full_features)
    )
    
    # Call prediction service
    result = await prediction_service.predict_mortality(mortality_request, None)
    
    return result
