"""
Integration tests for MediAI platform
Run with: pytest tests/test_integration.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

api_path = Path(__file__).parent.parent / "api"
apps_path = Path(__file__).parent.parent / "apps"
sys.path.insert(0, str(api_path))
sys.path.insert(0, str(apps_path))

from api.main import app
from apps.services.model_service import get_model_service

client = TestClient(app)


class TestEndToEndPrediction:
    """Test complete prediction workflow"""

    def test_sepsis_prediction_workflow(self, sample_sepsis_features):
        """Test complete sepsis prediction from API request to response"""
        response = client.post(
            "/api/v1/predict/sepsis",
            json={
                "patient_id": "TEST-001",
                "features": sample_sepsis_features
            }
        )

        # Check response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Check response structure
        data = response.json()
        assert "prediction" in data
        assert "metadata" in data

        # Check prediction fields
        prediction = data["prediction"]
        assert "risk_score" in prediction
        assert "risk_level" in prediction
        assert "recommendation" in prediction

        # Check metadata
        metadata = data["metadata"]
        assert "model_version" in metadata
        assert "features_used" in metadata

    def test_mortality_prediction_workflow(self, sample_mortality_features):
        """Test complete mortality prediction workflow"""
        response = client.post(
            "/api/v1/predict/mortality",
            json={
                "patient_id": "TEST-002",
                "features": sample_mortality_features
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert "metadata" in data

        prediction = data["prediction"]
        assert "risk_score" in prediction
        assert "risk_level" in prediction

    def test_health_check_integration(self):
        """Test health check with all components"""
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data

        # Check individual components
        components = data["components"]
        assert "api" in components
        assert components["api"] == "healthy"

    def test_model_info_integration(self):
        """Test model info endpoint"""
        response = client.get("/api/v1/models/info")

        assert response.status_code == 200

        data = response.json()
        assert "sepsis_model" in data
        assert "mortality_model" in data

        sepsis_info = data["sepsis_model"]
        assert "version" in sepsis_info
        assert "features" in sepsis_info

    def test_multiple_predictions_consistency(self, sample_sepsis_features):
        """Test that multiple predictions with same input produce consistent results"""
        responses = []
        for _ in range(3):
            response = client.post(
                "/api/v1/predict/sepsis",
                json={
                    "patient_id": "TEST-CONSISTENCY",
                    "features": sample_sepsis_features
                }
            )
            responses.append(response.json())

        # Check all predictions have same risk level
        risk_levels = [r["prediction"]["risk_level"] for r in responses]
        assert len(set(risk_levels)) == 1, "Risk levels should be consistent"

        # Check risk scores are very close (within 0.001)
        risk_scores = [r["prediction"]["risk_score"] for r in responses]
        assert max(risk_scores) - min(risk_scores) < 0.001


class TestAPIValidation:
    """Test API input validation"""

    def test_invalid_age(self):
        """Test validation rejects invalid age"""
        response = client.post(
            "/api/v1/predict/sepsis",
            json={
                "patient_id": "TEST",
                "features": {
                    "age": 200,  # Invalid
                    "gender": "M",
                }
            }
        )

        assert response.status_code == 422

    def test_missing_required_field(self):
        """Test validation requires all fields"""
        response = client.post(
            "/api/v1/predict/sepsis",
            json={
                "patient_id": "TEST",
                "features": {
                    "age": 65,
                    # Missing other required fields
                }
            }
        )

        assert response.status_code == 422

    def test_invalid_gender(self):
        """Test validation for gender field"""
        response = client.post(
            "/api/v1/predict/sepsis",
            json={
                "patient_id": "TEST",
                "features": {
                    "age": 65,
                    "gender": "X",  # Invalid
                }
            }
        )

        assert response.status_code == 422


class TestModelServiceIntegration:
    """Test model service integration"""

    def test_model_service_singleton(self):
        """Test that model service is singleton"""
        service1 = get_model_service()
        service2 = get_model_service()

        assert service1 is service2, "Model service should be singleton"

    def test_models_loaded_once(self):
        """Test that models are loaded only once"""
        service = get_model_service()

        # Models should already be loaded
        assert service.sepsis_model is not None
        assert service.mortality_model is not None

    def test_prediction_consistency_across_services(self, sample_sepsis_features):
        """Test predictions are consistent across service calls"""
        service = get_model_service()

        result1 = service.predict_sepsis(sample_sepsis_features)
        result2 = service.predict_sepsis(sample_sepsis_features)

        assert result1["risk_level"] == result2["risk_level"]
        assert abs(result1["risk_score"] - result2["risk_score"]) < 0.001
