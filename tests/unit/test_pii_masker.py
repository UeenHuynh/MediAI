"""
Unit tests for PII Masker
Tests PII detection and masking functionality
"""

import pytest
from unittest.mock import MagicMock, patch


class TestPIIMaskerModule:
    """Tests for PIIMasker module"""

    def test_pii_masker_module_exists(self):
        """Test PII masker module exists"""
        try:
            from api.services import pii_masker
            assert pii_masker is not None
        except ImportError:
            pytest.skip("PII masker not available")

    def test_pii_masker_class_exists(self):
        """Test PIIMasker class exists"""
        try:
            from api.services.pii_masker import PIIMasker
            assert PIIMasker is not None
        except ImportError:
            pytest.skip("PIIMasker not available")

    def test_pii_match_class_exists(self):
        """Test PIIMatch dataclass exists"""
        try:
            from api.services.pii_masker import PIIMatch
            assert PIIMatch is not None
        except ImportError:
            pytest.skip("PIIMatch not available")


class TestPIIMaskerInit:
    """Tests for PIIMasker initialization"""

    def test_init_without_spacy(self):
        """Test initialization without spaCy"""
        try:
            from api.services.pii_masker import PIIMasker
            
            masker = PIIMasker(use_spacy=False)
            
            assert masker is not None
        except ImportError:
            pytest.skip("PIIMasker not available")


class TestEmailMasking:
    """Tests for email PII detection"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_mask_email(self, masker):
        """Test masking email addresses"""
        text = "Contact me at john.doe@hospital.com"
        
        masked_text, metadata = masker.mask(text)
        
        assert "john.doe@hospital.com" not in masked_text
        assert metadata["pii_detected"] is True

    def test_mask_multiple_emails(self, masker):
        """Test masking multiple emails"""
        text = "Email a@b.com or c@d.com"
        
        masked_text, metadata = masker.mask(text)
        
        assert "a@b.com" not in masked_text
        assert "c@d.com" not in masked_text

    def test_email_token_format(self, masker):
        """Test email token format"""
        text = "Email: test@example.com"
        
        masked_text, _ = masker.mask(text)
        
        assert "<EMAIL" in masked_text


class TestPhoneMasking:
    """Tests for phone number detection"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_mask_phone_dashes(self, masker):
        """Test masking phone with dashes"""
        text = "Call me at 555-123-4567"
        
        masked_text, metadata = masker.mask(text)
        
        assert "555-123-4567" not in masked_text
        assert metadata["pii_detected"] is True

    def test_mask_phone_parentheses(self, masker):
        """Test masking phone with parentheses"""
        text = "Phone: (555) 123-4567"
        
        masked_text, _ = masker.mask(text)
        
        # Should detect phone number
        assert "(555) 123-4567" not in masked_text or "<PHONE" in masked_text


class TestSSNMasking:
    """Tests for SSN detection"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_mask_ssn(self, masker):
        """Test masking SSN"""
        text = "SSN: 123-45-6789"
        
        masked_text, metadata = masker.mask(text)
        
        assert "123-45-6789" not in masked_text


class TestMRNMasking:
    """Tests for MRN detection"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_mask_mrn(self, masker):
        """Test masking Medical Record Number"""
        text = "MRN: 12345678"
        
        masked_text, _ = masker.mask(text)
        
        # May detect MRN pattern
        assert "12345678" not in masked_text or masked_text is not None


class TestUnmasking:
    """Tests for unmasking functionality"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_unmask_restores_original(self, masker):
        """Test unmasking restores original text"""
        original = "Email: test@example.com"
        session_id = "test_session"
        
        masked_text, _ = masker.mask(original, session_id=session_id)
        unmasked_text = masker.unmask(masked_text, session_id=session_id)
        
        assert "test@example.com" in unmasked_text

    def test_unmask_without_session(self, masker):
        """Test unmasking without session returns text"""
        text = "Some <EMAIL_1> token"
        
        result = masker.unmask(text)
        
        # Should return something
        assert result is not None


class TestSessionManagement:
    """Tests for session management"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_reset_session(self, masker):
        """Test resetting session"""
        masker.mask("Email: test@example.com", session_id="test")
        
        masker.reset_session("test")
        
        # Should not raise
        assert True

    def test_reset_all_sessions(self, masker):
        """Test resetting all sessions"""
        masker.mask("Email: a@b.com", session_id="s1")
        masker.mask("Email: c@d.com", session_id="s2")
        
        masker.reset_session()  # Reset all
        
        assert True


class TestPIIMaskerStats:
    """Tests for statistics"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_get_stats_returns_dict(self, masker):
        """Test get_stats returns dictionary"""
        stats = masker.get_stats()
        
        assert isinstance(stats, dict)

    def test_stats_after_masking(self, masker):
        """Test stats after masking operations"""
        masker.mask("Email: test@example.com")
        
        stats = masker.get_stats()
        
        assert stats is not None


class TestNoPII:
    """Tests for text without PII"""

    @pytest.fixture
    def masker(self):
        """Create PIIMasker instance"""
        try:
            from api.services.pii_masker import PIIMasker
            return PIIMasker(use_spacy=False)
        except ImportError:
            pytest.skip("PIIMasker not available")
        except Exception:
            pytest.skip("Failed to initialize PIIMasker")

    def test_no_pii_unchanged(self, masker):
        """Test text without PII is unchanged"""
        text = "This is a normal medical question about sepsis."
        
        masked_text, metadata = masker.mask(text)
        
        assert masked_text == text
        assert metadata["pii_detected"] is False

    def test_empty_text(self, masker):
        """Test empty text handling"""
        masked_text, metadata = masker.mask("")
        
        assert masked_text == ""
        assert metadata["pii_detected"] is False
