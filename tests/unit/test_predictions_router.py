"""
Unit tests for Predictions router
Tests prediction API endpoints
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestPredictionsRouterConfig:
    """Tests for predictions router configuration"""

    def test_router_exists(self):
        """Test predictions router exists"""
        from api.routers.predictions import router
        
        assert router is not None

    def test_router_has_sepsis_endpoint(self):
        """Test sepsis prediction endpoint is registered"""
        from api.routers.predictions import router
        
        routes = [r.path for r in router.routes]
        
        assert "/predict/sepsis" in routes

    def test_router_has_mortality_endpoint(self):
        """Test mortality prediction endpoint is registered"""
        from api.routers.predictions import router
        
        routes = [r.path for r in router.routes]
        
        assert "/predict/mortality" in routes

    def test_router_has_models_info_endpoint(self):
        """Test models info endpoint is registered"""
        from api.routers.predictions import router
        
        routes = [r.path for r in router.routes]
        
        assert "/models/info" in routes


class TestPredictionService:
    """Tests for prediction service in router"""

    def test_prediction_service_initialized(self):
        """Test prediction service is initialized"""
        from api.routers.predictions import prediction_service
        
        assert prediction_service is not None

    def test_prediction_service_has_models(self):
        """Test prediction service has models dict"""
        from api.routers.predictions import prediction_service
        
        assert hasattr(prediction_service, 'models')
        assert isinstance(prediction_service.models, dict)


class TestGetModelsInfo:
    """Tests for /models/info endpoint"""

    @pytest.mark.asyncio
    async def test_get_models_info_returns_dict(self):
        """Test models info returns dictionary"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_models_info_has_sepsis_model(self):
        """Test models info includes sepsis model"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert "sepsis_model" in result

    @pytest.mark.asyncio
    async def test_get_models_info_has_mortality_model(self):
        """Test models info includes mortality model"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert "mortality_model" in result

    @pytest.mark.asyncio
    async def test_sepsis_model_info_fields(self):
        """Test sepsis model info has required fields"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        sepsis = result["sepsis_model"]
        
        assert "version" in sepsis
        assert "features" in sepsis
        assert "algorithm" in sepsis

    @pytest.mark.asyncio
    async def test_mortality_model_info_fields(self):
        """Test mortality model info has required fields"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        mortality = result["mortality_model"]
        
        assert "version" in mortality
        assert "features" in mortality
        assert "algorithm" in mortality

    @pytest.mark.asyncio
    async def test_model_versions_are_v2(self):
        """Test model versions are v2"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert "v2" in result["sepsis_model"]["version"]
        assert "v2" in result["mortality_model"]["version"]

    @pytest.mark.asyncio
    async def test_sepsis_has_42_features(self):
        """Test sepsis model has 42 features"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert result["sepsis_model"]["features"] == 42

    @pytest.mark.asyncio
    async def test_mortality_has_61_features(self):
        """Test mortality model has 61 features"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert result["mortality_model"]["features"] == 61

    @pytest.mark.asyncio
    async def test_models_use_lightgbm(self):
        """Test models use LightGBM algorithm"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert result["sepsis_model"]["algorithm"] == "LightGBM"
        assert result["mortality_model"]["algorithm"] == "LightGBM"

    @pytest.mark.asyncio
    async def test_models_have_metrics(self):
        """Test models have performance metrics"""
        from api.routers.predictions import get_models_info
        
        result = await get_models_info()
        
        assert "metrics" in result["sepsis_model"]
        assert "metrics" in result["mortality_model"]
        
        # Check specific metrics
        sepsis_metrics = result["sepsis_model"]["metrics"]
        assert "auc_roc" in sepsis_metrics
        assert "accuracy" in sepsis_metrics
