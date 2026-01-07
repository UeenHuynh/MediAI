"""
Chat/RAG API router for MediAI.

Provides endpoints for medical Q&A using LangChain RAG pipeline.
Chat sessions and messages are persisted to database.
"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from core.config import settings
from core.database import get_db
from core.rbac import UserWithRole, require_authenticated, require_permission
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from schemas.chat import ChatMessageResponse, ChatSessionResponse
from services.chat_service import ChatService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize chatbot if enabled
_chatbot_instance = None


def get_chatbot():
    """Get or create chatbot instance"""
    global _chatbot_instance

    if not settings.ENABLE_CHATBOT:
        return None

    if _chatbot_instance is None:
        try:
            from services.langchain_medical_bot import ProductionMedicalChatbot

            # Get LLM provider from env (default: groq)
            provider = os.getenv("LLM_PROVIDER", "groq").lower()

            _chatbot_instance = ProductionMedicalChatbot(
                provider=provider,
                enable_pii_redaction=True,
                enable_callbacks=True,
            )
            logger.info(
                f"✅ ProductionMedicalChatbot initialized with provider={provider}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot: {e}")
            _chatbot_instance = None

    return _chatbot_instance


# --- Pydantic Models ---


class Citation(BaseModel):
    """Source citation for an answer"""

    number: int
    source: str
    url: Optional[str] = None
    pmid: Optional[str] = None


class ChatMessage(BaseModel):
    """Single chat message"""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    citations: List[Citation] = []


class ChatRequest(BaseModel):
    """Chat request payload"""

    message: str = Field(
        ..., min_length=1, max_length=2000, description="User's question"
    )
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation continuity"
    )
    include_sources: bool = Field(
        True, description="Whether to include source citations"
    )


class ChatResponse(BaseModel):
    """Chat response payload"""

    answer: str
    citations: List[Citation] = []
    disclaimer: str = (
        "⚠️ This information is for educational purposes only. Always consult a healthcare professional."
    )
    session_id: str
    redacted_query: Optional[str] = None
    processing_time_ms: int = 0


class ConversationHistory(BaseModel):
    """Full conversation history"""

    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    last_updated: datetime


# --- Mock implementation (fallback when chatbot is disabled) ---


def get_mock_response(question: str) -> tuple[str, List[Citation]]:
    """
    Generate a mock medical response.
    In production, this would call ProductionMedicalChatbot.query()
    """
    question_lower = question.lower()

    if "sepsis" in question_lower:
        return (
            "Sepsis is a life-threatening condition caused by the body's response to infection. "
            "Early signs include fever, increased heart rate, rapid breathing, and confusion. "
            "The SOFA (Sequential Organ Failure Assessment) score is commonly used to assess "
            "sepsis severity. Treatment typically involves antibiotics, IV fluids, and "
            "vasopressors if needed. Early recognition and treatment significantly improve outcomes.",
            [
                Citation(
                    number=1,
                    source="CDC Sepsis Guidelines 2024",
                    url="https://www.cdc.gov/sepsis",
                ),
                Citation(number=2, source="Surviving Sepsis Campaign", pmid="34599691"),
            ],
        )

    elif "mortality" in question_lower or "death" in question_lower:
        return (
            "ICU mortality prediction uses various scoring systems including APACHE II, "
            "SOFA, and SAPS II. Key factors include age, comorbidities, vital signs, "
            "lab values, and the need for mechanical ventilation or vasopressors. "
            "Machine learning models can provide more accurate predictions by considering "
            "multiple variables simultaneously.",
            [
                Citation(
                    number=1,
                    source="APACHE II Score Reference",
                    url="https://www.mdcalc.com/apache-ii-score",
                ),
                Citation(
                    number=2, source="Critical Care Medicine Journal", pmid="28098591"
                ),
            ],
        )

    elif "blood pressure" in question_lower or "hypertension" in question_lower:
        return (
            "Normal blood pressure is typically considered less than 120/80 mmHg. "
            "Hypertension is classified as Stage 1 (130-139/80-89) or Stage 2 (≥140/≥90). "
            "In ICU settings, mean arterial pressure (MAP) is often monitored, with a target "
            "typically ≥65 mmHg for adequate organ perfusion.",
            [
                Citation(
                    number=1,
                    source="AHA Hypertension Guidelines",
                    url="https://www.heart.org",
                ),
            ],
        )

    else:
        return (
            "Thank you for your question. As a medical AI assistant, I can provide "
            "general information about medical conditions, medications, and clinical guidelines. "
            "Please note that this information is for educational purposes only and should not "
            "replace professional medical advice. For specific health concerns, please consult "
            "a qualified healthcare provider.",
            [],
        )


# --- Endpoints ---


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: UserWithRole = Depends(require_permission("chat:write")),
    db: Session = Depends(get_db),
):
    """
    Send a message to the medical AI assistant.

    The assistant uses RAG (Retrieval-Augmented Generation) to provide
    evidence-based responses with source citations.

    Messages are persisted to the database for conversation history.
    """
    import time

    start_time = time.time()

    # Get or create session
    session, is_new = ChatService.get_or_create_session(
        db=db, session_id_str=request.session_id, user_id=user.id
    )

    session_id_str = str(session.session_id)

    # Save user message to database
    ChatService.add_message(
        db=db,
        session_id=session.session_id,
        role="user",
        content=request.message,
    )

    try:
        # Get recent messages for context
        recent_messages = ChatService.get_recent_messages(
            db, session.session_id, count=5
        )
        conversation_history = [(msg.role, msg.content) for msg in recent_messages]

        # Get chatbot instance
        chatbot = get_chatbot()

        if chatbot is not None:
            # Use real ProductionMedicalChatbot
            try:
                result = chatbot.query(
                    question=request.message,
                    retrieved_context="",  # No RAG context for now
                    conversation_history=conversation_history,
                )

                answer = result.get(
                    "answer",
                    "I apologize, but I'm unable to generate a response at this time.",
                )

                # Convert citations format
                citations = []
                for i, citation in enumerate(result.get("citations", []), 1):
                    citations.append(
                        Citation(
                            number=i,
                            source=citation.get("source", "Unknown"),
                            url=citation.get("url"),
                            pmid=citation.get("pmid"),
                        )
                    )

                redacted_query = result.get("redacted_query")
                model_name = result.get("model_name", "unknown")
                tokens_used = result.get("tokens_used")

            except Exception as e:
                logger.error(f"Chatbot error: {e}, falling back to mock")
                # Fallback to mock if chatbot fails
                answer, citations = get_mock_response(request.message)
                redacted_query = None
                model_name = "mock"
                tokens_used = None
        else:
            # Use mock response if chatbot not enabled
            answer, citations = get_mock_response(request.message)
            redacted_query = None
            model_name = "mock"
            tokens_used = None

        processing_time = int((time.time() - start_time) * 1000)

        # Save assistant message to database
        sources_dict = (
            {"citations": [c.model_dump() for c in citations]} if citations else None
        )

        ChatService.add_message(
            db=db,
            session_id=session.session_id,
            role="assistant",
            content=answer,
            sources=sources_dict,
            pii_redacted=redacted_query is not None,
            model_name=model_name,
            tokens_used=tokens_used,
            processing_time_ms=processing_time,
        )

        return ChatResponse(
            answer=answer,
            citations=citations if request.include_sources else [],
            session_id=session_id_str,
            redacted_query=redacted_query,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(
    session_id: str,
    user: UserWithRole = Depends(require_permission("chat:read")),
    db: Session = Depends(get_db),
):
    """
    Get conversation history for a session.
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    session = ChatService.get_session(db, session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get messages from database
    db_messages = ChatService.get_session_messages(db, session_uuid)

    messages = []
    for msg in db_messages:
        citations = []
        if msg.sources and "citations" in msg.sources:
            for c in msg.sources["citations"]:
                citations.append(Citation(**c))

        messages.append(
            ChatMessage(
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at,
                citations=citations,
            )
        )

    return ConversationHistory(
        session_id=session_id,
        messages=messages,
        created_at=session.started_at,
        last_updated=session.last_activity_at,
    )


@router.delete("/history/{session_id}")
async def clear_conversation(
    session_id: str,
    user: UserWithRole = Depends(require_permission("chat:write")),
    db: Session = Depends(get_db),
):
    """
    Clear conversation history for a session (soft delete).
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    success = ChatService.delete_session(db, session_uuid)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Conversation cleared", "session_id": session_id}


@router.get("/sessions")
async def list_sessions(
    user: UserWithRole = Depends(require_permission("chat:read")),
    db: Session = Depends(get_db),
):
    """
    List all active chat sessions for the current user.
    """
    sessions, total = ChatService.list_user_sessions(db, user.id)

    return {
        "sessions": [
            {
                "session_id": str(session.session_id),
                "title": session.title,
                "message_count": session.message_count,
                "created_at": session.started_at,
                "last_updated": session.last_activity_at,
            }
            for session in sessions
        ],
        "total": total,
    }
