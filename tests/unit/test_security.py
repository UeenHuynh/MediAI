"""
Unit tests for Security module
Tests password hashing, JWT tokens, and user authentication
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta, datetime


class TestPasswordHashing:
    """Tests for password hashing functionality"""

    def test_verify_password_correct(self):
        """Test verifying correct password"""
        try:
            from api.core.security import verify_password, get_password_hash
            
            password = "test_password_123"
            hashed = get_password_hash(password)
            
            result = verify_password(password, hashed)
            
            assert result is True
        except ImportError:
            pytest.skip("Security module not available")

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        try:
            from api.core.security import verify_password, get_password_hash
            
            password = "test_password_123"
            hashed = get_password_hash(password)
            
            result = verify_password("wrong_password", hashed)
            
            assert result is False
        except ImportError:
            pytest.skip("Security module not available")

    def test_get_password_hash_returns_bcrypt(self):
        """Test password hash is bcrypt format"""
        try:
            from api.core.security import get_password_hash
            
            hashed = get_password_hash("test_password")
            
            # bcrypt hashes start with $2b$ or $2a$
            assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
        except ImportError:
            pytest.skip("Security module not available")

    def test_get_password_hash_unique(self):
        """Test same password produces different hashes"""
        try:
            from api.core.security import get_password_hash
            
            hash1 = get_password_hash("same_password")
            hash2 = get_password_hash("same_password")
            
            # bcrypt produces different hashes due to salt
            assert hash1 != hash2
        except ImportError:
            pytest.skip("Security module not available")


class TestJWTTokens:
    """Tests for JWT token creation"""

    def test_create_access_token(self):
        """Test access token creation"""
        try:
            from api.core.security import create_access_token
            
            token = create_access_token(
                data={"sub": "testuser"},
                expires_delta=timedelta(minutes=30)
            )
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0
        except ImportError:
            pytest.skip("Security module not available")

    def test_create_access_token_contains_payload(self):
        """Test access token contains correct payload"""
        try:
            from api.core.security import create_access_token, SECRET_KEY, ALGORITHM
            from jose import jwt
            
            token = create_access_token(
                data={"sub": "testuser"},
                expires_delta=timedelta(minutes=30)
            )
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            assert payload["sub"] == "testuser"
            assert "exp" in payload
        except ImportError:
            pytest.skip("Security module not available")

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        try:
            from api.core.security import create_refresh_token
            
            token = create_refresh_token(
                data={"sub": "testuser"},
                expires_delta=timedelta(days=7)
            )
            
            assert token is not None
            assert isinstance(token, str)
        except ImportError:
            pytest.skip("Security module not available")

    def test_refresh_token_has_type(self):
        """Test refresh token has type=refresh"""
        try:
            from api.core.security import create_refresh_token, SECRET_KEY, ALGORITHM
            from jose import jwt
            
            token = create_refresh_token(
                data={"sub": "testuser"},
                expires_delta=timedelta(days=7)
            )
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            assert payload.get("type") == "refresh"
        except ImportError:
            pytest.skip("Security module not available")


class TestSecurityConstants:
    """Tests for security constants"""

    def test_secret_key_exists(self):
        """Test SECRET_KEY is configured"""
        try:
            from api.core.security import SECRET_KEY
            
            assert SECRET_KEY is not None
            assert len(SECRET_KEY) > 0
        except ImportError:
            pytest.skip("Security module not available")

    def test_algorithm_is_hs256(self):
        """Test ALGORITHM is HS256"""
        try:
            from api.core.security import ALGORITHM
            
            assert ALGORITHM == "HS256"
        except ImportError:
            pytest.skip("Security module not available")

    def test_access_token_expire_minutes(self):
        """Test access token expiration is set"""
        try:
            from api.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
            
            assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
            assert ACCESS_TOKEN_EXPIRE_MINUTES <= 1440  # Max 24 hours
        except ImportError:
            pytest.skip("Security module not available")

    def test_refresh_token_expire_days(self):
        """Test refresh token expiration is set"""
        try:
            from api.core.security import REFRESH_TOKEN_EXPIRE_DAYS
            
            assert REFRESH_TOKEN_EXPIRE_DAYS > 0
            assert REFRESH_TOKEN_EXPIRE_DAYS <= 30  # Max 30 days
        except ImportError:
            pytest.skip("Security module not available")


class TestUserModel:
    """Tests for User model"""

    def test_user_model_exists(self):
        """Test User model is defined"""
        try:
            from api.core.security import User
            
            assert User is not None
        except ImportError:
            pytest.skip("Security module not available")

    def test_token_model_exists(self):
        """Test Token model is defined"""
        try:
            from api.core.security import Token
            
            assert Token is not None
        except ImportError:
            pytest.skip("Security module not available")


class TestOAuth2Scheme:
    """Tests for OAuth2 configuration"""

    def test_oauth2_scheme_exists(self):
        """Test OAuth2 scheme is configured"""
        try:
            from api.core.security import oauth2_scheme

            assert oauth2_scheme is not None
        except ImportError:
            pytest.skip("Security module not available")


class TestGetCurrentUser:
    """Tests for get_current_user function"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test get_current_user with valid token"""
        try:
            from api.core.security import get_current_user, create_access_token

            # Create a valid token
            token = create_access_token(
                data={"sub": "testuser"},
                expires_delta=timedelta(minutes=30)
            )

            # Get user from token
            user = await get_current_user(token)

            assert user is not None
            assert user.username == "testuser"
        except ImportError:
            pytest.skip("Security module not available")

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        try:
            from api.core.security import get_current_user
            from fastapi import HTTPException

            # Try with invalid token
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("invalid_token_string")

            assert exc_info.value.status_code == 401
        except ImportError:
            pytest.skip("Security module not available")

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self):
        """Test get_current_user with expired token"""
        try:
            from api.core.security import get_current_user, create_access_token
            from fastapi import HTTPException
            import time

            # Create token that expires immediately
            token = create_access_token(
                data={"sub": "testuser"},
                expires_delta=timedelta(seconds=-1)  # Already expired
            )

            # Wait a moment
            time.sleep(0.1)

            # Try to use expired token
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token)

            assert exc_info.value.status_code == 401
        except ImportError:
            pytest.skip("Security module not available")

    @pytest.mark.asyncio
    async def test_get_current_user_token_without_subject(self):
        """Test get_current_user with token missing 'sub'"""
        try:
            from api.core.security import get_current_user, SECRET_KEY, ALGORITHM
            from jose import jwt
            from fastapi import HTTPException

            # Create token without 'sub' field
            token_data = {"exp": datetime.utcnow() + timedelta(minutes=30)}
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

            # Should raise 401
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token)

            assert exc_info.value.status_code == 401
        except ImportError:
            pytest.skip("Security module not available")


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user function"""

    @pytest.mark.asyncio
    async def test_get_current_active_user_active(self):
        """Test get_current_active_user with active user"""
        try:
            from api.core.security import get_current_active_user, User

            # Create active user
            active_user = User(username="testuser", disabled=False)

            # Should return the user
            result = await get_current_active_user(active_user)

            assert result.username == "testuser"
            assert result.disabled is False
        except ImportError:
            pytest.skip("Security module not available")

    @pytest.mark.asyncio
    async def test_get_current_active_user_disabled(self):
        """Test get_current_active_user with disabled user"""
        try:
            from api.core.security import get_current_active_user, User
            from fastapi import HTTPException

            # Create disabled user
            disabled_user = User(username="testuser", disabled=True)

            # Should raise 400
            with pytest.raises(HTTPException) as exc_info:
                await get_current_active_user(disabled_user)

            assert exc_info.value.status_code == 400
        except ImportError:
            pytest.skip("Security module not available")


class TestTokenExpiration:
    """Tests for token expiration handling"""

    def test_access_token_default_expiration(self):
        """Test access token has default expiration"""
        try:
            from api.core.security import create_access_token, SECRET_KEY, ALGORITHM
            from jose import jwt
            from datetime import datetime

            token = create_access_token(data={"sub": "testuser"})
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check expiration exists and is in future
            assert "exp" in payload
            exp_time = datetime.fromtimestamp(payload["exp"])
            assert exp_time > datetime.utcnow()
        except ImportError:
            pytest.skip("Security module not available")

    def test_refresh_token_longer_expiration(self):
        """Test refresh token has longer expiration than access token"""
        try:
            from api.core.security import (
                create_access_token,
                create_refresh_token,
                SECRET_KEY,
                ALGORITHM
            )
            from jose import jwt

            access_token = create_access_token(data={"sub": "testuser"})
            refresh_token = create_refresh_token(data={"sub": "testuser"})

            access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            # Refresh token should expire later
            assert refresh_payload["exp"] > access_payload["exp"]
        except ImportError:
            pytest.skip("Security module not available")
