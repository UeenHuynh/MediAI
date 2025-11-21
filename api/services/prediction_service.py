"""
Prediction service handling model loading and inference
"""

import os
import pickle
import hashlib
import logging
from typing import Dict, Any
import redis
import json
from datetime import datetime
import pandas as pd

from core.config import settings
from models.schemas import (
    SepsisPredictionRequest,
    SepsisPredictionResponse,
    MortalityPredictionRequest,
    MortalityPredictionResponse,
    PredictionDetail,
    FeatureContribution,
    RiskLevel
)

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for ML predictions with caching"""

    def __init__(self):
        self.models = {}
        self.redis_client = None
        self._init_redis()
        self._load_models()

    def _init_redis(self):
        """Initialize Redis connection for caching"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Caching disabled.")
            self.redis_client = None

    def _load_models(self):
        """Load ML models from disk"""
        model_path = settings.MODEL_PATH

        # Load sepsis model
        sepsis_model_file = os.path.join(model_path, "sepsis_model_v1.pkl")
        if os.path.exists(sepsis_model_file):
            with open(sepsis_model_file, 'rb') as f:
                self.models['sepsis'] = pickle.load(f)
            logger.info("Sepsis model loaded")
        else:
            logger.warning(f"Sepsis model not found at {sepsis_model_file}")

        # Load mortality model
        mortality_model_file = os.path.join(model_path, "mortality_model_v1.pkl")
        if os.path.exists(mortality_model_file):
            with open(mortality_model_file, 'rb') as f:
                self.models['mortality'] = pickle.load(f)
            logger.info("Mortality model loaded")
        else:
            logger.warning(f"Mortality model not found at {mortality_model_file}")

    def _get_cache_key(self, patient_id: str, features: Dict) -> str:
        """Generate cache key from patient_id and features"""
        features_str = json.dumps(features, sort_keys=True)
        hash_str = hashlib.md5(features_str.encode()).hexdigest()
        return f"prediction:{patient_id}:{hash_str}"

    def _get_from_cache(self, cache_key: str) -> Any:
        """Get prediction from cache"""
        if not self.redis_client:
            return None

        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache read error: {str(e)}")

        return None

    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save prediction to cache"""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_SECONDS,
                json.dumps(data)
            )
            logger.info(f"Cached prediction with key: {cache_key}")
        except Exception as e:
            logger.error(f"Cache write error: {str(e)}")

    def _categorize_risk(self, probability: float) -> RiskLevel:
        """Categorize risk probability into levels"""
        if probability < 0.2:
            return RiskLevel.LOW
        elif probability < 0.5:
            return RiskLevel.MEDIUM
        elif probability < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _get_recommendation(self, risk_level: RiskLevel, model_type: str) -> str:
        """Get clinical recommendation based on risk level"""
        recommendations = {
            'sepsis': {
                RiskLevel.LOW: "Continue standard monitoring",
                RiskLevel.MEDIUM: "Increase monitoring frequency, consider early intervention",
                RiskLevel.HIGH: "Consider sepsis protocol, prepare for rapid response",
                RiskLevel.CRITICAL: "URGENT: Initiate sepsis protocol immediately"
            },
            'mortality': {
                RiskLevel.LOW: "Standard ICU care",
                RiskLevel.MEDIUM: "Enhanced monitoring and support",
                RiskLevel.HIGH: "Intensive care, consider escalation of therapy",
                RiskLevel.CRITICAL: "Critical condition - maximum support required"
            }
        }
        return recommendations[model_type][risk_level]

    async def predict_sepsis(
        self,
        request: SepsisPredictionRequest,
        db
    ) -> SepsisPredictionResponse:
        """
        Predict sepsis risk

        Args:
            request: Prediction request with patient features
            db: Database session

        Returns:
            Prediction response with risk score and explanations
        """
        # Check cache
        features_dict = request.features.dict()
        cache_key = self._get_cache_key(request.patient_id, features_dict)

        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result['metadata']['cached'] = True
            return SepsisPredictionResponse(**cached_result)

        # Check if model is loaded
        if 'sepsis' not in self.models:
            # Return dummy prediction for development
            logger.warning("Sepsis model not loaded, returning dummy prediction")
            return self._dummy_sepsis_prediction(request.patient_id)

        # Convert features to DataFrame
        features_df = pd.DataFrame([features_dict])

        # Make prediction
        model = self.models['sepsis']
        probability = model.predict_proba(features_df)[0][1]

        # Calculate feature importance (simplified - would use SHAP in production)
        top_features = self._get_top_features(features_df, model, 'sepsis')

        # Build response
        risk_level = self._categorize_risk(probability)

        result = {
            'patient_id': request.patient_id,
            'prediction': {
                'risk_score': float(probability),
                'risk_level': risk_level,
                'recommendation': self._get_recommendation(risk_level, 'sepsis')
            },
            'top_features': top_features,
            'metadata': {
                'model_version': 'v1',
                'timestamp': datetime.utcnow().isoformat(),
                'cached': False
            }
        }

        # Cache result
        self._save_to_cache(cache_key, result)

        return SepsisPredictionResponse(**result)

    async def predict_mortality(
        self,
        request: MortalityPredictionRequest,
        db
    ) -> MortalityPredictionResponse:
        """Predict mortality risk (similar structure to sepsis)"""

        # Check cache
        features_dict = request.features.dict()
        cache_key = self._get_cache_key(request.patient_id, features_dict)

        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result['metadata']['cached'] = True
            return MortalityPredictionResponse(**cached_result)

        # Check if model is loaded
        if 'mortality' not in self.models:
            logger.warning("Mortality model not loaded, returning dummy prediction")
            return self._dummy_mortality_prediction(request.patient_id)

        # Make prediction (similar to sepsis)
        features_df = pd.DataFrame([features_dict])
        model = self.models['mortality']
        probability = model.predict_proba(features_df)[0][1]

        top_features = self._get_top_features(features_df, model, 'mortality')
        risk_level = self._categorize_risk(probability)

        result = {
            'patient_id': request.patient_id,
            'prediction': {
                'risk_score': float(probability),
                'risk_level': risk_level,
                'recommendation': self._get_recommendation(risk_level, 'mortality')
            },
            'top_features': top_features,
            'metadata': {
                'model_version': 'v1',
                'timestamp': datetime.utcnow().isoformat(),
                'cached': False
            }
        }

        self._save_to_cache(cache_key, result)
        return MortalityPredictionResponse(**result)

    def _get_top_features(self, features_df, model, model_type: str):
        """Get top contributing features (simplified version)"""
        # In production, use SHAP here
        # For now, return top features by importance

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = features_df.columns

            top_indices = importances.argsort()[-10:][::-1]

            return [
                {
                    'feature': feature_names[i],
                    'value': float(features_df.iloc[0][feature_names[i]]),
                    'importance': float(importances[i])
                }
                for i in top_indices
            ]

        return []

    def _dummy_sepsis_prediction(self, patient_id: str) -> SepsisPredictionResponse:
        """Return dummy prediction when model not loaded"""
        return SepsisPredictionResponse(
            patient_id=patient_id,
            prediction=PredictionDetail(
                risk_score=0.45,
                risk_level=RiskLevel.MEDIUM,
                recommendation="Model not loaded - this is a dummy prediction"
            ),
            top_features=[
                FeatureContribution(feature="lactate", value=2.5, importance=0.15),
                FeatureContribution(feature="heart_rate", value=110, importance=0.12),
                FeatureContribution(feature="wbc", value=15, importance=0.10)
            ],
            metadata={
                'model_version': 'dummy',
                'timestamp': datetime.utcnow().isoformat(),
                'cached': False
            }
        )

    def _dummy_mortality_prediction(self, patient_id: str) -> MortalityPredictionResponse:
        """Return dummy prediction when model not loaded"""
        return MortalityPredictionResponse(
            patient_id=patient_id,
            prediction=PredictionDetail(
                risk_score=0.25,
                risk_level=RiskLevel.MEDIUM,
                recommendation="Model not loaded - this is a dummy prediction"
            ),
            top_features=[
                FeatureContribution(feature="age_points", value=4, importance=0.18),
                FeatureContribution(feature="gcs_score", value=10, importance=0.14),
                FeatureContribution(feature="worst_lactate_24h", value=3.2, importance=0.11)
            ],
            metadata={
                'model_version': 'dummy',
                'timestamp': datetime.utcnow().isoformat(),
                'cached': False
            }
        )
