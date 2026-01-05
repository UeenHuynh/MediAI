"""
Kafka Consumer - Learning Example
Purpose: Consume prediction events and save to database

Learning Objectives:
1. Understand consumer groups and offset management
2. Learn message processing patterns
3. Handle deserialization
4. Implement idempotent processing
"""

import json
import logging
import signal
import sys
from typing import Dict, Any
from datetime import datetime

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logging.warning("kafka-python not installed")

import psycopg2
from psycopg2.extras import Json


logger = logging.getLogger(__name__)


class PredictionEventConsumer:
    """
    Simple Kafka consumer for learning.

    Features:
    - Consumes prediction events
    - Saves to PostgreSQL
    - Handles graceful shutdown
    - Basic error handling
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        postgres_url: str = "postgresql://postgres:postgres123@localhost:5434/mimic_iv",
        group_id: str = "prediction-processor"
    ):
        self.running = False

        # Kafka consumer
        if KAFKA_AVAILABLE:
            self.consumer = KafkaConsumer(
                'predictions.sepsis',
                'predictions.mortality',
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                # Learning: These configs affect delivery guarantees
                auto_offset_reset='earliest',  # Start from beginning if no offset
                enable_auto_commit=False,      # Manual commit for at-least-once delivery
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000,      # Poll timeout
            )
            logger.info(f"✅ Kafka consumer connected (group: {group_id})")
        else:
            raise RuntimeError("kafka-python not available")

        # Database connection
        self.db_conn = psycopg2.connect(postgres_url)
        self.db_cursor = self.db_conn.cursor()
        logger.info("✅ Database connected")

        # Create events table if not exists
        self._create_events_table()

        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

    def _create_events_table(self):
        """Create table to store events."""
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                patient_id VARCHAR(100) NOT NULL,
                prediction JSONB NOT NULL,
                metadata JSONB,
                event_timestamp TIMESTAMPTZ NOT NULL,
                processed_at TIMESTAMPTZ DEFAULT NOW(),
                kafka_partition INTEGER,
                kafka_offset BIGINT,
                UNIQUE(event_type, patient_id, kafka_partition, kafka_offset)
            );

            CREATE INDEX IF NOT EXISTS idx_prediction_events_patient
            ON prediction_events(patient_id);

            CREATE INDEX IF NOT EXISTS idx_prediction_events_timestamp
            ON prediction_events(event_timestamp DESC);
        """)
        self.db_conn.commit()
        logger.info("✅ Events table ready")

    def _process_event(self, message) -> bool:
        """
        Process a single event.

        Args:
            message: Kafka message

        Returns:
            True if processed successfully
        """
        try:
            event = message.value
            logger.info(f"📥 Processing: {event['event_type']} for {event['patient_id']}")

            # Save to database (idempotent: unique constraint prevents duplicates)
            self.db_cursor.execute("""
                INSERT INTO prediction_events (
                    event_type, patient_id, prediction, metadata,
                    event_timestamp, kafka_partition, kafka_offset
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_type, patient_id, kafka_partition, kafka_offset)
                DO NOTHING
            """, (
                event['event_type'],
                event['patient_id'],
                Json(event['prediction']),
                Json(event.get('metadata', {})),
                event['timestamp'],
                message.partition,
                message.offset
            ))

            self.db_conn.commit()

            logger.info(
                f"✅ Saved: partition={message.partition}, "
                f"offset={message.offset}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error processing event: {e}")
            self.db_conn.rollback()
            return False

    def start(self):
        """Start consuming events."""
        self.running = True
        logger.info("🚀 Starting consumer loop...")

        try:
            for message in self.consumer:
                if not self.running:
                    break

                # Process event
                success = self._process_event(message)

                # Commit offset only if successful
                if success:
                    self.consumer.commit()

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown."""
        logger.info("🛑 Shutting down...")
        self.running = False

        if hasattr(self, 'consumer'):
            self.consumer.close()
            logger.info("Kafka consumer closed")

        if hasattr(self, 'db_conn'):
            self.db_cursor.close()
            self.db_conn.close()
            logger.info("Database connection closed")

    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}")
        self.shutdown()
        sys.exit(0)


# Run consumer
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    consumer = PredictionEventConsumer(
        bootstrap_servers="localhost:9092",
        postgres_url="postgresql://postgres:postgres123@localhost:5434/mimic_iv",
        group_id="prediction-processor-learning"
    )

    consumer.start()
