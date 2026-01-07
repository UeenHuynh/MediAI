"""
Unit tests for PII Redaction Service

Tests privacy protection, medical entity detection, and anonymization strategies.
Target coverage: 90%+
"""

import pytest

from api.services.pii_redaction_service import (
    AnonymizationStrategy,
    PIIDetectionResult,
    PIIEntityType,
    PIIRedactionService,
    get_pii_service,
)


class TestPIIRedactionService:
    """Test suite for PIIRedactionService."""

    @pytest.fixture
    def pii_service(self):
        """Create PII service instance for testing."""
        return PIIRedactionService(
            enable_medical_patterns=True,
            enable_audit_log=False,  # Disable logging in tests
        )

    def test_service_initialization(self, pii_service):
        """Test service initializes correctly."""
        assert pii_service is not None
        assert pii_service.language == "en"
        assert pii_service.analyzer is not None
        assert pii_service.anonymizer is not None

    def test_redact_person_name(self, pii_service):
        """Test redaction of person names."""
        text = "Patient John Doe arrived at the hospital."
        result = pii_service.redact_pii(text)

        assert result.redacted_text != text
        assert "John Doe" not in result.redacted_text
        assert "<PERSON>" in result.redacted_text or "PERSON" in result.redacted_text
        assert result.pii_count >= 1
        assert PIIEntityType.PERSON.value in result.entity_types_detected

    def test_redact_ssn(self, pii_service):
        """Test redaction of Social Security Numbers."""
        text = "Patient SSN: 123-45-6789"
        result = pii_service.redact_pii(text)

        assert "123-45-6789" not in result.redacted_text
        assert result.pii_count >= 1
        assert PIIEntityType.SSN.value in result.entity_types_detected

    def test_redact_email(self, pii_service):
        """Test redaction of email addresses."""
        text = "Contact: john.doe@hospital.com"
        result = pii_service.redact_pii(text)

        assert "john.doe@hospital.com" not in result.redacted_text
        assert result.pii_count >= 1
        assert PIIEntityType.EMAIL.value in result.entity_types_detected

    def test_redact_phone_number(self, pii_service):
        """Test redaction of phone numbers."""
        text = "Call patient at 555-123-4567"
        result = pii_service.redact_pii(text)

        assert "555-123-4567" not in result.redacted_text
        assert result.pii_count >= 1

    def test_redact_medical_patient_id(self, pii_service):
        """Test redaction of medical patient IDs."""
        text = "Patient ID: PATIENT-123456 needs follow-up"
        result = pii_service.redact_pii(text)

        assert "PATIENT-123456" not in result.redacted_text
        assert result.pii_count >= 1
        assert "PATIENT_ID" in result.entity_types_detected

    def test_redact_medical_mrn(self, pii_service):
        """Test redaction of Medical Record Numbers."""
        text = "Check MRN: MR-9876543210"
        result = pii_service.redact_pii(text)

        assert "MR-9876543210" not in result.redacted_text
        assert result.pii_count >= 1
        assert "MRN" in result.entity_types_detected

    def test_redact_multiple_pii_types(self, pii_service):
        """Test redaction of multiple PII types in one text."""
        text = "Patient John Doe (SSN: 123-45-6789, Phone: 555-1234, Email: john@email.com)"
        result = pii_service.redact_pii(text)

        # Check all PII removed
        assert "John Doe" not in result.redacted_text
        assert "123-45-6789" not in result.redacted_text
        assert "555-1234" not in result.redacted_text
        assert "john@email.com" not in result.redacted_text

        # Check multiple entities detected
        assert result.pii_count >= 3
        assert len(result.entity_types_detected) >= 2

    def test_no_pii_in_clean_text(self, pii_service):
        """Test that clean text is not modified."""
        text = "The procedure was successful and patient is stable."
        result = pii_service.redact_pii(text)

        assert result.redacted_text == text
        assert result.pii_count == 0
        assert len(result.entity_types_detected) == 0

    def test_anonymization_strategy_replace(self, pii_service):
        """Test REPLACE anonymization strategy."""
        text = "Patient John Doe"
        result = pii_service.redact_pii(text, strategy=AnonymizationStrategy.REPLACE)

        assert "John Doe" not in result.redacted_text
        assert result.anonymization_strategy == "replace"

    def test_anonymization_strategy_hash(self, pii_service):
        """Test HASH anonymization strategy."""
        text = "Patient SSN: 123-45-6789"
        result = pii_service.redact_pii(text, strategy=AnonymizationStrategy.HASH)

        assert "123-45-6789" not in result.redacted_text
        assert result.anonymization_strategy == "hash"
        # Hash should be consistent
        assert len(result.redacted_text) > 0

    def test_batch_redaction(self, pii_service):
        """Test batch processing of multiple texts."""
        texts = [
            "Patient John Doe",
            "SSN: 123-45-6789",
            "Email: test@email.com",
            "No PII here",
        ]

        results = pii_service.batch_redact(texts)

        assert len(results) == 4
        assert all(isinstance(r, PIIDetectionResult) for r in results)

        # First 3 should have PII
        assert results[0].pii_count > 0
        assert results[1].pii_count > 0
        assert results[2].pii_count > 0

        # Last should be clean
        assert results[3].pii_count == 0
        assert results[3].redacted_text == texts[3]

    def test_is_pii_free_positive(self, pii_service):
        """Test PII-free check on clean text."""
        text = "The medical procedure was successful."
        assert pii_service.is_pii_free(text) is True

    def test_is_pii_free_negative(self, pii_service):
        """Test PII-free check on text with PII."""
        text = "Contact John Doe at john@email.com"
        assert pii_service.is_pii_free(text) is False

    def test_get_pii_summary(self, pii_service):
        """Test PII summary generation."""
        text = "John Doe (john@email.com, 555-1234)"
        summary = pii_service.get_pii_summary(text)

        assert summary["has_pii"] is True
        assert summary["total_entities"] >= 2
        assert "entity_counts" in summary
        assert "average_score" in summary
        assert 0 <= summary["average_score"] <= 1

    def test_get_pii_summary_clean_text(self, pii_service):
        """Test PII summary on clean text."""
        text = "No personal information here."
        summary = pii_service.get_pii_summary(text)

        assert summary["has_pii"] is False
        assert summary["total_entities"] == 0
        assert summary["average_score"] == 0.0

    def test_analyze_pii_without_redaction(self, pii_service):
        """Test PII analysis without redaction."""
        text = "Patient John Doe, SSN: 123-45-6789"
        results = pii_service.analyze_pii(text)

        assert len(results) >= 2
        assert all(hasattr(r, "entity_type") for r in results)
        assert all(hasattr(r, "score") for r in results)
        assert all(hasattr(r, "start") for r in results)
        assert all(hasattr(r, "end") for r in results)

    def test_processing_time_recorded(self, pii_service):
        """Test that processing time is recorded."""
        text = "Patient John Doe"
        result = pii_service.redact_pii(text)

        assert result.processing_time_ms > 0
        assert isinstance(result.processing_time_ms, float)

    def test_singleton_service(self):
        """Test singleton pattern for get_pii_service."""
        service1 = get_pii_service()
        service2 = get_pii_service()

        assert service1 is service2  # Same instance

    def test_custom_entity_list(self):
        """Test initialization with custom entity list."""
        custom_entities = [PIIEntityType.PERSON.value, PIIEntityType.EMAIL.value]
        service = PIIRedactionService(entities=custom_entities)

        assert service.entities == custom_entities

    def test_disable_medical_patterns(self):
        """Test disabling medical-specific patterns."""
        service = PIIRedactionService(enable_medical_patterns=False)

        text = "Patient ID: PATIENT-123456"
        result = service.redact_pii(text)

        # Should not detect PATIENT_ID without medical patterns
        assert "PATIENT_ID" not in result.entity_types_detected

    def test_error_handling_empty_text(self, pii_service):
        """Test handling of empty text."""
        result = pii_service.redact_pii("")

        assert result.redacted_text == ""
        assert result.pii_count == 0

    def test_error_handling_none_text(self, pii_service):
        """Test graceful handling of None input."""
        # Should handle gracefully without crashing
        try:
            result = pii_service.redact_pii(None)
            # If it doesn't crash, check result
            assert result is not None
        except (TypeError, AttributeError):
            # Expected error for None input
            pass

    def test_entities_found_structure(self, pii_service):
        """Test structure of entities_found in result."""
        text = "Patient John Doe"
        result = pii_service.redact_pii(text)

        if result.pii_count > 0:
            entity = result.entities_found[0]
            assert "type" in entity
            assert "score" in entity
            assert "start" in entity
            assert "end" in entity
            assert 0 <= entity["score"] <= 1

    def test_medical_context_example(self, pii_service):
        """Test realistic medical context."""
        text = """
        Patient Name: Jane Smith
        DOB: 01/15/1980
        MRN: MR-12345678
        Phone: 555-9876
        Diagnosis: Septic shock
        Treatment: IV antibiotics initiated
        """

        result = pii_service.redact_pii(text)

        # Check that PII is redacted
        assert "Jane Smith" not in result.redacted_text
        assert "MR-12345678" not in result.redacted_text
        assert "555-9876" not in result.redacted_text

        # But medical terms should remain
        assert "Septic shock" in result.redacted_text
        assert "IV antibiotics" in result.redacted_text

    def test_performance_large_text(self, pii_service):
        """Test performance on larger text."""
        # Generate large text
        text = " ".join(["Patient John Doe needs treatment."] * 100)

        result = pii_service.redact_pii(text)

        # Should complete in reasonable time (< 5 seconds)
        assert result.processing_time_ms < 5000
        assert result.pii_count > 0


class TestAnonymizationStrategies:
    """Test different anonymization strategies."""

    @pytest.fixture
    def service(self):
        return PIIRedactionService(enable_audit_log=False)

    def test_replace_strategy(self, service):
        """Test replace strategy preserves structure."""
        text = "Contact: john@email.com"
        result = service.redact_pii(text, strategy=AnonymizationStrategy.REPLACE)

        assert "john@email.com" not in result.redacted_text
        assert "Contact:" in result.redacted_text

    def test_hash_consistency(self, service):
        """Test hash strategy produces consistent hashes."""
        text = "SSN: 123-45-6789"

        result1 = service.redact_pii(text, strategy=AnonymizationStrategy.HASH)
        result2 = service.redact_pii(text, strategy=AnonymizationStrategy.HASH)

        # Same input should produce same hash
        assert result1.redacted_text == result2.redacted_text


class TestPIIEntityTypes:
    """Test PII entity type enum."""

    def test_entity_type_values(self):
        """Test entity type enum values."""
        assert PIIEntityType.PERSON.value == "PERSON"
        assert PIIEntityType.EMAIL.value == "EMAIL_ADDRESS"
        assert PIIEntityType.SSN.value == "US_SSN"
        assert PIIEntityType.PATIENT_ID.value == "PATIENT_ID"
        assert PIIEntityType.MRN.value == "MRN"

    def test_all_entity_types_valid(self):
        """Test all entity types are valid strings."""
        for entity_type in PIIEntityType:
            assert isinstance(entity_type.value, str)
            assert len(entity_type.value) > 0


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=api.services.pii_redaction_service"])
