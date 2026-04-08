"""
Chat/RAG API router for MediAI.

Provides endpoints for medical Q&A using LangChain RAG pipeline.
Chat sessions and messages are persisted to database.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from core.config import settings
from core.database import get_db
from core.rbac import UserWithRole, require_permission
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from services.chat_service import ChatService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize chatbot if enabled
_chatbot_instance = None
_chat_rag_service_instance = None


def resolve_chatbot_provider() -> str:
    """
    Resolve a supported chatbot provider from settings.

    The chatbot implementation currently supports only Groq, OpenAI, and
    Bedrock. If the configured provider is unsupported for this code path
    (for example `gemini`), fall back to the first supported provider with
    credentials available in settings.
    """
    configured = (settings.LLM_PROVIDER or "groq").lower()
    supported = {"groq", "openai", "bedrock"}

    if configured in supported:
        return configured

    fallback_order = [
        ("groq", settings.GROQ_API_KEY),
        ("openai", settings.OPENAI_API_KEY),
        ("bedrock", settings.AWS_ACCESS_KEY_ID),
    ]

    for provider, credential in fallback_order:
        if credential:
            logger.warning(
                "Unsupported chatbot provider '%s'; falling back to '%s'",
                configured,
                provider,
            )
            return provider

    logger.warning(
        "Unsupported chatbot provider '%s' and no supported fallback credentials found; defaulting to 'groq'",
        configured,
    )
    return "groq"


def get_chatbot():
    """Get or create chatbot instance"""
    global _chatbot_instance

    if not settings.ENABLE_CHATBOT:
        return None

    if _chatbot_instance is None:
        try:
            from services.langchain_medical_bot import ProductionMedicalChatbot

            provider = resolve_chatbot_provider()

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


def get_chat_rag_service():
    """Get or create chat retrieval adapter."""
    global _chat_rag_service_instance

    if _chat_rag_service_instance is None:
        try:
            from services.chat_rag_service import ChatRAGService

            _chat_rag_service_instance = ChatRAGService()
            logger.info("✅ ChatRAGService initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChatRAGService: {e}")
            _chat_rag_service_instance = None

    return _chat_rag_service_instance


# --- Pydantic Models ---


class Citation(BaseModel):
    """Source citation for an answer"""

    number: int
    source: str
    title: Optional[str] = None
    url: Optional[str] = None
    pmid: Optional[str] = None
    tier: Optional[str] = None
    source_type: Optional[str] = None


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

    # ICU admission / general ICU management
    if any(kw in question_lower for kw in ["nhập icu", "vào icu", "icu admission", "mới vào icu",
                                            "nhập icu", "đánh giá icu", "vừa vào icu",
                                            "bệnh nhân icu", "icu patient"]):
        return (
            "Khi bệnh nhân vừa nhập ICU, cần thực hiện đánh giá hệ thống theo khung ABCDE ngay lập tức:\n\n"
            "**A — Airway (Đường thở):** Đường thở có thông thoáng không? Cần đặt nội khí quản hay đã đặt? "
            "Nếu chưa, đánh giá ngay nguy cơ suy hô hấp. [1]\n\n"
            "**B — Breathing (Hô hấp):** SpO₂, nhịp thở, PaO₂/FiO₂. "
            "Nếu cần thở máy: Vt 6 mL/kg IBW, Pplat < 30 cmH₂O.\n\n"
            "**C — Circulation (Tuần hoàn):** MAP mục tiêu ≥ 65 mmHg. "
            "Nếu tụt huyết áp: truyền dịch tinh thể 30 mL/kg, nếu không đáp ứng → norepinephrine. [1]\n\n"
            "**D — Disability (Thần kinh):** GCS, đồng tử, mức độ an thần.\n\n"
            "**E — Exposure (Tìm ổ bệnh):** Tìm nguồn nhiễm trùng, kiểm tra toàn thân.\n\n"
            "**Xét nghiệm cần làm ngay:**\n"
            "• Lactate máu — đánh giá tưới máu mô [1]\n"
            "• Cấy máu ×2 bộ — TRƯỚC khi dùng kháng sinh\n"
            "• CBC, BMP/CMP, đông máu (PT/INR, aPTT, fibrinogen)\n"
            "• ABG/VBG — cân bằng acid-base, PaO₂/FiO₂\n"
            "• Procalcitonin, CRP\n\n"
            "**Nếu nghi ngờ sepsis (SOFA ≥ 2):** [2]\n"
            "→ Kháng sinh phổ rộng trong vòng 1 giờ — không chờ kết quả xét nghiệm\n"
            "→ Theo dõi: lactate mỗi 2h, UO ≥ 0.5 mL/kg/h, MAP liên tục",
            [
                Citation(
                    number=1,
                    source="Surviving Sepsis Campaign Guidelines 2021",
                    url="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8101533/",
                    pmid="34599691",
                    tier="pubmed",
                    source_type="live_api",
                ),
                Citation(
                    number=2,
                    source="Singer M et al. – Sepsis-3 Definition (JAMA, 2016)",
                    url="https://pubmed.ncbi.nlm.nih.gov/26903338/",
                    pmid="26903338",
                    tier="pubmed",
                    source_type="live_api",
                ),
            ],
        )

    if "sepsis" in question_lower:
        high_risk = any(
            kw in question_lower
            for kw in ["85%", "85 %", "nguy cơ cao", "high risk", "xác suất cao", "hành động", "action"]
        )
        if high_risk:
            return (
                "Với xác suất sepsis 85%, đây là tình trạng khẩn cấp lâm sàng. [1] "
                "Cần thực hiện ngay gói can thiệp sepsis (Sepsis Bundle):\n"
                "• Cấy máu trước khi dùng kháng sinh (nếu có thể trong 45 phút)\n"
                "• Bắt đầu kháng sinh phổ rộng ngay lập tức\n"
                "• Truyền dịch tinh thể 30 mL/kg trong 3 giờ đầu nếu có hạ huyết áp hoặc lactate ≥ 4 mmol/L\n"
                "• Đo lactate máu và theo dõi huyết áp trung bình (MAP) ≥ 65 mmHg [2]\n"
                "• Nếu MAP không đạt dù bù dịch đủ: dùng vasopressor (norepinephrine ưu tiên)\n"
                "• Escalate lên ICU / hội chẩn cấp cứu ngay nếu có suy tạng",
                [
                    Citation(
                        number=1,
                        source="Surviving Sepsis Campaign Guidelines 2021",
                        url="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8101533/",
                        pmid="34599691",
                        tier="pubmed",
                        source_type="live_api",
                    ),
                    Citation(
                        number=2,
                        source="CDC Sepsis Clinical Guidelines",
                        url="https://www.cdc.gov/sepsis",
                        tier="cag",
                        source_type="local",
                    ),
                ],
            )
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

    elif any(kw in question_lower for kw in ["sofa", "sequential organ failure", "apache", "saps", "scoring system", "thang điểm"]):
        # Determine which scoring system is being asked about
        if "apache" in question_lower:
            return (
                "APACHE II (Acute Physiology and Chronic Health Evaluation II) là thang điểm đánh giá "
                "độ nặng bệnh trong ICU, được tính tại thời điểm nhập viện. [1]\n\n"
                "Bao gồm 12 thông số sinh lý cấp tính (nhiệt độ, MAP, nhịp tim, nhịp thở, PaO₂/FiO₂, "
                "pH máu, Na⁺, K⁺, creatinine, hematocrit, bạch cầu, Glasgow Coma Scale) "
                "cộng với điểm tuổi và bệnh mãn tính. [2]\n\n"
                "Thang điểm dao động 0–71; điểm càng cao, nguy cơ tử vong càng lớn. "
                "APACHE II ≥ 25 thường tương ứng tử vong > 50%.",
                [
                    Citation(
                        number=1,
                        source="Knaus WA et al. – APACHE II (Critical Care Medicine, 1985)",
                        url="https://pubmed.ncbi.nlm.nih.gov/3928249/",
                        pmid="3928249",
                        tier="pubmed",
                        source_type="live_api",
                    ),
                    Citation(
                        number=2,
                        source="MDCalc – APACHE II Score Calculator",
                        url="https://www.mdcalc.com/calc/1868/apache-ii-score",
                        tier="cag",
                        source_type="local",
                    ),
                ],
            )
        else:
            # Default: SOFA
            return (
                "SOFA (Sequential Organ Failure Assessment) là thang điểm đánh giá suy tạng tuần tự, "
                "được dùng rộng rãi trong ICU để theo dõi tiến triển bệnh và chẩn đoán sepsis. [1]\n\n"
                "SOFA đánh giá 6 hệ cơ quan:\n"
                "• Hô hấp: PaO₂/FiO₂ ratio\n"
                "• Đông máu: Số lượng tiểu cầu\n"
                "• Gan: Bilirubin huyết thanh\n"
                "• Tim mạch: MAP hoặc nhu cầu vasopressor\n"
                "• Thần kinh: Điểm Glasgow Coma Scale (GCS)\n"
                "• Thận: Creatinine hoặc lượng nước tiểu [2]\n\n"
                "Mỗi hệ cơ quan được chấm 0–4 điểm; tổng SOFA ≥ 2 điểm so với baseline "
                "là tiêu chí chẩn đoán sepsis (theo định nghĩa Sepsis-3). "
                "SOFA tăng ≥ 2 điểm trong 24h thường liên quan đến tỷ lệ tử vong > 10%.",
                [
                    Citation(
                        number=1,
                        source="Singer M et al. – Sepsis-3 Definition (JAMA, 2016)",
                        url="https://pubmed.ncbi.nlm.nih.gov/26903338/",
                        pmid="26903338",
                        tier="pubmed",
                        source_type="live_api",
                    ),
                    Citation(
                        number=2,
                        source="Vincent JL et al. – SOFA Score (Intensive Care Med, 1996)",
                        url="https://pubmed.ncbi.nlm.nih.gov/8844239/",
                        pmid="8844239",
                        tier="pubmed",
                        source_type="live_api",
                    ),
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
        rag_result = {
            "retrieved_context": "",
            "source_docs": [],
            "retrieval_context": None,
        }
        disclaimer = ChatResponse.model_fields["disclaimer"].default

        if chatbot is not None:
            # Use real ProductionMedicalChatbot
            try:
                rag_service = get_chat_rag_service()
                if rag_service is not None:
                    rag_result = rag_service.build_retrieval_package(
                        question=request.message,
                        conversation_history=conversation_history,
                    )

                result = chatbot.query(
                    question=request.message,
                    retrieved_context=rag_result["retrieved_context"],
                    source_docs=rag_result["source_docs"],
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
                            title=citation.get("title"),
                            url=citation.get("url"),
                            pmid=citation.get("pmid"),
                            tier=citation.get("tier"),
                            source_type=citation.get("source_type"),
                        )
                    )

                redacted_query = result.get("redacted_query")
                model_name = result.get("model_name", "unknown")
                tokens_used = result.get("tokens_used")
                disclaimer = result.get("disclaimer", disclaimer)

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
        pii_redacted = redacted_query is not None and redacted_query != request.message

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
            retrieval_context=rag_result["retrieval_context"],
            pii_redacted=pii_redacted,
            redaction_applied=(
                {"redacted_query": redacted_query} if pii_redacted else None
            ),
            model_name=model_name,
            tokens_used=tokens_used,
            processing_time_ms=processing_time,
        )

        return ChatResponse(
            answer=answer,
            citations=citations if request.include_sources else [],
            disclaimer=disclaimer,
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
