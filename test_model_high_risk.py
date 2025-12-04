"""
Test script for high-risk sepsis patient
"""

import sys
sys.path.append('/home/neeyuhuynh/Desktop/MediAI/apps')

from services.model_service import get_model_service

# Test data - high-risk sepsis patient
high_risk_patient = {
    # Demographics
    'age': 75,
    'gender': 'F',

    # Critical vitals
    'heart_rate': 135,
    'sbp': 75,
    'dbp': 45,
    'temperature': 39.2,
    'respiratory_rate': 32,
    'spo2': 85,
    'gcs': 10,

    # Critical lab values
    'wbc': 22.0,
    'lactate': 6.5,
    'creatinine': 3.5,
    'bilirubin': 3.0,
    'platelets': 80.0,
    'hemoglobin': 8.0,
    'sodium': 128.0,
    'potassium': 5.8,
    'glucose': 250.0,
    'bun': 55.0,
    'ph': 7.15,
    'pao2': 55.0,
    'paco2': 55.0,
    'bicarbonate': 14.0,
    'albumin': 2.0
}

print("🚨 Testing High-Risk Sepsis Patient")
print("=" * 60)

model_service = get_model_service()

print("\n🔬 Running prediction on critical patient...")
result = model_service.predict_sepsis(high_risk_patient)

print("\n📊 Prediction Results:")
print("=" * 60)
print(f"Risk Score: {result.get('risk_score', 'N/A'):.2%}")
print(f"Risk Level: {result.get('risk_color', '')} {result.get('risk_level', 'N/A')}")
print(f"\n💡 Recommendation:")
print(result.get('recommendation', 'N/A'))

if 'error' in result:
    print(f"\n❌ Error: {result['error']}")
else:
    print("\n✅ Prediction successful!")

print("\n" + "=" * 60)
