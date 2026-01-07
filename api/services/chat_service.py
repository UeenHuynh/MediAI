"""
Chat Service

Handles database operations for chat sessions and messages.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.chat import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat session and message management"""

    # ==================== SESSION OPERATIONS ====================

    @staticmethod
    def create_session(
        db: Session, user_id: int, title: Optional[str] = None
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            db: Database session
            user_id: User ID who owns this session
            title: Optional session title

        Returns:
            Created ChatSession object
        """
        session = ChatSession(
            user_id=user_id,
            title=title,
            message_count=0,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        logger.info(f"Created chat session: {session.session_id} for user {user_id}")
        return session

    @staticmethod
    def get_session(db: Session, session_id: UUID) -> Optional[ChatSession]:
        """
        Get chat session by UUID.

        Args:
            db: Database session
            session_id: Session UUID

        Returns:
            ChatSession object or None if not found
        """
        return (
            db.query(ChatSession)
            .filter(ChatSession.session_id == session_id, ChatSession.is_active == True)
            .first()
        )

    @staticmethod
    def get_session_by_id(db: Session, id: int) -> Optional[ChatSession]:
        """
        Get chat session by integer ID.

        Args:
            db: Database session
            id: Session integer ID

        Returns:
            ChatSession object or None if not found
        """
        return (
            db.query(ChatSession)
            .filter(ChatSession.id == id, ChatSession.is_active == True)
            .first()
        )

    @staticmethod
    def list_user_sessions(
        db: Session, user_id: int, skip: int = 0, limit: int = 50
    ) -> Tuple[List[ChatSession], int]:
        """
        List all chat sessions for a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of sessions, total count)
        """
        query = db.query(ChatSession).filter(
            ChatSession.user_id == user_id, ChatSession.is_active == True
        )

        total = query.count()
        sessions = (
            query.order_by(desc(ChatSession.last_activity_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return sessions, total

    @staticmethod
    def update_session_title(
        db: Session, session_id: UUID, title: str
    ) -> Optional[ChatSession]:
        """
        Update session title (e.g., from first message).

        Args:
            db: Database session
            session_id: Session UUID
            title: New title

        Returns:
            Updated ChatSession or None if not found
        """
        session = ChatService.get_session(db, session_id)
        if not session:
            return None

        session.title = title[:200]  # Truncate to max length
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: UUID) -> bool:
        """
        Soft delete a chat session.

        Args:
            db: Database session
            session_id: Session UUID

        Returns:
            True if deleted, False if not found
        """
        session = ChatService.get_session(db, session_id)
        if not session:
            return False

        session.is_active = False
        db.commit()
        logger.info(f"Deleted chat session: {session_id}")
        return True

    # ==================== MESSAGE OPERATIONS ====================

    @staticmethod
    def add_message(
        db: Session,
        session_id: UUID,
        role: str,
        content: str,
        sources: Optional[dict] = None,
        retrieval_context: Optional[dict] = None,
        pii_redacted: bool = False,
        redaction_applied: Optional[dict] = None,
        model_name: Optional[str] = None,
        tokens_used: Optional[int] = None,
        processing_time_ms: Optional[int] = None,
    ) -> Optional[ChatMessage]:
        """
        Add a message to a chat session.

        Args:
            db: Database session
            session_id: Session UUID
            role: 'user' or 'assistant'
            content: Message content
            sources: Citation sources (for assistant)
            retrieval_context: RAG context (for assistant)
            pii_redacted: Whether PII was redacted
            redaction_applied: Details of redaction
            model_name: LLM model used
            tokens_used: Token count
            processing_time_ms: Processing time

        Returns:
            Created ChatMessage or None if session not found
        """
        # Verify session exists
        session = ChatService.get_session(db, session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None

        # Create message
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            retrieval_context=retrieval_context,
            pii_redacted=pii_redacted,
            redaction_applied=redaction_applied,
            model_name=model_name,
            tokens_used=tokens_used,
            processing_time_ms=processing_time_ms,
        )

        db.add(message)

        # Update session metadata
        session.message_count += 1
        session.last_activity_at = datetime.utcnow()

        # Auto-generate title from first user message
        if session.title is None and role == "user":
            session.title = content[:100] + ("..." if len(content) > 100 else "")

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_session_messages(
        db: Session, session_id: UUID, limit: int = 100
    ) -> List[ChatMessage]:
        """
        Get all messages for a session.

        Args:
            db: Database session
            session_id: Session UUID
            limit: Maximum messages to return

        Returns:
            List of ChatMessage objects
        """
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_messages(
        db: Session, session_id: UUID, count: int = 5
    ) -> List[ChatMessage]:
        """
        Get the most recent messages for context.

        Args:
            db: Database session
            session_id: Session UUID
            count: Number of recent messages

        Returns:
            List of recent ChatMessage objects (oldest to newest)
        """
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(count)
            .all()
        )

        # Return in chronological order
        return list(reversed(messages))

    @staticmethod
    def get_or_create_session(
        db: Session, session_id_str: Optional[str], user_id: int
    ) -> Tuple[ChatSession, bool]:
        """
        Get existing session or create new one.

        Args:
            db: Database session
            session_id_str: Session UUID string (or None for new)
            user_id: User ID

        Returns:
            Tuple of (ChatSession, is_new)
        """
        if session_id_str:
            try:
                session_uuid = UUID(session_id_str)
                session = ChatService.get_session(db, session_uuid)
                if session:
                    return session, False
            except ValueError:
                # Invalid UUID, create new session
                pass

        # Create new session
        session = ChatService.create_session(db, user_id)
        return session, True
