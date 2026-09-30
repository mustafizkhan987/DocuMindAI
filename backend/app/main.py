"""
DocuMind AI — FastAPI Application Entry Point
=============================================

Task 1: Project Foundation
Version: 0.1.0

This is the main FastAPI application that serves as the backend for
DocuMind AI — an AI-powered GST-aware document & invoice intelligence
platform for Indian businesses.

Current scope (Task 1):
    - GET /          → API info
    - GET /health    → Health check
    - /docs          → Swagger UI
    - /redoc         → ReDoc UI

Future tasks will add:
    - Document upload endpoints  (Task 5)
    - OCR pipeline               (Task 7)
    - Invoice extraction         (Task 9)
    - GSTIN validation           (Task 11)
    - PostgreSQL persistence     (Task 16)
    - Analytics                  (Task 21)
    - RAG / Q&A                  (Task 29-30)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# ---------------------------------------------------------------------------
# Application Configuration
# ---------------------------------------------------------------------------
APP_NAME = os.getenv("APP_NAME", "DocuMind AI")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_ENV = os.getenv("APP_ENV", "development")

# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="DocuMind AI API",
    description=(
        "AI-Powered GST-Aware Document & Invoice Intelligence Platform. "
        "Processes Indian business documents: invoices, receipts, purchase "
        "orders, bills and more. Extracts structured data, validates GSTIN, "
        "checks GST tax components and detects anomalies."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "DocuMind AI",
        "url": "https://github.com/mustafizkhan987/DocuMind-AI",
    },
    license_info={
        "name": "MIT",
    },
)

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
# In development, allow localhost and the Android emulator's host address.
# In production this should be locked to specific origins.
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://10.0.2.2:8000,http://localhost:8000",
)
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
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
            "version": APP_VERSION,
            "environment": APP_ENV,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }
    )


@app.get(
    "/health",
    summary="Health Check",
    description=(
        "Health check endpoint. Returns the current status of the API. "
        "Future tasks will extend this to check database connectivity, "
        "AI service availability, etc."
    ),
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
            "version": APP_VERSION,
            "environment": APP_ENV,
        }
    )
