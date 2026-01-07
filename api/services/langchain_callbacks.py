"""
LangChain Callbacks for Monitoring and Observability

Provides custom callback handlers for tracking LLM usage, costs, latency,
and errors in production medical chatbot.

Author: MediAI Team
Version: 1.0.0
"""

import logging
import time
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MedicalChatbotCallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler for medical chatbot monitoring.

    Tracks:
    - Token usage (prompt, completion, total)
    - Latency (LLM call duration)
    - Errors and retries
    - PII detection events
    - Cost estimation
    - Response quality metrics

    Example:
        >>> from langchain.chains import LLMChain
        >>> callback = MedicalChatbotCallbackHandler()
        >>> chain = LLMChain(llm=llm, callbacks=[callback])
        >>> result = chain.run("Patient query")
        >>> print(callback.get_metrics())
    """

    def __init__(self, log_to_file: bool = False, metrics_file: Optional[str] = None):
        """
        Initialize callback handler.

        Args:
            log_to_file: Whether to log metrics to file
            metrics_file: Optional file path for metrics logging
        """
        super().__init__()

        self.log_to_file = log_to_file
        self.metrics_file = metrics_file

        # Metrics tracking
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.llm_calls = 0
        self.errors = 0
        self.start_time = None
        self.end_time = None
        self.latency_ms = 0

        # Call history
        self.call_history: List[Dict[str, Any]] = []

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when LLM starts running."""
        self.start_time = time.time()
        self.llm_calls += 1

        logger.info(f"LLM call #{self.llm_calls} started")
        logger.debug(f"Prompt length: {len(prompts[0])} chars")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends running."""
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000

        # Extract token usage from response
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            prompt_tokens = token_usage.get("prompt_tokens", 0)
            completion_tokens = token_usage.get("completion_tokens", 0)
            total_tokens = token_usage.get("total_tokens", 0)

            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.total_tokens += total_tokens

            # Estimate cost (Groq pricing as example)
            # Adjust based on actual provider
            cost = self._estimate_cost(prompt_tokens, completion_tokens)
            self.total_cost += cost

            # Log metrics
            logger.info(
                f"LLM call #{self.llm_calls} completed: "
                f"{total_tokens} tokens, "
                f"{self.latency_ms:.2f}ms, "
                f"${cost:.6f}"
            )

            # Record call
            call_record = {
                "call_number": self.llm_calls,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": self.latency_ms,
                "cost": cost,
                "timestamp": self.end_time,
            }
            self.call_history.append(call_record)

            # Write to file if enabled
            if self.log_to_file and self.metrics_file:
                self._write_metrics_to_file(call_record)

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors."""
        self.errors += 1
        logger.error(f"LLM error #{self.errors}: {error}", exc_info=True)

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Called when chain starts running."""
        logger.debug("Chain started")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain ends running."""
        logger.debug("Chain completed")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when chain errors."""
        logger.error(f"Chain error: {error}", exc_info=True)

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost based on token usage.

        Groq pricing (example - free tier):
        - Prompt: $0
        - Completion: $0

        For paid tiers, update these rates.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD
        """
        # Groq free tier - no cost
        # For other providers, use actual pricing
        # OpenAI GPT-4 example:
        # prompt_cost = prompt_tokens * 0.00003  # $0.03 per 1K tokens
        # completion_cost = completion_tokens * 0.00006  # $0.06 per 1K tokens

        prompt_cost = 0
        completion_cost = 0

        return prompt_cost + completion_cost

    def _write_metrics_to_file(self, metrics: Dict[str, Any]) -> None:
        """Write metrics to file."""
        try:
            import json

            with open(self.metrics_file, "a") as f:
                f.write(json.dumps(metrics) + "\n")
        except Exception as e:
            logger.error(f"Failed to write metrics to file: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics summary.

        Returns:
            Dictionary with all tracked metrics
        """
        return {
            "total_llm_calls": self.llm_calls,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "total_errors": self.errors,
            "average_latency_ms": round(
                sum(c["latency_ms"] for c in self.call_history)
                / max(len(self.call_history), 1),
                2,
            ),
            "call_history": self.call_history,
        }

    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.llm_calls = 0
        self.errors = 0
        self.call_history = []

        logger.info("Metrics reset")

    def print_summary(self) -> None:
        """Print metrics summary to console."""
        metrics = self.get_metrics()

        print("\n" + "=" * 60)
        print("LANGCHAIN METRICS SUMMARY")
        print("=" * 60)
        print(f"Total LLM Calls:       {metrics['total_llm_calls']}")
        print(f"Total Tokens:          {metrics['total_tokens']:,}")
        print(f"  - Prompt Tokens:     {metrics['prompt_tokens']:,}")
        print(f"  - Completion Tokens: {metrics['completion_tokens']:,}")
        print(f"Total Cost:            ${metrics['total_cost_usd']:.6f}")
        print(f"Average Latency:       {metrics['average_latency_ms']:.2f}ms")
        print(f"Errors:                {metrics['total_errors']}")
        print("=" * 60 + "\n")


class StreamlitCallbackHandler(BaseCallbackHandler):
    """
    Callback handler for Streamlit UI integration.

    Displays LLM progress in Streamlit app.
    """

    def __init__(self, streamlit_container=None):
        """
        Initialize Streamlit callback.

        Args:
            streamlit_container: Streamlit container for updates
        """
        super().__init__()
        self.container = streamlit_container

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Update Streamlit UI when LLM starts."""
        if self.container:
            self.container.info("🤖 Generating response...")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Update Streamlit UI when LLM ends."""
        if self.container:
            self.container.success("✅ Response generated")


class PIIDetectionCallbackHandler(BaseCallbackHandler):
    """
    Callback handler for PII detection events.

    Logs and tracks PII redaction events for compliance.
    """

    def __init__(self):
        """Initialize PII callback."""
        super().__init__()
        self.pii_events: List[Dict[str, Any]] = []

    def log_pii_detection(
        self, query: str, entities_detected: List[Dict[str, Any]], redacted_query: str
    ) -> None:
        """
        Log PII detection event.

        Args:
            query: Original query (not stored for privacy)
            entities_detected: List of detected PII entities
            redacted_query: Redacted version of query
        """
        event = {
            "timestamp": time.time(),
            "num_entities": len(entities_detected),
            "entity_types": [e["type"] for e in entities_detected],
            "query_length": len(query),
            "redacted_length": len(redacted_query),
        }

        self.pii_events.append(event)

        logger.warning(
            f"PII detected: {len(entities_detected)} entities "
            f"({', '.join(set(e['type'] for e in entities_detected))})"
        )

    def get_pii_summary(self) -> Dict[str, Any]:
        """Get PII detection summary."""
        if not self.pii_events:
            return {
                "total_events": 0,
                "total_entities": 0,
                "entity_type_counts": {},
            }

        total_entities = sum(e["num_entities"] for e in self.pii_events)

        # Count entity types
        entity_type_counts = {}
        for event in self.pii_events:
            for entity_type in event["entity_types"]:
                entity_type_counts[entity_type] = (
                    entity_type_counts.get(entity_type, 0) + 1
                )

        return {
            "total_events": len(self.pii_events),
            "total_entities": total_entities,
            "entity_type_counts": entity_type_counts,
        }


# Global callback instances for app-wide use
_global_callback_handler: Optional[MedicalChatbotCallbackHandler] = None
_global_pii_callback: Optional[PIIDetectionCallbackHandler] = None


def get_callback_handler() -> MedicalChatbotCallbackHandler:
    """Get or create global callback handler."""
    global _global_callback_handler

    if _global_callback_handler is None:
        _global_callback_handler = MedicalChatbotCallbackHandler()
        logger.info("Created global MedicalChatbotCallbackHandler")

    return _global_callback_handler


def get_pii_callback() -> PIIDetectionCallbackHandler:
    """Get or create global PII callback."""
    global _global_pii_callback

    if _global_pii_callback is None:
        _global_pii_callback = PIIDetectionCallbackHandler()
        logger.info("Created global PIIDetectionCallbackHandler")

    return _global_pii_callback


if __name__ == "__main__":
    # Example usage
    callback = MedicalChatbotCallbackHandler(
        log_to_file=True, metrics_file="metrics.jsonl"
    )

    # Simulate LLM calls
    from langchain.schema import Generation, LLMResult

    callback.on_llm_start({}, ["Test prompt"])

    # Simulate response
    result = LLMResult(
        generations=[[Generation(text="Test response")]],
        llm_output={
            "token_usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "total_tokens": 150,
            }
        },
    )

    callback.on_llm_end(result)
    callback.print_summary()
