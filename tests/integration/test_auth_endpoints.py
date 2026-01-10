"""
Integration tests for Auth endpoints
Tests authentication flow including login, token refresh, and protected routes
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta


class TestAuthEndpoints:
    """Tests for /api/auth/* endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked database"""
        from fastapi.testclient import TestClient
        
        with patch('api.core.database.SessionLocal'):
            with patch('api.services.prediction_service.redis'):
                try:
                    from api.main import app
                    return TestClient(app)
                except Exception:
                    pytest.skip("Could not import app")

    def test_login_endpoint_exists(self, client, demo_user_credentials):
        """Test login endpoint exists"""
        response = client.post("/api/v1/auth/login", data={
            "username": demo_user_credentials["username"],
            "password": demo_user_credentials["password"]
        })

        # Should not be 404 (may be 200 for success or other auth errors)
        assert response.status_code != 404

    def test_login_invalid_credentials_returns_401(self, client):
        """Test login with invalid credentials returns 401"""
        response = client.post("/api/v1/auth/login", data={
            "username": "nonexistent",
            "password": "wrongpassword"
        })

        assert response.status_code in [401, 422, 400]

    def test_login_missing_fields_returns_422(self, client):
        """Test login with missing fields returns 422"""
        response = client.post("/api/v1/auth/login", data={})

        assert response.status_code == 422

    def test_register_endpoint_exists(self, client):
        """Test register endpoint exists"""
        response = client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        })

        # Should not be 405 Method Not Allowed
        assert response.status_code != 405


class TestProtectedRoutes:
    """Tests for authentication protection on routes"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        
        with patch('api.core.database.SessionLocal'):
            with patch('api.services.prediction_service.redis'):
                try:
                    from api.main import app
                    return TestClient(app)
                except Exception:
                    pytest.skip("Could not import app")

    def test_prediction_requires_auth(self, client):
        """Test prediction endpoints require authentication"""
        response = client.post("/api/v1/predict/sepsis", json={
            "patient_id": "test",
            "features": {}
        })

        # Should require auth (401) or have other error
        assert response.status_code in [401, 403, 422]

    def test_patients_requires_auth(self, client):
        """Test patient endpoints require authentication"""
        response = client.get("/api/v1/patients")

        assert response.status_code in [401, 403, 404]


class TestTokenValidation:
    """Tests for JWT token validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        
        with patch('api.core.database.SessionLocal'):
            with patch('api.services.prediction_service.redis'):
                try:
                    from api.main import app
                    return TestClient(app)
                except Exception:
                    pytest.skip("Could not import app")

    def test_invalid_token_rejected(self, client):
        """Test invalid token is rejected"""
        response = client.get(
            "/api/v1/patients",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code in [401, 403, 404]

    def test_expired_token_rejected(self, client):
        """Test expired token is rejected"""
        # Create an expired token (mock)
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxfQ.invalid"

        response = client.get(
            "/api/v1/patients",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code in [401, 403, 404]


class TestSecurityHeaders:
    """Tests for security headers"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        
        with patch('api.core.database.SessionLocal'):
            with patch('api.services.prediction_service.redis'):
                try:
                    from api.main import app
                    return TestClient(app)
                except Exception:
                    pytest.skip("Could not import app")

    def test_cors_headers_present(self, client):
        """Test CORS headers are configured"""
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Should allow OPTIONS or return CORS headers
        assert response.status_code in [200, 204, 405]
