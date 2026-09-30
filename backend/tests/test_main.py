"""
DocuMind AI — Main API Tests
=============================

Tests for root API endpoints, documentation endpoints, and OpenAPI schemas.
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
    assert schema["info"]["title"] == "DocuMind AI"
    assert schema["info"]["version"] == "0.1.0"
