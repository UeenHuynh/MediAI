"""
Unit tests for LLM Provider Service
Tests Groq API integration, HuggingFace fallback, and orchestration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import os


class TestLLMOrchestratorInit:
    """Tests for LLMOrchestrator initialization"""

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_init_groq_primary(self, mock_rate_limiter, mock_groq_llm):
        """Test initialization with Groq as primary provider"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_llm.return_value = Mock()
        mock_rate_limiter.return_value = Mock()

        orchestrator = LLMOrchestrator(
            primary_provider="groq",
            fallback_provider="huggingface",
            groq_api_key="test_key"
        )

        assert orchestrator.primary_provider == "groq"
        assert orchestrator.fallback_provider == "huggingface"
        mock_groq_llm.assert_called_once()
        assert orchestrator.groq_client is not None

    @patch('api.services.llm_provider.HuggingFaceLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_init_huggingface_primary(self, mock_rate_limiter, mock_hf_llm):
        """Test initialization with HuggingFace as primary"""
        from api.services.llm_provider import LLMOrchestrator

        mock_hf_llm.return_value = Mock()
        mock_rate_limiter.return_value = Mock()

        orchestrator = LLMOrchestrator(
            primary_provider="huggingface",
            fallback_provider="groq",
            hf_token="test_token"
        )

        assert orchestrator.primary_provider == "huggingface"
        mock_hf_llm.assert_called_once()
        assert orchestrator.hf_client is not None

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_init_with_env_vars(self, mock_rate_limiter, mock_groq_llm):
        """Test initialization using environment variables"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_llm.return_value = Mock()
        mock_rate_limiter.return_value = Mock()

        with patch.dict(os.environ, {'GROQ_API_KEY': 'env_key'}):
            orchestrator = LLMOrchestrator(primary_provider="groq")

        mock_groq_llm.assert_called_once()
        assert orchestrator.groq_client is not None

    @patch('api.services.llm_provider.GroqLLM', side_effect=Exception("Init failed"))
    @patch('api.services.rate_limiter.RateLimiter')
    def test_init_groq_failure_graceful(self, mock_rate_limiter, mock_groq_llm):
        """Test graceful handling when Groq init fails"""
        from api.services.llm_provider import LLMOrchestrator

        mock_rate_limiter.return_value = Mock()

        # Should not raise, should handle gracefully
        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="bad_key")

        assert orchestrator.groq_client is None

    @patch('api.services.rate_limiter.RateLimiter')
    def test_init_rate_limiter(self, mock_rate_limiter):
        """Test rate limiter initialization"""
        from api.services.llm_provider import LLMOrchestrator

        mock_rate_limiter.return_value = Mock()

        with patch.dict(os.environ, {'GROQ_RATE_LIMIT': '50'}):
            orchestrator = LLMOrchestrator()

        mock_rate_limiter.assert_called_once_with(max_calls=50, period=60)
        assert orchestrator.rate_limiter is not None


class TestLLMOrchestratorGenerate:
    """Tests for LLMOrchestrator.generate() method"""

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_generate_groq_success(self, mock_rate_limiter, mock_groq):
        """Test successful generation with Groq"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.chat.return_value = {
            "content": "This is a test response from Groq",
            "model": "llama-3.1-70b-versatile",
            "finish_reason": "stop"
        }
        mock_groq.return_value = mock_groq_instance

        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.can_proceed.return_value = True
        mock_rate_limiter_instance.remaining_calls.return_value = 25
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")

        messages = [{"role": "user", "content": "What is sepsis?"}]
        result = orchestrator.generate(messages, max_tokens=500, temperature=0.5)

        assert result["content"] == "This is a test response from Groq"
        assert result["provider"] == "groq"
        assert result["model"] == "llama-3.1-70b-versatile"
        assert result["finish_reason"] == "stop"

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_generate_respects_rate_limit(self, mock_rate_limiter, mock_groq):
        """Test that rate limiting is checked"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.chat.return_value = {
            "content": "Response",
            "model": "llama-3.1-70b-versatile",
            "finish_reason": "stop"
        }
        mock_groq.return_value = mock_groq_instance

        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.can_proceed.return_value = True
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")

        messages = [{"role": "user", "content": "Test"}]
        orchestrator.generate(messages)

        mock_rate_limiter_instance.can_proceed.assert_called_once()

    def test_generate_rate_limit_exceeded_fallback(self):
        """Test fallback when rate limit is exceeded"""
        with patch('api.services.llm_provider.GroqLLM') as mock_groq, \
             patch('api.services.llm_provider.HuggingFaceLLM') as mock_hf, \
             patch('api.services.rate_limiter.RateLimiter') as mock_rate_limiter:

            from api.services.llm_provider import LLMOrchestrator

            # Setup Groq (rate limited)
            mock_groq_instance = Mock()
            mock_groq.return_value = mock_groq_instance

            # Setup HuggingFace (fallback)
            mock_hf_instance = Mock()
            mock_hf_instance.chat.return_value = {
                "content": "Fallback response",
                "model": "microsoft/phi-2"
            }
            mock_hf.return_value = mock_hf_instance

            # Setup rate limiter (exceeded)
            mock_rate_limiter_instance = Mock()
            mock_rate_limiter_instance.can_proceed.return_value = False
            mock_rate_limiter.return_value = mock_rate_limiter_instance

            orchestrator = LLMOrchestrator(
                primary_provider="groq",
                fallback_provider="huggingface"
            )
            orchestrator.groq_client = mock_groq_instance
            orchestrator.hf_client = mock_hf_instance
            orchestrator.rate_limiter = mock_rate_limiter_instance

            messages = [{"role": "user", "content": "Test"}]
            result = orchestrator.generate(messages)

            # Should use HuggingFace fallback
            assert result["provider"] == "huggingface"
            assert result["content"] == "Fallback response"

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_generate_force_provider(self, mock_rate_limiter, mock_groq):
        """Test forcing specific provider"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.chat.return_value = {
            "content": "Response",
            "model": "llama-3.1-70b-versatile",
            "finish_reason": "stop"
        }
        mock_groq.return_value = mock_groq_instance

        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.can_proceed.return_value = True
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")

        messages = [{"role": "user", "content": "Test"}]
        result = orchestrator.generate(messages, force_provider="groq")

        assert result["provider"] == "groq"

    def test_generate_groq_error_fallback(self):
        """Test fallback when Groq fails"""
        with patch('api.services.llm_provider.GroqLLM') as mock_groq, \
             patch('api.services.llm_provider.HuggingFaceLLM') as mock_hf, \
             patch('api.services.rate_limiter.RateLimiter') as mock_rate_limiter:

            from api.services.llm_provider import LLMOrchestrator

            # Setup Groq (fails)
            mock_groq_instance = Mock()
            mock_groq_instance.chat.side_effect = Exception("API Error")
            mock_groq.return_value = mock_groq_instance

            # Setup HuggingFace (works)
            mock_hf_instance = Mock()
            mock_hf_instance.chat.return_value = {
                "content": "HF response",
                "model": "microsoft/phi-2"
            }
            mock_hf.return_value = mock_hf_instance

            mock_rate_limiter_instance = Mock()
            mock_rate_limiter_instance.can_proceed.return_value = True
            mock_rate_limiter.return_value = mock_rate_limiter_instance

            orchestrator = LLMOrchestrator(
                primary_provider="groq",
                fallback_provider="huggingface"
            )
            orchestrator.groq_client = mock_groq_instance
            orchestrator.hf_client = mock_hf_instance
            orchestrator.rate_limiter = mock_rate_limiter_instance

            messages = [{"role": "user", "content": "Test"}]
            result = orchestrator.generate(messages)

            assert result["provider"] == "huggingface"
            assert result["content"] == "HF response"

    def test_generate_all_providers_fail(self):
        """Test error response when all providers fail"""
        with patch('api.services.llm_provider.GroqLLM') as mock_groq, \
             patch('api.services.llm_provider.HuggingFaceLLM') as mock_hf, \
             patch('api.services.rate_limiter.RateLimiter') as mock_rate_limiter:

            from api.services.llm_provider import LLMOrchestrator

            mock_groq_instance = Mock()
            mock_groq_instance.chat.side_effect = Exception("Groq failed")
            mock_groq.return_value = mock_groq_instance

            mock_hf_instance = Mock()
            mock_hf_instance.chat.side_effect = Exception("HF failed")
            mock_hf.return_value = mock_hf_instance

            mock_rate_limiter_instance = Mock()
            mock_rate_limiter_instance.can_proceed.return_value = True
            mock_rate_limiter.return_value = mock_rate_limiter_instance

            orchestrator = LLMOrchestrator(
                primary_provider="groq",
                fallback_provider="huggingface"
            )
            orchestrator.groq_client = mock_groq_instance
            orchestrator.hf_client = mock_hf_instance
            orchestrator.rate_limiter = mock_rate_limiter_instance

            messages = [{"role": "user", "content": "Test"}]
            result = orchestrator.generate(messages)

            assert result["provider"] == "error"
            assert "unable to generate" in result["content"].lower()
            assert result["finish_reason"] == "error"

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_generate_with_custom_params(self, mock_rate_limiter, mock_groq):
        """Test generation with custom max_tokens and temperature"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.chat.return_value = {
            "content": "Response",
            "model": "llama-3.1-70b-versatile",
            "finish_reason": "stop"
        }
        mock_groq.return_value = mock_groq_instance

        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.can_proceed.return_value = True
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")

        messages = [{"role": "user", "content": "Test"}]
        orchestrator.generate(messages, max_tokens=1000, temperature=0.8)

        mock_groq_instance.chat.assert_called_once_with(
            messages=messages,
            max_tokens=1000,
            temperature=0.8
        )


class TestLLMOrchestratorAnalyzeImage:
    """Tests for LLMOrchestrator.analyze_image() method"""

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_analyze_image_success(self, mock_rate_limiter, mock_groq):
        """Test successful image analysis"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.analyze_image.return_value = {
            "content": "This image shows a chest X-ray with signs of pneumonia",
            "model": "llama-3.2-11b-vision-preview",
            "provider": "groq"
        }
        mock_groq.return_value = mock_groq_instance
        mock_rate_limiter.return_value = Mock()

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")
        orchestrator.groq_client = mock_groq_instance

        result = orchestrator.analyze_image(
            image_data="https://example.com/xray.jpg",
            prompt="Analyze this X-ray",
            max_tokens=500
        )

        assert result["content"] == "This image shows a chest X-ray with signs of pneumonia"
        assert result["provider"] == "groq"
        mock_groq_instance.analyze_image.assert_called_once()

    @patch('api.services.rate_limiter.RateLimiter')
    def test_analyze_image_no_groq_client(self, mock_rate_limiter):
        """Test image analysis when Groq client not available"""
        from api.services.llm_provider import LLMOrchestrator

        mock_rate_limiter.return_value = Mock()

        orchestrator = LLMOrchestrator(primary_provider="huggingface")
        orchestrator.groq_client = None

        result = orchestrator.analyze_image("test.jpg", "Analyze")

        assert result["provider"] == "error"
        assert "not available" in result["content"].lower()

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_analyze_image_error_handling(self, mock_rate_limiter, mock_groq):
        """Test error handling in image analysis"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.analyze_image.side_effect = Exception("Vision API error")
        mock_groq.return_value = mock_groq_instance
        mock_rate_limiter.return_value = Mock()

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")
        orchestrator.groq_client = mock_groq_instance

        result = orchestrator.analyze_image("test.jpg", "Analyze")

        assert result["provider"] == "error"
        assert "failed" in result["content"].lower()


class TestLLMOrchestratorGetStatus:
    """Tests for LLMOrchestrator.get_status() method"""

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_get_status_both_available(self, mock_rate_limiter, mock_groq):
        """Test status with both providers available"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq.return_value = Mock()
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.remaining_calls.return_value = 28
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        with patch('api.services.llm_provider.HuggingFaceLLM') as mock_hf:
            mock_hf.return_value = Mock()

            orchestrator = LLMOrchestrator(
                primary_provider="groq",
                fallback_provider="huggingface"
            )

            status = orchestrator.get_status()

            assert status["primary"] == "groq"
            assert status["fallback"] == "huggingface"
            assert status["groq_available"] is True
            assert status["hf_available"] is True
            assert status["rate_limit_remaining"] == 28

    @patch('api.services.rate_limiter.RateLimiter')
    def test_get_status_only_groq(self, mock_rate_limiter):
        """Test status with only Groq available"""
        from api.services.llm_provider import LLMOrchestrator

        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.remaining_calls.return_value = 30
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        with patch('api.services.llm_provider.GroqLLM') as mock_groq:
            mock_groq.return_value = Mock()

            orchestrator = LLMOrchestrator(primary_provider="groq")

            status = orchestrator.get_status()

            assert status["groq_available"] is True
            assert status["hf_available"] is False


class TestGroqLLM:
    """Tests for GroqLLM class"""

    def test_init_import_error(self):
        """Test GroqLLM raises error when groq package not installed"""
        from api.services.llm_provider import GroqLLM

        with patch.dict('sys.modules', {'groq': None}):
            with pytest.raises(ImportError, match="groq package not installed"):
                GroqLLM(api_key="test_key")

    @patch('groq.Groq')
    def test_init_success(self, mock_groq_class):
        """Test successful GroqLLM initialization"""
        from api.services.llm_provider import GroqLLM

        mock_client = Mock()
        mock_groq_class.return_value = mock_client

        with patch.dict(os.environ, {'GROQ_MODEL': 'llama-3.1-8b-instant'}):
            groq_llm = GroqLLM(api_key="test_key")

        assert groq_llm.client == mock_client
        assert groq_llm.chat_model == "llama-3.1-8b-instant"
        mock_groq_class.assert_called_once_with(api_key="test_key")

    @patch('groq.Groq')
    def test_chat_success(self, mock_groq_class):
        """Test successful chat completion"""
        from api.services.llm_provider import GroqLLM

        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Sepsis is a life-threatening condition"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "llama-3.1-70b-versatile"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        groq_llm = GroqLLM(api_key="test_key")
        groq_llm.client = mock_client

        messages = [{"role": "user", "content": "What is sepsis?"}]
        result = groq_llm.chat(messages, max_tokens=800, temperature=0.3)

        assert result["content"] == "Sepsis is a life-threatening condition"
        assert result["model"] == "llama-3.1-70b-versatile"
        assert result["finish_reason"] == "stop"

        mock_client.chat.completions.create.assert_called_once_with(
            model=groq_llm.chat_model,
            messages=messages,
            max_tokens=800,
            temperature=0.3
        )

    @patch('groq.Groq')
    def test_chat_error(self, mock_groq_class):
        """Test chat error handling"""
        from api.services.llm_provider import GroqLLM

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_groq_class.return_value = mock_client

        groq_llm = GroqLLM(api_key="test_key")
        groq_llm.client = mock_client

        messages = [{"role": "user", "content": "Test"}]

        with pytest.raises(Exception, match="API Error"):
            groq_llm.chat(messages)

    @patch('groq.Groq')
    def test_analyze_image_with_url(self, mock_groq_class):
        """Test image analysis with URL"""
        from api.services.llm_provider import GroqLLM

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Image analysis result"
        mock_response.model = "llama-3.2-11b-vision-preview"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        groq_llm = GroqLLM(api_key="test_key")
        groq_llm.client = mock_client

        result = groq_llm.analyze_image(
            image_data="https://example.com/image.jpg",
            prompt="Analyze this image",
            max_tokens=500
        )

        assert result["content"] == "Image analysis result"
        assert result["provider"] == "groq"

    @patch('groq.Groq')
    def test_analyze_image_with_bytes(self, mock_groq_class):
        """Test image analysis with bytes data"""
        from api.services.llm_provider import GroqLLM

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Analyzed bytes image"
        mock_response.model = "llama-3.2-11b-vision-preview"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        groq_llm = GroqLLM(api_key="test_key")
        groq_llm.client = mock_client

        image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        result = groq_llm.analyze_image(
            image_data=image_bytes,
            prompt="Analyze",
            max_tokens=300
        )

        assert result["content"] == "Analyzed bytes image"
        # Verify base64 encoding was triggered
        mock_client.chat.completions.create.assert_called_once()


class TestHuggingFaceLLM:
    """Tests for HuggingFaceLLM class"""

    def test_init_import_error(self):
        """Test HuggingFaceLLM raises error when transformers not installed"""
        from api.services.llm_provider import HuggingFaceLLM

        with patch.dict('sys.modules', {'torch': None, 'transformers': None}):
            with pytest.raises(ImportError, match="transformers/torch not installed"):
                HuggingFaceLLM()

    def test_messages_to_prompt_system_message(self):
        """Test _messages_to_prompt with system message"""
        # Create a minimal mock HF instance without full initialization
        from api.services.llm_provider import HuggingFaceLLM

        # Create instance attributes directly for testing
        hf_llm = object.__new__(HuggingFaceLLM)

        messages = [
            {"role": "system", "content": "You are a medical assistant"},
            {"role": "user", "content": "What is diabetes?"}
        ]

        prompt = hf_llm._messages_to_prompt(messages)

        assert "System: You are a medical assistant" in prompt
        assert "User: What is diabetes?" in prompt
        assert prompt.endswith("Assistant:")

    def test_messages_to_prompt_multi_turn(self):
        """Test _messages_to_prompt with multiple turns"""
        from api.services.llm_provider import HuggingFaceLLM

        hf_llm = object.__new__(HuggingFaceLLM)

        messages = [
            {"role": "user", "content": "What is sepsis?"},
            {"role": "assistant", "content": "Sepsis is a serious condition"},
            {"role": "user", "content": "What are the symptoms?"}
        ]

        prompt = hf_llm._messages_to_prompt(messages)

        assert "User: What is sepsis?" in prompt
        assert "Assistant: Sepsis is a serious condition" in prompt
        assert "User: What are the symptoms?" in prompt
        assert prompt.endswith("Assistant:")


class TestGetLLMOrchestrator:
    """Tests for get_llm_orchestrator() convenience function"""

    @patch('api.services.llm_provider.LLMOrchestrator')
    def test_get_llm_orchestrator_default(self, mock_orchestrator_class):
        """Test get_llm_orchestrator with defaults"""
        from api.services.llm_provider import get_llm_orchestrator

        mock_orchestrator_class.return_value = Mock()

        with patch.dict(os.environ, {
            'LLM_PRIMARY_PROVIDER': 'groq',
            'LLM_FALLBACK_PROVIDER': 'huggingface'
        }):
            orchestrator = get_llm_orchestrator()

        mock_orchestrator_class.assert_called_once()

    @patch('api.services.llm_provider.LLMOrchestrator')
    def test_get_llm_orchestrator_with_kwargs(self, mock_orchestrator_class):
        """Test get_llm_orchestrator with custom kwargs"""
        from api.services.llm_provider import get_llm_orchestrator

        mock_orchestrator_class.return_value = Mock()

        orchestrator = get_llm_orchestrator(groq_api_key="custom_key")

        call_kwargs = mock_orchestrator_class.call_args[1]
        assert call_kwargs['groq_api_key'] == "custom_key"


class TestLLMProviderEnum:
    """Tests for LLMProvider enum"""

    def test_enum_values(self):
        """Test LLMProvider enum has correct values"""
        from api.services.llm_provider import LLMProvider

        assert LLMProvider.GROQ.value == "groq"
        assert LLMProvider.HUGGINGFACE.value == "huggingface"

    def test_enum_members(self):
        """Test LLMProvider enum members"""
        from api.services.llm_provider import LLMProvider

        members = [e.value for e in LLMProvider]
        assert "groq" in members
        assert "huggingface" in members
        assert len(members) == 2


class TestEdgeCases:
    """Tests for edge cases and error scenarios"""

    @patch('api.services.rate_limiter.RateLimiter')
    def test_orchestrator_no_providers_available(self, mock_rate_limiter):
        """Test orchestrator when no providers initialize successfully"""
        from api.services.llm_provider import LLMOrchestrator

        mock_rate_limiter.return_value = Mock()

        orchestrator = LLMOrchestrator(primary_provider="groq")
        orchestrator.groq_client = None
        orchestrator.hf_client = None

        messages = [{"role": "user", "content": "Test"}]
        result = orchestrator.generate(messages)

        # Should return error response
        assert result["provider"] == "error"
        assert result["finish_reason"] == "error"

    @patch('api.services.llm_provider.GroqLLM')
    @patch('api.services.rate_limiter.RateLimiter')
    def test_generate_empty_messages(self, mock_rate_limiter, mock_groq):
        """Test generate with empty messages list"""
        from api.services.llm_provider import LLMOrchestrator

        mock_groq_instance = Mock()
        mock_groq_instance.chat.return_value = {
            "content": "Response",
            "model": "llama-3.1-70b-versatile",
            "finish_reason": "stop"
        }
        mock_groq.return_value = mock_groq_instance

        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.can_proceed.return_value = True
        mock_rate_limiter.return_value = mock_rate_limiter_instance

        orchestrator = LLMOrchestrator(primary_provider="groq", groq_api_key="test_key")
        orchestrator.groq_client = mock_groq_instance
        orchestrator.rate_limiter = mock_rate_limiter_instance

        # Should handle empty messages
        result = orchestrator.generate([])

        assert result is not None
        mock_groq_instance.chat.assert_called_once_with(
            messages=[],
            max_tokens=800,
            temperature=0.3
        )

    def test_hf_messages_formatting(self):
        """Test HuggingFace messages are formatted correctly"""
        from api.services.llm_provider import HuggingFaceLLM

        hf_llm = object.__new__(HuggingFaceLLM)

        # Test with all role types
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"}
        ]

        prompt = hf_llm._messages_to_prompt(messages)

        assert "System: System message" in prompt
        assert "User: User message" in prompt
        assert "Assistant: Assistant message" in prompt
