"""
Pydantic schemas for Prediction History API
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class PredictionResponse(BaseModel):
    """Schema for prediction history response"""
    id: int
    patient_id: Optional[int] = None
    prediction_type: str  # 'sepsis' or 'mortality'
    model_version: str

    # Input and results
    input_features: dict
    risk_score: Decimal
    risk_percentage: Decimal
    risk_category: Optional[str] = None
    confidence: Optional[Decimal] = None

    # SHAP explanations
    shap_values: Optional[dict] = None
    top_features: Optional[dict] = None

    # Metadata
    predicted_by: Optional[int] = None
    predicted_at: datetime

    # Outcome tracking
    actual_outcome: Optional[bool] = None
    outcome_recorded_at: Optional[datetime] = None
    outcome_notes: Optional[str] = None

    created_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class PredictionListResponse(BaseModel):
    """Schema for paginated predictions list"""
    total: int
    predictions: List[PredictionResponse]
    page: int
    page_size: int
