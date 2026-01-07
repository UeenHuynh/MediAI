"""
Simplified MediAI FastAPI Application for deployment testing
"""

import logging
import os
from datetime import datetime

import psycopg2
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MediAI - ICU Risk Prediction API",
    description="REST API for sepsis and mortality risk prediction in ICU patients (Simplified)",
    version="1.0.0-simple",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MediAI API (Simplified)",
        "version": "1.0.0-simple",
        "description": "ICU Risk Prediction API",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # Check PostgreSQL
    try:
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:${POSTGRES_PASSWORD:-postgres}@postgres:5432/mimic_iv",
        )
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
        r = redis.from_url(REDIS_URL)
        r.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health check failed: %s", e)
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.get("/api/v1/data/stats")
async def get_data_stats():
    """Get database statistics"""
    try:
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:${POSTGRES_PASSWORD:-postgres}@postgres:5432/mimic_iv",
        )
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        stats = {}

        # Get row counts - table names are hardcoded, no SQL injection risk
        # nosec B608 - table names from trusted hardcoded list only
        tables = ["raw.patients", "raw.icustays", "raw.chartevents"]
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")  # nosec B608
                count = cursor.fetchone()[0]
                stats[table.replace("raw.", "")] = count
            except Exception:
                stats[table.replace("raw.", "")] = "N/A"

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error("Failed to get data stats: %s", e)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn

    # nosec B104 - Bind to all interfaces required for development/Docker
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
