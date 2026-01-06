"""
Vital Signs API Router

Endpoints for vital signs management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.vital import VitalCreate, VitalResponse, VitalListResponse
from services.vital_service import VitalService
from services.patient_service import PatientService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vitals", tags=["vitals"])


@router.post(
    "/",
    response_model=VitalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record vital signs"
)
def create_vital(
    vital_data: VitalCreate,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Record vital signs for a patient.

    **Required permissions:** vitals:write

    **Request body:**
    - patient_id: Patient ID
    - Vital signs measurements (heart_rate, bp, temperature, etc.)

    **Returns:**
    - Created vital signs record
    """
    try:
        # Verify patient exists
        patient = PatientService.get_patient(db, vital_data.patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {vital_data.patient_id} not found"
            )

        # Create vital record
        vital = VitalService.create_vital(db, vital_data, recorded_by=None)

        logger.info(f"Created vital record for patient {vital_data.patient_id}")
        return vital

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vital record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vital record"
        )


@router.get(
    "/{vital_id}",
    response_model=VitalResponse,
    summary="Get vital signs by ID"
)
def get_vital(
    vital_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific vital signs record by ID.

    **Required permissions:** vitals:read
    """
    vital = VitalService.get_vital(db, vital_id)
    if not vital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vital record with ID {vital_id} not found"
        )

    return vital


@router.get(
    "/patient/{patient_id}",
    response_model=VitalListResponse,
    summary="Get all vitals for a patient"
)
def list_patient_vitals(
    patient_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all vital signs records for a specific patient.

    **Required permissions:** vitals:read

    **Returns:**
    - Paginated list of vital signs (most recent first)
    """
    # Verify patient exists
    patient = PatientService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    skip = (page - 1) * page_size
    vitals, total = VitalService.list_vitals_for_patient(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=page_size
    )

    return VitalListResponse(
        total=total,
        vitals=vitals,
        page=page,
        page_size=page_size
    )


@router.get(
    "/patient/{patient_id}/latest",
    response_model=VitalResponse,
    summary="Get latest vital signs"
)
def get_latest_vitals(
    patient_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the most recent vital signs for a patient.

    **Required permissions:** vitals:read
    """
    vitals = VitalService.get_latest_vitals(db, patient_id, count=1)
    if not vitals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No vital signs found for patient {patient_id}"
        )

    return vitals[0]


@router.delete(
    "/{vital_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vital signs record"
)
def delete_vital(
    vital_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a vital signs record.

    **Required permissions:** vitals:delete
    """
    success = VitalService.delete_vital(db, vital_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vital record with ID {vital_id} not found"
        )

    logger.info(f"Deleted vital record ID: {vital_id}")
    return None
