"""
Kafka Producer - Learning Example
Purpose: Send prediction events to Kafka asynchronously

Learning Objectives:
1. Understand Kafka producer configuration
2. Learn async message publishing
3. Handle producer errors and retries
4. Implement basic serialization
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logging.warning(
        "kafka-python not installed. Install with: pip install kafka-python"
    )


logger = logging.getLogger(__name__)


class EventProducer:
    """
    Minimal Kafka producer for learning purposes.

    Features:
    - Async event publishing
    - Graceful fallback if Kafka unavailable
    - JSON serialization
    - Error handling
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092", enabled: bool = True):
        self.enabled = enabled and KAFKA_AVAILABLE
        self.producer: Optional[KafkaProducer] = None

        if self.enabled:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    # Learning: These configs affect reliability vs performance
                    acks="all",  # Wait for all replicas (most reliable)
                    retries=3,  # Retry failed sends
                    max_in_flight_requests_per_connection=1,  # Guarantee ordering
                    compression_type="gzip",  # Reduce network bandwidth
                )
                logger.info(f"✅ Kafka producer connected to {bootstrap_servers}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Kafka: {e}")
                self.enabled = False

    def send_prediction_event(
        self,
        prediction_type: str,
        patient_id: str,
        prediction_result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send prediction event to Kafka.

        Args:
            prediction_type: "sepsis" or "mortality"
            patient_id: Patient identifier
            prediction_result: Prediction output
            metadata: Additional context

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Kafka disabled, skipping event")
            return False

        event = {
            "event_type": f"prediction.{prediction_type}",
            "timestamp": datetime.utcnow().isoformat(),
            "patient_id": patient_id,
            "prediction": prediction_result,
            "metadata": metadata or {},
        }

        topic = f"predictions.{prediction_type}"

        try:
            # Async send with callback
            future = self.producer.send(topic, value=event)

            # Learning: Can choose to wait or fire-and-forget
            # For learning, let's wait and handle errors
            record_metadata = future.get(timeout=10)

            logger.info(
                f"✅ Event sent to Kafka: {topic} "
                f"(partition={record_metadata.partition}, "
                f"offset={record_metadata.offset})"
            )
            return True

        except KafkaError as e:
            logger.error(f"❌ Failed to send to Kafka: {e}")
            return False

    def close(self):
        """Flush and close producer."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


# Example usage for learning
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize producer
    producer = EventProducer(bootstrap_servers="localhost:9092", enabled=True)

    # Send test event
    test_prediction = {"risk_score": 0.75, "risk_level": "HIGH", "confidence": 0.92}

    success = producer.send_prediction_event(
        prediction_type="sepsis",
        patient_id="patient_12345",
        prediction_result=test_prediction,
        metadata={"model_version": "v1.0"},
    )

    print(f"Event sent: {success}")

    # Cleanup
    producer.close()
