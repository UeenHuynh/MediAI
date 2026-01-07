"""
Prediction model for MediAI prediction history.

Stores all sepsis and mortality predictions with input features and SHAP explanations.
"""

from datetime import datetime
from typing import Optional

from core.database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship


class Prediction(Base):
    """Prediction history for sepsis and mortality models"""

    __tablename__ = "predictions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(
        Integer,
        ForeignKey("public.patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Prediction metadata
    prediction_type = Column(
        String(20), nullable=False, index=True
    )  # 'sepsis' or 'mortality'
    model_version = Column(String(20), default="v2", nullable=False)
    model_file = Column(String(100), nullable=True)

    # Input features (stored as JSONB for flexibility)
    input_features = Column(JSON, nullable=False)

    # Prediction results
    risk_score = Column(Numeric(6, 4), nullable=False)  # 0.0000 to 1.0000
    risk_percentage = Column(Numeric(5, 2), nullable=False)  # 0.00 to 100.00
    confidence = Column(Numeric(6, 4), nullable=True)

    # Risk category (calculated from risk_percentage)
    risk_category = Column(
        String(20), nullable=True
    )  # 'low', 'medium', 'high', 'critical'

    # SHAP explanations (for interpretability)
    shap_values = Column(JSON, nullable=True)
    top_features = Column(JSON, nullable=True)  # Top 5-10 contributing features

    # User and timing
    predicted_by = Column(Integer, ForeignKey("public.users.id"), nullable=True)
    predicted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Outcome tracking (for model evaluation)
    actual_outcome = Column(Boolean, nullable=True)  # True/False/NULL
    outcome_recorded_at = Column(DateTime, nullable=True)
    outcome_notes = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(id={self.id}, type='{self.prediction_type}', risk={self.risk_percentage}%)>"

    @property
    def calculate_risk_category(self) -> str:
        """Calculate risk category from risk percentage"""
        if self.risk_percentage < 10:
            return "low"
        elif self.risk_percentage < 30:
            return "medium"
        elif self.risk_percentage < 70:
            return "high"
        else:
            return "critical"
