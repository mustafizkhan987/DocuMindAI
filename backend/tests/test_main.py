"""
DocuMind AI — Backend Tests
============================

Task 1: Project Foundation
Tests for the base API endpoints: GET / and GET /health.

Run with:
    cd backend
    pytest tests/ -v
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# ---------------------------------------------------------------------------
# Test Client Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
async def async_client():
    """Async HTTP test client for the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Test: GET /
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_root_returns_200(async_client: AsyncClient):
    """GET / should return HTTP 200."""
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_returns_message(async_client: AsyncClient):
    """GET / should return the expected message field."""
    response = await async_client.get("/")
    body = response.json()
    assert body["message"] == "DocuMind AI API is running"


@pytest.mark.asyncio
async def test_root_returns_version(async_client: AsyncClient):
    """GET / should return the current API version."""
    response = await async_client.get("/")
    body = response.json()
    assert "version" in body
    assert body["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_root_contains_docs_link(async_client: AsyncClient):
    """GET / should advertise the /docs endpoint."""
    response = await async_client.get("/")
    body = response.json()
    assert body.get("docs") == "/docs"


# ---------------------------------------------------------------------------
# Test: GET /health
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Test: /docs and /redoc
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_docs_endpoint_accessible(async_client: AsyncClient):
    """Swagger UI /docs should be accessible (HTTP 200)."""
    response = await async_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_redoc_endpoint_accessible(async_client: AsyncClient):
    """ReDoc UI /redoc should be accessible (HTTP 200)."""
    response = await async_client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_schema_accessible(async_client: AsyncClient):
    """OpenAPI JSON schema should be accessible."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "DocuMind AI API"
    assert schema["info"]["version"] == "0.1.0"
