"""
Configuration management using Pydantic Settings
"""

from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    # nosec B104 - Bind to all interfaces required for Docker deployment
    API_HOST: str = "0.0.0.0"  # nosec B104
    API_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5434/mimic_iv"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000

    # Model Configuration
    MODEL_PATH: str = "./models"
    SEPSIS_MODEL_VERSION: str = "v1"
    MORTALITY_MODEL_VERSION: str = "v1"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:8501",  # Streamlit
        "http://localhost:3000",  # React (if used)
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Logging
    LOG_LEVEL: str = "INFO"

    # Feature Engineering
    SEPSIS_FEATURES_COUNT: int = 42
    MORTALITY_FEATURES_COUNT: int = 65

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create global settings instance
settings = Settings()
