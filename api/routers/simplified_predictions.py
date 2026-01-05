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

    Uses smart feature imputation to make vent/vaso flags affect predictions
    """
    import time

    patient_id = request.patient_id or f"WEB_{int(time.time())}"

    # Convert to dict for imputation
    patient_data = {
        "age": request.age,
        "gender": request.gender,
        "sofa_score": request.sofa_score,
        "los_hours": request.los_hours,
        "charlson_index": request.charlson_index,
        "mechanical_ventilation": request.mechanical_ventilation,
        "vasopressor_use": request.vasopressor_use,
    }

    # Impute full 61 features - vent/vaso flags will affect GCS, FiO2, SpO2, MAP, lactate
    full_features = imputer.impute_mortality_features(patient_data)

    # Create full prediction request
    mortality_request = MortalityPredictionRequest(
        patient_id=patient_id,
        features=MortalityFeatures(**full_features)
    )

    # Call prediction service
    result = await prediction_service.predict_mortality(mortality_request, None)

    return result
