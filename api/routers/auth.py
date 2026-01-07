"""
Authentication endpoints for JWT token generation
Prefix: /api/v1/auth
"""

from datetime import timedelta

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    Token,
    User,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    verify_password,
)
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

router = APIRouter()

# Demo users database (in production, use real database)
# Passwords should be set via environment variables
import os

_DEMO_PASSWORD_HASH = os.getenv(
    "DEMO_USER_PASSWORD_HASH",
    "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.OPVcKH1Y1kMfFS",  # Default: changeme
)
_ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_USER_PASSWORD_HASH",
    "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.OPVcKH1Y1kMfFS",  # Default: changeme
)

DEMO_USERS = {
    "demo": {
        "username": "demo",
        "full_name": "Demo User",
        "email": "demo@mediai.com",
        "hashed_password": _DEMO_PASSWORD_HASH,
        "disabled": False,
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@mediai.com",
        "hashed_password": _ADMIN_PASSWORD_HASH,
        "disabled": False,
    },
}


def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    user = DEMO_USERS.get(username)
    if not user:
        return False
    # In a real app, verify_password handles the check
    # For this demo, we can just check if hashed passwords match or verify
    try:
        if verify_password(password, user["hashed_password"]):
            return user
    except Exception:
        pass
    return False


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests

    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/login" \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "username=demo&password=demo123"
    ```
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # Create Refresh Token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user["username"]}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str = Body(..., embed=True)):
    """
    Refresh access token using refresh token via body
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception

        # Verify user still exists
        user = DEMO_USERS.get(username)
        if not user:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Create new Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    # Optionally rotate refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_refresh_token(
        data={"sub": username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user info

    Requires authentication header:
    ```bash
    curl -X GET "http://localhost:8000/api/v1/auth/me" \\
      -H "Authorization: Bearer <your_token>"
    ```
    """
    return current_user
