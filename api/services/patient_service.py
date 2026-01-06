"""
Patient CRUD Service

Handles all database operations for patient management.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.patient import Patient
from schemas.patient import PatientCreate, PatientUpdate
from core.encryption import encrypt_field, decrypt_field


class PatientService:
    """Service for patient CRUD operations"""

    @staticmethod
    def create_patient(
        db: Session,
        patient_data: PatientCreate,
        created_by: Optional[int] = None
    ) -> Patient:
        """
        Create a new patient with encrypted PII

        Args:
            db: Database session
            patient_data: Patient creation data
            created_by: User ID who created the patient

        Returns:
            Created Patient object
        """
        # Prepare medical history data
        medical_history = patient_data.medical_history or {}
        current_medications = {"medications": patient_data.current_medications or []}
        allergies = {"allergies": patient_data.allergies or []}

        # Create patient with encrypted sensitive fields
        patient = Patient(
            patient_code=patient_data.patient_code,
            full_name=patient_data.full_name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            admission_date=patient_data.admission_date,
            department=patient_data.department,
            chief_complaint=patient_data.chief_complaint,
            # Encrypt sensitive PII
            encrypted_ssn=encrypt_field(patient_data.ssn) if patient_data.ssn else None,
            encrypted_address=encrypt_field(patient_data.address) if patient_data.address else None,
            encrypted_phone=encrypt_field(patient_data.phone) if patient_data.phone else None,
            # JSON fields
            medical_history=medical_history,
            current_medications=current_medications,
            allergies=allergies,
            # Metadata
            created_by=created_by,
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
        """
        Get patient by ID

        Args:
            db: Database session
            patient_id: Patient ID

        Returns:
            Patient object or None if not found
        """
        return db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.is_active == True
        ).first()

    @staticmethod
    def get_patient_by_code(db: Session, patient_code: str) -> Optional[Patient]:
        """
        Get patient by patient code

        Args:
            db: Database session
            patient_code: Patient code

        Returns:
            Patient object or None if not found
        """
        return db.query(Patient).filter(
            Patient.patient_code == patient_code,
            Patient.is_active == True
        ).first()

    @staticmethod
    def list_patients(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        department: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Patient], int]:
        """
        List patients with pagination and filters

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            department: Filter by department
            search: Search in patient code or name

        Returns:
            Tuple of (list of patients, total count)
        """
        query = db.query(Patient).filter(Patient.is_active == True)

        # Apply filters
        if department:
            query = query.filter(Patient.department == department)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Patient.patient_code.ilike(search_pattern)) |
                (Patient.full_name.ilike(search_pattern))
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        patients = query.order_by(
            Patient.admission_date.desc()
        ).offset(skip).limit(limit).all()

        return patients, total

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: int,
        patient_data: PatientUpdate
    ) -> Optional[Patient]:
        """
        Update patient information

        Args:
            db: Database session
            patient_id: Patient ID
            patient_data: Updated patient data

        Returns:
            Updated Patient object or None if not found
        """
        patient = PatientService.get_patient(db, patient_id)
        if not patient:
            return None

        # Update fields if provided
        update_data = patient_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(patient, field):
                setattr(patient, field, value)

        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def delete_patient(db: Session, patient_id: int) -> bool:
        """
        Soft delete a patient (set is_active=False)

        Args:
            db: Database session
            patient_id: Patient ID

        Returns:
            True if deleted, False if not found
        """
        patient = PatientService.get_patient(db, patient_id)
        if not patient:
            return False

        patient.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_active_patients_count(db: Session) -> int:
        """
        Get count of active patients

        Args:
            db: Database session

        Returns:
            Count of active patients
        """
        return db.query(func.count(Patient.id)).filter(
            Patient.is_active == True
        ).scalar()
