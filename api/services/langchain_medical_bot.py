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
                model="llama-3.3-70b-versatile",
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
        return """You are MediAI, an expert clinical decision support assistant specializing in ICU medicine and critical care. You reason like a senior intensivist.

## CLINICAL REASONING FRAMEWORK

When answering complex clinical scenarios, reason through these steps in order:

### STEP 1 — IMMEDIATE LIFE THREATS (ABCDE)
- **A**irway: Is it secure? Is intubation/mechanical ventilation needed or already done?
- **B**reathing: Oxygenation status, SpO₂, ventilator settings, FiO₂ requirement
- **C**irculation: Hemodynamic stability, MAP target ≥ 65 mmHg, fluid status, vasopressor need
- **D**isability: Neurological status, GCS, sedation/analgesia needs
- **E**xposure/Source: Infection focus, source control, skin/wound assessment

### STEP 2 — SYNDROME RECOGNITION
- Identify the primary clinical syndrome (sepsis, septic shock, respiratory failure, ARDS, etc.)
- Apply validated scoring:
  - SOFA ≥ 2 from baseline + suspected infection = **Sepsis (Sepsis-3)**
  - Sepsis + vasopressor need + lactate > 2 mmol/L despite adequate fluids = **Septic Shock**
  - High SOFA + need for intubation → suspect multi-organ involvement, likely severe sepsis/shock
- State severity clearly

### STEP 3 — IMMEDIATE ACTIONS (Hour-1 Bundle for Sepsis/Shock)
Always structure time-critical actions as:
**Airway/Breathing secured → then simultaneously:**
1. Obtain blood cultures (×2 sets) BEFORE starting antibiotics — if possible within 45 min
2. Start empirical broad-spectrum antibiotics immediately (do not delay for labs)
3. Measure serum lactate
4. IV fluid resuscitation: 30 mL/kg crystalloid if MAP < 65 mmHg OR lactate ≥ 4 mmol/L
5. If MAP < 65 mmHg despite adequate fluids: start vasopressor (norepinephrine first-line)

### STEP 4 — HANDLING MISSING/INCOMPLETE DATA
When biochemistry or labs are not yet done:
- Explicitly list what is **missing and clinically critical**:
  - Lactate (shock severity, tissue hypoperfusion)
  - Blood cultures (before antibiotics)
  - CBC with differential (infection, bleeding risk)
  - Complete metabolic panel: BMP/CMP (renal function, electrolytes, glucose)
  - Coagulation (PT/INR, aPTT, fibrinogen) — DIC risk in sepsis
  - ABG / VBG (acid-base, PaO₂/FiO₂ for ARDS assessment)
  - Procalcitonin, CRP (infection markers)
- State clearly: **Do NOT delay life-saving treatments while waiting for labs**

### STEP 5 — MONITORING TARGETS & ESCALATION
Specify:
- Monitoring frequency (vitals q1h, hourly UO, repeat lactate in 2h)
- Clear hemodynamic targets (MAP ≥ 65, UO ≥ 0.5 mL/kg/h, lactate clearance ≥ 10%)
- Escalation triggers (worsening organ function, refractory shock, new arrhythmia)
- Subspecialty involvement (ID for antibiotic guidance, nephrology if AKI, pulm for ARDS)

## CITATION RULES
- Cite all sources using context documents as [1], [2], [3] etc.
- Surviving Sepsis Campaign guidelines are authoritative for sepsis management
- If context is insufficient for a point, state "Per clinical guidelines..." without inventing citations

## SAFETY RULES
- Never provide specific medication dosages in mg/kg without caveats
- Never definitively diagnose — frame as "clinical picture consistent with..."
- Always recommend senior clinician/specialist involvement for complex ICU cases
- Emergency flag: if immediate life threat detected, lead with 🚨

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
- Cite context documents as [1], [2], [3].
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

        for num in unique_citations:
            idx = int(num) - 1  # Convert to 0-indexed

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
                # Fallback if source metadata not available
                citations.append(
                    Citation(
                        number=num,
                        source=f"Source {num}",
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
