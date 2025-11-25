"""
Basic API tests
Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert response.json()["name"] == "MediAI API"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data


def test_models_info_endpoint():
    """Test models info endpoint"""
    response = client.get("/api/v1/models/info")
    assert response.status_code == 200
    data = response.json()
    assert "sepsis_model" in data
    assert "mortality_model" in data


def test_sepsis_prediction_invalid_input():
    """Test sepsis prediction with invalid input"""
    response = client.post(
        "/api/v1/predict/sepsis",
        json={
            "patient_id": "TEST",
            "features": {
                "age": 200,  # Invalid: >120
            }
        }
    )
    assert response.status_code == 422  # Validation error


# Note: Full prediction test requires models to be loaded
# def test_sepsis_prediction_valid():
#     """Test sepsis prediction with valid input"""
#     # Implementation when models are available
#     pass
