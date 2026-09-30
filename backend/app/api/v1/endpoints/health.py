"""
DocuMind AI — Health API v1 Endpoint
===================================

Provides detailed health check information including application status,
version, environment, and database connectivity.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import check_database_connection

router = APIRouter()


@router.get(
    "/health",
    summary="Versioned Health Check",
    description="Returns detailed health status of the API service and its database connection.",
    tags=["Health"],
)
async def v1_health_check() -> JSONResponse:
    """
    Versioned health check endpoint for API v1.

    Returns:
        JSONResponse with status, service name, version, environment, and database connectivity status.
    """
    db_healthy = check_database_connection()
    db_status = "connected" if db_healthy else "disconnected"

    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "database": db_status,
        }
    )
