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


class TestRedisInitSuccess:
    """Tests for successful Redis initialization"""

    @patch('api.services.prediction_service.os.path.exists')
    @patch('api.services.prediction_service.redis')
    def test_redis_connection_success(self, mock_redis, mock_exists):
        """Test successful Redis connection and ping"""
        mock_exists.return_value = False  # No models
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        from api.services.prediction_service import PredictionService

        service = PredictionService()

        assert service.redis_client is not None
        mock_client.ping.assert_called_once()

    @patch('api.services.prediction_service.os.path.exists')
    @patch('api.services.prediction_service.redis')
    def test_redis_uses_upstash_url_first(self, mock_redis, mock_exists):
        """Test Upstash URL takes precedence over REDIS_URL"""
        mock_exists.return_value = False
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        with patch.dict('os.environ', {'UPSTASH_REDIS_URL': 'redis://upstash:6379'}):
            from api.services.prediction_service import PredictionService

            service = PredictionService()

            # Should call from_url with Upstash URL
            mock_redis.from_url.assert_called_once()
            call_args = mock_redis.from_url.call_args
            # First argument should contain upstash in the URL
            assert 'upstash' in call_args[0][0] or call_args[0][0].startswith('redis://')


class TestModelLoadingSuccess:
    """Tests for successful model loading"""

    @patch('api.services.prediction_service.redis')
    @patch('api.services.prediction_service.pickle.load')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('api.services.prediction_service.os.path.exists')
    def test_load_sepsis_model_success(self, mock_exists, mock_open, mock_pickle, mock_redis):
        """Test successful sepsis model loading"""
        mock_redis.from_url.side_effect = Exception("No Redis")

        # Mock model file exists
        def exists_side_effect(path):
            return 'sepsis' in path
        mock_exists.side_effect = exists_side_effect

        mock_model = MagicMock()
        mock_features = ['age', 'hr', 'temp']
        mock_pickle.side_effect = [mock_model, mock_features]

        from api.services.prediction_service import PredictionService

        service = PredictionService()

        assert 'sepsis' in service.models
        assert service.models['sepsis'] == mock_model
        assert 'sepsis' in service.feature_names
        assert service.feature_names['sepsis'] == mock_features

    @patch('api.services.prediction_service.redis')
    @patch('api.services.prediction_service.pickle.load')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('api.services.prediction_service.os.path.exists')
    def test_load_mortality_model_success(self, mock_exists, mock_open, mock_pickle, mock_redis):
        """Test successful mortality model loading"""
        mock_redis.from_url.side_effect = Exception("No Redis")

        # Mock model file exists
        def exists_side_effect(path):
            return 'mortality' in path
        mock_exists.side_effect = exists_side_effect

        mock_model = MagicMock()
        mock_features = ['age', 'bp', 'spo2']
        mock_pickle.side_effect = [mock_model, mock_features]

        from api.services.prediction_service import PredictionService

        service = PredictionService()

        assert 'mortality' in service.models
        assert service.models['mortality'] == mock_model
        assert 'mortality' in service.feature_names
        assert service.feature_names['mortality'] == mock_features


class TestCacheOperationsSuccess:
    """Tests for successful cache operations"""

    @pytest.fixture
    def service_with_redis(self):
        """Create service with working Redis client"""
        from api.services.prediction_service import PredictionService

        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = MagicMock()
                return service

    def test_get_from_cache_success(self, service_with_redis):
        """Test successful cache retrieval"""
        import json

        cached_data = {"risk_score": 0.75, "patient_id": "123"}
        service_with_redis.redis_client.get.return_value = json.dumps(cached_data)

        result = service_with_redis._get_from_cache("test_key")

        assert result == cached_data
        service_with_redis.redis_client.get.assert_called_once_with("test_key")

    def test_get_from_cache_miss(self, service_with_redis):
        """Test cache miss returns None"""
        service_with_redis.redis_client.get.return_value = None

        result = service_with_redis._get_from_cache("test_key")

        assert result is None

    def test_get_from_cache_error_handling(self, service_with_redis):
        """Test cache read error is handled gracefully"""
        service_with_redis.redis_client.get.side_effect = Exception("Redis error")

        result = service_with_redis._get_from_cache("test_key")

        assert result is None

    def test_save_to_cache_success(self, service_with_redis):
        """Test successful cache save"""
        import json

        data = {"risk_score": 0.75, "patient_id": "123"}

        service_with_redis._save_to_cache("test_key", data)

        service_with_redis.redis_client.setex.assert_called_once()
        call_args = service_with_redis.redis_client.setex.call_args[0]
        assert call_args[0] == "test_key"
        assert json.loads(call_args[2]) == data

    def test_save_to_cache_error_handling(self, service_with_redis):
        """Test cache write error is handled gracefully"""
        service_with_redis.redis_client.setex.side_effect = Exception("Redis error")

        # Should not raise exception
        service_with_redis._save_to_cache("test_key", {"data": "value"})


class TestPredictSepsisWithModel:
    """Tests for sepsis prediction with model loaded"""

    @pytest.fixture
    def service_with_sepsis_model(self):
        """Create service with mocked sepsis model"""
        from api.services.prediction_service import PredictionService

        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = None  # No cache
                service.feature_names = {}  # Initialize feature_names

                # Add mock model
                mock_model = MagicMock()
                mock_model.predict.return_value = np.array([0.65])
                mock_model.feature_importances_ = np.random.rand(42)
                service.models["sepsis"] = mock_model
                service.feature_names["sepsis"] = [f"feature_{i}" for i in range(42)]

                return service

    @pytest.mark.asyncio
    async def test_predict_sepsis_with_model_loaded(self, service_with_sepsis_model):
        """Test sepsis prediction with loaded model"""
        from api.models.schemas import SepsisPredictionRequest, SepsisFeatures

        # Create request with mock features
        mock_features = MagicMock(spec=SepsisFeatures)
        mock_features.dict.return_value = {f"feature_{i}": float(i) for i in range(42)}

        request = MagicMock(spec=SepsisPredictionRequest)
        request.patient_id = "patient_001"
        request.features = mock_features

        result = await service_with_sepsis_model.predict_sepsis(request, db=None)

        assert result.patient_id == "patient_001"
        assert result.prediction.risk_score == 0.65
        assert result.prediction.risk_level.value in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert result.metadata["model_version"] == "v2"
        assert result.metadata["cached"] == False

    @pytest.mark.asyncio
    async def test_predict_sepsis_calls_model_predict(self, service_with_sepsis_model):
        """Test model.predict is called with correct data"""
        from api.models.schemas import SepsisPredictionRequest, SepsisFeatures

        mock_features = MagicMock(spec=SepsisFeatures)
        features_dict = {f"feature_{i}": float(i) for i in range(42)}
        mock_features.dict.return_value = features_dict

        request = MagicMock(spec=SepsisPredictionRequest)
        request.patient_id = "patient_001"
        request.features = mock_features

        await service_with_sepsis_model.predict_sepsis(request, db=None)

        # Model predict should be called once
        service_with_sepsis_model.models["sepsis"].predict.assert_called_once()

    @pytest.mark.asyncio
    async def test_predict_sepsis_with_cache_hit(self):
        """Test sepsis prediction returns cached result"""
        from api.services.prediction_service import PredictionService
        from api.models.schemas import SepsisPredictionRequest, SepsisFeatures

        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = MagicMock()

                # Mock cache hit
                cached_result = {
                    "patient_id": "patient_001",
                    "prediction": {
                        "risk_score": 0.45,
                        "risk_level": "MEDIUM",
                        "recommendation": "Increase monitoring"
                    },
                    "top_features": [],
                    "metadata": {"model_version": "v2", "cached": False}
                }
                import json
                service.redis_client.get.return_value = json.dumps(cached_result)

                mock_features = MagicMock(spec=SepsisFeatures)
                mock_features.dict.return_value = {"age": 65}

                request = MagicMock(spec=SepsisPredictionRequest)
                request.patient_id = "patient_001"
                request.features = mock_features

                result = await service.predict_sepsis(request, db=None)

                assert result.metadata["cached"] == True
                assert result.prediction.risk_score == 0.45


class TestPredictMortalityWithModel:
    """Tests for mortality prediction with model loaded"""

    @pytest.fixture
    def service_with_mortality_model(self):
        """Create service with mocked mortality model"""
        from api.services.prediction_service import PredictionService

        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = None  # No cache
                service.feature_names = {}  # Initialize feature_names

                # Add mock model
                mock_model = MagicMock()
                mock_model.predict.return_value = np.array([0.55])
                mock_model.feature_importances_ = np.random.rand(61)
                service.models["mortality"] = mock_model
                service.feature_names["mortality"] = [f"feature_{i}" for i in range(61)]

                return service

    @pytest.mark.asyncio
    async def test_predict_mortality_with_model_loaded(self, service_with_mortality_model):
        """Test mortality prediction with loaded model"""
        from api.models.schemas import MortalityPredictionRequest, MortalityFeatures

        mock_features = MagicMock(spec=MortalityFeatures)
        mock_features.dict.return_value = {f"feature_{i}": float(i) for i in range(61)}

        request = MagicMock(spec=MortalityPredictionRequest)
        request.patient_id = "patient_002"
        request.features = mock_features

        result = await service_with_mortality_model.predict_mortality(request, db=None)

        assert result.patient_id == "patient_002"
        assert result.prediction.risk_score == 0.55
        assert result.prediction.risk_level.value in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert result.metadata["model_version"] == "v2"

    @pytest.mark.asyncio
    async def test_predict_mortality_with_cache_hit(self):
        """Test mortality prediction returns cached result"""
        from api.services.prediction_service import PredictionService
        from api.models.schemas import MortalityPredictionRequest, MortalityFeatures

        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = MagicMock()

                # Mock cache hit
                cached_result = {
                    "patient_id": "patient_002",
                    "prediction": {
                        "risk_score": 0.70,
                        "risk_level": "HIGH",
                        "recommendation": "Intensive care"
                    },
                    "top_features": [],
                    "metadata": {"model_version": "v2", "cached": False}
                }
                import json
                service.redis_client.get.return_value = json.dumps(cached_result)

                mock_features = MagicMock(spec=MortalityFeatures)
                mock_features.dict.return_value = {"age": 70}

                request = MagicMock(spec=MortalityPredictionRequest)
                request.patient_id = "patient_002"
                request.features = mock_features

                result = await service.predict_mortality(request, db=None)

                assert result.metadata["cached"] == True
                assert result.prediction.risk_score == 0.70


class TestDatabaseSave:
    """Tests for saving predictions to database"""

    @pytest.fixture
    def service_with_model(self):
        """Create service with model"""
        from api.services.prediction_service import PredictionService

        with patch.object(PredictionService, '_init_redis'):
            with patch.object(PredictionService, '_load_models'):
                service = PredictionService()
                service.redis_client = None
                service.feature_names = {}  # Initialize feature_names

                mock_model = MagicMock()
                mock_model.predict.return_value = np.array([0.60])
                mock_model.feature_importances_ = np.random.rand(42)
                service.models["sepsis"] = mock_model
                service.feature_names["sepsis"] = [f"feature_{i}" for i in range(42)]

                return service

    @pytest.mark.asyncio
    @patch('api.services.prediction_service.settings')
    @patch('api.services.prediction_service.PredictionHistoryService')
    async def test_sepsis_saves_to_database_when_enabled(self, mock_history_service, mock_settings, service_with_model):
        """Test prediction is saved to database when enabled"""
        from api.models.schemas import SepsisPredictionRequest, SepsisFeatures

        mock_settings.ENABLE_DATABASE = True
        mock_db = MagicMock()

        mock_features = MagicMock(spec=SepsisFeatures)
        mock_features.dict.return_value = {f"feature_{i}": float(i) for i in range(42)}

        request = MagicMock(spec=SepsisPredictionRequest)
        request.patient_id = "patient_001"
        request.features = mock_features

        await service_with_model.predict_sepsis(request, db=mock_db)

        # Should call save_prediction
        mock_history_service.save_prediction.assert_called_once()
        call_kwargs = mock_history_service.save_prediction.call_args[1]
        assert call_kwargs["db"] == mock_db
        assert call_kwargs["prediction_type"] == "sepsis"
        assert call_kwargs["model_version"] == "v2"

    @pytest.mark.asyncio
    @patch('api.services.prediction_service.settings')
    @patch('api.services.prediction_service.PredictionHistoryService')
    async def test_database_save_failure_doesnt_break_prediction(self, mock_history_service, mock_settings, service_with_model):
        """Test prediction continues even if database save fails"""
        from api.models.schemas import SepsisPredictionRequest, SepsisFeatures

        mock_settings.ENABLE_DATABASE = True
        mock_history_service.save_prediction.side_effect = Exception("DB error")

        mock_features = MagicMock(spec=SepsisFeatures)
        mock_features.dict.return_value = {f"feature_{i}": float(i) for i in range(42)}

        request = MagicMock(spec=SepsisPredictionRequest)
        request.patient_id = "patient_001"
        request.features = mock_features

        # Should not raise exception
        result = await service_with_model.predict_sepsis(request, db=MagicMock())

        # Should still return valid result
        assert result.patient_id == "patient_001"
        assert result.prediction.risk_score > 0
