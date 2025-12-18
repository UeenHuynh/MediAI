"""
Doctors API router for MediAI.

Provides endpoints for listing and retrieving doctor information.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from core.rbac import require_authenticated, UserWithRole


router = APIRouter(prefix="/doctors", tags=["doctors"])


# --- Pydantic Models ---

class DoctorBase(BaseModel):
    """Base doctor schema"""
    name: str
    specialty: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    available: bool = True


class DoctorResponse(DoctorBase):
    """Doctor response with ID"""
    id: int
    years_experience: int = 0
    rating: float = 4.5
    patients_count: int = 0
    
    class Config:
        from_attributes = True


class DoctorListResponse(BaseModel):
    """Paginated list of doctors"""
    doctors: List[DoctorResponse]
    total: int
    page: int
    page_size: int


# --- Mock Data (replace with database in production) ---

MOCK_DOCTORS = [
    DoctorResponse(
        id=1,
        name="Dr. Sarah Chen",
        specialty="Critical Care Medicine",
        email="sarah.chen@mediai.com",
        phone="+1-555-0101",
        department="ICU",
        avatar_url="/avatars/doctor-1.jpg",
        available=True,
        years_experience=12,
        rating=4.9,
        patients_count=1247,
    ),
    DoctorResponse(
        id=2,
        name="Dr. Michael Torres",
        specialty="Pulmonology",
        email="michael.torres@mediai.com",
        phone="+1-555-0102",
        department="Respiratory",
        avatar_url="/avatars/doctor-2.jpg",
        available=True,
        years_experience=8,
        rating=4.7,
        patients_count=892,
    ),
    DoctorResponse(
        id=3,
        name="Dr. Emily Watson",
        specialty="Infectious Disease",
        email="emily.watson@mediai.com",
        phone="+1-555-0103",
        department="Infectious Disease",
        avatar_url="/avatars/doctor-3.jpg",
        available=False,
        years_experience=15,
        rating=4.8,
        patients_count=2103,
    ),
    DoctorResponse(
        id=4,
        name="Dr. James Park",
        specialty="Emergency Medicine",
        email="james.park@mediai.com",
        phone="+1-555-0104",
        department="Emergency",
        avatar_url="/avatars/doctor-4.jpg",
        available=True,
        years_experience=10,
        rating=4.6,
        patients_count=1589,
    ),
    DoctorResponse(
        id=5,
        name="Dr. Lisa Nguyen",
        specialty="Nephrology",
        email="lisa.nguyen@mediai.com",
        phone="+1-555-0105",
        department="Renal",
        avatar_url="/avatars/doctor-5.jpg",
        available=True,
        years_experience=7,
        rating=4.9,
        patients_count=634,
    ),
]


# --- Endpoints ---

@router.get("", response_model=DoctorListResponse)
async def list_doctors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    search: Optional[str] = Query(None, description="Search by name"),
    user: UserWithRole = Depends(require_authenticated),
):
    """
    List all doctors with pagination and filtering.
    
    - **page**: Page number (starting from 1)
    - **page_size**: Number of items per page (max 50)
    - **specialty**: Filter by specialty
    - **available**: Filter by availability status
    - **search**: Search doctors by name
    """
    # Filter doctors
    filtered = MOCK_DOCTORS.copy()
    
    if specialty:
        filtered = [d for d in filtered if specialty.lower() in d.specialty.lower()]
    
    if available is not None:
        filtered = [d for d in filtered if d.available == available]
    
    if search:
        filtered = [d for d in filtered if search.lower() in d.name.lower()]
    
    # Pagination
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return DoctorListResponse(
        doctors=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    user: UserWithRole = Depends(require_authenticated),
):
    """
    Get a specific doctor by ID.
    
    - **doctor_id**: The unique identifier of the doctor
    """
    for doctor in MOCK_DOCTORS:
        if doctor.id == doctor_id:
            return doctor
    
    raise HTTPException(status_code=404, detail="Doctor not found")


@router.get("/{doctor_id}/schedule")
async def get_doctor_schedule(
    doctor_id: int,
    user: UserWithRole = Depends(require_authenticated),
):
    """
    Get a doctor's availability schedule.
    
    Returns mock schedule data.
    """
    # Find doctor
    doctor = None
    for d in MOCK_DOCTORS:
        if d.id == doctor_id:
            doctor = d
            break
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Mock schedule
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.name,
        "schedule": [
            {"day": "Monday", "hours": "9:00 AM - 5:00 PM", "available": True},
            {"day": "Tuesday", "hours": "9:00 AM - 5:00 PM", "available": True},
            {"day": "Wednesday", "hours": "9:00 AM - 1:00 PM", "available": True},
            {"day": "Thursday", "hours": "9:00 AM - 5:00 PM", "available": True},
            {"day": "Friday", "hours": "9:00 AM - 3:00 PM", "available": True},
            {"day": "Saturday", "hours": "Closed", "available": False},
            {"day": "Sunday", "hours": "Closed", "available": False},
        ],
    }
