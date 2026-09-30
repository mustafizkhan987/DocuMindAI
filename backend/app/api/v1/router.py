"""
DocuMind AI — API v1 Central Router
===================================

Aggregates all API v1 sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, documents

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router)
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
