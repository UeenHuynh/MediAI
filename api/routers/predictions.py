"""
Prediction endpoints for sepsis and mortality models
"""

import logging

from core.database import get_db
from core.security import User, get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Request
from models.schemas import (
    MortalityPredictionRequest,
    MortalityPredictionResponse,
    SepsisPredictionRequest,
    SepsisPredictionResponse,
)
from services.prediction_service import PredictionService
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Initialize prediction service
prediction_service = PredictionService()


@router.post("/predict/sepsis", response_model=SepsisPredictionResponse)
@limiter.limit("100/minute")
async def predict_sepsis(
    request: Request,
    sepsis_request: SepsisPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Predict sepsis risk for ICU patient

    Returns:
        - risk_score: Probability of sepsis onset within 6 hours (0-1)
        - risk_level: LOW, MEDIUM, HIGH, or CRITICAL
        - top_features: Most important features contributing to prediction
        - recommendation: Clinical recommendation based on risk level
    """
    try:
        logger.info("Sepsis prediction request for patient: %s", sepsis_request.patient_id)

        # Get prediction
        result = await prediction_service.predict_sepsis(sepsis_request, db)

        logger.info("Sepsis prediction completed: %s", result.prediction.risk_level)
        return result

    except ValueError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed") from e


@router.post("/predict/mortality", response_model=MortalityPredictionResponse)
@limiter.limit("100/minute")
async def predict_mortality(
    request: Request,
    mortality_request: MortalityPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Predict mortality risk for ICU patient

    Returns:
        - risk_score: Probability of hospital mortality (0-1)
        - risk_level: LOW, MEDIUM, HIGH, or CRITICAL
        - top_features: Most important features contributing to prediction
        - recommendation: Clinical recommendation based on risk level
    """
    try:
        logger.info("Mortality prediction request for patient: %s", mortality_request.patient_id)

        # Get prediction
        result = await prediction_service.predict_mortality(mortality_request, db)

        logger.info("Mortality prediction completed: %s", result.prediction.risk_level)
        return result

    except ValueError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed") from e


@router.get("/models/info")
async def get_models_info():
    """Get information about loaded models (v2)"""
    return {
        "sepsis_model": {
            "version": "v2.0",
            "features": 42,
            "algorithm": "LightGBM",
            "target": "sepsis_onset_within_6h",
            "source": "features_sepsis_6h.csv",
            "metrics": {
                "auc_roc": 0.847,
                "accuracy": 0.83,
                "recall": 0.53,
            },
        },
        "mortality_model": {
            "version": "v2.0",
            "features": 61,
            "algorithm": "LightGBM",
            "target": "hospital_mortality",
            "source": "features_mortality_24h.csv",
            "metrics": {
                "auc_roc": 0.963,
                "accuracy": 0.94,
                "recall": 0.64,
            },
        },
    }
