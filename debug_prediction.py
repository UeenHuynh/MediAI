"""
Debug script to trace prediction flow
"""

import sys

sys.path.append("/home/neeyuhuynh/Desktop/MediAI/apps")

from services.model_service import get_model_service

# Simulate form data exactly as it comes from UI
form_data = {
    "age": 65,
    "gender": "M",
    "bmi": 25.5,
    "heart_rate": 95,
    "sbp": 120,
    "dbp": 80,
    "temperature": 37.0,
    "respiratory_rate": 18,
    "spo2": 98,
    "gcs": 15,
    "wbc": 10.0,
    "lactate": 1.5,
    "creatinine": 1.0,
    "platelets": 250.0,
    "bilirubin": 0.8,
    "sodium": 140.0,
    "potassium": 4.0,
    "glucose": 100.0,
    "hemoglobin": 13.5,
    "bun": 15.0,
    "bicarbonate": None,  # Optional
    "pao2": None,
    "paco2": None,
    "ph": None,
    "albumin": None,
    "troponin": None,
    "respiratory_sofa": 0,
    "cardiovascular_sofa": 0,
    "hepatic_sofa": 0,
    "coagulation_sofa": 0,
    "renal_sofa": 0,
    "neurological_sofa": 0,
    "lactate_trend_12h": 0.0,
    "hr_trend_6h": 0.0,
    "wbc_trend_12h": 0.0,
    "sbp_trend_6h": 0.0,
    "temperature_trend_6h": 0.0,
    "rr_trend_6h": 0.0,
    "hour_of_admission": 12,
    "icu_los_so_far": 12.0,
}

print("=" * 80)
print("DEBUG: Testing Prediction Flow")
print("=" * 80)

# Get model service
print("\n1. Getting model service...")
model_service = get_model_service()
print(f"   Model loaded: {model_service.sepsis_model is not None}")
print(
    f"   Features count: {len(model_service.sepsis_features) if model_service.sepsis_features else 0}"
)

# Run prediction
print("\n2. Running prediction with form data...")
result = model_service.predict_sepsis(form_data)

print("\n3. Prediction Result:")
print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
print(f"   Has Error: {'error' in result}")

if "error" in result:
    print(f"   Error: {result['error']}")

print("\n" + "=" * 80)

# Now test with different values
print("\nTesting with HIGH RISK patient...")
high_risk_data = form_data.copy()
high_risk_data.update(
    {
        "age": 75,
        "heart_rate": 135,
        "sbp": 75,
        "temperature": 39.2,
        "respiratory_rate": 32,
        "spo2": 85,
        "gcs": 10,
        "wbc": 22.0,
        "lactate": 6.5,
        "creatinine": 3.5,
        "platelets": 80.0,
    }
)

result2 = model_service.predict_sepsis(high_risk_data)
print(f"   Risk Score: {result2.get('risk_score', 'N/A')}")
print(f"   Risk Level: {result2.get('risk_level', 'N/A')}")

print("\n" + "=" * 80)
print("✅ Debug complete!")
