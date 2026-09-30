import os
import pytest
import cv2
import numpy as np
from httpx import AsyncClient, ASGITransport
from fastapi import status
from unittest.mock import patch, MagicMock

from app.core.config import settings
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def mock_processed_image(tmp_path):
    settings.STORAGE_DIR = str(tmp_path / "documents")
    settings.PROCESSED_DIR = str(tmp_path / "processed")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    
    doc_id = "test-doc-ocr"
    img_path = tmp_path / "processed" / f"{doc_id}_page_1.png"
    
    # Create an image with some text
    img = np.ones((300, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, "DocuMind AI", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Invoice Number: INV-1001", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "GSTIN: 29ABCDE1234F1Z5", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Total: 1180.00", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imwrite(str(img_path), img)
    
    return doc_id

@pytest.mark.asyncio
async def test_ocr_missing_document(client: AsyncClient, tmp_path):
    settings.PROCESSED_DIR = str(tmp_path / "processed")
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    response = await client.post("/api/v1/documents/nonexistent-id/ocr")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
@patch('app.services.ocr_service.OCRService.ocr_engine', new_callable=MagicMock)
async def test_ocr_success_mocked(mock_engine_prop, client: AsyncClient, mock_processed_image):
    mock_engine = MagicMock()
    mock_engine_prop.__get__ = MagicMock(return_value=mock_engine)
    
    # EasyOCR output format: [(bbox, text, prob), ...]
    mock_ocr_result = [
        ([[10, 10], [200, 10], [200, 50], [10, 50]], "DocuMind AI Invoice", 0.98),
        ([[10, 60], [200, 60], [200, 100], [10, 100]], "Total: 1180.00", 0.95)
    ]
    
    mock_engine.readtext.return_value = mock_ocr_result
    
    response = await client.post(f"/api/v1/documents/{mock_processed_image}/ocr")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["document_id"] == mock_processed_image
    assert data["page_count"] == 1
    assert len(data["pages"]) == 1
    
    page = data["pages"][0]
    assert page["page_number"] == 1
    assert "DocuMind AI Invoice" in page["text"]
    assert "Total: 1180.00" in page["text"]
    assert page["confidence"] > 0.9

@pytest.mark.asyncio
async def test_ocr_success_integration(client: AsyncClient, mock_processed_image):
    """
    Actual integration test with the real OCR engine.
    This validates EasyOCR initialization and inference.
    """
    response = await client.post(f"/api/v1/documents/{mock_processed_image}/ocr")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["document_id"] == mock_processed_image
    assert data["page_count"] == 1
    assert len(data["pages"]) == 1
    
    page = data["pages"][0]
    assert page["page_number"] == 1
    
    # Verify the OCR actually extracted the text from the synthetic image
    assert "DocuMind" in page["text"]
    assert "INV_1001" in page["text"] or "INV-1001" in page["text"]
    assert "29ABCDE1234F1Z5" in page["text"]
    
    assert page["confidence"] is not None
    assert page["confidence"] > 0.0
