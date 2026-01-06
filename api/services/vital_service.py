"""
Vital Signs CRUD Service

Handles all database operations for vital signs management.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.vital import Vital
from schemas.vital import VitalCreate


class VitalService:
    """Service for vital signs CRUD operations"""

    @staticmethod
    def create_vital(
        db: Session,
        vital_data: VitalCreate,
        recorded_by: Optional[int] = None
    ) -> Vital:
        """
        Create a new vital signs record

        Args:
            db: Database session
            vital_data: Vital signs data
            recorded_by: User ID who recorded the vitals

        Returns:
            Created Vital object
        """
        vital = Vital(
            patient_id=vital_data.patient_id,
            recorded_at=vital_data.recorded_at or datetime.utcnow(),
            heart_rate=vital_data.heart_rate,
            systolic_bp=vital_data.systolic_bp,
            diastolic_bp=vital_data.diastolic_bp,
            mean_arterial_pressure=vital_data.mean_arterial_pressure,
            temperature=vital_data.temperature,
            respiratory_rate=vital_data.respiratory_rate,
            spo2=vital_data.spo2,
            gcs_eye=vital_data.gcs_eye,
            gcs_verbal=vital_data.gcs_verbal,
            gcs_motor=vital_data.gcs_motor,
            gcs_total=vital_data.gcs_total,
            weight=vital_data.weight,
            height=vital_data.height,
            bmi=vital_data.bmi,
            notes=vital_data.notes,
            recorded_by=recorded_by,
        )

        db.add(vital)
        db.commit()
        db.refresh(vital)
        return vital

    @staticmethod
    def get_vital(db: Session, vital_id: int) -> Optional[Vital]:
        """
        Get vital signs record by ID

        Args:
            db: Database session
            vital_id: Vital record ID

        Returns:
            Vital object or None if not found
        """
        return db.query(Vital).filter(Vital.id == vital_id).first()

    @staticmethod
    def list_vitals_for_patient(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Vital], int]:
        """
        List all vital signs for a specific patient

        Args:
            db: Database session
            patient_id: Patient ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of vitals, total count)
        """
        query = db.query(Vital).filter(Vital.patient_id == patient_id)

        # Get total count
        total = query.count()

        # Get records ordered by most recent first
        vitals = query.order_by(
            desc(Vital.recorded_at)
        ).offset(skip).limit(limit).all()

        return vitals, total

    @staticmethod
    def get_latest_vitals(db: Session, patient_id: int, count: int = 1) -> List[Vital]:
        """
        Get the most recent vital signs for a patient

        Args:
            db: Database session
            patient_id: Patient ID
            count: Number of recent records to return

        Returns:
            List of most recent Vital objects
        """
        return db.query(Vital).filter(
            Vital.patient_id == patient_id
        ).order_by(
            desc(Vital.recorded_at)
        ).limit(count).all()

    @staticmethod
    def delete_vital(db: Session, vital_id: int) -> bool:
        """
        Delete a vital signs record

        Args:
            db: Database session
            vital_id: Vital record ID

        Returns:
            True if deleted, False if not found
        """
        vital = VitalService.get_vital(db, vital_id)
        if not vital:
            return False

        db.delete(vital)
        db.commit()
        return True
