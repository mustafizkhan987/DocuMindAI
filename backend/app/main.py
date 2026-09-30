"""
DocuMind AI — FastAPI Application Entry Point
=============================================

Task 2: FastAPI Backend Foundation
Version: 0.1.0

This is the refactored, modular FastAPI application for DocuMind AI.

Responsibilities:
    - Application instantiation with async lifespan management
    - Pydantic Settings integration
    - Middleware setup (CORS)
    - Centralized exception handlers
    - API v1 router registration (/api/v1/...)
    - Root and legacy health endpoints (GET /, GET /health)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import register_exception_handlers
from app.api.v1.router import api_router


# ---------------------------------------------------------------------------
# Lifespan Context Manager (Startup / Shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Application lifespan context manager handling startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Powered GST-Aware Document & Invoice Intelligence Platform. "
        "Processes Indian business documents: invoices, receipts, purchase "
        "orders, bills and more. Extracts structured data, validates GSTIN, "
        "checks GST tax components and detects anomalies."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "DocuMind AI",
        "url": "https://github.com/mustafizkhan987/DocuMindAI",
    },
    license_info={
        "name": "MIT",
    },
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
# Include API v1 routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Root & Base Health Endpoints
# ---------------------------------------------------------------------------
@app.get(
    "/",
    summary="API Root",
    description="Returns basic information about the DocuMind AI API.",
    tags=["Root"],
)
async def root() -> JSONResponse:
    """
    API root endpoint.

    Returns:
        JSON with API name, version, environment and available endpoints.
    """
    return JSONResponse(
        content={
            "message": "DocuMind AI API is running",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "v1_health": "/api/v1/health",
        }
    )


@app.get(
    "/health",
    summary="Health Check",
    description="Base health check endpoint returning status and API version.",
    tags=["Health"],
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns:
        JSON with status 'healthy' and API version.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }
    )
