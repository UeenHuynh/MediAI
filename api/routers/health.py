"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import redis

from core.database import get_db, test_connection
from core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Returns system status and component health
    """
    # Check database
    db_status = "healthy" if test_connection() else "unhealthy"

    # Check Redis
    redis_status = "healthy"
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception:
        redis_status = "unhealthy"

    overall_status = "healthy" if (db_status == "healthy" and redis_status == "healthy") else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        }
    }


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"alive": True}
