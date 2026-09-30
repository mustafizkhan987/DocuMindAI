import os
import json
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from pathlib import Path

from app.core.config import settings
from app.main import app
from app.schemas.classification import DocumentType

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def ocr_results_dir(tmp_path):
    settings.STORAGE_DIR = str(tmp_path / "storage")
    results_dir = Path(settings.STORAGE_DIR) / "ocr_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir

def create_mock_ocr_result(results_dir: Path, document_id: str, text: str):
    data = {
        "document_id": document_id,
        "page_count": 1,
        "text": text,
        "pages": [
            {"page_number": 1, "text": text, "confidence": 0.99}
        ]
    }
    with open(results_dir / f"{document_id}.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

@pytest.mark.asyncio
async def test_classify_invoice(client: AsyncClient, ocr_results_dir):
    doc_id = "test_invoice"
    text = "TAX INVOICE\nGSTIN: 29ABCDE1234F1Z5\nInvoice No: INV-100\nTotal: 100.00\nCGST: 9.00\nSGST: 9.00"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["document_id"] == doc_id
    assert data["document_type"] == DocumentType.INVOICE.value
    assert data["confidence"] > 0.5
    assert "tax invoice" in data["signals"]
    assert "gstin" in data["signals"]

@pytest.mark.asyncio
async def test_classify_receipt(client: AsyncClient, ocr_results_dir):
    doc_id = "test_receipt"
    text = "RETAIL RECEIPT\nPayment Received\nAmount Paid: $50.00\nTransaction ID: 987654321"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["document_type"] == DocumentType.RECEIPT.value

@pytest.mark.asyncio
async def test_classify_purchase_order(client: AsyncClient, ocr_results_dir):
    doc_id = "test_po"
    text = "PURCHASE ORDER\nPO Number: PO-2026-991\nSupplier: ACME Corp\nOrdered Quantity: 500 units"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["document_type"] == DocumentType.PURCHASE_ORDER.value

@pytest.mark.asyncio
async def test_classify_bill(client: AsyncClient, ocr_results_dir):
    doc_id = "test_bill"
    text = "ELECTRICITY BILL\nAmount Due: 150.00\nDue Date: 2026-10-15"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["document_type"] == DocumentType.BILL.value

@pytest.mark.asyncio
async def test_classify_other(client: AsyncClient, ocr_results_dir):
    doc_id = "test_other"
    text = "This is a random document about ducks.\nIt has nothing to do with business."
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["document_type"] == DocumentType.OTHER.value
    assert data["signals"] == ["no_strong_signals_found"]

@pytest.mark.asyncio
async def test_classify_mixed_signals(client: AsyncClient, ocr_results_dir):
    doc_id = "test_mixed"
    # An invoice usually has "invoice", "gstin". If it says "payment received", the invoice score should still be higher.
    text = "Tax Invoice\nGSTIN: 123\nPayment Received\nCGST\nSGST"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    data = response.json()
    assert data["document_type"] == DocumentType.INVOICE.value

@pytest.mark.asyncio
async def test_classify_case_differences(client: AsyncClient, ocr_results_dir):
    doc_id = "test_case"
    text = "tAX InVoIcE\ngSTIn: 123"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    data = response.json()
    assert data["document_type"] == DocumentType.INVOICE.value

@pytest.mark.asyncio
async def test_classify_ocr_noise(client: AsyncClient, ocr_results_dir):
    doc_id = "test_noise"
    # Punctuation/whitespace noise: "T.A.X I N V O I C E" is too far, but let's test "tax - invoice" and "gstin:"
    text = "tax - invoice\n\n\n\n  gstin: 123"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    data = response.json()
    assert data["document_type"] == DocumentType.INVOICE.value

@pytest.mark.asyncio
async def test_classify_empty_ocr(client: AsyncClient, ocr_results_dir):
    doc_id = "test_empty"
    create_mock_ocr_result(ocr_results_dir, doc_id, "    ")
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    data = response.json()
    assert data["document_type"] == DocumentType.OTHER.value
    assert data["signals"] == ["empty_text"]
    assert data["confidence"] == 0.0

@pytest.mark.asyncio
async def test_classify_missing_document(client: AsyncClient, ocr_results_dir):
    # OCR has not been performed
    response = await client.post("/api/v1/documents/missing_doc/classify")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_classify_confidence_range(client: AsyncClient, ocr_results_dir):
    doc_id = "test_conf"
    text = "TAX INVOICE\nGSTIN: 123\nCGST\nSGST\nIGST\nINVOICE NO\nTAXABLE VALUE\nHSN\n"
    # Lots of signals -> capped at 0.99
    create_mock_ocr_result(ocr_results_dir, doc_id, text * 5)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/classify")
    data = response.json()
    assert data["confidence"] == 0.99
