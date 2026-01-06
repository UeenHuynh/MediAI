"""
Pydantic schemas for API request/response validation
"""

from .patient import (
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)
from .vital import (
    VitalBase,
    VitalCreate,
    VitalResponse,
    VitalListResponse,
)
from .prediction import (
    PredictionResponse,
    PredictionListResponse,
)
from .chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
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
