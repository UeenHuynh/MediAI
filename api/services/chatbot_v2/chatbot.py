"""Stable chatbot v2 wrapper for free-tier friendly operation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    from api.core.redis_cache import cache_chat_response, get_cached_chat_response
    from api.services.langchain_medical_bot import ProductionMedicalChatbot
    from api.services.safety_guardrails import SafetyGuardrails
except ImportError:
    from core.redis_cache import cache_chat_response, get_cached_chat_response
    from services.langchain_medical_bot import ProductionMedicalChatbot
    from services.safety_guardrails import SafetyGuardrails

logger = logging.getLogger(__name__)


class ProductionMedicalChatbotV2:
    """
    Compatibility wrapper around the existing LangChain bot.

    Goals:
    - keep the current `query()` contract stable for the router
    - harden the response path with lightweight safety checks
    - allow free-tier deployments to degrade gracefully
    """

    def __init__(
        self,
        provider: str = "groq",
        enable_pii_redaction: bool = True,
        enable_callbacks: bool = True,
        enable_cache: bool = True,
    ):
        self.provider = provider
        self.enable_cache = enable_cache
        self.guardrails = SafetyGuardrails()
        self.legacy_bot = ProductionMedicalChatbot(
            provider=provider,
            enable_pii_redaction=enable_pii_redaction,
            enable_callbacks=enable_callbacks,
        )

    def _cache_eligible(
        self,
        question: str,
        conversation_history: Optional[List[Tuple[str, str]]] = None,
    ) -> bool:
        """Only cache straightforward single-turn questions."""
        return (
            self.enable_cache
            and bool(question.strip())
            and len(question.strip()) >= 12
            and not conversation_history
        )

    def _build_blocked_response(self) -> Dict[str, Any]:
        answer = self.guardrails.create_inappropriate_response()
        return {
            "answer": answer,
            "citations": [],
            "redacted_query": None,
            "pii_detected": [],
            "disclaimer": self.guardrails.disclaimer_not_clinical_use.strip(),
            "model_name": "chatbot_v2/blocked",
            "error": None,
        }

    def _apply_safety(
        self,
        question: str,
        answer: str,
        disclaimer: Optional[str],
    ) -> Tuple[str, str]:
        """
        Apply lightweight safety framing without discarding the model answer.
        """
        is_emergency, _ = self.guardrails.check_emergency(question)
        final_answer = answer

        if is_emergency:
            answer_lower = answer.lower()
            if "911" not in answer and "emergency number" not in answer_lower:
                final_answer = (
                    "🚨 This may describe an emergency scenario. "
                    "Escalate immediately to qualified clinicians and call 911 or "
                    "your local emergency number when appropriate.\n\n"
                    f"{answer}"
                )

        is_safe, issues = self.guardrails.validate_response(final_answer)
        if not is_safe:
            logger.warning("Chatbot V2 safety review found issues: %s", issues)
            final_answer = (
                "⚠️ Safety review added extra caution to this response.\n\n"
                f"{final_answer}"
            )

        final_disclaimer = disclaimer or self.guardrails.disclaimer_standard.strip()
        if is_emergency:
            final_disclaimer = self.guardrails.disclaimer_emergency.strip()

        return final_answer, final_disclaimer

    def query(
        self,
        question: str,
        retrieved_context: str = "",
        source_docs: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Tuple[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Run the wrapped chatbot with cache and safety enhancements."""
        normalized_question = question.strip()
        is_inappropriate, _ = self.guardrails.check_inappropriate(normalized_question)
        if is_inappropriate:
            return self._build_blocked_response()

        if self._cache_eligible(normalized_question, conversation_history):
            cached = get_cached_chat_response(normalized_question)
            if cached:
                logger.info(
                    "LLM_TRACE provider=%s model=cache_hit fallback_used=False",
                    self.provider,
                )
                cached_result = dict(cached)
                cached_result.setdefault("model_name", "chatbot_v2/cache")
                cached_result.setdefault("error", None)
                return cached_result

        result = self.legacy_bot.query(
            question=normalized_question,
            retrieved_context=retrieved_context,
            source_docs=source_docs,
            conversation_history=conversation_history,
        )

        final_answer, final_disclaimer = self._apply_safety(
            question=normalized_question,
            answer=result.get("answer", ""),
            disclaimer=result.get("disclaimer"),
        )

        response = {
            "answer": final_answer,
            "citations": result.get("citations", []),
            "redacted_query": result.get("redacted_query"),
            "pii_detected": result.get("pii_detected", []),
            "disclaimer": final_disclaimer,
            "model_name": result.get(
                "model_name", f"chatbot_v2/{self.provider or 'unknown'}"
            ),
            "error": result.get("error"),
        }

        logger.info(
            "LLM_TRACE provider=%s model=%s fallback_used=%s error=%s",
            self.provider,
            response.get("model_name", "unknown"),
            response.get("model_name") == "chatbot_v2/blocked",
            bool(response.get("error")),
        )

        if self._cache_eligible(normalized_question, conversation_history) and not response.get(
            "error"
        ):
            cache_chat_response(normalized_question, response)

        return response

    def clear_memory(self) -> None:
        """Delegate to the wrapped chatbot."""
        self.legacy_bot.clear_memory()

    def get_memory_summary(self) -> str:
        """Delegate to the wrapped chatbot."""
        return self.legacy_bot.get_memory_summary()

    def get_metrics(self) -> Dict[str, Any]:
        """Delegate to the wrapped chatbot."""
        return self.legacy_bot.get_metrics()

    def get_pii_summary(self) -> Dict[str, Any]:
        """Delegate to the wrapped chatbot."""
        return self.legacy_bot.get_pii_summary()
