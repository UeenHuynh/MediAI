"""
Model Service
Load and run predictions with local ML models
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List


class ModelService:
    """Service for loading and running ML models"""

    def __init__(self):
        # Try multiple paths for models directory
        possible_paths = [
            Path("/models"),  # Docker mount path
            Path(__file__).parent.parent.parent / "models",  # Local path
        ]

        self.models_dir = None
        for path in possible_paths:
            if path.exists():
                self.models_dir = path
                break

        if self.models_dir is None:
            print("❌ Models directory not found!")

        self.sepsis_model = None
        self.sepsis_features = None
        self.mortality_model = None
        self.mortality_features = None
        self._load_sepsis_model()
        self._load_mortality_model()

    def _load_sepsis_model(self):
        """Load sepsis prediction model"""
        try:
            model_path = self.models_dir / "sepsis_lightgbm_v1.pkl"
            features_path = self.models_dir / "sepsis_feature_names.pkl"

            with open(model_path, 'rb') as f:
                self.sepsis_model = pickle.load(f)

            with open(features_path, 'rb') as f:
                self.sepsis_features = pickle.load(f)

            print(f"✅ Sepsis model loaded with {len(self.sepsis_features)} features")
        except Exception as e:
            print(f"❌ Failed to load sepsis model: {e}")
            self.sepsis_model = None
            self.sepsis_features = None

    def _load_mortality_model(self):
        """Load mortality prediction model"""
        try:
            model_path = self.models_dir / "mortality_lightgbm_v1.pkl"
            features_path = self.models_dir / "mortality_feature_names.pkl"

            with open(model_path, 'rb') as f:
                self.mortality_model = pickle.load(f)

            with open(features_path, 'rb') as f:
                self.mortality_features = pickle.load(f)

            print(f"✅ Mortality model loaded with {len(self.mortality_features)} features")
        except Exception as e:
            print(f"❌ Failed to load mortality model: {e}")
            self.mortality_model = None
            self.mortality_features = None

    def predict_sepsis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict sepsis risk from input data

        Args:
            input_data: Dictionary with patient features

        Returns:
            Dictionary with prediction results
        """
        print(f"🔬 predict_sepsis called with {len(input_data)} features")

        if self.sepsis_model is None:
            print("❌ Model not loaded")
            return {
                "error": "Model not loaded",
                "risk_score": 0.5,
                "risk_level": "Unknown",
                "recommendation": "Model unavailable - using mock prediction"
            }

        try:
            # Prepare features
            print("📊 Preparing features...")
            features_df = self._prepare_sepsis_features(input_data)
            print(f"✅ Features prepared: {features_df.shape}")

            # Predict
            print("🤖 Running model prediction...")
            pred_proba = self.sepsis_model.predict(features_df)[0]
            print(f"✅ Prediction: {pred_proba:.4f}")

            # Determine risk level
            if pred_proba < 0.3:
                risk_level = "Low"
                color = "🟢"
            elif pred_proba < 0.6:
                risk_level = "Medium"
                color = "🟡"
            elif pred_proba < 0.8:
                risk_level = "High"
                color = "🟠"
            else:
                risk_level = "Critical"
                color = "🔴"

            # Generate recommendation
            recommendation = self._generate_recommendation(pred_proba, risk_level)

            return {
                "risk_score": float(pred_proba),
                "risk_level": risk_level,
                "risk_color": color,
                "recommendation": recommendation,
                "model_version": "sepsis_lightgbm_v1",
                "features_used": len(self.sepsis_features)
            }

        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return {
                "error": str(e),
                "risk_score": 0.5,
                "risk_level": "Unknown",
                "recommendation": "Error during prediction"
            }

    def _prepare_sepsis_features(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for model prediction"""

        # Calculate derived features
        features = {}

        # Basic demographics
        features['age'] = input_data.get('age', 65)
        features['gender'] = 1 if input_data.get('gender', 'M') == 'M' else 0

        # Vital signs
        features['heart_rate'] = input_data.get('heart_rate', 90)
        features['sbp'] = input_data.get('sbp', 120)
        features['dbp'] = input_data.get('dbp', 80)
        features['temperature'] = input_data.get('temperature', 37.0)
        features['respiratory_rate'] = input_data.get('respiratory_rate', 18)
        features['spo2'] = input_data.get('spo2', 98)
        features['gcs'] = input_data.get('gcs', 15)

        # Lab values
        features['wbc'] = input_data.get('wbc', 10.0)
        features['lactate'] = input_data.get('lactate', 1.5)
        features['creatinine'] = input_data.get('creatinine', 1.0)
        features['bilirubin'] = input_data.get('bilirubin', 0.8)
        features['platelets'] = input_data.get('platelets', 250.0)
        features['hemoglobin'] = input_data.get('hemoglobin', 13.5)
        features['sodium'] = input_data.get('sodium', 140.0)
        features['potassium'] = input_data.get('potassium', 4.0)
        features['glucose'] = input_data.get('glucose', 100.0)
        features['bun'] = input_data.get('bun', 15.0)

        # Optional lab values - handle None
        features['ph'] = input_data.get('ph') or 7.4
        features['pao2'] = input_data.get('pao2') or 90.0
        features['paco2'] = input_data.get('paco2') or 40.0
        features['bicarbonate'] = input_data.get('bicarbonate') or 24.0
        features['albumin'] = input_data.get('albumin') or 4.0

        # Calculate MAP
        features['map'] = features['dbp'] + (features['sbp'] - features['dbp']) / 3

        # Calculate clinical scores (simplified)
        features['sofa_score'] = self._calculate_sofa_simple(features)
        features['apache_ii_score'] = self._calculate_apache_simple(features)
        features['qsofa_score'] = self._calculate_qsofa(features)
        features['sirs_score'] = self._calculate_sirs(features)
        features['mews_score'] = self._calculate_mews(features)

        # Derived metrics
        features['shock_index'] = features['heart_rate'] / features['sbp'] if features['sbp'] > 0 else 0
        features['pulse_pressure'] = features['sbp'] - features['dbp']
        features['pf_ratio'] = (features['pao2'] / 0.21) if features['spo2'] > 90 else 200  # Simplified
        features['anion_gap'] = features['sodium'] - (110 + features['bicarbonate'])  # Simplified
        features['bun_creatinine_ratio'] = features['bun'] / features['creatinine'] if features['creatinine'] > 0 else 15
        features['lactate_albumin_ratio'] = features['lactate'] / features['albumin'] if features['albumin'] > 0 else 0.5

        # Boolean features
        features['is_hypotensive'] = 1 if features['sbp'] < 90 else 0
        features['is_tachycardic'] = 1 if features['heart_rate'] > 100 else 0
        features['is_tachypneic'] = 1 if features['respiratory_rate'] > 20 else 0
        features['is_hypoxic'] = 1 if features['spo2'] < 90 else 0
        features['has_aki'] = 1 if features['creatinine'] > 1.5 else 0
        features['has_thrombocytopenia'] = 1 if features['platelets'] < 150 else 0

        # Create DataFrame with correct feature order
        df = pd.DataFrame([features])
        df = df[self.sepsis_features]  # Ensure correct order

        return df

    def _calculate_sofa_simple(self, features: Dict) -> float:
        """Simplified SOFA score calculation"""
        score = 0
        # Respiratory
        if features['pao2'] < 400: score += 1
        if features['pao2'] < 300: score += 1
        # Cardiovascular
        if features['map'] < 70: score += 1
        # Renal
        if features['creatinine'] > 1.2: score += 1
        if features['creatinine'] > 2.0: score += 1
        # Coagulation
        if features['platelets'] < 150: score += 1
        if features['platelets'] < 100: score += 1
        return min(score, 24)  # Max 24

    def _calculate_apache_simple(self, features: Dict) -> float:
        """Simplified APACHE-II calculation"""
        score = 0
        # Age
        if features['age'] > 65: score += 5
        elif features['age'] > 55: score += 3
        # Vital signs
        if features['heart_rate'] > 110 or features['heart_rate'] < 55: score += 3
        if features['map'] < 70 or features['map'] > 110: score += 3
        if features['temperature'] > 38.5 or features['temperature'] < 36: score += 2
        if features['respiratory_rate'] > 24: score += 2
        # Labs
        if features['sodium'] < 130 or features['sodium'] > 150: score += 2
        if features['potassium'] < 3.0 or features['potassium'] > 5.5: score += 2
        if features['creatinine'] > 1.5: score += 2
        return min(score, 71)  # Max 71

    def _calculate_qsofa(self, features: Dict) -> int:
        """Calculate qSOFA score"""
        score = 0
        if features['respiratory_rate'] >= 22: score += 1
        if features['sbp'] <= 100: score += 1
        if features['gcs'] < 15: score += 1
        return score

    def _calculate_sirs(self, features: Dict) -> int:
        """Calculate SIRS criteria"""
        score = 0
        if features['temperature'] > 38 or features['temperature'] < 36: score += 1
        if features['heart_rate'] > 90: score += 1
        if features['respiratory_rate'] > 20: score += 1
        if features['wbc'] > 12 or features['wbc'] < 4: score += 1
        return score

    def _calculate_mews(self, features: Dict) -> int:
        """Calculate MEWS score"""
        score = 0
        # Respiratory rate
        if features['respiratory_rate'] >= 30: score += 3
        elif features['respiratory_rate'] >= 21: score += 2
        elif features['respiratory_rate'] <= 8: score += 2
        # Heart rate
        if features['heart_rate'] >= 130: score += 3
        elif features['heart_rate'] >= 111: score += 2
        elif features['heart_rate'] <= 40: score += 2
        # SBP
        if features['sbp'] <= 70: score += 3
        elif features['sbp'] <= 80: score += 2
        elif features['sbp'] >= 200: score += 2
        return score

    def _generate_recommendation(self, risk_score: float, risk_level: str) -> str:
        """Generate clinical recommendation"""
        if risk_level == "Critical":
            return "🚨 URGENT: High sepsis risk detected. Immediate intervention required. Consider sepsis bundle: blood cultures, broad-spectrum antibiotics, fluid resuscitation."
        elif risk_level == "High":
            return "⚠️ WARNING: Elevated sepsis risk. Close monitoring and early intervention recommended. Consider repeat lactate, frequent vitals."
        elif risk_level == "Medium":
            return "⚡ CAUTION: Moderate sepsis risk. Monitor closely for deterioration. Consider trending labs and vital signs."
        else:
            return "✅ Low sepsis risk. Continue routine monitoring. Reassess if clinical status changes."

    def predict_mortality(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict mortality risk from input data

        Args:
            input_data: Dictionary with patient features (13 features)

        Returns:
            Dictionary with prediction results
        """
        print(f"💀 predict_mortality called with {len(input_data)} features")

        if self.mortality_model is None:
            print("❌ Mortality model not loaded")
            return {
                "error": "Model not loaded",
                "risk_score": 0.5,
                "risk_level": "Unknown",
                "recommendation": "Model unavailable - using mock prediction"
            }

        try:
            # Prepare features
            print("📊 Preparing mortality features...")
            features_df = self._prepare_mortality_features(input_data)
            print(f"✅ Features prepared: {features_df.shape}")

            # Predict
            print("🤖 Running mortality prediction...")
            pred_proba = self.mortality_model.predict(features_df)[0]
            print(f"✅ Prediction: {pred_proba:.4f}")

            # Determine risk level
            if pred_proba < 0.2:
                risk_level = "Low"
                color = "🟢"
            elif pred_proba < 0.5:
                risk_level = "Medium"
                color = "🟡"
            elif pred_proba < 0.75:
                risk_level = "High"
                color = "🟠"
            else:
                risk_level = "Critical"
                color = "🔴"

            # Generate recommendation
            recommendation = self._generate_mortality_recommendation(pred_proba, risk_level)

            return {
                "risk_score": float(pred_proba),
                "risk_level": risk_level,
                "risk_color": color,
                "recommendation": recommendation,
                "model_version": "mortality_lightgbm_v1",
                "features_used": len(self.mortality_features)
            }

        except Exception as e:
            print(f"❌ Mortality prediction error: {e}")
            return {
                "error": str(e),
                "risk_score": 0.5,
                "risk_level": "Unknown",
                "recommendation": "Error during prediction"
            }

    def _prepare_mortality_features(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for mortality prediction (13 features)"""

        features = {}

        # Demographics
        features['age'] = input_data.get('age', 65)
        features['gender'] = 1 if input_data.get('gender', 'M') == 'M' else 0

        # Worst vitals/labs in first 24h
        features['worst_heart_rate'] = input_data.get('worst_heart_rate', 100)
        features['worst_sbp_low'] = input_data.get('worst_sbp_low', 100)
        features['worst_temperature_high'] = input_data.get('worst_temperature_high', 37.5)
        features['worst_respiratory_rate'] = input_data.get('worst_respiratory_rate', 20)
        features['worst_spo2'] = input_data.get('worst_spo2', 95)
        features['worst_gcs'] = input_data.get('worst_gcs', 14)
        features['worst_lactate'] = input_data.get('worst_lactate', 2.0)
        features['worst_creatinine'] = input_data.get('worst_creatinine', 1.2)

        # Clinical scores
        features['sofa_day1'] = input_data.get('sofa_day1', 3)
        features['apache_ii_score'] = input_data.get('apache_ii_score', 10)

        # Interventions
        features['vasopressor_use'] = 1 if input_data.get('vasopressor_use', False) else 0

        # Create DataFrame with correct feature order
        df = pd.DataFrame([features])
        df = df[self.mortality_features]  # Ensure correct order

        return df

    def _generate_mortality_recommendation(self, risk_score: float, risk_level: str) -> str:
        """Generate mortality risk recommendation"""
        if risk_level == "Critical":
            return "🚨 CRITICAL: Very high mortality risk (>75%). Intensive monitoring and aggressive treatment required. Consider ICU escalation, family discussion."
        elif risk_level == "High":
            return "⚠️ HIGH RISK: Significant mortality risk (50-75%). Close monitoring essential. Review treatment goals and escalation plans."
        elif risk_level == "Medium":
            return "⚡ MODERATE RISK: Moderate mortality risk (20-50%). Continue current treatment. Monitor for deterioration."
        else:
            return "✅ LOW RISK: Low mortality risk (<20%). Continue routine ICU care. Reassess regularly."


# Global instance
_model_service = None

def get_model_service() -> ModelService:
    """Get or create model service instance"""
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service
