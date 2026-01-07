"""
Patient model for MediAI patient management.

Stores patient demographics, admission data, and medical history.
"""

from datetime import date, datetime
from typing import Optional

from core.database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class Patient(Base):
    """Patient model for patient management"""

    __tablename__ = "patients"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(50), unique=True, index=True, nullable=False)

    # Demographics
    full_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)  # 'M', 'F', 'Other'

    # Admission
    admission_date = Column(DateTime, nullable=True)
    department = Column(String(100), nullable=True)

    # Encrypted PII (HIPAA compliance)
    encrypted_ssn = Column(Text, nullable=True)
    encrypted_address = Column(Text, nullable=True)
    encrypted_phone = Column(Text, nullable=True)

    # Clinical data
    chief_complaint = Column(Text, nullable=True)
    medical_history = Column(JSON, nullable=True)  # JSONB for flexible data
    current_medications = Column(JSON, nullable=True)
    allergies = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    discharge_date = Column(DateTime, nullable=True)

    # Metadata
    created_by = Column(Integer, ForeignKey("public.users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vitals = relationship(
        "Vital", back_populates="patient", cascade="all, delete-orphan"
    )
    predictions = relationship(
        "Prediction", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Patient(id={self.id}, code='{self.patient_code}', name='{self.full_name}')>"
