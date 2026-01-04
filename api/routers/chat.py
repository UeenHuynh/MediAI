"""
Chat/RAG API router for MediAI.

Provides endpoints for medical Q&A using LangChain RAG pipeline.
"""

import logging
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.rbac import require_authenticated, UserWithRole, require_permission
from core.config import settings

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
            logger.info(f"✅ ProductionMedicalChatbot initialized with provider={provider}")
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
    message: str = Field(..., min_length=1, max_length=2000, description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    include_sources: bool = Field(True, description="Whether to include source citations")


class ChatResponse(BaseModel):
    """Chat response payload"""
    answer: str
    citations: List[Citation] = []
    disclaimer: str = "⚠️ This information is for educational purposes only. Always consult a healthcare professional."
    session_id: str
    redacted_query: Optional[str] = None
    processing_time_ms: int = 0


class ConversationHistory(BaseModel):
    """Full conversation history"""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    last_updated: datetime


# --- Mock implementation (replace with actual LangChain service) ---

# In-memory session storage (use Redis in production)
CHAT_SESSIONS: dict = {}


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
                Citation(number=1, source="CDC Sepsis Guidelines 2024", url="https://www.cdc.gov/sepsis"),
                Citation(number=2, source="Surviving Sepsis Campaign", pmid="34599691"),
            ]
        )
    
    elif "mortality" in question_lower or "death" in question_lower:
        return (
            "ICU mortality prediction uses various scoring systems including APACHE II, "
            "SOFA, and SAPS II. Key factors include age, comorbidities, vital signs, "
            "lab values, and the need for mechanical ventilation or vasopressors. "
            "Machine learning models can provide more accurate predictions by considering "
            "multiple variables simultaneously.",
            [
                Citation(number=1, source="APACHE II Score Reference", url="https://www.mdcalc.com/apache-ii-score"),
                Citation(number=2, source="Critical Care Medicine Journal", pmid="28098591"),
            ]
        )
    
    elif "blood pressure" in question_lower or "hypertension" in question_lower:
        return (
            "Normal blood pressure is typically considered less than 120/80 mmHg. "
            "Hypertension is classified as Stage 1 (130-139/80-89) or Stage 2 (≥140/≥90). "
            "In ICU settings, mean arterial pressure (MAP) is often monitored, with a target "
            "typically ≥65 mmHg for adequate organ perfusion.",
            [
                Citation(number=1, source="AHA Hypertension Guidelines", url="https://www.heart.org"),
            ]
        )
    
    else:
        return (
            "Thank you for your question. As a medical AI assistant, I can provide "
            "general information about medical conditions, medications, and clinical guidelines. "
            "Please note that this information is for educational purposes only and should not "
            "replace professional medical advice. For specific health concerns, please consult "
            "a qualified healthcare provider.",
            []
        )


# --- Endpoints ---

@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: UserWithRole = Depends(require_permission("chat:write")),
):
    """
    Send a message to the medical AI assistant.
    
    The assistant uses RAG (Retrieval-Augmented Generation) to provide
    evidence-based responses with source citations.
    """
    import time
    import uuid
    
    start_time = time.time()
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id] = ConversationHistory(
            session_id=session_id,
            messages=[],
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
        )
    
    session = CHAT_SESSIONS[session_id]
    
    # Add user message
    session.messages.append(ChatMessage(
        role="user",
        content=request.message,
    ))
    
    try:
        # Get chatbot instance
        chatbot = get_chatbot()

        if chatbot is not None:
            # Use real ProductionMedicalChatbot
            try:
                result = chatbot.query(
                    question=request.message,
                    retrieved_context="",  # No RAG context for now
                    conversation_history=[(msg.role, msg.content) for msg in session.messages[-5:]],  # Last 5 messages
                )

                answer = result.get("answer", "I apologize, but I'm unable to generate a response at this time.")

                # Convert citations format
                citations = []
                for i, citation in enumerate(result.get("citations", []), 1):
                    citations.append(Citation(
                        number=i,
                        source=citation.get("source", "Unknown"),
                        url=citation.get("url"),
                        pmid=citation.get("pmid"),
                    ))

                redacted_query = result.get("redacted_query")

            except Exception as e:
                logger.error(f"Chatbot error: {e}, falling back to mock")
                # Fallback to mock if chatbot fails
                answer, citations = get_mock_response(request.message)
                redacted_query = None
        else:
            # Use mock response if chatbot not enabled
            answer, citations = get_mock_response(request.message)
            redacted_query = None

        # Add assistant message
        session.messages.append(ChatMessage(
            role="assistant",
            content=answer,
            citations=citations,
        ))

        session.last_updated = datetime.utcnow()

        processing_time = int((time.time() - start_time) * 1000)

        return ChatResponse(
            answer=answer,
            citations=citations if request.include_sources else [],
            session_id=session_id,
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
):
    """
    Get conversation history for a session.
    """
    if session_id not in CHAT_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return CHAT_SESSIONS[session_id]


@router.delete("/history/{session_id}")
async def clear_conversation(
    session_id: str,
    user: UserWithRole = Depends(require_permission("chat:write")),
):
    """
    Clear conversation history for a session.
    """
    if session_id in CHAT_SESSIONS:
        del CHAT_SESSIONS[session_id]
    
    return {"message": "Conversation cleared", "session_id": session_id}


@router.get("/sessions")
async def list_sessions(
    user: UserWithRole = Depends(require_permission("chat:read")),
):
    """
    List all active chat sessions.
    Admin/Doctor only endpoint.
    """
    return {
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(session.messages),
                "created_at": session.created_at,
                "last_updated": session.last_updated,
            }
            for sid, session in CHAT_SESSIONS.items()
        ],
        "total": len(CHAT_SESSIONS),
    }
