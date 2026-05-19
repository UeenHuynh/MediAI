"""
Health check and metrics endpoints
"""

from datetime import datetime

import redis
from core.config import settings
from core.database import get_db, test_connection
from core.metrics import get_metrics
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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

        r = redis.from_url(redis_url, socket_timeout=3, socket_connect_timeout=3)
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


@router.get("/health/chatbot")
async def chatbot_status():
    """Debug: check chatbot initialization status"""
    import os
    result = {
        "ENABLE_CHATBOT": os.getenv("ENABLE_CHATBOT", "not set"),
        "ENABLE_CHATBOT_V2": os.getenv("ENABLE_CHATBOT_V2", "not set"),
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "not set"),
        "GROQ_API_KEY_SET": bool(os.getenv("GROQ_API_KEY")),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "not set"),
    }
    try:
        from routers.chat import get_chatbot, get_chat_rag_service
        chatbot = get_chatbot()
        result["chatbot_instance"] = type(chatbot).__name__ if chatbot else None
        result["chatbot_error"] = None
        rag = get_chat_rag_service()
        result["rag_instance"] = type(rag).__name__ if rag else None
    except Exception as e:
        result["chatbot_error"] = str(e)

    # Try a quick LLM call
    try:
        if chatbot:
            test_result = chatbot.query(
                question="test",
                retrieved_context="",
                source_docs=[],
            )
            result["llm_test"] = "ok" if not test_result.get("error") else test_result["error"]
        else:
            result["llm_test"] = "chatbot is None"
    except Exception as e:
        result["llm_test"] = f"{type(e).__name__}: {str(e)[:200]}"

    return result


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
