"""
Health check and metrics endpoints
"""

from datetime import datetime

import redis
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db, test_connection
from core.metrics import get_metrics

router = APIRouter()


@router.get("/health")
async def health_check(_db: Session = Depends(get_db)):
    """
    Health check endpoint
    Returns system status and component health
    """
    # Check database
    db_status = "healthy" if test_connection() else "unhealthy"

    # Check Redis (try Upstash first, then fallback)
    redis_status = "healthy"
    try:
        import os
        # Try Upstash first (production)
        upstash_url = os.getenv("UPSTASH_REDIS_URL")
        redis_url = upstash_url or settings.REDIS_URL

        r = redis.from_url(
            redis_url,
            socket_timeout=3,
            socket_connect_timeout=3
        )
        r.ping()
    except Exception:
        redis_status = "unhealthy"

    overall_status = (
        "healthy"
        if (db_status == "healthy" and redis_status == "healthy")
        else "degraded"
    )

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {"database": db_status, "redis": redis_status, "api": "healthy"},
    }


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"alive": True}


@router.get("/metrics/json")
async def json_metrics():
    """
    JSON metrics endpoint for dashboards.
    
    Returns all metrics in structured JSON format:
    - Latency: API response times (p50, p95, p99)
    - Throughput: Requests per minute
    - Cache: Hit/miss rates
    - Predictions: Count by type and risk category
    - Resources: Memory and CPU usage
    """
    return get_metrics()

