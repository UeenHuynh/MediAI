"""
Pytest configuration and fixtures
"""

import sys
from pathlib import Path

import pytest

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "api"))
sys.path.insert(0, str(project_root / "apps"))


@pytest.fixture
def sample_sepsis_features():
    """Sample sepsis features for testing"""
    return {
        "age": 65,
        "gender": "M",
        "heart_rate": 110,
        "sbp": 90,
        "dbp": 60,
        "temperature": 38.5,
        "respiratory_rate": 24,
        "spo2": 92,
        "gcs": 14,
        "wbc": 15.0,
        "lactate": 3.5,
        "creatinine": 1.8,
        "bilirubin": 1.2,
        "platelets": 120.0,
        "hemoglobin": 10.5,
        "sodium": 135.0,
        "potassium": 4.5,
        "glucose": 180.0,
        "bun": 30.0,
    }


@pytest.fixture
def sample_mortality_features():
    """Sample mortality features for testing"""
    return {
        "age": 75,
        "gender": "F",
        "worst_heart_rate": 145,
        "worst_sbp_low": 65,
        "worst_temperature_high": 39.5,
        "worst_respiratory_rate": 35,
        "worst_spo2": 82,
        "worst_gcs": 9,
        "worst_lactate": 6.5,
        "worst_creatinine": 3.8,
        "sofa_day1": 14,
        "apache_ii_score": 28,
        "vasopressor_use": True,
    }


@pytest.fixture
def low_risk_sepsis_features():
    """Low risk sepsis patient"""
    return {
        "age": 45,
        "gender": "M",
        "heart_rate": 75,
        "sbp": 120,
        "dbp": 80,
        "temperature": 37.0,
        "respiratory_rate": 16,
        "spo2": 98,
        "gcs": 15,
        "wbc": 8.0,
        "lactate": 1.0,
        "creatinine": 0.9,
        "bilirubin": 0.7,
        "platelets": 250.0,
        "hemoglobin": 14.0,
        "sodium": 140.0,
        "potassium": 4.0,
        "glucose": 100.0,
        "bun": 15.0,
    }


@pytest.fixture
def high_risk_sepsis_features():
    """High risk sepsis patient"""
    return {
        "age": 80,
        "gender": "F",
        "heart_rate": 135,
        "sbp": 75,
        "dbp": 45,
        "temperature": 39.8,
        "respiratory_rate": 32,
        "spo2": 85,
        "gcs": 10,
        "wbc": 22.0,
        "lactate": 6.0,
        "creatinine": 3.5,
        "bilirubin": 2.5,
        "platelets": 80.0,
        "hemoglobin": 8.5,
        "sodium": 128.0,
        "potassium": 5.8,
        "glucose": 250.0,
        "bun": 50.0,
    }


@pytest.fixture
def demo_user_credentials():
    """Demo user credentials for testing (password: demo123)"""
    return {
        "username": "demo",
        "password": "demo123",
        "hashed_password": "$2b$12$8Zfhb7536dY3OaHbV5RS6uefmkTUM7I3AsatOzkoHOaTHumcl71c6"
    }


@pytest.fixture
def admin_user_credentials():
    """Admin user credentials for testing (password: demo123)"""
    return {
        "username": "admin",
        "password": "demo123",
        "hashed_password": "$2b$12$8Zfhb7536dY3OaHbV5RS6uefmkTUM7I3AsatOzkoHOaTHumcl71c6"
    }
