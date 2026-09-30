import os
import shutil
import pytest
import cv2
import numpy as np
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.core.config import settings
from app.main import app
from app.services.document_service import document_service

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def dummy_image(tmp_path):
    img_path = tmp_path / "dummy.jpg"
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # add some noise
    noise = np.random.randint(0, 50, (100, 100, 3), dtype=np.uint8)
    img = cv2.subtract(img, noise)
    cv2.imwrite(str(img_path), img)
    return img_path

@pytest.mark.asyncio
async def test_preprocessing_success(client: AsyncClient, tmp_path, dummy_image):
    # Setup storage
    settings.STORAGE_DIR = str(tmp_path / "documents")
    settings.PROCESSED_DIR = str(tmp_path / "processed")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    
    # Simulate an uploaded document
    doc_id = "test-doc-id-123"
    shutil_copy = tmp_path / "documents" / f"{doc_id}.jpg"
    with open(dummy_image, "rb") as f_in, open(shutil_copy, "wb") as f_out:
        f_out.write(f_in.read())

    response = await client.post(f"/api/v1/documents/{doc_id}/preprocess")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["document_id"] == doc_id
    assert data["status"] == "processed"
    assert data["page_count"] == 1
    assert "100x100" in data["original_dimensions"][0]
    assert len(data["processed_pages"]) == 1
    
    processed_file = os.path.join(settings.PROCESSED_DIR, data["processed_pages"][0])
    assert os.path.exists(processed_file)
    
    # Verify original file is untouched
    assert os.path.exists(shutil_copy)

@pytest.mark.asyncio
async def test_preprocessing_not_found(client: AsyncClient, tmp_path):
    settings.STORAGE_DIR = str(tmp_path / "documents")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    
    response = await client.post("/api/v1/documents/nonexistent-id/preprocess")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_preprocessing_corrupted_image(client: AsyncClient, tmp_path):
    settings.STORAGE_DIR = str(tmp_path / "documents")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    
    doc_id = "corrupted-id"
    corrupt_file = tmp_path / "documents" / f"{doc_id}.jpg"
    with open(corrupt_file, "wb") as f:
        f.write(b"not an image")
        
    response = await client.post(f"/api/v1/documents/{doc_id}/preprocess")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to load image" in response.json()["detail"]
