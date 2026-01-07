"""
Patient API Router

Endpoints for patient management (CRUD operations).
"""

import logging
from typing import Optional

from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from services.patient_service import PatientService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    # TODO: Add authentication dependency here
    # current_user: User = Depends(get_current_user)
):
    """
    Create a new patient record.

    **Required permissions:** patients:write

    **Request body:**
    - patient_code: Unique patient identifier
    - full_name: Patient's full name
    - Optional: demographics, medical history, etc.

    **Returns:**
    - Created patient object (without encrypted PII)
    """
    try:
        # Check if patient code already exists
        existing = PatientService.get_patient_by_code(db, patient_data.patient_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Patient with code '{patient_data.patient_code}' already exists",
            )

        # Create patient
        # TODO: Pass current_user.id as created_by
        patient = PatientService.create_patient(db, patient_data, created_by=None)

        logger.info(f"Created patient: {patient.patient_code}")
        return patient

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient",
        )


@router.get(
    "/{patient_id}", response_model=PatientResponse, summary="Get patient by ID"
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Get a patient by ID.

    **Required permissions:** patients:read

    **Returns:**
    - Patient object (without encrypted PII)
    """
    patient = PatientService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )

    return patient


@router.get(
    "/", response_model=PatientListResponse, summary="List patients with pagination"
)
def list_patients(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search in patient code or name"),
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    List patients with pagination and optional filters.

    **Required permissions:** patients:read

    **Query parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - department: Filter by department
    - search: Search query for patient code or name

    **Returns:**
    - Paginated list of patients
    """
    skip = (page - 1) * page_size
    patients, total = PatientService.list_patients(
        db, skip=skip, limit=page_size, department=department, search=search
    )

    total_pages = (total + page_size - 1) // page_size

    return PatientListResponse(
        total=total,
        patients=patients,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.put("/{patient_id}", response_model=PatientResponse, summary="Update patient")
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Update patient information.

    **Required permissions:** patients:write

    **Request body:**
    - Any patient fields to update (partial update supported)

    **Returns:**
    - Updated patient object
    """
    patient = PatientService.update_patient(db, patient_id, patient_data)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )

    logger.info(f"Updated patient: {patient.patient_code}")
    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete patient (soft delete)",
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Soft delete a patient (sets is_active=False).

    **Required permissions:** patients:delete

    **Note:** This is a soft delete. The patient record is kept in the database
    but marked as inactive.
    """
    success = PatientService.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )

    logger.info(f"Deleted patient ID: {patient_id}")
    return None


@router.get(
    "/code/{patient_code}",
    response_model=PatientResponse,
    summary="Get patient by code",
)
def get_patient_by_code(
    patient_code: str,
    db: Session = Depends(get_db),
    # TODO: Add authentication
):
    """
    Get a patient by patient code.

    **Required permissions:** patients:read

    **Returns:**
    - Patient object
    """
    patient = PatientService.get_patient_by_code(db, patient_code)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with code '{patient_code}' not found",
        )

    return patient
