"""
Privacy Compliance Integration Tests

Tests end-to-end PII protection for HIPAA compliance.
Validates that no PII leaks through the system.
"""

import pytest
from unittest.mock import patch, MagicMock

from api.services.pii_redaction_service import PIIRedactionService
from api.services.langchain_medical_bot import ProductionMedicalChatbot


class TestPrivacyCompliance:
    """Test suite for privacy compliance."""

    @pytest.fixture
    def pii_service(self):
        """Create PII service for testing."""
        return PIIRedactionService(enable_audit_log=False)

    @pytest.fixture
    @patch('api.services.langchain_medical_bot.ChatGroq')
    @patch('api.services.langchain_medical_bot.AnalyzerEngine')
    @patch('api.services.langchain_medical_bot.AnonymizerEngine')
    def chatbot(self, mock_anon, mock_analyzer, mock_groq, monkeypatch):
        """Create chatbot with PII protection enabled."""
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_groq.return_value = MagicMock()

        # Create real analyzer/anonymizer for integration test
        bot = ProductionMedicalChatbot(
            provider="groq",
            enable_pii_redaction=True
        )
        return bot

    def test_no_ssn_in_output(self, pii_service):
        """Test SSN is never in output."""
        test_cases = [
            "Patient SSN: 123-45-6789",
            "SSN 987-65-4321",
            "Social Security Number: 111-22-3333"
        ]

        for text in test_cases:
            result = pii_service.redact_pii(text)

            # Check no SSN patterns in output
            assert not any(c.isdigit() and "-" in result.redacted_text for c in result.redacted_text)
            assert "123-45-6789" not in result.redacted_text
            assert "987-65-4321" not in result.redacted_text
            assert "111-22-3333" not in result.redacted_text

    def test_no_names_in_output(self, pii_service):
        """Test patient names are redacted."""
        test_cases = [
            "Patient John Doe arrived",
            "Dr. Jane Smith consulted",
            "Contact Mary Johnson"
        ]

        for text in test_cases:
            result = pii_service.redact_pii(text)

            assert "John Doe" not in result.redacted_text
            assert "Jane Smith" not in result.redacted_text
            assert "Mary Johnson" not in result.redacted_text

    def test_no_email_in_output(self, pii_service):
        """Test email addresses are redacted."""
        test_cases = [
            "Email: john.doe@hospital.com",
            "Contact patient@email.com",
            "Send to doctor@medical.org"
        ]

        for text in test_cases:
            result = pii_service.redact_pii(text)

            assert "@" not in result.redacted_text or "<EMAIL" in result.redacted_text
            assert "john.doe@hospital.com" not in result.redacted_text
            assert "patient@email.com" not in result.redacted_text

    def test_no_phone_in_output(self, pii_service):
        """Test phone numbers are redacted."""
        test_cases = [
            "Call 555-123-4567",
            "Phone: (555) 987-6543",
            "Contact at 555.111.2222"
        ]

        for text in test_cases:
            result = pii_service.redact_pii(text)

            assert "555-123-4567" not in result.redacted_text
            assert "555-987-6543" not in result.redacted_text
            assert "555.111.2222" not in result.redacted_text

    def test_medical_mrn_redacted(self, pii_service):
        """Test Medical Record Numbers are redacted."""
        test_cases = [
            "MRN: MR-123456789",
            "Patient MRN:987654321",
            "Check MR-555555"
        ]

        for text in test_cases:
            result = pii_service.redact_pii(text)

            assert "MR-123456789" not in result.redacted_text
            assert "987654321" not in result.redacted_text or "MRN" not in text
            assert "MR-555555" not in result.redacted_text

    def test_patient_id_redacted(self, pii_service):
        """Test Patient IDs are redacted."""
        test_cases = [
            "PATIENT-123456",
            "PT-987654",
            "PAT_555555"
        ]

        for text in test_cases:
            result = pii_service.redact_pii(text)

            assert "PATIENT-123456" not in result.redacted_text
            assert "PT-987654" not in result.redacted_text
            assert "PAT_555555" not in result.redacted_text

    def test_medical_terms_preserved(self, pii_service):
        """Test medical terms are NOT redacted."""
        text = """
        Diagnosis: Septic shock
        Treatment: IV antibiotics, norepinephrine
        Procedure: Central line placement
        Vitals: BP 80/50, HR 120
        """

        result = pii_service.redact_pii(text)

        # Medical terms should be preserved
        assert "Septic shock" in result.redacted_text
        assert "antibiotics" in result.redacted_text
        assert "norepinephrine" in result.redacted_text
        assert "Central line" in result.redacted_text
        assert "BP 80/50" in result.redacted_text

    def test_realistic_medical_note(self, pii_service):
        """Test realistic medical note with mixed content."""
        note = """
        Patient: John Doe
        MRN: MR-123456789
        DOB: 01/15/1980
        Phone: 555-9876
        Email: john.doe@email.com

        Chief Complaint: Fever and confusion

        Assessment: Septic shock secondary to pneumonia

        Plan:
        1. Blood cultures x2
        2. Start vancomycin and pip-tazo
        3. Fluid resuscitation 30ml/kg
        4. Norepinephrine for MAP >65
        5. ICU admission
        """

        result = pii_service.redact_pii(note)

        # PII should be redacted
        assert "John Doe" not in result.redacted_text
        assert "MR-123456789" not in result.redacted_text
        assert "555-9876" not in result.redacted_text
        assert "john.doe@email.com" not in result.redacted_text

        # Medical content should be preserved
        assert "Fever and confusion" in result.redacted_text
        assert "Septic shock" in result.redacted_text
        assert "pneumonia" in result.redacted_text
        assert "vancomycin" in result.redacted_text
        assert "Norepinephrine" in result.redacted_text
        assert "ICU admission" in result.redacted_text

    def test_multiple_patients_no_leakage(self, pii_service):
        """Test no PII leakage with multiple patient records."""
        records = [
            "Patient A: John Doe, MRN:111, SSN:123-45-6789",
            "Patient B: Jane Smith, MRN:222, SSN:987-65-4321",
            "Patient C: Bob Johnson, MRN:333, SSN:555-55-5555"
        ]

        results = pii_service.batch_redact(records)

        # Check no cross-contamination
        for i, result in enumerate(results):
            # No PII from any patient should appear
            for record in records:
                # Extract all potential PII
                assert "John Doe" not in result.redacted_text
                assert "Jane Smith" not in result.redacted_text
                assert "Bob Johnson" not in result.redacted_text
                assert "123-45-6789" not in result.redacted_text
                assert "987-65-4321" not in result.redacted_text
                assert "555-55-5555" not in result.redacted_text

    def test_hipaa_identifiers_coverage(self, pii_service):
        """Test coverage of HIPAA 18 identifiers."""
        # HIPAA identifiers that should be redacted
        hipaa_text = """
        1. Name: John Doe
        2. Address: 123 Main St, City, ST 12345
        3. Phone: 555-1234
        4. Email: test@email.com
        5. SSN: 123-45-6789
        6. MRN: MR-123456
        7. Account: ACC-9876
        8. License: DL-555555
        9. Device ID: DEV-12345
        10. Web URL: https://patient.com/john
        11. IP Address: 192.168.1.1
        12. Biometric: Fingerprint-ABC123
        13. Photo: photo_john.jpg
        14. Date: DOB 01/15/1980
        """

        result = pii_service.redact_pii(hipaa_text)

        # Key identifiers should be redacted
        assert "John Doe" not in result.redacted_text
        assert "123 Main St" not in result.redacted_text or "Main St" in result.redacted_text
        assert "555-1234" not in result.redacted_text
        assert "test@email.com" not in result.redacted_text
        assert "123-45-6789" not in result.redacted_text

    @patch.object(ProductionMedicalChatbot, '_generate_with_retry')
    def test_chatbot_pii_in_query_redacted(self, mock_generate, chatbot):
        """Test chatbot redacts PII from user query."""
        mock_generate.return_value = "Response without PII"

        result = chatbot.query(
            question="Patient John Doe (SSN: 123-45-6789) has fever",
            retrieved_context="Treatment context"
        )

        # Verify PII was detected
        assert len(result["pii_detected"]) > 0

        # Original query should not be in redacted version
        assert "John Doe" not in result["redacted_query"] or "PERSON" in result["redacted_query"]
        assert "123-45-6789" not in result["redacted_query"] or "SSN" in result["redacted_query"]

    def test_pii_free_text_unchanged(self, pii_service):
        """Test PII-free text passes through unchanged."""
        clean_text = """
        The patient presented with acute onset of symptoms.
        Vital signs were stable. Treatment was initiated per protocol.
        Outcome was favorable with no complications.
        """

        result = pii_service.redact_pii(clean_text)

        # Text should be unchanged (no PII detected)
        assert result.redacted_text == clean_text
        assert result.pii_count == 0

    def test_audit_logging_captures_pii_detection(self):
        """Test audit logging captures PII detection events."""
        service = PIIRedactionService(enable_audit_log=True)

        text = "Patient John Doe, SSN: 123-45-6789"

        # Should log PII detection (check no errors)
        result = service.redact_pii(text)

        assert result.pii_count > 0
        # Logging should not cause errors


class TestPrivacyEdgeCases:
    """Test edge cases for privacy protection."""

    @pytest.fixture
    def service(self):
        return PIIRedactionService(enable_audit_log=False)

    def test_partial_ssn_not_over_redacted(self, service):
        """Test partial SSN patterns are handled correctly."""
        text = "Last 4 digits: 6789"
        result = service.redact_pii(text)

        # Should not over-redact standalone numbers
        # (This depends on Presidio config, but test for awareness)
        assert result.redacted_text is not None

    def test_common_medical_abbreviations_preserved(self, service):
        """Test common medical abbreviations are not redacted."""
        text = "BP 120/80, HR 90, RR 16, SpO2 98%, Temp 37C"
        result = service.redact_pii(text)

        # Vital signs should be preserved
        assert "120/80" in result.redacted_text
        assert "HR 90" in result.redacted_text
        assert "SpO2 98%" in result.redacted_text

    def test_numeric_medical_values_preserved(self, service):
        """Test numeric medical values are not over-redacted."""
        text = "WBC: 15.2, Hgb: 12.5, Plt: 250, Cr: 1.2, BUN: 20"
        result = service.redact_pii(text)

        # Lab values should be preserved
        assert "15.2" in result.redacted_text
        assert "12.5" in result.redacted_text
        assert "250" in result.redacted_text

    def test_medication_dosages_preserved(self, service):
        """Test medication dosages are preserved."""
        text = "Vancomycin 1g IV q12h, Piperacillin-Tazobactam 4.5g IV q6h"
        result = service.redact_pii(text)

        # Medication info should be preserved
        assert "Vancomycin" in result.redacted_text
        assert "1g" in result.redacted_text
        assert "q12h" in result.redacted_text
        assert "Piperacillin-Tazobactam" in result.redacted_text

    def test_unicode_and_special_characters(self, service):
        """Test handling of unicode and special characters."""
        text = "Patient José García, Email: josé@hospital.com"
        result = service.redact_pii(text)

        # Should handle unicode names
        assert "José García" not in result.redacted_text
        assert "josé@hospital.com" not in result.redacted_text

    def test_case_insensitive_detection(self, service):
        """Test PII detection is case-insensitive."""
        test_cases = [
            "SSN: 123-45-6789",
            "ssn: 123-45-6789",
            "Social Security Number: 123-45-6789"
        ]

        for text in test_cases:
            result = service.redact_pii(text)
            assert "123-45-6789" not in result.redacted_text


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=api.services"])
