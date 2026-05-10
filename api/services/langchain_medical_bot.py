"""
Production-Ready Medical Chatbot with LangChain Integration

This module provides a HIPAA-aware, vendor-agnostic medical chatbot with:
- PII redaction using Microsoft Presidio
- Multi-vendor LLM support (Groq, OpenAI, AWS Bedrock)
- Conversation memory with token management
- Structured medical response format
- Comprehensive error handling and retry logic

Author: MediAI Team
Version: 1.0.0
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from api.core.config import settings
except ImportError:
    from core.config import settings

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Groq auth error — fail fast, never retry
try:
    from groq import AuthenticationError as GroqAuthError
except ImportError:
    class GroqAuthError(Exception):  # type: ignore
        pass

# Optional AWS Bedrock (only if package available)
try:
    from langchain_aws import ChatBedrock
    _BEDROCK_AVAILABLE = True
except ImportError:
    _BEDROCK_AVAILABLE = False
    ChatBedrock = None  # type: ignore

# Optional PII redaction (requires presidio + spacy model)
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    _PRESIDIO_AVAILABLE = True
except ImportError:
    _PRESIDIO_AVAILABLE = False
    AnalyzerEngine = None  # type: ignore
    AnonymizerEngine = None  # type: ignore

# Import callbacks
try:
    from api.services.langchain_callbacks import (
        get_callback_handler,
        get_pii_callback,
    )
except ImportError:
    # When running from api/ directory
    from services.langchain_callbacks import (
        get_callback_handler,
        get_pii_callback,
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Citation(BaseModel):
    """Citation model for structured output."""

    number: str = Field(..., description="Citation number (e.g., '1', '2')")
    source: str = Field(..., description="Source name/identifier")
    title: Optional[str] = Field(None, description="Human-readable title")
    url: Optional[str] = Field(None, description="URL to the source")
    pmid: Optional[str] = Field(None, description="PubMed ID if applicable")
    tier: Optional[str] = Field(None, description="Retrieval tier identifier")
    source_type: Optional[str] = Field(
        None, description="Source classification such as 'live_api' or 'local'"
    )


class MedicalResponse(BaseModel):
    """Structured medical response model."""

    answer: str = Field(..., description="The medical response text")
    citations: List[Citation] = Field(
        default_factory=list, description="List of citations used in the response"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    disclaimer: str = Field(
        default="⚠️ This is informational only. Consult healthcare provider.",
        description="Medical disclaimer",
    )
    redacted_query: Optional[str] = Field(None, description="Query with PII redacted")


class ProductionMedicalChatbot:
    """
    Production-ready medical chatbot with privacy-first design.

    Features:
    - Automatic PII detection and redaction
    - Vendor-agnostic LLM (supports Groq, OpenAI, AWS Bedrock)
    - Conversation memory with automatic summarization
    - Token budget management
    - Structured medical response format
    - Retry logic with exponential backoff
    - HIPAA-aware (privacy-by-design principles)

    Example:
        >>> bot = ProductionMedicalChatbot(provider="groq")
        >>> result = bot.query(
        ...     question="Patient has BP 80/50, what should I do?",
        ...     retrieved_context="[1] Hypotension guidelines..."
        ... )
        >>> print(result["answer"])
    """

    # PII entities to detect and redact
    PII_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "MEDICAL_LICENSE",
        "US_SSN",
        "IBAN_CODE",
        "CREDIT_CARD",
        "US_PASSPORT",
        "US_DRIVER_LICENSE",
        "DATE_TIME",  # Dates can be identifying
        "LOCATION",  # Specific locations can be PII
    ]

    def __init__(
        self,
        provider: str = "groq",
        max_token_limit: int = 12000,
        memory_max_tokens: int = 500,
        temperature: float = 0.3,
        enable_pii_redaction: bool = True,
        enable_callbacks: bool = True,
    ):
        """
        Initialize the medical chatbot.

        Args:
            provider: LLM provider ("groq", "openai", or "bedrock")
            max_token_limit: Maximum context tokens for the model
            memory_max_tokens: Maximum tokens for conversation summary
            temperature: LLM temperature (0.0-1.0)
            enable_pii_redaction: Enable PII detection and redaction
            enable_callbacks: Enable LangChain callbacks for monitoring

        Raises:
            ValueError: If provider is unsupported
            RuntimeError: If required dependencies are missing
        """
        logger.info(f"Initializing ProductionMedicalChatbot with provider={provider}")

        self.provider = provider
        self.max_tokens = max_token_limit
        self.temperature = temperature
        self.enable_pii_redaction = enable_pii_redaction
        self.enable_callbacks = enable_callbacks

        # Initialize callbacks for monitoring
        self.callback_handler = None
        self.pii_callback = None
        if self.enable_callbacks:
            self.callback_handler = get_callback_handler()
            self.pii_callback = get_pii_callback()
            logger.info("LangChain callbacks enabled")

        # Initialize LLM (vendor-agnostic)
        try:
            self.llm = self._init_llm(provider, temperature)
        except ValueError as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise RuntimeError(f"LLM initialization failed: {e}") from e

        # Initialize PII protection
        if self.enable_pii_redaction:
            if not _PRESIDIO_AVAILABLE:
                logger.warning("Presidio not available — PII redaction disabled")
                self.enable_pii_redaction = False
            else:
                try:
                    self.analyzer = AnalyzerEngine()
                    self.anonymizer = AnonymizerEngine()
                    logger.info("PII redaction enabled with Presidio")
                except Exception as e:
                    logger.warning(f"PII redaction initialization failed: {e}")
                    self.enable_pii_redaction = False

        # Initialize conversation memory (simple message history for now)
        self.memory_max_tokens = memory_max_tokens
        self.message_history = ChatMessageHistory()
        self.memory = self.message_history

        # Create structured prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_prompt()),
                ("human", self._get_user_template()),
            ]
        )

        # Create LCEL chain with callbacks
        callbacks = [self.callback_handler] if self.callback_handler else []
        output_parser = StrOutputParser()

        # Modern LangChain 1.x LCEL chain
        self.chain = (
            self.prompt | self.llm.with_config({"callbacks": callbacks}) | output_parser
        )

        logger.info("ProductionMedicalChatbot initialized successfully")

    def _init_llm(self, provider: str, temperature: float):
        """
        Initialize vendor-agnostic LLM.

        Args:
            provider: LLM provider name
            temperature: Sampling temperature

        Returns:
            Initialized LLM instance

        Raises:
            ValueError: If provider is unsupported
        """
        if provider == "groq":
            api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")

            return ChatGroq(
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                temperature=temperature,
                api_key=api_key,
                max_tokens=2048,
            )

        elif provider == "openai":
            api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                api_key=api_key,
            )

        elif provider == "bedrock":
            if not _BEDROCK_AVAILABLE:
                raise ValueError("langchain-aws not installed; cannot use bedrock provider")
            return ChatBedrock(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                model_kwargs={"temperature": temperature},
            )

        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                "Supported: 'groq', 'openai', 'bedrock'"
            )

    def _redact_pii(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Redact PII from text using Microsoft Presidio.

        Args:
            text: Input text that may contain PII

        Returns:
            Tuple of (redacted_text, detected_entities)
        """
        if not self.enable_pii_redaction:
            return text, []

        try:
            # Analyze text for PII
            results = self.analyzer.analyze(
                text=text,
                language="en",
                entities=self.PII_ENTITIES,
            )

            # Anonymize detected PII
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
            )

            # Log PII detection (without revealing content)
            if results:
                detected_types = {r.entity_type for r in results}
                logger.info(f"PII detected and redacted: {detected_types}")

            return anonymized.text, [
                {
                    "type": r.entity_type,
                    "score": r.score,
                    "start": r.start,
                    "end": r.end,
                }
                for r in results
            ]

        except Exception as e:
            logger.error(f"PII redaction failed: {e}")
            # Fail-safe: return original text if redaction fails
            return text, []

    def _get_system_prompt(self) -> str:
        """
        Get system prompt with ICU clinical reasoning framework.

        Returns:
            System prompt string
        """
        return """Bạn là ICU Copilot dành cho bác sĩ hồi sức tích cực. Vai trò của bạn là hỗ trợ lập luận lâm sàng theo từng ca bệnh cụ thể trong ICU, không phải chỉ nhắc lại guideline hay checklist. Bạn phải ưu tiên tư duy theo dữ kiện của bệnh nhân trước mắt, phân tầng mức độ nặng, nhận diện vấn đề đe dọa tính mạng, và đề xuất hướng xử trí có giải thích rõ lợi ích-nguy cơ trong đúng bối cảnh ca bệnh.

## MỤC TIÊU CỐT LÕI
- Ưu tiên an toàn người bệnh.
- Nhận diện và xử trí ngay các vấn đề đe dọa tính mạng có thể đảo ngược.
- Phân biệt điều gì đã biết, điều gì chưa biết, và điều gì cần bổ sung để đổi quyết định.
- Không trả lời kiểu template chung chung.
- Không áp dụng guideline một cách máy móc nếu ca bệnh có yếu tố khiến chiến lược chuẩn cần điều chỉnh.
- Luôn reasoning theo ICU thực chiến, không chỉ tóm tắt sách vở.

## NGUYÊN TẮC CHẤT LƯỢNG BẮT BUỘC
1. Không được trả lời như một mẫu có thể áp dụng nguyên xi cho mọi bệnh nhân cùng hội chứng.
2. Mỗi kết luận phải gắn trực tiếp với ít nhất một dữ kiện cụ thể của ca bệnh. Nếu không gắn được, bỏ kết luận đó.
3. Nếu hai hướng xử trí cạnh tranh nhau, phải so sánh rõ: lợi ích, nguy cơ, khi nào nghiêng về hướng A, khi nào nghiêng về hướng B.
4. Phải tách rõ: quyết định dựa trên dữ kiện hiện có vs quyết định còn phụ thuộc dữ liệu cần bổ sung.
5. Nếu thiếu dữ liệu quan trọng, phải nói chính xác dữ liệu nào còn thiếu và dữ liệu đó sẽ thay đổi quyết định như thế nào.
6. Không được dùng "guideline nói thế" như lý do duy nhất. Phải giải thích sinh lý bệnh và logic hồi sức.
7. Nếu ca bệnh có bệnh nền làm thay đổi xử trí chuẩn (suy tim, ARDS, AKI, xơ gan, tăng áp phổi, chảy máu, suy giảm miễn dịch, DNR/DNI), phải nói rõ tại sao phác đồ chuẩn không thể áp dụng máy móc.
8. Nếu nhận thấy câu trả lời bạn sắp đưa ra quá giống một câu trả lời sepsis/shock/ARDS chung chung, hãy dừng lại và chỉ ra điểm khác biệt thật sự của ca bệnh này trước khi kết luận.
9. Nếu có thông tin mâu thuẫn, hãy chỉ ra mâu thuẫn đó thay vì giả vờ như không có.
10. Nếu bằng chứng không đủ chắc, nói rõ mức độ chắc chắn của kết luận.
11. Không được quên hậu quả của chọn sai thứ tự ưu tiên hồi sức.
12. Không được bỏ qua việc theo dõi đáp ứng sau can thiệp.

## KHUNG PHÂN TÍCH CỐ ĐỊNH

**BƯỚC 1 — TÓM TẮT CA BỆNH**
Viết 2–4 câu: hội chứng chính hiện tại, vấn đề đe dọa tính mạng nhất, dữ kiện nào đang kéo mức độ nặng lên, bệnh nền nào làm thay đổi chiến lược xử trí.

**BƯỚC 2 — ƯU TIÊN THEO THỨ TỰ XỬ TRÍ**
Liệt kê 3–5 vấn đề quan trọng nhất theo đúng thứ tự ưu tiên trong ICU theo ca thật, không theo mẫu cố định.

**BƯỚC 3 — ABCDE NHƯNG KHÔNG MÁY MÓC**
Phân tích theo A, B, C, D, E. Nếu A đã kiểm soát, nói rõ vì sao điều đó không cho phép trì hoãn B/C/D/E. Nếu C là vấn đề chính, ưu tiên lý giải chiến lược huyết động chi tiết.

**BƯỚC 4 — CHẨN ĐOÁN PHÂN BIỆT**
2–4 chẩn đoán quan trọng nhất: ưu tiên nguyên nhân nguy hiểm, có thể đảo ngược, thay đổi xử trí ngay.

**BƯỚC 5 — SO SÁNH CÁC CHIẾN LƯỢC CẠNH TRANH**
Nếu có tranh chấp hướng xử trí, bắt buộc so sánh (ví dụ: bù dịch tích cực vs vận mạch sớm; NIV/HFNC vs đặt nội khí quản; an thần sâu vs giảm an thần). Mỗi hướng phải có: lý do ủng hộ, lý do chống lại, dữ kiện nào trong ca này làm nghiêng cán cân.

**BƯỚC 6 — QUYẾT ĐỊNH DỰA TRÊN DỮ KIỆN HIỆN CÓ VS CÒN PHỤ THUỘC DỮ LIỆU**
A. Quyết định ngay bây giờ dựa trên dữ kiện hiện có.
B. Chỉ quyết định sau khi có thêm dữ liệu X/Y/Z (ví dụ: POCUS tim/phổi/IVC/VTI, ECG/troponin/BNP, ABG/VBG, lactate trend, CRT, urine output trend, PLR response, cultures/source workup, ventilator waveforms, renal indices).

**BƯỚC 7 — KẾ HOẠCH 15 PHÚT ĐẦU / 60 PHÚT ĐẦU**
- 15 phút đầu: hành động ngay lập tức
- 60 phút đầu: đánh giá đáp ứng và bước tiếp theo
- Mục tiêu theo dõi đáp ứng
- Dấu hiệu buộc phải đổi hướng

**BƯỚC 8 — SAI LẦM DỄ MẮC NẾU XỬ TRÍ THEO HƯỚNG KHÁC**
2–4 sai lầm quan trọng nhất: ví dụ ép đủ 30 mL/kg ở bệnh nhân suy tim, trì hoãn vận mạch khi giảm tưới máu, bỏ sót sốc hỗn hợp, tưởng SpO2 ổn là B ổn hoàn toàn.

## MODULE BỔ SUNG THEO LOẠI CA

**SHOCK / HUYẾT ĐỘNG:** Loại sốc khả dĩ nhất, loại cần loại trừ ngay, khả năng sốc hỗn hợp, dấu hiệu gợi ý từng loại, lý do chọn dịch/vận mạch/inotrope, dữ liệu POCUS/PLR/VTI/IVC/CRT/ScvO2/lactate/UO sẽ thay đổi chiến lược thế nào, hậu quả nếu ưu tiên sai thứ tự.

**SEPSIS / SEPTIC SHOCK:** Nguồn nhiễm khả dĩ nhất, nguồn cần loại trừ ngay, thứ tự ưu tiên kháng sinh/source control/dịch/vận mạch trong ca này, khi nào norepinephrine sớm hơn chuẩn, khi nào không ép đủ bolus chuẩn, phân biệt "sepsis bundle chuẩn" vs "điều chỉnh theo ca này".

**SUY HÔ HẤP / THỞ MÁY:** Kiểu suy hô hấp, mục tiêu oxygenation/ventilation thực tế, chỉ định HFNC/NIV/intubation/chỉnh ventilator, nguy cơ auto-PEEP/VILI/barotrauma, tương tác huyết động với áp lực dương.

**AKI / TOAN KIỀM / ĐIỆN GIẢI:** Bất thường đe dọa tính mạng ngay, phân loại nguyên nhân, chỉ định lọc máu, điều gì làm trước khi có đủ xét nghiệm.

**THẦN KINH / GIẢM TRI GIÁC:** Nguyên nhân có thể đảo ngược ngay, phân biệt thần kinh nguyên phát vs chuyển hóa/hô hấp/sốc/độc chất, cần CT/EEG/glucose/ABG/ammonia/độc chất không, bảo vệ não không bỏ quên ABC.

**HẬU PHẪU:** Biến chứng đe dọa tính mạng, xuất huyết/sepsis/PE/tamponade/ACS/abdominal compartment/anastomotic leak/ischemia, điều gì cần gọi phẫu thuật ngay.

**BỆNH NỀN QUAN TRỌNG:** Luôn điều chỉnh reasoning nếu có suy tim, COPD/tăng áp phổi, xơ gan, CKD/ESRD, ARDS, ung thư/suy giảm miễn dịch, steroid/ức chế miễn dịch, thai kỳ, DNR/DNI. Phải nói rõ bệnh nền nào làm thay đổi hướng xử trí chuẩn.

## ĐỊNH DẠNG BẮT BUỘC
A. Nhận định ban đầu
B. 3–5 ưu tiên cao nhất
C. Lập luận chính theo dữ kiện ca bệnh
D. Điều còn thiếu nhưng có thể đổi quyết định
E. Kế hoạch 15 phút đầu
F. Kế hoạch 60 phút đầu
G. Sai lầm dễ mắc nếu xử trí theo hướng khác

## CITATION RULES
- If context documents are provided above, you may cite them as [1], [2], [3].
- Only cite documents that are actually listed in the Retrieved Clinical Evidence section.
- Do NOT invent, fabricate, or hallucinate citations or references.
- If no context documents are provided, do not include any [N] markers.

## SAFETY RULES
- Never provide specific medication dosages without caveats
- Never definitively diagnose — frame as "clinical picture consistent with..."
- Emergency flag: if immediate life threat detected, lead with 🚨
- If the question is general/non-case-specific, still reason from physiology not templates

## DISCLAIMER
Always end with:
⚠️ Thông tin này chỉ mang tính hỗ trợ lâm sàng. Mọi quyết định điều trị phải do bác sĩ có thẩm quyền thực hiện dựa trên đánh giá toàn diện bệnh nhân."""

    def _get_user_template(self) -> str:
        """
        Get user message template with clinical context injection.

        Returns:
            User template string
        """
        return """Retrieved Clinical Evidence:
{context}

Conversation History:
{chat_history}

Clinical Question / Scenario:
{question}

Instructions:
- If this describes a patient scenario with multiple variables, apply the ABCDE → Syndrome Recognition → Immediate Actions → Missing Data → Monitoring framework.
- If data is missing (e.g., labs not done yet), explicitly flag what is needed and why, but do NOT delay action recommendations.
- If context documents are listed above, you may cite them with [N]. Do NOT invent citations that are not in the context.
- Respond ENTIRELY in the same language as the question. If the question is in Vietnamese, answer 100% in Vietnamese — do NOT mix in any other language characters (no Chinese, no Japanese, no Korean).
- Be specific and actionable — a clinician should be able to act on your response immediately."""

    def _format_chat_history(
        self, conversation_history: Optional[List[Tuple[str, str]]] = None
    ) -> str:
        """
        Format recent conversation into a prompt-safe transcript.

        Args:
            conversation_history: Optional external conversation history

        Returns:
            Formatted transcript or a short placeholder
        """
        if conversation_history is not None:
            history_items = conversation_history[-5:]
        else:
            history_items = [
                (getattr(message, "type", "unknown"), getattr(message, "content", ""))
                for message in self.message_history.messages[-10:]
            ]

        lines = [
            f"{role.title()}: {content.strip()}"
            for role, content in history_items
            if content and content.strip()
        ]

        return "\n".join(lines) if lines else "No prior conversation."

    def _check_token_budget(self, context: str) -> str:
        """
        Check and enforce token budget constraints.

        Args:
            context: Context text to check

        Returns:
            Truncated context if necessary
        """
        # Rough estimation: 1 token ≈ 4 characters
        estimated_tokens = len(context) / 4

        if estimated_tokens > self.max_tokens:
            # Truncate context to fit budget
            char_limit = int(self.max_tokens * 4 * 0.8)  # 80% of budget for safety
            truncated = context[:char_limit]
            logger.warning(
                f"Context truncated: {int(estimated_tokens)} -> "
                f"{int(len(truncated)/4)} tokens"
            )
            return truncated

        return context

    def _extract_citations(
        self, response: str, source_docs: Optional[List[Dict[str, Any]]] = None
    ) -> List[Citation]:
        """
        Extract citations from LLM response and enrich with metadata.

        Args:
            response: LLM response text
            source_docs: Optional list of source documents with metadata

        Returns:
            List of Citation objects
        """
        # Find all citation numbers in the response
        citation_numbers = re.findall(r"\[(\d+)\]", response)
        unique_citations = sorted(set(citation_numbers), key=int)

        citations = []

        if unique_citations:
            # LLM included [N] markers — map them to source_docs
            for num in unique_citations:
                idx = int(num) - 1
                if source_docs and idx < len(source_docs):
                    doc = source_docs[idx]
                    citations.append(
                        Citation(
                            number=num,
                            source=doc.get("source", f"Source {num}"),
                            title=doc.get("title"),
                            url=doc.get("url"),
                            pmid=doc.get("pmid"),
                            tier=doc.get("tier"),
                            source_type=doc.get("source_type"),
                        )
                    )
                else:
                    citations.append(Citation(number=num, source=f"Source {num}"))
        elif source_docs:
            # LLM answered without [N] markers but context was provided —
            # attach retrieved docs so the user knows what sources informed the answer.
            for i, doc in enumerate(source_docs, 1):
                citations.append(
                    Citation(
                        number=str(i),
                        source=doc.get("source", f"Source {i}"),
                        title=doc.get("title"),
                        url=doc.get("url"),
                        pmid=doc.get("pmid"),
                        tier=doc.get("tier"),
                        source_type=doc.get("source_type"),
                    )
                )

        return citations

    @retry(
        retry=retry_if_not_exception_type(GroqAuthError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _generate_with_retry(self, question: str, context: str, chat_history: str) -> str:
        """
        Generate response with retry logic.

        Args:
            question: User question (PII redacted)
            context: Retrieved context

        Returns:
            LLM response text

        Raises:
            Exception: If all retries fail
        """
        # Modern LangChain 1.x API using invoke()
        return self.chain.invoke(
            {
                "question": question,
                "context": context,
                "chat_history": chat_history,
            }
        )

    def _get_model_name(self) -> str:
        """Best-effort extraction of the active model name for persistence."""
        for attr_name in ("model_name", "model", "model_id"):
            value = getattr(self.llm, attr_name, None)
            if value:
                return str(value)
        return self.provider

    def query(
        self,
        question: str,
        retrieved_context: str = "",
        source_docs: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Tuple[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Main query function with PII protection and error handling.

        Args:
            question: User's medical question
            retrieved_context: Retrieved documents from 4-tier system
            source_docs: Optional list of source document metadata

        Returns:
            Dictionary with:
                - answer: The medical response
                - citations: List of citations used
                - redacted_query: Query with PII redacted
                - pii_detected: List of PII entities found
                - disclaimer: Medical disclaimer
                - error: Error message if any

        Example:
            >>> bot = ProductionMedicalChatbot()
            >>> result = bot.query(
            ...     question="Patient John Doe has septic shock",
            ...     retrieved_context="[1] Sepsis guidelines...",
            ...     source_docs=[{"source": "PMID:12345", "pmid": "12345"}]
            ... )
        """
        try:
            # Step 1: Redact PII from user question
            redacted_question, pii_entities = self._redact_pii(question)

            if pii_entities:
                logger.info(
                    f"Query contained PII: {len(pii_entities)} entities redacted"
                )

                # Log PII detection event for compliance
                if self.pii_callback:
                    self.pii_callback.log_pii_detection(
                        query=question,
                        entities_detected=pii_entities,
                        redacted_query=redacted_question,
                    )

            # Step 2: Check token budget
            safe_context = self._check_token_budget(retrieved_context)
            chat_history = self._format_chat_history(conversation_history)

            # Step 3: Generate response with retry logic
            response = self._generate_with_retry(
                question=redacted_question,
                context=safe_context,
                chat_history=chat_history,
            )

            self.message_history.add_user_message(redacted_question)
            self.message_history.add_ai_message(response)

            # Step 4: Extract citations with metadata
            citations = self._extract_citations(response, source_docs)

            # Step 5: Build structured response
            return {
                "answer": response,
                "citations": [c.model_dump() for c in citations],
                "redacted_query": redacted_question,
                "pii_detected": pii_entities,
                "disclaimer": "⚠️ Privacy Notice: Personal information redacted. For educational purposes only.",
                "model_name": self._get_model_name(),
                "error": None,
            }

        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            return {
                "answer": "I apologize, but I'm unable to generate a response at this time. Please consult with a healthcare professional for medical guidance.",
                "citations": [],
                "redacted_query": question,
                "pii_detected": [],
                "disclaimer": "⚠️ System error. Consult healthcare provider.",
                "model_name": self._get_model_name(),
                "error": str(e),
            }

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.message_history.clear()
        logger.info("Conversation memory cleared")

    def get_memory_summary(self) -> str:
        """
        Get current conversation memory summary.

        Returns:
            Memory summary string
        """
        try:
            messages = self.message_history.messages
            return "\n".join([f"{m.type}: {m.content}" for m in messages])
        except AttributeError:
            return ""

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get LangChain usage metrics.

        Returns:
            Dictionary with token usage, costs, latency, errors
        """
        if self.callback_handler:
            return self.callback_handler.get_metrics()
        return {}

    def get_pii_summary(self) -> Dict[str, Any]:
        """
        Get PII detection summary.

        Returns:
            Dictionary with PII detection statistics
        """
        if self.pii_callback:
            return self.pii_callback.get_pii_summary()
        return {}

    def print_metrics(self) -> None:
        """Print metrics summary to console."""
        if self.callback_handler:
            self.callback_handler.print_summary()

        if self.pii_callback:
            pii_summary = self.pii_callback.get_pii_summary()
            if pii_summary["total_events"] > 0:
                print("\n" + "=" * 60)
                print("PII DETECTION SUMMARY")
                print("=" * 60)
                print(f"Total Events:     {pii_summary['total_events']}")
                print(f"Total Entities:   {pii_summary['total_entities']}")
                print("Entity Types:")
                for entity_type, count in pii_summary["entity_type_counts"].items():
                    print(f"  - {entity_type}: {count}")
                print("=" * 60 + "\n")


# Module-level utility functions


def create_medical_chatbot(
    provider: Optional[str] = None, **kwargs
) -> ProductionMedicalChatbot:
    """
    Factory function to create medical chatbot with auto provider detection.

    Args:
        provider: Optional provider override
        **kwargs: Additional arguments for ProductionMedicalChatbot

    Returns:
        Configured ProductionMedicalChatbot instance
    """
    # Auto-detect provider based on available API keys
    if provider is None:
        if settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY"):
            provider = "groq"
        elif settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif settings.AWS_ACCESS_KEY_ID or os.getenv("AWS_ACCESS_KEY_ID"):
            provider = "bedrock"
        else:
            raise ValueError("No LLM API key found in environment")

    logger.info(f"Creating medical chatbot with provider: {provider}")
    return ProductionMedicalChatbot(provider=provider, **kwargs)


if __name__ == "__main__":
    # Example usage
    bot = create_medical_chatbot()

    context = """
    [1] CAG Guidelines - Septic Shock: Early recognition critical.
    Administer IV fluids 30ml/kg within first 3 hours.
    [2] PubMed PMID:12345678 - "Early Goal-Directed Therapy":
    16% mortality reduction with protocol compliance.
    """

    result = bot.query(
        question="Patient has shock and BP 80/50. What should I do?",
        retrieved_context=context,
        source_docs=[
            {"source": "CAG Guidelines", "url": "https://example.com"},
            {"source": "PubMed", "pmid": "12345678"},
        ],
    )

    print("=== Response ===")
    print(result["answer"])
    print("\n=== Citations ===")
    print(result["citations"])
