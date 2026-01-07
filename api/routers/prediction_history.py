"""
Prediction History API Router

Endpoints for viewing prediction history and statistics.
"""

import logging
from typing import Optional

from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from schemas.prediction import PredictionListResponse, PredictionResponse
from services.patient_service import PatientService
from services.prediction_history_service import PredictionHistoryService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["prediction-history"])


class OutcomeUpdate(BaseModel):
    """Schema for updating prediction outcome"""

    actual_outcome: bool
    outcome_notes: Optional[str] = None


@router.get(
    "/{prediction_id}",
    response_model=PredictionResponse,
    summary="Get prediction by ID",
)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Get a specific prediction by ID.

    **Required permissions:** predictions:read

    **Returns:**
    - Full prediction details including SHAP values
    """
    prediction = PredictionHistoryService.get_prediction(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found",
        )

    return prediction


@router.get(
    "/patient/{patient_id}/history",
    response_model=PredictionListResponse,
    summary="Get patient's prediction history",
)
def get_patient_predictions(
    patient_id: int,
    prediction_type: Optional[str] = Query(
        None, description="Filter by 'sepsis' or 'mortality'"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all predictions for a specific patient.

    **Required permissions:** predictions:read

    **Query parameters:**
    - prediction_type: Filter by 'sepsis' or 'mortality'
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 200)

    **Returns:**
    - Paginated list of predictions (most recent first)
    """
    # Verify patient exists
    patient = PatientService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )

    skip = (page - 1) * page_size
    predictions, total = PredictionHistoryService.list_predictions_for_patient(
        db,
        patient_id=patient_id,
        prediction_type=prediction_type,
        skip=skip,
        limit=page_size,
    )

    return PredictionListResponse(
        total=total, predictions=predictions, page=page, page_size=page_size
    )


@router.get(
    "/", response_model=PredictionListResponse, summary="List all predictions (admin)"
)
def list_all_predictions(
    prediction_type: Optional[str] = Query(
        None, description="Filter by 'sepsis' or 'mortality'"
    ),
    risk_category: Optional[str] = Query(None, description="Filter by risk category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
    # TODO: Add admin authentication
):
    """
    List all predictions with optional filters.

    **Required permissions:** predictions:read (admin)

    **Query parameters:**
    - prediction_type: Filter by 'sepsis' or 'mortality'
    - risk_category: Filter by 'low', 'medium', 'high', or 'critical'
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 200)

    **Returns:**
    - Paginated list of all predictions
    """
    skip = (page - 1) * page_size
    predictions, total = PredictionHistoryService.list_all_predictions(
        db,
        prediction_type=prediction_type,
        risk_category=risk_category,
        skip=skip,
        limit=page_size,
    )

    return PredictionListResponse(
        total=total, predictions=predictions, page=page, page_size=page_size
    )


@router.get(
    "/patient/{patient_id}/latest/{prediction_type}",
    response_model=PredictionResponse,
    summary="Get patient's latest prediction",
)
def get_latest_prediction(
    patient_id: int,
    prediction_type: str,
    db: Session = Depends(get_db),
):
    """
    Get the most recent prediction for a patient.

    **Required permissions:** predictions:read

    **Path parameters:**
    - patient_id: Patient ID
    - prediction_type: 'sepsis' or 'mortality'

    **Returns:**
    - Most recent prediction of the specified type
    """
    # Verify patient exists
    patient = PatientService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )

    # Validate prediction type
    if prediction_type not in ["sepsis", "mortality"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="prediction_type must be 'sepsis' or 'mortality'",
        )

    prediction = PredictionHistoryService.get_latest_prediction_for_patient(
        db, patient_id, prediction_type
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {prediction_type} predictions found for patient {patient_id}",
        )

    return prediction


@router.post(
    "/{prediction_id}/outcome",
    response_model=PredictionResponse,
    summary="Update prediction outcome",
)
def update_prediction_outcome(
    prediction_id: int,
    outcome_data: OutcomeUpdate,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Update the actual outcome for a prediction (for model evaluation).

    **Required permissions:** predictions:write

    **Request body:**
    - actual_outcome: True/False - did the predicted event occur?
    - outcome_notes: Optional notes about the outcome

    **Returns:**
    - Updated prediction object
    """
    prediction = PredictionHistoryService.update_outcome(
        db, prediction_id, outcome_data.actual_outcome, outcome_data.outcome_notes
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found",
        )

    logger.info(
        f"Updated outcome for prediction {prediction_id}: {outcome_data.actual_outcome}"
    )
    return prediction


@router.get("/statistics", summary="Get prediction statistics")
def get_prediction_statistics(
    prediction_type: Optional[str] = Query(
        None, description="Filter by 'sepsis' or 'mortality'"
    ),
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Get statistics about predictions.

    **Required permissions:** predictions:read

    **Query parameters:**
    - prediction_type: Optional filter by type

    **Returns:**
    - Statistics including counts by category, type, and averages
    """
    stats = PredictionHistoryService.get_prediction_statistics(db, prediction_type)
    return stats
