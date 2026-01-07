#!/usr/bin/env python3
"""
🏥 MediAI - Sepsis Prediction Model Training V2
Train LightGBM model với CSV features (42 features)

KAGGLE SETUP:
1. Upload CSV: features_sepsis_6h.csv to /kaggle/input/mediai-sepsis/
2. Enable GPU: Settings → Accelerator → GPU T4 x2
3. Run: python kaggle_sepsis_training_v2.py
4. Download: sepsis_lightgbm_v2.pkl, sepsis_feature_names_v2.pkl
"""

import json
import warnings

import joblib
import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split

warnings.filterwarnings("ignore")

print("=" * 80)
print("🏥 MediAI - Sepsis Prediction Model Training V2")
print("=" * 80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("\n📊 Loading data...")

# Kaggle path (change này nếu run local)
CSV_PATH = "/kaggle/input/mediai-sepsis/features_sepsis_6h.csv"
# Local path: CSV_PATH = 'data/sample_kaggle/features_sepsis_6h.csv'

try:
    df = pd.read_csv(CSV_PATH)
    print(f"✅ Loaded: {df.shape}")
except FileNotFoundError:
    print("⚠️  Kaggle path not found, trying local path...")
    CSV_PATH = "../../data/sample_kaggle/features_sepsis_6h.csv"
    df = pd.read_csv(CSV_PATH)
    print(f"✅ Loaded from local: {df.shape}")

# ============================================================================
# 2. PREPARE FEATURES
# ============================================================================

print("\n🔧 Preparing features...")

# Remove IDs and label
ID_COLS = ["subject_id", "hadm_id", "stay_id"]
LABEL_COL = "sepsis_label"

# Extract features (exactly 42 features from CSV)
feature_cols = [col for col in df.columns if col not in ID_COLS + [LABEL_COL]]

X = df[feature_cols].copy()
y = df[LABEL_COL].copy()

print(f"✅ Features: {len(feature_cols)}")
print(f"✅ Samples: {len(y)}")
print(f"✅ Positive rate: {y.mean():.1%}")

# Verify 42 features
assert len(feature_cols) == 42, f"Expected 42 features, got {len(feature_cols)}"

# Save feature names
feature_names = list(feature_cols)
print(f"\n📝 Feature list (first 10):")
for i, f in enumerate(feature_names[:10]):
    print(f"   {i+1}. {f}")
print(f"   ... ({len(feature_names)} total)")

# ============================================================================
# 3. TRAIN-TEST SPLIT
# ============================================================================

print("\n✂️  Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✅ Train: {X_train.shape}, Positive: {y_train.mean():.1%}")
print(f"✅ Test: {X_test.shape}, Positive: {y_test.mean():.1%}")

# ============================================================================
# 4. HANDLE CLASS IMBALANCE (SMOTE)
# ============================================================================

print("\n⚖️  Balancing classes with SMOTE...")

smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

print(
    f"✅ Before SMOTE: {len(y_train)} samples, {y_train.sum()} positive ({y_train.mean():.1%})"
)
print(
    f"✅ After SMOTE: {len(y_train_balanced)} samples, {y_train_balanced.sum()} positive ({y_train_balanced.mean():.1%})"
)

# ============================================================================
# 5. TRAIN LIGHTGBM MODEL
# ============================================================================

print("\n🚀 Training LightGBM model...")

# Hyperparameters (tuned for sepsis prediction)
params = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "max_depth": -1,
    "min_child_samples": 20,
    "reg_alpha": 0.1,
    "reg_lambda": 0.1,
    "verbose": -1,
    "device": "gpu",  # Comment this line nếu không có GPU
    "gpu_platform_id": 0,
    "gpu_device_id": 0,
}

# Create dataset (convert to numpy arrays for compatibility)
train_data = lgb.Dataset(
    (
        X_train_balanced.values
        if hasattr(X_train_balanced, "values")
        else X_train_balanced
    ),
    label=(
        y_train_balanced.values
        if hasattr(y_train_balanced, "values")
        else y_train_balanced
    ),
)
valid_data = lgb.Dataset(
    X_test.values if hasattr(X_test, "values") else X_test,
    label=y_test.values if hasattr(y_test, "values") else y_test,
    reference=train_data,
)

# Train with early stopping
print("Training... (this may take 2-5 minutes)")
model = lgb.train(
    params,
    train_data,
    num_boost_round=1000,
    valid_sets=[train_data, valid_data],
    valid_names=["train", "valid"],
    callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(period=100)],
)

print(f"✅ Training completed! Best iteration: {model.best_iteration}")

# ============================================================================
# 6. EVALUATE MODEL
# ============================================================================

print("\n📊 Evaluating model...")

# Predictions
y_pred_proba = model.predict(X_test, num_iteration=model.best_iteration)
y_pred = (y_pred_proba >= 0.5).astype(int)

# Metrics
auc = roc_auc_score(y_test, y_pred_proba)
acc = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\n{'='*60}")
print(f"📈 MODEL PERFORMANCE")
print(f"{'='*60}")
print(f"AUC-ROC:   {auc:.4f}")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"{'='*60}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"TN: {cm[0,0]}, FP: {cm[0,1]}")
print(f"FN: {cm[1,0]}, TP: {cm[1,1]}")

# Classification Report
print(f"\n{classification_report(y_test, y_pred)}")

# ============================================================================
# 7. FEATURE IMPORTANCE
# ============================================================================

print("\n🔍 Feature Importance (Top 15)...")

feature_importance = pd.DataFrame(
    {
        "feature": feature_names,
        "importance": model.feature_importance(importance_type="gain"),
    }
)
feature_importance = feature_importance.sort_values("importance", ascending=False)

print(feature_importance.head(15).to_string(index=False))

# Plot
plt.figure(figsize=(10, 8))
top_20 = feature_importance.head(20)
plt.barh(top_20["feature"], top_20["importance"])
plt.xlabel("Importance (Gain)")
plt.title("Top 20 Feature Importance - Sepsis Model V2")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("sepsis_feature_importance_v2.png", dpi=150, bbox_inches="tight")
print("✅ Saved: sepsis_feature_importance_v2.png")

# ROC Curve
plt.figure(figsize=(8, 6))
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}", linewidth=2)
plt.plot([0, 1], [0, 1], "k--", label="Random")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Sepsis Model V2")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("sepsis_roc_curve_v2.png", dpi=150, bbox_inches="tight")
print("✅ Saved: sepsis_roc_curve_v2.png")

# ============================================================================
# 8. SAVE MODEL & METADATA
# ============================================================================

print("\n💾 Saving model and metadata...")

# Save model
joblib.dump(model, "sepsis_lightgbm_v2.pkl")
print("✅ Saved: sepsis_lightgbm_v2.pkl")

# Save feature names
joblib.dump(feature_names, "sepsis_feature_names_v2.pkl")
print("✅ Saved: sepsis_feature_names_v2.pkl")

# Save feature importance
feature_importance.to_csv("sepsis_feature_importance_v2.csv", index=False)
print("✅ Saved: sepsis_feature_importance_v2.csv")

# Save metadata
metadata = {
    "model_type": "LightGBM",
    "model_version": "v2.0",
    "task": "Sepsis Prediction (6h window)",
    "num_features": len(feature_names),
    "feature_names": feature_names,
    "training_samples": len(y_train_balanced),
    "test_samples": len(y_test),
    "class_balance_method": "SMOTE",
    "metrics": {
        "auc_roc": float(auc),
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
    },
    "best_iteration": int(model.best_iteration),
    "hyperparameters": params,
}

with open("sepsis_model_metadata_v2.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("✅ Saved: sepsis_model_metadata_v2.json")

# ============================================================================
# DONE
# ============================================================================

print("\n" + "=" * 80)
print("🎉 TRAINING COMPLETED!")
print("=" * 80)
print("\n📥 Download these files from Kaggle Output:")
print("   1. sepsis_lightgbm_v2.pkl (~2-5 MB)")
print("   2. sepsis_feature_names_v2.pkl")
print("   3. sepsis_model_metadata_v2.json")
print("   4. sepsis_feature_importance_v2.csv")
print("   5. sepsis_feature_importance_v2.png")
print("   6. sepsis_roc_curve_v2.png")
print("\n🚀 Copy files to: api/models/")
print("=" * 80)
