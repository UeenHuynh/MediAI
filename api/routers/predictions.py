"""
Prediction endpoints for sepsis and mortality models
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from models.schemas import (
    SepsisPredictionRequest,
    SepsisPredictionResponse,
    MortalityPredictionRequest,
    MortalityPredictionResponse
)
from services.prediction_service import PredictionService
from core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize prediction service
prediction_service = PredictionService()


@router.post("/predict/sepsis", response_model=SepsisPredictionResponse)
async def predict_sepsis(
    request: SepsisPredictionRequest,
    db: Session = Depends(get_db)
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
        logger.info(f"Sepsis prediction request for patient: {request.patient_id}")

        # Get prediction
        result = await prediction_service.predict_sepsis(request, db)

        logger.info(f"Sepsis prediction completed: {result.prediction.risk_level}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.post("/predict/mortality", response_model=MortalityPredictionResponse)
async def predict_mortality(
    request: MortalityPredictionRequest,
    db: Session = Depends(get_db)
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
        logger.info(f"Mortality prediction request for patient: {request.patient_id}")

        # Get prediction
        result = await prediction_service.predict_mortality(request, db)

        logger.info(f"Mortality prediction completed: {result.prediction.risk_level}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.get("/models/info")
async def get_models_info():
    """Get information about loaded models"""
    return {
        "sepsis_model": {
            "version": "v1",
            "features": 42,
            "algorithm": "LightGBM",
            "target": "sepsis_onset_within_6h"
        },
        "mortality_model": {
            "version": "v1",
            "features": 65,
            "algorithm": "LightGBM",
            "target": "hospital_mortality"
        }
    }
