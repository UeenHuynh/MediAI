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

    # Data Source Configuration
    DATA_SOURCE: str = "csv"  # Options: "csv", "database"
    CSV_DATA_PATH: str = "./data/sample_kaggle"

    # Feature Flags
    ENABLE_DATABASE: bool = False
    ENABLE_PREDICTIONS: bool = True
    ENABLE_CHATBOT: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000

    # Qdrant Configuration
    QDRANT_URL: str = ""  # e.g., https://xyz.cloud.qdrant.io
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "medical_knowledge"

    # Model Configuration
    MODEL_PATH: str = "./models"
    SEPSIS_MODEL_VERSION: str = "v2"
    MORTALITY_MODEL_VERSION: str = "v2"
    SEPSIS_MODEL_FILE: str = "sepsis_lightgbm_v2.pkl"
    SEPSIS_FEATURES_FILE: str = "sepsis_feature_names_v2.pkl"
    MORTALITY_MODEL_FILE: str = "mortality_lightgbm_v2.pkl"
    MORTALITY_FEATURES_FILE: str = "mortality_feature_names_v2.pkl"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:8501",  # Streamlit local
        "http://localhost:3000",  # React local
        "https://*.vercel.app",  # Vercel deployments
        "https://*.onrender.com",  # Render deployments
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
    MORTALITY_FEATURES_COUNT: int = 61

    class Config:
        # Look for .env in parent directory (project root)
        from pathlib import Path

        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create global settings instance
settings = Settings()
