"""
Pydantic schemas for Chat API
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session"""
    user_id: int
    title: Optional[str] = Field(None, max_length=200)


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: int
    session_id: UUID
    user_id: int
    title: Optional[str] = None
    started_at: datetime
    last_activity_at: datetime
    is_active: bool
    message_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    session_id: UUID
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)

    # Optional metadata (for assistant messages)
    sources: Optional[dict] = None
    retrieval_context: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    session_id: UUID
    role: str
    content: str
    sources: Optional[dict] = None
    retrieval_context: Optional[dict] = None
    pii_redacted: bool
    model_name: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response"""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
