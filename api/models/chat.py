"""
Chat models for MediAI medical chatbot.

Stores chat sessions and messages for conversation persistence.
"""

import uuid
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
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ChatSession(Base):
    """Chat session for grouping related messages"""

    __tablename__ = "chat_sessions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("public.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Session metadata
    title = Column(String(200), nullable=True)  # Auto-generated from first message
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True)

    # Message count (for quick lookup)
    message_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """Individual chat message within a session"""

    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # RAG metadata (for assistant messages)
    sources = Column(JSON, nullable=True)  # List of PubMed citations
    retrieval_context = Column(JSON, nullable=True)  # Retrieved documents

    # PII redaction (HIPAA compliance)
    pii_redacted = Column(Boolean, default=False)
    redaction_applied = Column(JSON, nullable=True)  # What was redacted

    # Model metadata (for assistant messages)
    model_name = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"
