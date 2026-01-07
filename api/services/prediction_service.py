"""
Prediction service handling model loading and inference
"""

import hashlib
import json
import logging
import os
import pickle
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import redis
from core.config import settings
from services.prediction_history_service import PredictionHistoryService

from models.schemas import (
    FeatureContribution,
    MortalityPredictionRequest,
    MortalityPredictionResponse,
    PredictionDetail,
    RiskLevel,
    SepsisPredictionRequest,
    SepsisPredictionResponse,
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
            # Try Upstash first (production), then fallback to REDIS_URL
            upstash_url = os.getenv("UPSTASH_REDIS_URL")
            redis_url = upstash_url or settings.REDIS_URL

            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self.redis_client.ping()
            logger.info(
                "✅ Redis connected for caching (TTL: %ss)", settings.CACHE_TTL_SECONDS
            )
        except Exception as e:
            logger.warning("Redis connection failed: %s. Caching disabled.", str(e))
            self.redis_client = None

    def _load_models(self):
        """Load ML models v2 from disk"""
        model_path = settings.MODEL_PATH
        self.feature_names = {}

        # Load sepsis model v2
        sepsis_model_file = os.path.join(model_path, "sepsis_lightgbm_v2.pkl")
        sepsis_features_file = os.path.join(model_path, "sepsis_feature_names_v2.pkl")

        if os.path.exists(sepsis_model_file):
            with open(sepsis_model_file, "rb") as f:
                self.models["sepsis"] = pickle.load(f)  # nosec B301
            if os.path.exists(sepsis_features_file):
                with open(sepsis_features_file, "rb") as f:
                    self.feature_names["sepsis"] = pickle.load(f)  # nosec B301
            logger.info("Sepsis model v2 loaded (42 features)")
        else:
            logger.warning("Sepsis model v2 not found at %s", sepsis_model_file)

        # Load mortality model v2
        mortality_model_file = os.path.join(model_path, "mortality_lightgbm_v2.pkl")
        mortality_features_file = os.path.join(
            model_path, "mortality_feature_names_v2.pkl"
        )

        if os.path.exists(mortality_model_file):
            with open(mortality_model_file, "rb") as f:
                self.models["mortality"] = pickle.load(f)  # nosec B301
            if os.path.exists(mortality_features_file):
                with open(mortality_features_file, "rb") as f:
                    self.feature_names["mortality"] = pickle.load(f)  # nosec B301
            logger.info("Mortality model v2 loaded (61 features)")
        else:
            logger.warning("Mortality model v2 not found at %s", mortality_model_file)

    def _get_cache_key(self, patient_id: str, features: Dict) -> str:
        """Generate cache key from patient_id and features"""
        features_str = json.dumps(features, sort_keys=True)
        # Use SHA256 for cache key (more secure than MD5)
        hash_str = hashlib.sha256(features_str.encode()).hexdigest()
        return f"prediction:{patient_id}:{hash_str}"

    def _get_from_cache(self, cache_key: str) -> Any:
        """Get prediction from cache"""
        if not self.redis_client:
            return None

        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info("Cache hit for key: %s", cache_key)
                return json.loads(cached)
        except Exception as e:
            logger.error("Cache read error: %s", str(e))

        return None

    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save prediction to cache"""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(
                cache_key, settings.CACHE_TTL_SECONDS, json.dumps(data)
            )
            logger.info("Cached prediction with key: %s", cache_key)
        except Exception as e:
            logger.error("Cache write error: %s", str(e))

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
            "sepsis": {
                RiskLevel.LOW: "Continue standard monitoring",
                RiskLevel.MEDIUM: "Increase monitoring frequency, consider early intervention",
                RiskLevel.HIGH: "Consider sepsis protocol, prepare for rapid response",
                RiskLevel.CRITICAL: "URGENT: Initiate sepsis protocol immediately",
            },
            "mortality": {
                RiskLevel.LOW: "Standard ICU care",
                RiskLevel.MEDIUM: "Enhanced monitoring and support",
                RiskLevel.HIGH: "Intensive care, consider escalation of therapy",
                RiskLevel.CRITICAL: "Critical condition - maximum support required",
            },
        }
        return recommendations[model_type][risk_level]

    async def predict_sepsis(
        self, request: SepsisPredictionRequest, db
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
            cached_result["metadata"]["cached"] = True
            return SepsisPredictionResponse(**cached_result)

        # Check if model is loaded
        if "sepsis" not in self.models:
            # Return dummy prediction for development
            logger.warning("Sepsis model not loaded, returning dummy prediction")
            return self._dummy_sepsis_prediction(request.patient_id)

        # Convert features to DataFrame
        features_df = pd.DataFrame([features_dict])

        # Make prediction
        model = self.models["sepsis"]
        probability = model.predict(features_df)[
            0
        ]  # LightGBM returns probability directly

        # Calculate feature importance (simplified - would use SHAP in production)
        top_features = self._get_top_features(features_df, model, "sepsis")

        # Build response
        risk_level = self._categorize_risk(probability)

        result = {
            "patient_id": request.patient_id,
            "prediction": {
                "risk_score": float(probability),
                "risk_level": risk_level,
                "recommendation": self._get_recommendation(risk_level, "sepsis"),
            },
            "top_features": top_features,
            "metadata": {
                "model_version": "v2",
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False,
            },
        }

        # Save to database if enabled
        if settings.ENABLE_DATABASE and db:
            try:
                PredictionHistoryService.save_prediction(
                    db=db,
                    prediction_type="sepsis",
                    input_features=features_dict,
                    risk_score=float(probability),
                    risk_percentage=float(probability * 100),
                    model_version="v2",
                    model_file="sepsis_lightgbm_v2.pkl",
                    shap_values=None,  # TODO: Add SHAP values
                    top_features={
                        ft["feature"]: ft["importance"] for ft in top_features
                    },
                    patient_id=None,  # TODO: Extract from request if available
                    predicted_by=None,  # TODO: Get from auth
                )
                logger.info(
                    f"Saved sepsis prediction to database for patient {request.patient_id}"
                )
            except Exception as e:
                logger.error(f"Failed to save prediction to database: {str(e)}")
                # Don't fail the request if DB save fails

        # Cache result
        self._save_to_cache(cache_key, result)

        return SepsisPredictionResponse(**result)

    async def predict_mortality(
        self, request: MortalityPredictionRequest, db
    ) -> MortalityPredictionResponse:
        """Predict mortality risk (similar structure to sepsis)"""

        # Check cache
        features_dict = request.features.dict()
        cache_key = self._get_cache_key(request.patient_id, features_dict)

        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result["metadata"]["cached"] = True
            return MortalityPredictionResponse(**cached_result)

        # Check if model is loaded
        if "mortality" not in self.models:
            logger.warning("Mortality model not loaded, returning dummy prediction")
            return self._dummy_mortality_prediction(request.patient_id)

        # Make prediction (similar to sepsis)
        features_df = pd.DataFrame([features_dict])
        model = self.models["mortality"]
        probability = model.predict(features_df)[
            0
        ]  # LightGBM returns probability directly

        top_features = self._get_top_features(features_df, model, "mortality")
        risk_level = self._categorize_risk(probability)

        result = {
            "patient_id": request.patient_id,
            "prediction": {
                "risk_score": float(probability),
                "risk_level": risk_level,
                "recommendation": self._get_recommendation(risk_level, "mortality"),
            },
            "top_features": top_features,
            "metadata": {
                "model_version": "v2",
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False,
            },
        }

        # Save to database if enabled
        if settings.ENABLE_DATABASE and db:
            try:
                PredictionHistoryService.save_prediction(
                    db=db,
                    prediction_type="mortality",
                    input_features=features_dict,
                    risk_score=float(probability),
                    risk_percentage=float(probability * 100),
                    model_version="v2",
                    model_file="mortality_lightgbm_v2.pkl",
                    shap_values=None,  # TODO: Add SHAP values
                    top_features={
                        ft["feature"]: ft["importance"] for ft in top_features
                    },
                    patient_id=None,  # TODO: Extract from request if available
                    predicted_by=None,  # TODO: Get from auth
                )
                logger.info(
                    f"Saved mortality prediction to database for patient {request.patient_id}"
                )
            except Exception as e:
                logger.error(f"Failed to save prediction to database: {str(e)}")
                # Don't fail the request if DB save fails

        self._save_to_cache(cache_key, result)
        return MortalityPredictionResponse(**result)

    def _get_top_features(self, features_df, model, model_type: str):
        """Get top contributing features (simplified version)"""
        # In production, use SHAP here
        # For now, return top features by importance

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            feature_names = features_df.columns

            top_indices = importances.argsort()[-10:][::-1]

            return [
                {
                    "feature": feature_names[i],
                    "value": float(features_df.iloc[0][feature_names[i]]),
                    "importance": float(importances[i]),
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
                recommendation="Model not loaded - this is a dummy prediction",
            ),
            top_features=[
                FeatureContribution(feature="lactate", value=2.5, importance=0.15),
                FeatureContribution(feature="heart_rate", value=110, importance=0.12),
                FeatureContribution(feature="wbc", value=15, importance=0.10),
            ],
            metadata={
                "model_version": "dummy",
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False,
            },
        )

    def _dummy_mortality_prediction(
        self, patient_id: str
    ) -> MortalityPredictionResponse:
        """Return dummy prediction when model not loaded"""
        return MortalityPredictionResponse(
            patient_id=patient_id,
            prediction=PredictionDetail(
                risk_score=0.25,
                risk_level=RiskLevel.MEDIUM,
                recommendation="Model not loaded - this is a dummy prediction",
            ),
            top_features=[
                FeatureContribution(feature="age_points", value=4, importance=0.18),
                FeatureContribution(feature="gcs_score", value=10, importance=0.14),
                FeatureContribution(
                    feature="worst_lactate_24h", value=3.2, importance=0.11
                ),
            ],
            metadata={
                "model_version": "dummy",
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False,
            },
        )
