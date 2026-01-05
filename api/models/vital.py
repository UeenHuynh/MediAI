"""
Vital signs model for MediAI patient monitoring.

Stores vital signs, lab results, and clinical measurements.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class Vital(Base):
    """Vital signs and clinical measurements"""

    __tablename__ = "vitals"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Vital Signs
    heart_rate = Column(Integer, nullable=True)  # bpm
    systolic_bp = Column(Integer, nullable=True)  # mmHg
    diastolic_bp = Column(Integer, nullable=True)  # mmHg
    mean_arterial_pressure = Column(Numeric(5, 1), nullable=True)  # mmHg
    temperature = Column(Numeric(4, 1), nullable=True)  # Celsius
    respiratory_rate = Column(Integer, nullable=True)  # breaths/min
    spo2 = Column(Integer, nullable=True)  # %

    # Glasgow Coma Scale
    gcs_eye = Column(Integer, nullable=True)  # 1-4
    gcs_verbal = Column(Integer, nullable=True)  # 1-5
    gcs_motor = Column(Integer, nullable=True)  # 1-6
    gcs_total = Column(Integer, nullable=True)  # 3-15

    # Additional measurements
    weight = Column(Numeric(5, 1), nullable=True)  # kg
    height = Column(Numeric(5, 1), nullable=True)  # cm
    bmi = Column(Numeric(4, 1), nullable=True)

    # Clinical notes
    notes = Column(Text, nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="vitals")

    def __repr__(self):
        return f"<Vital(id={self.id}, patient_id={self.patient_id}, recorded_at={self.recorded_at})>"
