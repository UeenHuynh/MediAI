"""
Prediction Service with Kafka Integration (Learning Example)

Shows how to integrate Kafka producer with existing prediction service using feature flags.
"""

import logging
from typing import Any, Dict, Optional

from api.config.feature_flags import get_feature_flags

# Conditional import
try:
    from streaming.kafka_producer import EventProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    EventProducer = None

logger = logging.getLogger(__name__)


class PredictionServiceWithKafka:
    """
    Wrapper around existing prediction service with optional Kafka integration.

    Usage:
        service = PredictionServiceWithKafka(base_service)
        result = service.predict_sepsis(patient_data)
        # Automatically sends to Kafka if feature flag enabled
    """

    def __init__(self, base_prediction_service):
        """
        Initialize with base prediction service.

        Args:
            base_prediction_service: Existing prediction service (from api/services/)
        """
        self.base_service = base_prediction_service
        self.feature_flags = get_feature_flags()

        # Initialize Kafka producer if enabled
        self.kafka_producer: Optional[EventProducer] = None
        if self.feature_flags.enable_kafka_streaming and KAFKA_AVAILABLE:
            try:
                self.kafka_producer = EventProducer(
                    bootstrap_servers="kafka:9092", enabled=True  # Docker service name
                )
                logger.info("✅ Kafka producer initialized (learning mode)")
            except Exception as e:
                logger.warning(f"⚠️ Kafka unavailable, running without streaming: {e}")

    def predict_sepsis(
        self, patient_data: Dict[str, Any], patient_id: str
    ) -> Dict[str, Any]:
        """
        Predict sepsis risk with optional Kafka event publishing.

        Args:
            patient_data: Patient features
            patient_id: Patient identifier

        Returns:
            Prediction result
        """
        # 1. Get prediction from base service (always runs)
        result = self.base_service.predict_sepsis(patient_data)

        # 2. Send to Kafka if feature enabled (async, non-blocking)
        if self.kafka_producer:
            try:
                self.kafka_producer.send_prediction_event(
                    prediction_type="sepsis",
                    patient_id=patient_id,
                    prediction_result=result,
                    metadata={
                        "model_version": self.base_service.model_version,
                        "feature_count": len(patient_data),
                    },
                )
                logger.debug(f"📤 Sent sepsis prediction to Kafka: {patient_id}")
            except Exception as e:
                # Log error but don't fail the prediction
                logger.error(f"❌ Failed to send to Kafka (non-critical): {e}")

        return result

    def predict_mortality(
        self, patient_data: Dict[str, Any], patient_id: str
    ) -> Dict[str, Any]:
        """
        Predict mortality risk with optional Kafka event publishing.

        Args:
            patient_data: Patient features
            patient_id: Patient identifier

        Returns:
            Prediction result
        """
        # 1. Get prediction
        result = self.base_service.predict_mortality(patient_data)

        # 2. Send to Kafka if enabled
        if self.kafka_producer:
            try:
                self.kafka_producer.send_prediction_event(
                    prediction_type="mortality",
                    patient_id=patient_id,
                    prediction_result=result,
                    metadata={
                        "model_version": self.base_service.model_version,
                        "feature_count": len(patient_data),
                    },
                )
                logger.debug(f"📤 Sent mortality prediction to Kafka: {patient_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send to Kafka (non-critical): {e}")

        return result

    def close(self):
        """Cleanup resources."""
        if self.kafka_producer:
            self.kafka_producer.close()
            logger.info("Kafka producer closed")


# Example usage in FastAPI endpoint
"""
from fastapi import APIRouter, Depends
from api.services.prediction_service import PredictionService
from api.services.prediction_service_with_kafka import PredictionServiceWithKafka

router = APIRouter()

@router.post("/api/v1/predict/sepsis")
async def predict_sepsis(
    patient_data: PatientData,
    base_service: PredictionService = Depends(get_prediction_service)
):
    # Wrap with Kafka integration
    service = PredictionServiceWithKafka(base_service)

    result = service.predict_sepsis(
        patient_data=patient_data.dict(),
        patient_id=patient_data.patient_id
    )

    return result
"""
