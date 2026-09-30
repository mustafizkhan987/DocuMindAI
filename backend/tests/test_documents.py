import os
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.core.config import settings
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_upload_successful_pdf(client: AsyncClient, tmp_path):
    # Override storage dir for tests
    original_storage = settings.STORAGE_DIR
    settings.STORAGE_DIR = str(tmp_path)
    
    file_content = b"%PDF-1.4\nTest PDF content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    
    response = await client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["original_filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size_bytes"] == len(file_content)
    assert data["status"] == "uploaded"
    assert "document_id" in data
    assert "stored_filename" in data
    
    # Verify file is stored
    stored_path = tmp_path / data["stored_filename"]
    assert stored_path.exists()
    assert stored_path.read_bytes() == file_content
    
    settings.STORAGE_DIR = original_storage

@pytest.mark.asyncio
async def test_upload_empty_file(client: AsyncClient, tmp_path):
    original_storage = settings.STORAGE_DIR
    settings.STORAGE_DIR = str(tmp_path)
    
    file_content = b""
    files = {"file": ("empty.pdf", file_content, "application/pdf")}
    
    response = await client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    settings.STORAGE_DIR = original_storage

@pytest.mark.asyncio
async def test_upload_unsupported_file_type(client: AsyncClient, tmp_path):
    original_storage = settings.STORAGE_DIR
    settings.STORAGE_DIR = str(tmp_path)
    
    file_content = b"Some content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    
    response = await client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    settings.STORAGE_DIR = original_storage

@pytest.mark.asyncio
async def test_upload_oversized_file(client: AsyncClient, tmp_path):
    original_storage = settings.STORAGE_DIR
    settings.STORAGE_DIR = str(tmp_path)
    
    original_max = settings.MAX_UPLOAD_SIZE_MB
    settings.MAX_UPLOAD_SIZE_MB = 1 # 1 MB
    
    file_content = b"0" * (1024 * 1024 + 100) # Slightly over 1MB
    files = {"file": ("large.pdf", file_content, "application/pdf")}
    
    response = await client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    
    settings.MAX_UPLOAD_SIZE_MB = original_max
    settings.STORAGE_DIR = original_storage
