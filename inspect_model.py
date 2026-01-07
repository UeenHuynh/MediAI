"""
Inspect model details and prediction output
"""

import sys

sys.path.append("/home/neeyuhuynh/Desktop/MediAI/apps")

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

# Load model
models_dir = Path("/home/neeyuhuynh/Desktop/MediAI/models")
model_path = models_dir / "sepsis_lightgbm_v1.pkl"

with open(model_path, "rb") as f:
    model = pickle.load(f)

print("=" * 80)
print("MODEL INSPECTION")
print("=" * 80)

print(f"\nModel type: {type(model)}")
print(f"Model class: {model.__class__.__name__}")

# Check if it's a LightGBM Booster
if hasattr(model, "num_trees"):
    print(f"Number of trees: {model.num_trees()}")

if hasattr(model, "num_feature"):
    print(f"Number of features: {model.num_feature()}")

# Check prediction methods
print(f"\nAvailable methods:")
methods = [m for m in dir(model) if not m.startswith("_") and "predict" in m.lower()]
for method in methods:
    print(f"  - {method}")

# Test prediction with simple data
print("\n" + "=" * 80)
print("TESTING PREDICTIONS")
print("=" * 80)

# Load feature names
with open(models_dir / "sepsis_feature_names.pkl", "rb") as f:
    feature_names = pickle.load(f)

print(f"\nFeatures expected: {len(feature_names)}")
print(f"Feature names: {feature_names[:10]}...")

# Create test data - all normal values
normal_data = {
    "age": 65,
    "gender": 0,
    "heart_rate": 80,
    "sbp": 120,
    "dbp": 80,
    "map": 93.33,
    "temperature": 37.0,
    "respiratory_rate": 16,
    "spo2": 98,
    "gcs": 15,
    "wbc": 8.0,
    "lactate": 1.0,
    "creatinine": 1.0,
    "bilirubin": 0.8,
    "platelets": 250.0,
    "hemoglobin": 13.5,
    "sodium": 140.0,
    "potassium": 4.0,
    "glucose": 100.0,
    "bun": 15.0,
    "ph": 7.4,
    "pao2": 95.0,
    "paco2": 40.0,
    "bicarbonate": 24.0,
    "albumin": 4.0,
    "sofa_score": 0,
    "apache_ii_score": 5,
    "qsofa_score": 0,
    "sirs_score": 0,
    "mews_score": 0,
    "shock_index": 0.67,
    "pulse_pressure": 40,
    "pf_ratio": 452,
    "anion_gap": 6,
    "bun_creatinine_ratio": 15,
    "lactate_albumin_ratio": 0.25,
    "is_hypotensive": 0,
    "is_tachycardic": 0,
    "is_tachypneic": 0,
    "is_hypoxic": 0,
    "has_aki": 0,
    "has_thrombocytopenia": 0,
}

# Create critical patient
critical_data = normal_data.copy()
critical_data.update(
    {
        "age": 75,
        "lactate": 7.0,
        "sbp": 65,
        "map": 51.67,
        "heart_rate": 140,
        "temperature": 39.5,
        "respiratory_rate": 38,
        "spo2": 82,
        "gcs": 10,
        "wbc": 25.0,
        "creatinine": 4.0,
        "bilirubin": 3.5,
        "platelets": 60.0,
        "sofa_score": 12,
        "apache_ii_score": 25,
        "qsofa_score": 3,
        "sirs_score": 4,
        "shock_index": 2.15,
        "is_hypotensive": 1,
        "is_tachycardic": 1,
        "is_tachypneic": 1,
        "is_hypoxic": 1,
        "has_aki": 1,
        "has_thrombocytopenia": 1,
    }
)

df_normal = pd.DataFrame([normal_data])[feature_names]
df_critical = pd.DataFrame([critical_data])[feature_names]

print("\n--- Test 1: Normal patient ---")
pred_normal = model.predict(df_normal)
print(f"Raw output: {pred_normal}")
print(
    f"Type: {type(pred_normal)}, Shape: {pred_normal.shape if hasattr(pred_normal, 'shape') else 'N/A'}"
)
print(f"Value: {pred_normal[0]}")

print("\n--- Test 2: Critical patient ---")
pred_critical = model.predict(df_critical)
print(f"Raw output: {pred_critical}")
print(f"Value: {pred_critical[0]}")

# Try predict_proba if available
if hasattr(model, "predict_proba"):
    print("\n--- Testing predict_proba ---")
    proba_normal = model.predict_proba(df_normal)
    print(f"Normal proba: {proba_normal}")

    proba_critical = model.predict_proba(df_critical)
    print(f"Critical proba: {proba_critical}")

print("\n" + "=" * 80)
print("✅ Inspection complete!")
