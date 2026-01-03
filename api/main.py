"""
MediAI FastAPI Application
Main entry point for the REST API serving ML predictions
"""

import logging
import time
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import auth, health, predictions, doctors, chat
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting MediAI API...")

    # Only initialize database if enabled
    if settings.ENABLE_DATABASE:
        init_db()
        logger.info("Database initialized")
    else:
        logger.info("Database disabled - using CSV data source")

    yield
    # Shutdown
    logger.info("Shutting down MediAI API...")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="MediAI - ICU Risk Prediction API",
    description="REST API for sepsis and mortality risk prediction in ICU patients",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - restricted permissions for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("%s %s - %.3fs", request.method, request.url.path, process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    logger.error("Global exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error occurred"}
    )


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(health.router, tags=["Health"])
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(doctors.router, prefix="/api/v1", tags=["Doctors"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MediAI API",
        "version": "1.0.0",
        "description": "ICU Risk Prediction API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
