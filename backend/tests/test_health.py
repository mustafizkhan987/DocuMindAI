"""
DocuMind AI — Health Endpoints Tests
====================================

Tests for GET /health and GET /api/v1/health endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def async_client():
    """Async HTTP test client for the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_health_returns_200(async_client: AsyncClient):
    """GET /health should return HTTP 200."""
    response = await async_client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_healthy(async_client: AsyncClient):
    """GET /health should return status 'healthy'."""
    response = await async_client.get("/health")
    body = response.json()
    assert body["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_returns_version(async_client: AsyncClient):
    """GET /health should include the API version."""
    response = await async_client.get("/health")
    body = response.json()
    assert "version" in body
    assert body["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_v1_health_returns_200(async_client: AsyncClient):
    """GET /api/v1/health should return HTTP 200."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_v1_health_contains_database_status(async_client: AsyncClient):
    """GET /api/v1/health should return service name, version, and database status."""
    response = await async_client.get("/api/v1/health")
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "DocuMind AI"
    assert "database" in body
    assert body["database"] in ["connected", "disconnected"]
