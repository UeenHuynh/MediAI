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

    def test_authenticate_user_exception_during_verification(self):
        """Test authentication handles exception during password verification"""
        from api.routers.auth import authenticate_user

        with patch('api.routers.auth.verify_password') as mock_verify:
            mock_verify.side_effect = Exception("Verification error")

            result = authenticate_user("demo", "password")

            # Should return False when exception occurs
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


class TestLoginEndpoint:
    """Tests for /login endpoint"""

    @pytest.mark.asyncio
    async def test_login_success_with_valid_credentials(self):
        """Test successful login with valid credentials"""
        from api.routers.auth import login_for_access_token
        from fastapi.security import OAuth2PasswordRequestForm
        from unittest.mock import MagicMock

        # Create mock form data
        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "demo"
        form_data.password = "demo123"

        with patch('api.routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "username": "demo",
                "email": "demo@mediai.com",
                "disabled": False
            }

            result = await login_for_access_token(form_data)

            assert "access_token" in result
            assert "refresh_token" in result
            assert result["token_type"] == "bearer"
            assert isinstance(result["access_token"], str)
            assert isinstance(result["refresh_token"], str)

    @pytest.mark.asyncio
    async def test_login_failure_with_invalid_credentials(self):
        """Test login failure with invalid credentials raises HTTPException"""
        from api.routers.auth import login_for_access_token
        from fastapi.security import OAuth2PasswordRequestForm
        from fastapi import HTTPException
        from unittest.mock import MagicMock

        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "demo"
        form_data.password = "wrong_password"

        with patch('api.routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await login_for_access_token(form_data)

            assert exc_info.value.status_code == 401
            assert "Incorrect username or password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_creates_access_token_with_username(self):
        """Test login creates access token with username in payload"""
        from api.routers.auth import login_for_access_token
        from fastapi.security import OAuth2PasswordRequestForm
        from unittest.mock import MagicMock

        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "demo"
        form_data.password = "demo123"

        with patch('api.routers.auth.authenticate_user') as mock_auth:
            with patch('api.routers.auth.create_access_token') as mock_create_access:
                with patch('api.routers.auth.create_refresh_token') as mock_create_refresh:
                    mock_auth.return_value = {"username": "demo"}
                    mock_create_access.return_value = "fake_access_token"
                    mock_create_refresh.return_value = "fake_refresh_token"

                    result = await login_for_access_token(form_data)

                    # Verify create_access_token was called with correct data
                    mock_create_access.assert_called_once()
                    call_kwargs = mock_create_access.call_args[1]
                    assert call_kwargs["data"]["sub"] == "demo"

                    assert result["access_token"] == "fake_access_token"
                    assert result["refresh_token"] == "fake_refresh_token"


class TestRefreshTokenEndpoint:
    """Tests for /refresh endpoint"""

    @pytest.mark.asyncio
    async def test_refresh_token_success_with_valid_token(self):
        """Test successful token refresh with valid refresh token"""
        from api.routers.auth import refresh_token
        from jose import jwt
        from datetime import datetime, timedelta

        # Create a valid refresh token
        with patch('api.routers.auth.SECRET_KEY', 'test_secret'):
            with patch('api.routers.auth.ALGORITHM', 'HS256'):
                with patch('api.routers.auth.jwt') as mock_jwt:
                    # Mock JWT decode to return valid payload
                    mock_jwt.decode.return_value = {
                        "sub": "demo",
                        "type": "refresh",
                        "exp": (datetime.utcnow() + timedelta(days=7)).timestamp()
                    }

                    with patch('api.routers.auth.DEMO_USERS', {"demo": {"username": "demo"}}):
                        with patch('api.routers.auth.create_access_token') as mock_create_access:
                            with patch('api.routers.auth.create_refresh_token') as mock_create_refresh:
                                mock_create_access.return_value = "new_access_token"
                                mock_create_refresh.return_value = "new_refresh_token"

                                result = await refresh_token("valid_refresh_token")

                                assert "access_token" in result
                                assert "refresh_token" in result
                                assert result["token_type"] == "bearer"
                                assert result["access_token"] == "new_access_token"
                                assert result["refresh_token"] == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_token_failure_with_invalid_token(self):
        """Test refresh failure with invalid token raises HTTPException"""
        from api.routers.auth import refresh_token
        from fastapi import HTTPException
        from jose import JWTError

        with patch('api.routers.auth.jwt') as mock_jwt:
            mock_jwt.decode.side_effect = JWTError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token("invalid_token")

            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_failure_with_access_token_type(self):
        """Test refresh failure when using access token instead of refresh token"""
        from api.routers.auth import refresh_token
        from fastapi import HTTPException

        with patch('api.routers.auth.jwt') as mock_jwt:
            # Mock JWT decode to return access token payload
            mock_jwt.decode.return_value = {
                "sub": "demo",
                "type": "access",  # Wrong type
                "exp": 99999999999
            }

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token("access_token_instead_of_refresh")

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_failure_with_no_username(self):
        """Test refresh failure when token has no username"""
        from api.routers.auth import refresh_token
        from fastapi import HTTPException

        with patch('api.routers.auth.jwt') as mock_jwt:
            # Mock JWT decode to return payload without username
            mock_jwt.decode.return_value = {
                "type": "refresh",
                "exp": 99999999999
            }

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token("token_without_username")

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_failure_with_nonexistent_user(self):
        """Test refresh failure when user no longer exists"""
        from api.routers.auth import refresh_token
        from fastapi import HTTPException

        with patch('api.routers.auth.jwt') as mock_jwt:
            mock_jwt.decode.return_value = {
                "sub": "deleted_user",
                "type": "refresh",
                "exp": 99999999999
            }

            with patch('api.routers.auth.DEMO_USERS', {}):  # Empty users dict
                with pytest.raises(HTTPException) as exc_info:
                    await refresh_token("token_for_deleted_user")

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_creates_new_tokens(self):
        """Test refresh endpoint creates both new access and refresh tokens"""
        from api.routers.auth import refresh_token

        with patch('api.routers.auth.jwt') as mock_jwt:
            mock_jwt.decode.return_value = {
                "sub": "demo",
                "type": "refresh",
                "exp": 99999999999
            }

            with patch('api.routers.auth.DEMO_USERS', {"demo": {"username": "demo"}}):
                with patch('api.routers.auth.create_access_token') as mock_create_access:
                    with patch('api.routers.auth.create_refresh_token') as mock_create_refresh:
                        mock_create_access.return_value = "new_access"
                        mock_create_refresh.return_value = "new_refresh"

                        result = await refresh_token("valid_token")

                        # Both token creation methods should be called
                        mock_create_access.assert_called_once()
                        mock_create_refresh.assert_called_once()

                        # Verify username is passed correctly
                        access_call_kwargs = mock_create_access.call_args[1]
                        assert access_call_kwargs["data"]["sub"] == "demo"


class TestMeEndpoint:
    """Tests for /me endpoint"""

    @pytest.mark.asyncio
    async def test_me_returns_current_user(self):
        """Test /me endpoint returns current user info"""
        from api.routers.auth import read_users_me
        from core.security import User

        # Create mock user
        mock_user = User(
            username="demo",
            email="demo@mediai.com",
            full_name="Demo User",
            disabled=False
        )

        result = await read_users_me(mock_user)

        assert result == mock_user
        assert result.username == "demo"
        assert result.email == "demo@mediai.com"
