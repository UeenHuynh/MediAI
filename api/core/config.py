"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/mimic_iv"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000

    # Model Configuration
    MODEL_PATH: str = "./models"
    SEPSIS_MODEL_VERSION: str = "v1"
    MORTALITY_MODEL_VERSION: str = "v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",  # Streamlit
        "http://localhost:3000",  # React (if used)
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Feature Engineering
    SEPSIS_FEATURES_COUNT: int = 42
    MORTALITY_FEATURES_COUNT: int = 65

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
