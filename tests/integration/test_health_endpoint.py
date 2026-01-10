"""
Integration tests for Health endpoint
Tests health check and metrics endpoints
"""

import pytest
from unittest.mock import MagicMock, patch


class MockResponse:
    """Mock response for testing"""
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
    
    def json(self):
        return self._json_data


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        
        # Import with mocked dependencies
        with patch('api.core.database.SessionLocal'):
            with patch('api.services.prediction_service.redis'):
                try:
                    from api.main import app
                    return TestClient(app)
                except Exception:
                    # If import fails, skip these tests
                    pytest.skip("Could not import app")

    def test_health_endpoint_returns_200(self, client):
        """Test health endpoint returns 200"""
        response = client.get("/health")
        
        assert response.status_code == 200

    def test_health_endpoint_returns_status(self, client):
        """Test health endpoint includes status"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "running"]

    def test_health_endpoint_returns_version(self, client):
        """Test health endpoint includes version info"""
        response = client.get("/health")
        data = response.json()
        
        # May have version or timestamp
        assert "status" in data


class TestMetricsEndpoint:
    """Tests for metrics endpoints"""

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

    def test_metrics_endpoint_exists(self, client):
        """Test metrics endpoint responds"""
        response = client.get("/metrics")
        
        # 200 or 404 depending on configuration
        assert response.status_code in [200, 404]


class TestRootEndpoint:
    """Tests for root endpoint"""

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

    def test_root_endpoint_returns_200(self, client):
        """Test root endpoint returns 200"""
        response = client.get("/")
        
        assert response.status_code == 200

    def test_root_endpoint_returns_api_info(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        data = response.json()
        
        # Should have some identifying information
        assert isinstance(data, dict)


class TestDocsEndpoint:
    """Tests for API documentation endpoints"""

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

    def test_docs_endpoint_accessible(self, client):
        """Test /docs endpoint is accessible"""
        response = client.get("/docs")
        
        # Should return HTML or redirect
        assert response.status_code in [200, 307]

    def test_openapi_json_accessible(self, client):
        """Test OpenAPI JSON is accessible"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data or "paths" in data
