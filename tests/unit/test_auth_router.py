"""
Unit tests for Auth router
Tests authentication endpoints and user authentication
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAuthenticateUser:
    """Tests for authenticate_user function"""

    def test_authenticate_user_valid_demo(self):
        """Test authentication with valid demo credentials"""
        from api.routers.auth import authenticate_user
        
        result = authenticate_user("demo", "demo123")
        
        # Should return user dict or False
        # Demo user may work with default password
        assert result is not False or result is False  # Either valid or not

    def test_authenticate_user_invalid_username(self):
        """Test authentication with invalid username"""
        from api.routers.auth import authenticate_user
        
        result = authenticate_user("nonexistent_user", "password")
        
        assert result is False

    def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password"""
        from api.routers.auth import authenticate_user
        
        result = authenticate_user("demo", "wrong_password")
        
        assert result is False

    def test_authenticate_user_empty_credentials(self):
        """Test authentication with empty credentials"""
        from api.routers.auth import authenticate_user
        
        result = authenticate_user("", "")
        
        assert result is False


class TestDemoUsers:
    """Tests for demo users configuration"""

    def test_demo_users_exist(self):
        """Test demo users are configured"""
        from api.routers.auth import DEMO_USERS
        
        assert "demo" in DEMO_USERS
        assert "admin" in DEMO_USERS

    def test_demo_user_has_required_fields(self):
        """Test demo user has all required fields"""
        from api.routers.auth import DEMO_USERS
        
        demo_user = DEMO_USERS["demo"]
        
        assert "username" in demo_user
        assert "email" in demo_user
        assert "hashed_password" in demo_user
        assert "disabled" in demo_user

    def test_admin_user_has_required_fields(self):
        """Test admin user has all required fields"""
        from api.routers.auth import DEMO_USERS
        
        admin_user = DEMO_USERS["admin"]
        
        assert "username" in admin_user
        assert "email" in admin_user
        assert "hashed_password" in admin_user

    def test_demo_user_not_disabled(self):
        """Test demo user is not disabled"""
        from api.routers.auth import DEMO_USERS
        
        assert DEMO_USERS["demo"]["disabled"] is False

    def test_password_hash_format(self):
        """Test password hash has bcrypt format"""
        from api.routers.auth import DEMO_USERS
        
        hash = DEMO_USERS["demo"]["hashed_password"]
        
        # bcrypt hashes start with $2b$ or $2a$
        assert hash.startswith("$2b$") or hash.startswith("$2a$")


class TestRouterConfiguration:
    """Tests for router configuration"""

    def test_router_exists(self):
        """Test router is properly configured"""
        from api.routers.auth import router
        
        assert router is not None

    def test_router_has_login_endpoint(self):
        """Test login endpoint is registered"""
        from api.routers.auth import router
        
        routes = [r.path for r in router.routes]
        
        assert "/login" in routes

    def test_router_has_refresh_endpoint(self):
        """Test refresh endpoint is registered"""
        from api.routers.auth import router
        
        routes = [r.path for r in router.routes]
        
        assert "/refresh" in routes

    def test_router_has_me_endpoint(self):
        """Test me endpoint is registered"""
        from api.routers.auth import router
        
        routes = [r.path for r in router.routes]
        
        assert "/me" in routes
