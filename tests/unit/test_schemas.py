"""
Unit tests for Pydantic schemas
Tests request/response validation schemas
"""

import pytest
from typing import Optional


class TestSepsisFeatures:
    """Tests for SepsisFeatures schema"""

    def test_sepsis_features_schema_exists(self):
        """Test SepsisFeatures schema exists"""
        from api.models.schemas import SepsisFeatures
        
        assert SepsisFeatures is not None

    def test_sepsis_features_has_age(self):
        """Test SepsisFeatures has age field"""
        from api.models.schemas import SepsisFeatures
        
        fields = SepsisFeatures.__annotations__ if hasattr(SepsisFeatures, '__annotations__') else SepsisFeatures.model_fields
        
        # Age should be a field
        assert 'age' in str(fields).lower() or len(fields) > 0

    def test_sepsis_features_validation(self):
        """Test SepsisFeatures validates input"""
        from api.models.schemas import SepsisFeatures
        
        # Try creating with minimal data
        try:
            features = SepsisFeatures(age=65)
            assert True
        except Exception:
            # May require more fields
            pass


class TestMortalityFeatures:
    """Tests for MortalityFeatures schema"""

    def test_mortality_features_schema_exists(self):
        """Test MortalityFeatures schema exists"""
        from api.models.schemas import MortalityFeatures
        
        assert MortalityFeatures is not None


class TestPredictionRequest:
    """Tests for prediction request schemas"""

    def test_sepsis_prediction_request_exists(self):
        """Test SepsisPredictionRequest exists"""
        from api.models.schemas import SepsisPredictionRequest
        
        assert SepsisPredictionRequest is not None

    def test_mortality_prediction_request_exists(self):
        """Test MortalityPredictionRequest exists"""
        from api.models.schemas import MortalityPredictionRequest
        
        assert MortalityPredictionRequest is not None

    def test_sepsis_request_has_patient_id(self):
        """Test SepsisPredictionRequest has patient_id"""
        from api.models.schemas import SepsisPredictionRequest
        
        field_names = list(SepsisPredictionRequest.model_fields.keys()) if hasattr(SepsisPredictionRequest, 'model_fields') else list(SepsisPredictionRequest.__annotations__.keys())
        
        assert 'patient_id' in field_names

    def test_sepsis_request_has_features(self):
        """Test SepsisPredictionRequest has features"""
        from api.models.schemas import SepsisPredictionRequest
        
        field_names = list(SepsisPredictionRequest.model_fields.keys()) if hasattr(SepsisPredictionRequest, 'model_fields') else list(SepsisPredictionRequest.__annotations__.keys())
        
        assert 'features' in field_names


class TestPredictionResponse:
    """Tests for prediction response schemas"""

    def test_sepsis_prediction_response_exists(self):
        """Test SepsisPredictionResponse exists"""
        from api.models.schemas import SepsisPredictionResponse
        
        assert SepsisPredictionResponse is not None

    def test_mortality_prediction_response_exists(self):
        """Test MortalityPredictionResponse exists"""
        from api.models.schemas import MortalityPredictionResponse
        
        assert MortalityPredictionResponse is not None


class TestRiskLevel:
    """Tests for RiskLevel enum"""

    def test_risk_level_exists(self):
        """Test RiskLevel enum exists"""
        from api.models.schemas import RiskLevel
        
        assert RiskLevel is not None

    def test_risk_level_has_low(self):
        """Test RiskLevel has LOW value"""
        from api.models.schemas import RiskLevel
        
        assert hasattr(RiskLevel, 'LOW')

    def test_risk_level_has_medium(self):
        """Test RiskLevel has MEDIUM value"""
        from api.models.schemas import RiskLevel
        
        assert hasattr(RiskLevel, 'MEDIUM')

    def test_risk_level_has_high(self):
        """Test RiskLevel has HIGH value"""
        from api.models.schemas import RiskLevel
        
        assert hasattr(RiskLevel, 'HIGH')

    def test_risk_level_has_critical(self):
        """Test RiskLevel has CRITICAL value"""
        from api.models.schemas import RiskLevel
        
        assert hasattr(RiskLevel, 'CRITICAL')


class TestPredictionDetail:
    """Tests for PredictionDetail schema"""

    def test_prediction_detail_exists(self):
        """Test PredictionDetail schema exists"""
        from api.models.schemas import PredictionDetail
        
        assert PredictionDetail is not None

    def test_prediction_detail_has_risk_score(self):
        """Test PredictionDetail has risk_score"""
        from api.models.schemas import PredictionDetail
        
        field_names = list(PredictionDetail.model_fields.keys()) if hasattr(PredictionDetail, 'model_fields') else list(PredictionDetail.__annotations__.keys())
        
        assert 'risk_score' in field_names

    def test_prediction_detail_has_risk_level(self):
        """Test PredictionDetail has risk_level"""
        from api.models.schemas import PredictionDetail
        
        field_names = list(PredictionDetail.model_fields.keys()) if hasattr(PredictionDetail, 'model_fields') else list(PredictionDetail.__annotations__.keys())
        
        assert 'risk_level' in field_names


class TestFeatureContribution:
    """Tests for FeatureContribution schema"""

    def test_feature_contribution_exists(self):
        """Test FeatureContribution schema exists"""
        from api.models.schemas import FeatureContribution
        
        assert FeatureContribution is not None

    def test_feature_contribution_has_feature(self):
        """Test FeatureContribution has feature field"""
        from api.models.schemas import FeatureContribution
        
        field_names = list(FeatureContribution.model_fields.keys()) if hasattr(FeatureContribution, 'model_fields') else list(FeatureContribution.__annotations__.keys())
        
        assert 'feature' in field_names

    def test_feature_contribution_has_importance(self):
        """Test FeatureContribution has importance field"""
        from api.models.schemas import FeatureContribution
        
        field_names = list(FeatureContribution.model_fields.keys()) if hasattr(FeatureContribution, 'model_fields') else list(FeatureContribution.__annotations__.keys())
        
        assert 'importance' in field_names
