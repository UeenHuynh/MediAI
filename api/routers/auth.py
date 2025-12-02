"""
Authentication endpoints for JWT token generation
"""

from datetime import timedelta

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User,
    create_access_token,
    get_current_active_user,
    verify_password,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

# Demo users database (in production, use real database)
DEMO_USERS = {
    "demo": {
        "username": "demo",
        "full_name": "Demo User",
        "email": "demo@mediai.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5sTSQ/xvCJ3jq",  # demo123
        "disabled": False,
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@mediai.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # admin123
        "disabled": False,
    },
}


def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    user = DEMO_USERS.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests

    Example:
    ```bash
    curl -X POST "http://localhost:8000/token" \\
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user info

    Requires authentication header:
    ```bash
    curl -X GET "http://localhost:8000/users/me" \\
      -H "Authorization: Bearer <your_token>"
    ```
    """
    return current_user
