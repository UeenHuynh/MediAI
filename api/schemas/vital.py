"""
Pydantic schemas for Vital Signs API
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class VitalBase(BaseModel):
    """Base vital signs schema"""
    # Vital Signs
    heart_rate: Optional[int] = Field(None, ge=0, le=300)
    systolic_bp: Optional[int] = Field(None, ge=0, le=300)
    diastolic_bp: Optional[int] = Field(None, ge=0, le=200)
    mean_arterial_pressure: Optional[Decimal] = Field(None, ge=0, le=250)
    temperature: Optional[Decimal] = Field(None, ge=30, le=45, description="Temperature in Celsius")
    respiratory_rate: Optional[int] = Field(None, ge=0, le=100)
    spo2: Optional[int] = Field(None, ge=0, le=100, description="Oxygen saturation %")

    # Glasgow Coma Scale
    gcs_eye: Optional[int] = Field(None, ge=1, le=4)
    gcs_verbal: Optional[int] = Field(None, ge=1, le=5)
    gcs_motor: Optional[int] = Field(None, ge=1, le=6)
    gcs_total: Optional[int] = Field(None, ge=3, le=15)

    # Additional measurements
    weight: Optional[Decimal] = Field(None, ge=0, le=500, description="Weight in kg")
    height: Optional[Decimal] = Field(None, ge=0, le=300, description="Height in cm")
    bmi: Optional[Decimal] = Field(None, ge=0, le=100)

    # Notes
    notes: Optional[str] = None


class VitalCreate(VitalBase):
    """Schema for creating vital signs record"""
    patient_id: int
    recorded_at: Optional[datetime] = None


class VitalResponse(VitalBase):
    """Schema for vital signs response"""
    id: int
    patient_id: int
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class VitalListResponse(BaseModel):
    """Schema for paginated vitals list"""
    total: int
    vitals: List[VitalResponse]
    page: int
    page_size: int
