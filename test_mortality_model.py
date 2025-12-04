"""
Test mortality model
"""

import sys
sys.path.append('/home/neeyuhuynh/Desktop/MediAI/apps')

from services.model_service import get_model_service

model_service = get_model_service()

print("=" * 80)
print("TESTING MORTALITY MODEL")
print("=" * 80)

# Test 1: Low risk patient
low_risk = {
    "age": 45,
    "gender": "M",
    "worst_heart_rate": 90,
    "worst_sbp_low": 110,
    "worst_temperature_high": 37.5,
    "worst_respiratory_rate": 18,
    "worst_spo2": 97,
    "worst_gcs": 15,
    "worst_lactate": 1.5,
    "worst_creatinine": 1.0,
    "sofa_day1": 2,
    "apache_ii_score": 8,
    "vasopressor_use": False
}

print("\n1. LOW RISK PATIENT:")
result = model_service.predict_mortality(low_risk)
print(f"   Risk Score: {result['risk_score']:.2%}")
print(f"   Risk Level: {result['risk_color']} {result['risk_level']}")
print(f"   Recommendation: {result['recommendation'][:80]}...")

# Test 2: High risk patient
high_risk = {
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
    "vasopressor_use": True
}

print("\n2. HIGH RISK PATIENT:")
result = model_service.predict_mortality(high_risk)
print(f"   Risk Score: {result['risk_score']:.2%}")
print(f"   Risk Level: {result['risk_color']} {result['risk_level']}")
print(f"   Recommendation: {result['recommendation'][:80]}...")

# Test 3: Medium risk
medium_risk = {
    "age": 65,
    "gender": "M",
    "worst_heart_rate": 120,
    "worst_sbp_low": 85,
    "worst_temperature_high": 38.5,
    "worst_respiratory_rate": 28,
    "worst_spo2": 90,
    "worst_gcs": 12,
    "worst_lactate": 3.5,
    "worst_creatinine": 2.2,
    "sofa_day1": 8,
    "apache_ii_score": 18,
    "vasopressor_use": False
}

print("\n3. MEDIUM RISK PATIENT:")
result = model_service.predict_mortality(medium_risk)
print(f"   Risk Score: {result['risk_score']:.2%}")
print(f"   Risk Level: {result['risk_color']} {result['risk_level']}")
print(f"   Recommendation: {result['recommendation'][:80]}...")

print("\n" + "=" * 80)
print("✅ Mortality model test complete!")
