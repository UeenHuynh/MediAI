"""
LLM Provider Service - Layer 6
Supports Groq API (primary) and HuggingFace (fallback)
"""

import logging
import os
from enum import Enum
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""

    GROQ = "groq"
    HUGGINGFACE = "huggingface"


class LLMOrchestrator:
    """
    Orchestrates LLM requests with automatic fallback
    Primary: Groq API (fast, free tier)
    Fallback: HuggingFace local models
    """

    def __init__(
        self,
        primary_provider: str = "groq",
        fallback_provider: str = "huggingface",
        groq_api_key: Optional[str] = None,
        hf_token: Optional[str] = None,
    ):
        """
        Initialize LLM orchestrator

        Args:
            primary_provider: Primary LLM provider (default: groq)
            fallback_provider: Fallback provider (default: huggingface)
            groq_api_key: Groq API key
            hf_token: HuggingFace token (optional)
        """
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider

        # Initialize providers
        self.groq_client = None
        self.hf_client = None

        # Initialize Groq
        if primary_provider == "groq" or fallback_provider == "groq":
            try:
                self.groq_client = GroqLLM(
                    api_key=groq_api_key or os.getenv("GROQ_API_KEY")
                )
                logger.info("✅ Groq API initialized")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize Groq: {e}")

        # Initialize HuggingFace
        if primary_provider == "huggingface" or fallback_provider == "huggingface":
            try:
                self.hf_client = HuggingFaceLLM(
                    token=hf_token or os.getenv("HUGGINGFACE_TOKEN")
                )
                logger.info("✅ HuggingFace initialized")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize HuggingFace: {e}")

        # Rate limiter
        from .rate_limiter import RateLimiter

        self.rate_limiter = RateLimiter(
            max_calls=int(os.getenv("GROQ_RATE_LIMIT", 30)), period=60  # per minute
        )

    def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 800,
        temperature: float = 0.3,
        force_provider: Optional[str] = None,
    ) -> Dict:
        """
        Generate response with automatic fallback

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            force_provider: Force specific provider (optional)

        Returns:
            {
                "content": str,
                "provider": str,
                "model": str,
                "finish_reason": str
            }
        """
        # Determine which provider to use
        provider = force_provider or self.primary_provider

        try:
            # Try primary provider
            if provider == "groq" and self.groq_client:
                if self.rate_limiter.can_proceed():
                    result = self.groq_client.chat(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    return {
                        "content": result["content"],
                        "provider": "groq",
                        "model": result["model"],
                        "finish_reason": result.get("finish_reason", "stop"),
                    }
                else:
                    logger.warning("⚠️ Groq rate limit exceeded, using fallback")
                    raise Exception("Rate limit exceeded")

            elif provider == "huggingface" and self.hf_client:
                result = self.hf_client.chat(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return {
                    "content": result["content"],
                    "provider": "huggingface",
                    "model": result["model"],
                    "finish_reason": "stop",
                }

        except Exception as e:
            logger.error(f"❌ {provider} failed: {e}")

            # Try fallback
            if self.fallback_provider != provider:
                logger.info(f"🔄 Falling back to {self.fallback_provider}")
                return self.generate(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    force_provider=self.fallback_provider,
                )

        # Both failed
        return {
            "content": "I apologize, but I'm unable to generate a response at this time. Please try again later.",
            "provider": "error",
            "model": "none",
            "finish_reason": "error",
        }

    def analyze_image(
        self,
        image_data: Union[str, bytes],
        prompt: str,
        max_tokens: int = 500,
    ) -> Dict:
        """
        Analyze image using Groq Vision

        Args:
            image_data: Image URL or base64 encoded bytes
            prompt: Text prompt for analysis
            max_tokens: Maximum tokens in response

        Returns:
            {
                "content": str,
                "provider": "groq",
                "model": str
            }
        """
        if not self.groq_client:
            return {
                "content": "Vision API not available. Please configure Groq API key.",
                "provider": "error",
                "model": "none",
            }

        try:
            result = self.groq_client.analyze_image(
                image_data=image_data,
                prompt=prompt,
                max_tokens=max_tokens,
            )
            return result

        except Exception as e:
            logger.error(f"❌ Vision analysis failed: {e}")
            return {
                "content": f"Failed to analyze image: {str(e)}",
                "provider": "error",
                "model": "none",
            }

    def get_status(self) -> Dict:
        """Get status of all providers"""
        return {
            "primary": self.primary_provider,
            "fallback": self.fallback_provider,
            "groq_available": self.groq_client is not None,
            "hf_available": self.hf_client is not None,
            "rate_limit_remaining": self.rate_limiter.remaining_calls(),
        }


class GroqLLM:
    """Groq API client"""

    def __init__(self, api_key: str):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key from https://console.groq.com/
        """
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")

        self.client = Groq(api_key=api_key)
        self.chat_model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        self.vision_model = os.getenv(
            "GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview"
        )
        logger.info(f"Groq initialized with model: {self.chat_model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 800,
        temperature: float = 0.3,
    ) -> Dict:
        """
        Generate chat completion

        Args:
            messages: Conversation messages
            max_tokens: Max output tokens
            temperature: Sampling temperature

        Returns:
            {"content": str, "model": str, "finish_reason": str}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            raise

    def analyze_image(
        self,
        image_data: Union[str, bytes],
        prompt: str,
        max_tokens: int = 500,
    ) -> Dict:
        """
        Analyze image with Groq Vision

        Args:
            image_data: Image URL or base64 string
            prompt: Analysis prompt
            max_tokens: Max output tokens

        Returns:
            {"content": str, "model": str, "provider": "groq"}
        """
        # Prepare image content
        if isinstance(image_data, bytes):
            import base64

            image_url = (
                f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
            )
        else:
            image_url = image_data

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=messages,
            max_tokens=max_tokens,
        )

        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "provider": "groq",
        }


class HuggingFaceLLM:
    """HuggingFace local model fallback"""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize HuggingFace client

        Args:
            token: HuggingFace API token (optional, for private models)
        """
        try:
            import torch
            from transformers import pipeline
        except ImportError:
            raise ImportError(
                "transformers/torch not installed. Run: pip install transformers torch"
            )

        self.token = token
        model_name = os.getenv("HF_LOCAL_MODEL", "microsoft/phi-2")

        logger.info(
            f"Loading HuggingFace model: {model_name} (this may take a while...)"
        )

        # Determine device
        device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if device == 0 else "CPU"
        logger.info(f"Using device: {device_name}")

        try:
            self.generator = pipeline(
                "text-generation",
                model=model_name,
                device=device,
                token=token,
                max_new_tokens=500,
            )
            self.model_name = model_name
            logger.info(f"✅ HuggingFace model loaded: {model_name}")

        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> Dict:
        """
        Generate response using local model

        Args:
            messages: Conversation messages
            max_tokens: Max output tokens
            temperature: Sampling temperature

        Returns:
            {"content": str, "model": str}
        """
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)

        try:
            result = self.generator(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id,
            )

            # Extract generated text (remove prompt)
            generated = result[0]["generated_text"]
            if generated.startswith(prompt):
                generated = generated[len(prompt):].strip()

            return {
                "content": generated,
                "model": self.model_name,
            }

        except Exception as e:
            logger.error(f"HuggingFace generation error: {e}")
            raise

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to single prompt"""
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


# Convenience functions
def get_llm_orchestrator(**kwargs) -> LLMOrchestrator:
    """Get configured LLM orchestrator instance"""
    return LLMOrchestrator(
        primary_provider=os.getenv("LLM_PRIMARY_PROVIDER", "groq"),
        fallback_provider=os.getenv("LLM_FALLBACK_PROVIDER", "huggingface"),
        **kwargs,
    )
