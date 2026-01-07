"""
Pydantic schemas for API request/response validation
"""

from .chat import (
    ChatHistoryResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)
from .patient import (
    PatientBase,
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from .prediction import (
    PredictionListResponse,
    PredictionResponse,
)
from .vital import (
    VitalBase,
    VitalCreate,
    VitalListResponse,
    VitalResponse,
)

__all__ = [
    # Patient
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "PatientListResponse",
    # Vital
    "VitalBase",
    "VitalCreate",
    "VitalResponse",
    "VitalListResponse",
    # Prediction
    "PredictionResponse",
    "PredictionListResponse",
    # Chat
    "ChatSessionCreate",
    "ChatSessionResponse",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatHistoryResponse",
]
