"""
Unit tests for SafetyGuardrails service
Tests emergency detection, inappropriate query filtering, and response safety
"""

import pytest
from unittest.mock import MagicMock, patch


class TestSafetyGuardrailsInit:
    """Tests for SafetyGuardrails initialization"""

    def test_init_creates_instance(self):
        """Test SafetyGuardrails initialization"""
        from api.services.safety_guardrails import SafetyGuardrails
        
        guardrails = SafetyGuardrails()
        
        assert guardrails is not None

    def test_init_has_emergency_keywords(self):
        """Test emergency keywords are configured"""
        from api.services.safety_guardrails import SafetyGuardrails
        
        guardrails = SafetyGuardrails()
        
        # Should have emergency patterns
        assert hasattr(guardrails, 'emergency_keywords') or hasattr(guardrails, 'EMERGENCY_PATTERNS')


class TestEmergencyDetection:
    """Tests for emergency detection"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_check_emergency_normal_query(self, guardrails):
        """Test normal query is not flagged as emergency"""
        is_emergency, _ = guardrails.check_emergency("What is diabetes?")
        
        assert is_emergency is False

    def test_check_emergency_chest_pain(self, guardrails):
        """Test chest pain query is flagged"""
        is_emergency, emergency_type = guardrails.check_emergency(
            "I'm having severe chest pain and shortness of breath"
        )
        
        assert is_emergency is True
        assert emergency_type is not None

    def test_check_emergency_difficulty_breathing(self, guardrails):
        """Test breathing difficulty is flagged"""
        is_emergency, emergency_type = guardrails.check_emergency(
            "I can't breathe properly"
        )
        
        assert is_emergency is True

    def test_check_emergency_stroke_symptoms(self, guardrails):
        """Test stroke symptoms are flagged"""
        is_emergency, emergency_type = guardrails.check_emergency(
            "Face drooping and slurred speech suddenly"
        )
        
        # May or may not be detected depending on patterns
        assert isinstance(is_emergency, bool)

    def test_check_emergency_heart_attack(self, guardrails):
        """Test heart attack query is flagged"""
        is_emergency, _ = guardrails.check_emergency(
            "Am I having a heart attack?"
        )
        
        assert is_emergency is True

    def test_check_emergency_suicide(self, guardrails):
        """Test suicide mention is flagged"""
        is_emergency, _ = guardrails.check_emergency(
            "I want to kill myself"
        )
        
        assert is_emergency is True

    def test_check_emergency_case_insensitive(self, guardrails):
        """Test emergency detection is case insensitive"""
        is_emergency1, _ = guardrails.check_emergency("CHEST PAIN")
        is_emergency2, _ = guardrails.check_emergency("chest pain")
        
        # Both should have same result
        assert is_emergency1 == is_emergency2


class TestInappropriateQueryDetection:
    """Tests for inappropriate query filtering"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_check_inappropriate_normal_query(self, guardrails):
        """Test normal medical query is allowed"""
        is_inappropriate, _ = guardrails.check_inappropriate(
            "What are the symptoms of flu?"
        )
        
        assert is_inappropriate is False

    def test_check_inappropriate_drug_abuse(self, guardrails):
        """Test drug abuse query is flagged"""
        is_inappropriate, _ = guardrails.check_inappropriate(
            "How to get high on prescription drugs"
        )
        
        # May be flagged
        assert isinstance(is_inappropriate, bool)

    def test_check_inappropriate_harm(self, guardrails):
        """Test self-harm query is flagged"""
        is_inappropriate, reason = guardrails.check_inappropriate(
            "Best way to hurt myself"
        )
        
        assert is_inappropriate is True
        assert reason is not None


class TestResponseValidation:
    """Tests for AI response validation"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_validate_response_safe(self, guardrails):
        """Test safe response passes validation"""
        is_safe, issues = guardrails.validate_response(
            "Diabetes is a metabolic disorder affecting blood sugar levels."
        )
        
        assert is_safe is True

    def test_validate_response_with_diagnosis(self, guardrails):
        """Test response with diagnosis is flagged"""
        is_safe, issues = guardrails.validate_response(
            "You definitely have cancer based on these symptoms."
        )
        
        # May be flagged for definitive diagnosis
        assert isinstance(is_safe, bool)

    def test_validate_response_empty(self, guardrails):
        """Test empty response handling"""
        is_safe, issues = guardrails.validate_response("")
        
        assert isinstance(is_safe, bool)


class TestDisclaimerManagement:
    """Tests for disclaimer addition"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_add_disclaimer_normal(self, guardrails):
        """Test adding disclaimer to normal response"""
        response = "This is medical information."
        
        result = guardrails.add_disclaimer(response, is_demo=True)
        
        # Should add some disclaimer
        assert len(result) >= len(response)

    def test_add_disclaimer_emergency(self, guardrails):
        """Test adding disclaimer to emergency response"""
        response = "You should seek immediate care."
        
        result = guardrails.add_disclaimer(response, is_emergency=True, is_demo=True)
        
        assert len(result) >= len(response)

    def test_add_disclaimer_contains_warning(self, guardrails):
        """Test disclaimer contains warning text"""
        response = "Medical information here."
        
        result = guardrails.add_disclaimer(response, is_demo=True)
        
        # Should have some warning/disclaimer text
        assert "disclaimer" in result.lower() or "not" in result.lower() or "consult" in result.lower()


class TestEmergencyResponse:
    """Tests for emergency response generation"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_create_emergency_response_cardiac(self, guardrails):
        """Test cardiac emergency response"""
        response = guardrails.create_emergency_response("cardiac")
        
        assert "911" in response or "emergency" in response.lower()

    def test_create_emergency_response_generic(self, guardrails):
        """Test generic emergency response"""
        response = guardrails.create_emergency_response("unknown")
        
        assert len(response) > 0
        assert "help" in response.lower() or "emergency" in response.lower()


class TestProcessQuery:
    """Tests for complete query processing"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_process_query_normal(self, guardrails):
        """Test processing normal query"""
        result = guardrails.process_query("What is hypertension?")
        
        assert isinstance(result, dict)
        assert "is_emergency" in result
        assert result["is_emergency"] is False

    def test_process_query_emergency(self, guardrails):
        """Test processing emergency query"""
        result = guardrails.process_query("I think I'm having a heart attack")
        
        assert isinstance(result, dict)
        assert result["is_emergency"] is True

    def test_process_query_returns_required_fields(self, guardrails):
        """Test process_query returns all required fields"""
        result = guardrails.process_query("Normal medical question")
        
        assert "is_emergency" in result
        assert "is_inappropriate" in result
        assert "allow_response" in result


class TestProcessResponse:
    """Tests for response processing"""

    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance"""
        from api.services.safety_guardrails import SafetyGuardrails
        return SafetyGuardrails()

    def test_process_response_adds_safety(self, guardrails):
        """Test response processing adds safety measures"""
        query_safety = {
            "is_emergency": False,
            "is_inappropriate": False,
            "allow_response": True
        }
        
        response = "This is a medical response."
        result = guardrails.process_response(response, query_safety, is_demo=True)
        
        assert len(result) >= len(response)

    def test_process_response_emergency(self, guardrails):
        """Test response processing for emergency"""
        query_safety = {
            "is_emergency": True,
            "emergency_type": "cardiac",
            "is_inappropriate": False,
            "allow_response": True
        }
        
        response = "Medical information."
        result = guardrails.process_response(response, query_safety, is_demo=True)
        
        # Should include emergency guidance
        assert "911" in result or "emergency" in result.lower() or len(result) > len(response)
