"""
Unit tests for ProductionMedicalChatbot

Tests LangChain integration, vendor-agnostic LLM, and medical response generation.
Target coverage: 85%+
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError

from api.services.langchain_medical_bot import (
    Citation,
    MedicalResponse,
    ProductionMedicalChatbot,
    create_medical_chatbot,
)


class TestCitationModel:
    """Test Citation Pydantic model."""

    def test_citation_creation_valid(self):
        """Test creating valid citation."""
        citation = Citation(
            number="1", source="PubMed", url="https://pubmed.com/123", pmid="123"
        )

        assert citation.number == "1"
        assert citation.source == "PubMed"
        assert citation.url == "https://pubmed.com/123"
        assert citation.pmid == "123"

    def test_citation_minimal(self):
        """Test citation with only required fields."""
        citation = Citation(number="1", source="Test Source")

        assert citation.number == "1"
        assert citation.source == "Test Source"
        assert citation.url is None
        assert citation.pmid is None

    def test_citation_validation_error(self):
        """Test citation validation error on missing required field."""
        with pytest.raises(ValidationError):
            Citation(number="1")  # Missing source


class TestMedicalResponseModel:
    """Test MedicalResponse Pydantic model."""

    def test_medical_response_creation(self):
        """Test creating valid medical response."""
        citations = [Citation(number="1", source="Test")]

        response = MedicalResponse(
            answer="Test answer",
            citations=citations,
            confidence=0.85,
            disclaimer="Test disclaimer",
            redacted_query="Test query",
        )

        assert response.answer == "Test answer"
        assert len(response.citations) == 1
        assert response.confidence == 0.85
        assert response.disclaimer == "Test disclaimer"
        assert response.redacted_query == "Test query"

    def test_medical_response_defaults(self):
        """Test medical response with default values."""
        response = MedicalResponse(answer="Test")

        assert response.answer == "Test"
        assert response.citations == []
        assert response.confidence == 0.0
        assert "informational only" in response.disclaimer.lower()

    def test_confidence_validation(self):
        """Test confidence score validation (0-1 range)."""
        # Valid confidence
        response = MedicalResponse(answer="Test", confidence=0.5)
        assert response.confidence == 0.5

        # Invalid confidence (> 1)
        with pytest.raises(ValidationError):
            MedicalResponse(answer="Test", confidence=1.5)

        # Invalid confidence (< 0)
        with pytest.raises(ValidationError):
            MedicalResponse(answer="Test", confidence=-0.1)


class TestProductionMedicalChatbot:
    """Test suite for ProductionMedicalChatbot."""

    @pytest.fixture
    def mock_env_groq(self, monkeypatch):
        """Mock environment with Groq API key."""
        monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")

    @pytest.fixture
    def mock_env_openai(self, monkeypatch):
        """Mock environment with OpenAI API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")

    @pytest.fixture
    @patch("api.services.langchain_medical_bot.ChatGroq")
    @patch("api.services.langchain_medical_bot.AnalyzerEngine")
    @patch("api.services.langchain_medical_bot.AnonymizerEngine")
    def chatbot(self, mock_anonymizer, mock_analyzer, mock_groq, mock_env_groq):
        """Create chatbot instance with mocked dependencies."""
        # Mock LLM
        mock_llm_instance = MagicMock()
        mock_groq.return_value = mock_llm_instance

        # Mock PII engines
        mock_analyzer_instance = MagicMock()
        mock_anonymizer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_anonymizer.return_value = mock_anonymizer_instance

        # Create chatbot
        bot = ProductionMedicalChatbot(provider="groq", enable_pii_redaction=True)

        return bot

    def test_initialization_groq(self, chatbot):
        """Test chatbot initializes with Groq provider."""
        assert chatbot.provider == "groq"
        assert chatbot.llm is not None
        assert chatbot.memory is not None
        assert chatbot.chain is not None

    @patch("api.services.langchain_medical_bot.ChatOpenAI")
    @patch("api.services.langchain_medical_bot.AnalyzerEngine")
    @patch("api.services.langchain_medical_bot.AnonymizerEngine")
    def test_initialization_openai(
        self, mock_anonymizer, mock_analyzer, mock_openai, mock_env_openai
    ):
        """Test chatbot initializes with OpenAI provider."""
        mock_openai.return_value = MagicMock()
        mock_analyzer.return_value = MagicMock()
        mock_anonymizer.return_value = MagicMock()

        bot = ProductionMedicalChatbot(provider="openai")

        assert bot.provider == "openai"
        mock_openai.assert_called_once()

    def test_initialization_unsupported_provider(self, mock_env_groq):
        """Test error on unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            ProductionMedicalChatbot(provider="invalid_provider")

    def test_initialization_no_api_key(self):
        """Test error when no API key is provided."""
        with pytest.raises(ValueError, match="API_KEY not found"):
            ProductionMedicalChatbot(provider="groq")

    def test_pii_redaction_enabled(self, chatbot):
        """Test PII redaction is enabled."""
        assert chatbot.enable_pii_redaction is True
        assert chatbot.analyzer is not None
        assert chatbot.anonymizer is not None

    @patch("api.services.langchain_medical_bot.ChatGroq")
    @patch("api.services.langchain_medical_bot.AnalyzerEngine")
    def test_pii_redaction_disabled(self, mock_analyzer, mock_groq, mock_env_groq):
        """Test PII redaction can be disabled."""
        mock_groq.return_value = MagicMock()

        bot = ProductionMedicalChatbot(provider="groq", enable_pii_redaction=False)

        assert bot.enable_pii_redaction is False

    def test_system_prompt_includes_guidelines(self, chatbot):
        """Test system prompt includes medical guidelines."""
        prompt = chatbot._get_system_prompt()

        assert "medical" in prompt.lower()
        assert "cite" in prompt.lower() or "citation" in prompt.lower()
        assert "emergency" in prompt.lower()
        assert "911" in prompt
        assert "consult" in prompt.lower()

    def test_user_template_includes_context(self, chatbot):
        """Test user template includes context slots."""
        template = chatbot._get_user_template()

        assert "{context}" in template
        assert "{question}" in template
        assert "{chat_history}" in template

    def test_check_token_budget_within_limit(self, chatbot):
        """Test token budget check when within limit."""
        short_text = "This is a short context."
        result = chatbot._check_token_budget(short_text)

        # Should not be truncated
        assert result == short_text

    def test_check_token_budget_exceeds_limit(self, chatbot):
        """Test token budget check when exceeds limit."""
        # Create very long text (> 12000 tokens * 4 chars)
        long_text = "A" * 60000

        result = chatbot._check_token_budget(long_text)

        # Should be truncated
        assert len(result) < len(long_text)

    def test_extract_citations_basic(self, chatbot):
        """Test extracting citations from response."""
        response = "According to [1] and [2], the treatment is effective. See also [3]."

        citations = chatbot._extract_citations(response)

        assert len(citations) == 3
        assert all(isinstance(c, Citation) for c in citations)
        assert citations[0].number == "1"
        assert citations[1].number == "2"
        assert citations[2].number == "3"

    def test_extract_citations_with_metadata(self, chatbot):
        """Test extracting citations with source metadata."""
        response = "Study [1] shows effectiveness."

        source_docs = [
            {
                "source": "PubMed",
                "title": "Paper title",
                "url": "https://pubmed.com/123",
                "pmid": "123",
                "tier": "pubmed",
                "source_type": "live_api",
            }
        ]

        citations = chatbot._extract_citations(response, source_docs)

        assert len(citations) == 1
        assert citations[0].source == "PubMed"
        assert citations[0].title == "Paper title"
        assert citations[0].url == "https://pubmed.com/123"
        assert citations[0].pmid == "123"
        assert citations[0].tier == "pubmed"
        assert citations[0].source_type == "live_api"

    def test_extract_citations_no_duplicates(self, chatbot):
        """Test citation extraction removes duplicates."""
        response = "Studies [1], [2], and [1] again show effectiveness."

        citations = chatbot._extract_citations(response)

        # Should only have [1] and [2], no duplicates
        assert len(citations) == 2
        citation_numbers = [c.number for c in citations]
        assert "1" in citation_numbers
        assert "2" in citation_numbers

    def test_extract_citations_sorted(self, chatbot):
        """Test citations are sorted by number."""
        response = "See [3], [1], and [2]."

        citations = chatbot._extract_citations(response)

        # Should be sorted: 1, 2, 3
        numbers = [c.number for c in citations]
        assert numbers == ["1", "2", "3"]

    @patch.object(ProductionMedicalChatbot, "_generate_with_retry")
    def test_query_success(self, mock_generate, chatbot):
        """Test successful query execution."""
        # Mock LLM response
        mock_generate.return_value = "Treatment involves [1] antibiotics."

        # Mock PII redaction (no PII detected)
        chatbot._redact_pii = Mock(return_value=("test query", []))

        result = chatbot.query(
            question="What is the treatment?",
            retrieved_context="[1] Antibiotics are recommended.",
            source_docs=[{"source": "Guideline", "url": "http://test.com"}],
        )

        assert result["error"] is None
        assert "Treatment" in result["answer"]
        assert len(result["citations"]) >= 1
        assert result["redacted_query"] == "test query"

    @patch.object(ProductionMedicalChatbot, "_generate_with_retry")
    def test_query_with_pii_detection(self, mock_generate, chatbot):
        """Test query with PII detected and redacted."""
        # Mock LLM response
        mock_generate.return_value = "Patient should consult doctor."

        # Mock PII redaction (PII detected)
        pii_entities = [{"type": "PERSON", "score": 0.9}]
        chatbot._redact_pii = Mock(return_value=("<PERSON> has symptoms", pii_entities))

        result = chatbot.query(
            question="John Doe has symptoms", retrieved_context="Context here"
        )

        assert result["error"] is None
        assert len(result["pii_detected"]) == 1
        assert result["pii_detected"][0]["type"] == "PERSON"
        assert result["redacted_query"] == "<PERSON> has symptoms"

    @patch.object(ProductionMedicalChatbot, "_generate_with_retry")
    def test_query_error_handling(self, mock_generate, chatbot):
        """Test query handles errors gracefully."""
        # Mock LLM error
        mock_generate.side_effect = Exception("LLM error")

        result = chatbot.query(
            question="What is the treatment?", retrieved_context="Context"
        )

        assert result["error"] is not None
        assert "unable to generate" in result["answer"].lower()
        assert "LLM error" in result["error"]

    def test_clear_memory(self, chatbot):
        """Test clearing conversation memory."""
        # Should not raise error
        chatbot.clear_memory()
        # Memory should be cleared (no exception)

    def test_get_memory_summary(self, chatbot):
        """Test getting memory summary."""
        summary = chatbot.get_memory_summary()
        # Should return string (empty or with content)
        assert isinstance(summary, str)

    @patch.object(ProductionMedicalChatbot, "_generate_with_retry")
    def test_token_budget_check_in_query(self, mock_generate, chatbot):
        """Test token budget is checked during query."""
        mock_generate.return_value = "Response"
        chatbot._redact_pii = Mock(return_value=("query", []))

        # Very long context
        long_context = "A" * 60000

        result = chatbot.query(question="Question", retrieved_context=long_context)

        # Should complete without error (context truncated internally)
        assert result["error"] is None


class TestCreateMedicalChatbot:
    """Test factory function for creating chatbot."""

    @patch("api.services.langchain_medical_bot.ProductionMedicalChatbot")
    def test_create_with_groq_key(self, mock_chatbot, monkeypatch):
        """Test auto-detection of Groq API key."""
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_chatbot.return_value = MagicMock()

        bot = create_medical_chatbot()

        mock_chatbot.assert_called_once()
        args, kwargs = mock_chatbot.call_args
        assert kwargs.get("provider") == "groq" or args[0] == "groq"

    @patch("api.services.langchain_medical_bot.ProductionMedicalChatbot")
    def test_create_with_openai_key(self, mock_chatbot, monkeypatch):
        """Test auto-detection of OpenAI API key."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        mock_chatbot.return_value = MagicMock()

        bot = create_medical_chatbot()

        mock_chatbot.assert_called_once()

    def test_create_no_api_key(self, monkeypatch):
        """Test error when no API key available."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)

        with pytest.raises(ValueError, match="No LLM API key"):
            create_medical_chatbot()

    @patch("api.services.langchain_medical_bot.ProductionMedicalChatbot")
    def test_create_with_explicit_provider(self, mock_chatbot, monkeypatch):
        """Test creating with explicit provider override."""
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_chatbot.return_value = MagicMock()

        bot = create_medical_chatbot(provider="groq", temperature=0.5)

        mock_chatbot.assert_called_once()
        args, kwargs = mock_chatbot.call_args
        assert kwargs.get("provider") == "groq"
        assert kwargs.get("temperature") == 0.5


class TestPIIEntities:
    """Test PII entity configuration."""

    @patch("api.services.langchain_medical_bot.ChatGroq")
    @patch("api.services.langchain_medical_bot.AnalyzerEngine")
    @patch("api.services.langchain_medical_bot.AnonymizerEngine")
    def test_pii_entities_list(self, mock_anon, mock_analyzer, mock_groq, monkeypatch):
        """Test PII entities list is comprehensive."""
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_groq.return_value = MagicMock()
        mock_analyzer.return_value = MagicMock()
        mock_anon.return_value = MagicMock()

        bot = ProductionMedicalChatbot(provider="groq")

        # Check PII_ENTITIES class attribute
        entities = ProductionMedicalChatbot.PII_ENTITIES

        assert "PERSON" in entities
        assert "EMAIL_ADDRESS" in entities
        assert "PHONE_NUMBER" in entities
        assert "US_SSN" in entities
        assert "MEDICAL_LICENSE" in entities
        assert len(entities) >= 10  # Should have at least 10 entity types


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=api.services.langchain_medical_bot"])
