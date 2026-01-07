"""
Feature Flags Configuration

Purpose: Toggle experimental/learning features without code changes

Learning Features:
- ENABLE_KAFKA_STREAMING: Async event publishing to Kafka
- ENABLE_TIMESCALEDB: Time-series optimized queries
- ENABLE_DUCKDB_ANALYTICS: Local analytics with DuckDB
- ENABLE_ADVANCED_CACHING: Multi-tier Redis caching
"""

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class FeatureFlags:
    """
    Feature flags for enabling/disabling components.

    Usage:
        flags = FeatureFlags.from_env()
        if flags.enable_kafka_streaming:
            producer.send_event(...)
    """

    # Learning Features
    enable_kafka_streaming: bool = False
    enable_timescaledb: bool = False
    enable_duckdb_analytics: bool = False
    enable_advanced_caching: bool = False

    # Monitoring & Observability
    enable_prometheus_metrics: bool = False
    enable_opentelemetry_tracing: bool = False

    # Security Features
    enable_rate_limiting: bool = True
    enable_request_validation: bool = True

    # Experimental
    enable_experimental_models: bool = False

    @classmethod
    def from_env(cls) -> "FeatureFlags":
        """Load feature flags from environment variables."""
        return cls(
            # Learning features (default: disabled)
            enable_kafka_streaming=os.getenv("FEATURE_KAFKA_STREAMING", "false").lower()
            == "true",
            enable_timescaledb=os.getenv("FEATURE_TIMESCALEDB", "false").lower()
            == "true",
            enable_duckdb_analytics=os.getenv("FEATURE_DUCKDB", "false").lower()
            == "true",
            enable_advanced_caching=os.getenv(
                "FEATURE_ADVANCED_CACHING", "false"
            ).lower()
            == "true",
            # Monitoring (default: disabled in dev)
            enable_prometheus_metrics=os.getenv("FEATURE_PROMETHEUS", "false").lower()
            == "true",
            enable_opentelemetry_tracing=os.getenv("FEATURE_TRACING", "false").lower()
            == "true",
            # Security (default: enabled)
            enable_rate_limiting=os.getenv("FEATURE_RATE_LIMITING", "true").lower()
            == "true",
            enable_request_validation=os.getenv(
                "FEATURE_REQUEST_VALIDATION", "true"
            ).lower()
            == "true",
            # Experimental (default: disabled)
            enable_experimental_models=os.getenv(
                "FEATURE_EXPERIMENTAL_MODELS", "false"
            ).lower()
            == "true",
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "kafka_streaming": self.enable_kafka_streaming,
            "timescaledb": self.enable_timescaledb,
            "duckdb_analytics": self.enable_duckdb_analytics,
            "advanced_caching": self.enable_advanced_caching,
            "prometheus_metrics": self.enable_prometheus_metrics,
            "opentelemetry_tracing": self.enable_opentelemetry_tracing,
            "rate_limiting": self.enable_rate_limiting,
            "request_validation": self.enable_request_validation,
            "experimental_models": self.enable_experimental_models,
        }


# Global instance
_feature_flags: FeatureFlags = None


def get_feature_flags() -> FeatureFlags:
    """Get global feature flags instance."""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags.from_env()
    return _feature_flags


def reload_feature_flags():
    """Reload feature flags from environment (for testing)."""
    global _feature_flags
    _feature_flags = FeatureFlags.from_env()


# Example usage
if __name__ == "__main__":
    flags = get_feature_flags()
    print("Feature Flags:")
    for key, value in flags.to_dict().items():
        status = "✅ ENABLED" if value else "❌ DISABLED"
        print(f"  {key}: {status}")
