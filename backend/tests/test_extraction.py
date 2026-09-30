import os
import json
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from pathlib import Path

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
async def test_extract_invoice_success(client: AsyncClient, ocr_results_dir):
    doc_id = "test_extract_1"
    # Provide enough signals for classification as INVOICE
    text = """
    ABC Traders
    GSTIN: 29ABCDE1234F1Z5
    TAX INVOICE
    Invoice Number: INV-1001
    Date: 28/09/2026
    
    Bill To:
    XYZ Enterprises
    GSTIN: 27ABCDE5678G1Z5
    
    Taxable Amount: 1000.00
    CGST: Rs. 90.00
    SGST: Rs. 90.00
    Grand Total: 1180.00
    """
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["document_id"] == doc_id
    assert data["invoice_number"] == "INV-1001"
    assert data["invoice_date"] == "28/09/2026"
    assert data["seller_name"] == "ABC Traders"
    assert data["seller_gstin"] == "29ABCDE1234F1Z5"
    assert data["buyer_name"] == "XYZ Enterprises"
    assert data["buyer_gstin"] == "27ABCDE5678G1Z5"
    assert data["taxable_amount"] == "1000.00"
    assert data["cgst"] == "90.00"
    assert data["sgst"] == "90.00"
    assert data["igst"] is None
    assert data["total_tax"] == "180.00"
    assert data["grand_total"] == "1180.00"

@pytest.mark.asyncio
async def test_extract_different_date_formats(client: AsyncClient, ocr_results_dir):
    doc_id = "test_date_format"
    text = "TAX INVOICE\nDate: 2026-09-28\nInvoice No: INV-1002"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["invoice_date"] == "2026-09-28"

@pytest.mark.asyncio
async def test_extract_monetary_formats(client: AsyncClient, ocr_results_dir):
    doc_id = "test_monetary"
    text = "TAX INVOICE\nTaxable Value: ₹1,180.00\nTotal: INR 1180.00\nIGST: 180.00"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    data = response.json()
    assert data["taxable_amount"] == "1180.00"
    assert data["grand_total"] == "1180.00"
    assert data["igst"] == "180.00"
    assert data["total_tax"] == "180.00"

@pytest.mark.asyncio
async def test_extract_ocr_noise(client: AsyncClient, ocr_results_dir):
    doc_id = "test_noise"
    text = "TAX INVOICE\nInvoice Number : INV_1001\nGSTIN : 29ABCDE1234F1Z5"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    data = response.json()
    assert data["invoice_number"] == "INV_1001"
    assert data["seller_gstin"] == "29ABCDE1234F1Z5"

@pytest.mark.asyncio
async def test_extract_missing_fields(client: AsyncClient, ocr_results_dir):
    doc_id = "test_missing"
    text = "TAX INVOICE\nInvoice No: 1234"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    data = response.json()
    assert data["invoice_number"] == "1234"
    assert data["invoice_date"] is None
    assert data["seller_gstin"] is None

@pytest.mark.asyncio
async def test_extract_missing_ocr_result(client: AsyncClient, ocr_results_dir):
    response = await client.post("/api/v1/documents/missing_doc/extract")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "OCR text not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_extract_non_invoice_classification(client: AsyncClient, ocr_results_dir):
    doc_id = "test_receipt"
    text = "RETAIL RECEIPT\nAmount Paid: $50.00"
    create_mock_ocr_result(ocr_results_dir, doc_id, text)
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "only available for documents classified as Invoice" in response.json()["detail"]

@pytest.mark.asyncio
async def test_extract_empty_ocr(client: AsyncClient, ocr_results_dir):
    doc_id = "test_empty"
    create_mock_ocr_result(ocr_results_dir, doc_id, "   ")
    
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_extract_malformed_ocr(client: AsyncClient, ocr_results_dir):
    doc_id = "test_malformed"
    # Write bad json
    with open(ocr_results_dir / f"{doc_id}.json", "w", encoding="utf-8") as f:
        f.write("{ bad json }")
        
    response = await client.post(f"/api/v1/documents/{doc_id}/extract")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Corrupted OCR result file" in response.json()["detail"]
