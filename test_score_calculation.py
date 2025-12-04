"""
Test clinical score calculations
"""

import sys
sys.path.append('/home/neeyuhuynh/Desktop/MediAI/apps')

from services.model_service import ModelService

service = ModelService()

# Critical patient
critical_patient = {
    "age": 75,
    "gender": "F",
    "heart_rate": 140,
    "sbp": 65,
    "dbp": 40,
    "temperature": 39.5,
    "respiratory_rate": 38,
    "spo2": 82,
    "gcs": 10,
    "wbc": 25.0,
    "lactate": 7.0,
    "creatinine": 4.0,
    "bilirubin": 3.5,
    "platelets": 60.0,
    "hemoglobin": 7.5,
    "sodium": 128.0,
    "potassium": 5.8,
    "glucose": 250.0,
    "bun": 55.0,
    "ph": 7.15,
    "pao2": 50.0,
    "paco2": 55.0,
    "bicarbonate": 15.0,
    "albumin": 2.0
}

print("=" * 80)
print("TESTING CLINICAL SCORE CALCULATIONS")
print("=" * 80)

# Prepare features to see calculated scores
import pandas as pd

features_df = service._prepare_sepsis_features(critical_patient)

print("\nCritical Patient Features:")
print("-" * 80)

# Print all features
for col in features_df.columns:
    value = features_df[col].values[0]
    print(f"{col:30} = {value}")

print("\n" + "=" * 80)
print("Key Clinical Scores:")
print("-" * 80)

print(f"SOFA Score:      {features_df['sofa_score'].values[0]:.0f}")
print(f"APACHE-II Score: {features_df['apache_ii_score'].values[0]:.0f}")
print(f"qSOFA Score:     {features_df['qsofa_score'].values[0]:.0f}")
print(f"SIRS Score:      {features_df['sirs_score'].values[0]:.0f}")
print(f"MEWS Score:      {features_df['mews_score'].values[0]:.0f}")

print("\n" + "=" * 80)
print("Expected for critical patient:")
print("-" * 80)
print("SOFA Score:      12-15 (severe)")
print("APACHE-II Score: 20-30 (severe)")
print("qSOFA Score:     2-3 (high risk)")
print("SIRS Score:      3-4 (systemic inflammation)")
print("MEWS Score:      6-8 (critical)")

print("\n✅ Test complete!")
