"""
Test script for sepsis model prediction
"""

import sys
sys.path.append('/home/neeyuhuynh/Desktop/MediAI/apps')

from services.model_service import get_model_service

# Test data - a typical ICU patient
test_patient = {
    # Demographics
    'age': 65,
    'gender': 'M',

    # Vitals
    'heart_rate': 110,
    'sbp': 85,
    'dbp': 50,
    'temperature': 38.5,
    'respiratory_rate': 28,
    'spo2': 92,
    'gcs': 13,

    # Lab values
    'wbc': 15.0,
    'lactate': 3.5,
    'creatinine': 2.0,
    'bilirubin': 1.5,
    'platelets': 120.0,
    'hemoglobin': 10.0,
    'sodium': 135.0,
    'potassium': 4.5,
    'glucose': 180.0,
    'bun': 35.0,
    'ph': 7.30,
    'pao2': 75.0,
    'paco2': 45.0,
    'bicarbonate': 18.0,
    'albumin': 2.8
}

print("🧪 Testing Sepsis Model Prediction")
print("=" * 60)

# Get model service
model_service = get_model_service()

print(f"\n✅ Model loaded: {model_service.sepsis_model is not None}")
print(f"✅ Features count: {len(model_service.sepsis_features) if model_service.sepsis_features else 0}")

# Run prediction
print("\n🔬 Running prediction...")
result = model_service.predict_sepsis(test_patient)

print("\n📊 Prediction Results:")
print("=" * 60)
print(f"Risk Score: {result.get('risk_score', 'N/A'):.2%}")
print(f"Risk Level: {result.get('risk_color', '')} {result.get('risk_level', 'N/A')}")
print(f"Model Version: {result.get('model_version', 'N/A')}")
print(f"Features Used: {result.get('features_used', 'N/A')}")
print(f"\n💡 Recommendation:")
print(result.get('recommendation', 'N/A'))

if 'error' in result:
    print(f"\n❌ Error: {result['error']}")
else:
    print("\n✅ Prediction successful!")

print("\n" + "=" * 60)
