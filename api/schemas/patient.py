"""
Pydantic schemas for Patient API
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class PatientBase(BaseModel):
    """Base patient schema"""
    full_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(M|F|Other)$")
    department: Optional[str] = Field(None, max_length=100)
    chief_complaint: Optional[str] = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v and v not in ['M', 'F', 'Other']:
            raise ValueError('Gender must be M, F, or Other')
        return v


class PatientCreate(PatientBase):
    """Schema for creating a new patient"""
    patient_code: str = Field(..., min_length=1, max_length=50)
    admission_date: Optional[datetime] = None

    # Sensitive PII (will be encrypted)
    ssn: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    # Medical data (stored as JSON)
    medical_history: Optional[dict] = None
    current_medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class PatientUpdate(BaseModel):
    """Schema for updating patient data"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(M|F|Other)$")
    department: Optional[str] = Field(None, max_length=100)
    chief_complaint: Optional[str] = None
    discharge_date: Optional[datetime] = None
    is_active: Optional[bool] = None

    # Medical data
    medical_history: Optional[dict] = None
    current_medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: int
    patient_code: str
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Note: Encrypted fields are NOT returned in API responses for security

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    """Schema for paginated patient list"""
    total: int
    patients: List[PatientResponse]
    page: int
    page_size: int
    total_pages: int
