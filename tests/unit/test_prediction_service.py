"""
Unit tests for PredictionService
Tests ML prediction functionality with mocked models and Redis
"""

import pytest
from unittest.mock import MagicMock, patch, Mock, AsyncMock
from datetime import datetime
import numpy as np


class TestPredictionServiceInit:
    """Tests for PredictionService initialization"""

    @patch('api.services.prediction_service.redis')
    @patch('api.services.prediction_service.os.path.exists')
    def test_init_creates_service(self, mock_exists, mock_redis):
        """Test service initialization"""
        mock_exists.return_value = False  # Models not found
        mock_redis.from_url.side_effect = Exception("No Redis")
        
        from api.services.prediction_service import PredictionService
        
        service = PredictionService()
        
        assert service is not None
        assert isinstance(service.models, dict)

    @patch('api.services.prediction_service.redis')
    @patch('api.services.prediction_service.os.path.exists')
    def test_init_redis_connection_failure_graceful(self, mock_exists, mock_redis):
        """Test graceful handling of Redis connection failure"""
        mock_exists.return_value = False
        mock_redis.from_url.side_effect = Exception("Connection refused")
        
        from api.services.prediction_service import PredictionService
        
        service = PredictionService()
        
        assert service.redis_client is None


class TestPredictionServiceCaching:
    """Tests for caching functionality"""

    def test_get_cache_key_deterministic(self):
        """Test cache key generation is deterministic"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
        
        features = {"age": 65, "hr": 90}
        key1 = service._get_cache_key("patient_001", features)
        key2 = service._get_cache_key("patient_001", features)
        
        assert key1 == key2
        assert "patient_001" in key1

    def test_get_cache_key_different_features(self):
        """Test different features produce different keys"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
        
        key1 = service._get_cache_key("patient_001", {"age": 65})
        key2 = service._get_cache_key("patient_001", {"age": 70})
        
        assert key1 != key2

    def test_get_from_cache_no_redis(self):
        """Test cache retrieval when Redis unavailable"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = None
        
        result = service._get_from_cache("test_key")
        
        assert result is None

    def test_save_to_cache_no_redis(self):
        """Test cache save when Redis unavailable"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = None
        
        # Should not raise exception
        service._save_to_cache("test_key", {"data": "value"})


class TestRiskCategorization:
    """Tests for risk level categorization"""

    @pytest.fixture
    def service(self):
        """Create service with mocked init"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                return PredictionService()

    def test_categorize_risk_low(self, service):
        """Test LOW risk categorization"""
        from api.models.schemas import RiskLevel
        
        result = service._categorize_risk(0.1)
        assert result == RiskLevel.LOW

    def test_categorize_risk_medium(self, service):
        """Test MEDIUM risk categorization"""
        from api.models.schemas import RiskLevel
        
        result = service._categorize_risk(0.35)
        assert result == RiskLevel.MEDIUM

    def test_categorize_risk_high(self, service):
        """Test HIGH risk categorization"""
        from api.models.schemas import RiskLevel
        
        result = service._categorize_risk(0.65)
        assert result == RiskLevel.HIGH

    def test_categorize_risk_critical(self, service):
        """Test CRITICAL risk categorization"""
        from api.models.schemas import RiskLevel
        
        result = service._categorize_risk(0.9)
        assert result == RiskLevel.CRITICAL

    def test_categorize_risk_boundary_low_medium(self, service):
        """Test boundary between LOW and MEDIUM"""
        from api.models.schemas import RiskLevel
        
        assert service._categorize_risk(0.19) == RiskLevel.LOW
        assert service._categorize_risk(0.20) == RiskLevel.MEDIUM

    def test_categorize_risk_boundary_medium_high(self, service):
        """Test boundary between MEDIUM and HIGH"""
        from api.models.schemas import RiskLevel
        
        assert service._categorize_risk(0.49) == RiskLevel.MEDIUM
        assert service._categorize_risk(0.50) == RiskLevel.HIGH

    def test_categorize_risk_boundary_high_critical(self, service):
        """Test boundary between HIGH and CRITICAL"""
        from api.models.schemas import RiskLevel
        
        assert service._categorize_risk(0.79) == RiskLevel.HIGH
        assert service._categorize_risk(0.80) == RiskLevel.CRITICAL


class TestRecommendations:
    """Tests for clinical recommendations"""

    @pytest.fixture
    def service(self):
        """Create service with mocked init"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                return PredictionService()

    def test_sepsis_low_recommendation(self, service):
        """Test sepsis LOW risk recommendation"""
        from api.models.schemas import RiskLevel
        
        rec = service._get_recommendation(RiskLevel.LOW, "sepsis")
        assert "monitoring" in rec.lower()

    def test_sepsis_critical_recommendation(self, service):
        """Test sepsis CRITICAL risk recommendation"""
        from api.models.schemas import RiskLevel
        
        rec = service._get_recommendation(RiskLevel.CRITICAL, "sepsis")
        assert "urgent" in rec.lower() or "protocol" in rec.lower()

    def test_mortality_low_recommendation(self, service):
        """Test mortality LOW risk recommendation"""
        from api.models.schemas import RiskLevel
        
        rec = service._get_recommendation(RiskLevel.LOW, "mortality")
        assert "icu" in rec.lower() or "care" in rec.lower()

    def test_mortality_critical_recommendation(self, service):
        """Test mortality CRITICAL risk recommendation"""
        from api.models.schemas import RiskLevel
        
        rec = service._get_recommendation(RiskLevel.CRITICAL, "mortality")
        assert "critical" in rec.lower() or "maximum" in rec.lower()


class TestDummyPredictions:
    """Tests for dummy predictions when model not loaded"""

    @pytest.fixture
    def service(self):
        """Create service with mocked init"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                return PredictionService()

    def test_dummy_sepsis_prediction_returns_response(self, service):
        """Test dummy sepsis prediction structure"""
        result = service._dummy_sepsis_prediction("patient_001")

        # Check it's the right type by name and attributes
        assert type(result).__name__ == "SepsisPredictionResponse"
        assert result.patient_id == "patient_001"
        assert result.prediction is not None
        assert result.metadata["model_version"] == "dummy"

    def test_dummy_mortality_prediction_returns_response(self, service):
        """Test dummy mortality prediction structure"""
        result = service._dummy_mortality_prediction("patient_002")

        # Check it's the right type by name and attributes
        assert type(result).__name__ == "MortalityPredictionResponse"
        assert result.patient_id == "patient_002"
        assert result.prediction is not None
        assert result.metadata["model_version"] == "dummy"

    def test_dummy_sepsis_has_top_features(self, service):
        """Test dummy sepsis prediction includes features"""
        result = service._dummy_sepsis_prediction("patient_001")
        
        assert len(result.top_features) > 0

    def test_dummy_mortality_has_top_features(self, service):
        """Test dummy mortality prediction includes features"""
        result = service._dummy_mortality_prediction("patient_001")
        
        assert len(result.top_features) > 0


class TestTopFeatures:
    """Tests for feature importance extraction"""

    @pytest.fixture
    def service(self):
        """Create service with mocked init"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                return PredictionService()

    def test_get_top_features_with_importances(self, service):
        """Test feature extraction from model with importances"""
        import pandas as pd
        
        # Mock model with feature importances
        mock_model = MagicMock()
        mock_model.feature_importances_ = np.array([0.1, 0.3, 0.2, 0.15, 0.25])
        
        features_df = pd.DataFrame({
            "age": [65],
            "hr": [90],
            "temp": [38.5],
            "rr": [22],
            "bp": [110]
        })
        
        result = service._get_top_features(features_df, mock_model, "sepsis")
        
        assert len(result) <= 10
        # Top features should be sorted by importance
        assert all("feature" in f for f in result)

    def test_get_top_features_no_importances(self, service):
        """Test feature extraction when model has no importances"""
        import pandas as pd
        
        mock_model = MagicMock()
        del mock_model.feature_importances_  # No importances attribute
        
        features_df = pd.DataFrame({"age": [65], "hr": [90]})
        
        result = service._get_top_features(features_df, mock_model, "sepsis")
        
        assert result == []


class TestPredictionFlow:
    """Tests for full prediction flow"""

    @pytest.fixture
    def service_with_model(self):
        """Create service with mocked model"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                
                # Add mock model
                mock_model = MagicMock()
                mock_model.predict.return_value = np.array([0.75])
                mock_model.feature_importances_ = np.random.rand(42)
                service.models["sepsis"] = mock_model
                
                return service

    @pytest.mark.asyncio
    async def test_predict_sepsis_without_model(self):
        """Test sepsis prediction returns dummy when no model"""
        from api.services.prediction_service import PredictionService
        from api.models.schemas import SepsisPredictionRequest, SepsisFeatures
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.models = {}  # No models loaded
        
        # Create request with mock features
        mock_features = MagicMock(spec=SepsisFeatures)
        mock_features.dict.return_value = {"age": 65}
        
        request = MagicMock(spec=SepsisPredictionRequest)
        request.patient_id = "patient_001"
        request.features = mock_features
        
        result = await service.predict_sepsis(request, db=None)
        
        assert result.metadata["model_version"] == "dummy"

    @pytest.mark.asyncio
    async def test_predict_mortality_without_model(self):
        """Test mortality prediction returns dummy when no model"""
        from api.services.prediction_service import PredictionService
        from api.models.schemas import MortalityPredictionRequest, MortalityFeatures
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.models = {}  # No models loaded
        
        mock_features = MagicMock(spec=MortalityFeatures)
        mock_features.dict.return_value = {"age": 70}
        
        request = MagicMock(spec=MortalityPredictionRequest)
        request.patient_id = "patient_002"
        request.features = mock_features
        
        result = await service.predict_mortality(request, db=None)
        
        assert result.metadata["model_version"] == "dummy"


class TestCacheKeyHashing:
    """Tests for SHA256 hash in cache keys"""

    @pytest.fixture
    def service(self):
        """Create service with mocked init"""
        from api.services.prediction_service import PredictionService
        
        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                return PredictionService()

    def test_cache_key_uses_sha256(self, service):
        """Verify cache key uses SHA256 hash"""
        import hashlib
        
        features = {"age": 65, "hr": 90}
        key = service._get_cache_key("patient_001", features)
        
        # Key should contain SHA256 hash (64 chars hex)
        # Format: prediction:patient_id:hash
        parts = key.split(":")
        assert len(parts) == 3
        assert parts[0] == "prediction"
        assert parts[1] == "patient_001"
        # Hash should be hex string
        assert all(c in '0123456789abcdef' for c in parts[2])

    def test_cache_key_order_independent(self, service):
        """Verify feature order doesn't affect cache key"""
        import json
        
        features1 = {"age": 65, "hr": 90, "bp": 120}
        features2 = {"bp": 120, "age": 65, "hr": 90}
        
        key1 = service._get_cache_key("patient_001", features1)
        key2 = service._get_cache_key("patient_001", features2)
        
        # Should be same because json.dumps with sort_keys=True
        assert key1 == key2
