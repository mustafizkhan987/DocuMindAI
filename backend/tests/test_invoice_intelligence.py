"""Tests for Invoice Intelligence Service (Task 15).

Verifies the integration of the full Phase 2 document pipeline.
"""
from decimal import Decimal
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.classification import ClassificationResult, DocumentType
from app.schemas.invoice import CanonicalInvoice, Financials, Party
from app.schemas.invoice_intelligence import IntelligenceOverallStatus, IntelligenceIssueStatus
from app.services.invoice_intelligence_service import invoice_intelligence_service


# ── fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
def mock_document_exists(monkeypatch):
    from pathlib import Path
    monkeypatch.setattr("app.services.document_service.DocumentService.get_document_path_and_mime_type", lambda self, doc_id: (Path("fake"), "application/pdf"))


@pytest.fixture
def mock_intelligence_pipeline(monkeypatch, mock_document_exists):
    """Mock classification and extraction to simulate specific invoice scenarios."""
    
    def _mock(document_type=DocumentType.INVOICE, seller_gstin="29ABCDE1234F1ZW", buyer_gstin="29ABCDE1234F1ZW", financials=None):
        def _classify(self, doc_id):
            return ClassificationResult(
                document_id=doc_id,
                document_type=document_type,
                confidence=0.95,
                signals=["TAX INVOICE"] if document_type == DocumentType.INVOICE else ["RECEIPT"],
            )

        def _get_extraction_result(self, doc_id):
            if document_type != DocumentType.INVOICE:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Extraction not found")
                
            return CanonicalInvoice(
                document_id=doc_id,
                seller=Party(name="Seller", gstin=seller_gstin) if seller_gstin else Party(name="Seller"),
                buyer=Party(name="Buyer", gstin=buyer_gstin) if buyer_gstin else Party(name="Buyer"),
                financials=financials or Financials(
                    taxable_amount=Decimal("1000.00"),
                    cgst=Decimal("90.00"),
                    sgst=Decimal("90.00"),
                    igst=Decimal("0.00"),
                    total_tax=Decimal("180.00"),
                    grand_total=Decimal("1180.00")
                )
            )

        monkeypatch.setattr(
            "app.services.classification_service.ClassificationService.classify_document",
            _classify,
        )
        monkeypatch.setattr(
            "app.services.extraction_service.ExtractionService.get_extraction_result",
            _get_extraction_result,
        )
        
    return _mock


# ── tests ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_non_invoice_behavior(client: AsyncClient, mock_intelligence_pipeline):
    """Test non-invoice behavior."""
    mock_intelligence_pipeline(document_type=DocumentType.RECEIPT)
    
    resp = await client.post("/api/v1/documents/doc-1/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.INFORMATION_FOUND.value
    assert data["document_type"] == DocumentType.RECEIPT.value
    assert "not applied" in data["summary"]
    assert data["extraction"] is None


@pytest.mark.asyncio
async def test_valid_invoice(client: AsyncClient, mock_intelligence_pipeline):
    """Test a completely valid, consistent invoice."""
    mock_intelligence_pipeline()  # Defaults to valid same-state invoice with correct math
    
    resp = await client.post("/api/v1/documents/doc-2/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.CONSISTENT.value
    assert len(data["issues"]) == 0
    assert data["tax_type_validation"]["is_consistent"] is True
    assert data["mathematical_validation"]["overall_consistent"] is True


@pytest.mark.asyncio
async def test_invoice_with_gstin_issue(client: AsyncClient, mock_intelligence_pipeline):
    """Test invoice with invalid GSTIN."""
    mock_intelligence_pipeline(seller_gstin="INVALID_GSTIN")
    
    resp = await client.post("/api/v1/documents/doc-3/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.MISMATCH.value
    issues = [i for i in data["issues"] if i["category"] == "GSTIN"]
    assert len(issues) >= 1
    assert issues[0]["status"] == IntelligenceIssueStatus.MISMATCH.value


@pytest.mark.asyncio
async def test_invoice_with_jurisdiction_difference(client: AsyncClient, mock_intelligence_pipeline):
    """Test tax type mismatch due to jurisdiction difference.
    
    Seller is 29 (KA), Buyer is 27 (MH).
    Financials default to CGST+SGST, which is incorrect for inter-state (expects IGST).
    """
    mock_intelligence_pipeline(seller_gstin="29ABCDE1234F1ZW", buyer_gstin="27ABCDE1234F1Z0")
    
    resp = await client.post("/api/v1/documents/doc-4/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.MISMATCH.value
    issues = [i for i in data["issues"] if i["category"] == "Tax Type"]
    assert len(issues) >= 1
    assert issues[0]["status"] == IntelligenceIssueStatus.MISMATCH.value


@pytest.mark.asyncio
async def test_tax_type_review_required(client: AsyncClient, mock_intelligence_pipeline):
    """Test missing tax type components leading to REVIEW_REQUIRED."""
    fin = Financials(
        taxable_amount=Decimal("1000.00"),
        cgst=None, sgst=None, igst=None,
        total_tax=Decimal("180.00"),
        grand_total=Decimal("1180.00")
    )
    mock_intelligence_pipeline(financials=fin)
    
    resp = await client.post("/api/v1/documents/doc-5/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.REVIEW_REQUIRED.value
    issues = [i for i in data["issues"] if i["category"] == "Tax Type"]
    assert len(issues) >= 1
    assert issues[0]["status"] == IntelligenceIssueStatus.REVIEW_REQUIRED.value


@pytest.mark.asyncio
async def test_mathematical_mismatch(client: AsyncClient, mock_intelligence_pipeline):
    """Test mathematical mismatch (grand total incorrect)."""
    fin = Financials(
        taxable_amount=Decimal("1000.00"),
        cgst=Decimal("90.00"), sgst=Decimal("90.00"), igst=Decimal("0"),
        total_tax=Decimal("180.00"),
        grand_total=Decimal("9999.00")  # Mismatch!
    )
    mock_intelligence_pipeline(financials=fin)
    
    resp = await client.post("/api/v1/documents/doc-6/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.MISMATCH.value
    issues = [i for i in data["issues"] if "Mathematical" in i["category"]]
    assert len(issues) >= 1
    assert issues[0]["status"] == IntelligenceIssueStatus.MISMATCH.value


@pytest.mark.asyncio
async def test_missing_financial_value(client: AsyncClient, mock_intelligence_pipeline):
    """Test missing taxable_amount leading to math review required."""
    fin = Financials(
        taxable_amount=None,
        cgst=Decimal("90.00"), sgst=Decimal("90.00"), igst=Decimal("0"),
        total_tax=Decimal("180.00"),
        grand_total=Decimal("1180.00")
    )
    mock_intelligence_pipeline(financials=fin)
    
    resp = await client.post("/api/v1/documents/doc-7/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.REVIEW_REQUIRED.value
    issues = [i for i in data["issues"] if "Mathematical" in i["category"]]
    assert len(issues) >= 1
    assert issues[0]["status"] == IntelligenceIssueStatus.REVIEW_REQUIRED.value


@pytest.mark.asyncio
async def test_missing_gstin(client: AsyncClient, mock_intelligence_pipeline):
    """Test missing buyer GSTIN."""
    mock_intelligence_pipeline(buyer_gstin=None)
    
    resp = await client.post("/api/v1/documents/doc-8/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    # Missing buyer GSTIN -> REVIEW_REQUIRED
    # Which forces tax type validation to REVIEW_REQUIRED because jurisdiction is unavailable.
    assert data["overall_status"] == IntelligenceOverallStatus.REVIEW_REQUIRED.value
    issues = [i for i in data["issues"] if i["category"] == "GSTIN"]
    assert len(issues) >= 1
    assert issues[0]["status"] == IntelligenceIssueStatus.REVIEW_REQUIRED.value


@pytest.mark.asyncio
async def test_missing_extraction_result(client: AsyncClient, monkeypatch, mock_document_exists):
    """Test document missing extraction entirely."""
    from app.schemas.classification import ClassificationResult, DocumentType
    
    def _classify(self, doc_id):
        return ClassificationResult(
            document_id=doc_id, document_type=DocumentType.INVOICE, confidence=0.9
        )
    
    def _get_extraction_result(self, doc_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Extraction not found")
        
    monkeypatch.setattr(
        "app.services.classification_service.ClassificationService.classify_document",
        _classify,
    )
    monkeypatch.setattr(
        "app.services.extraction_service.ExtractionService.get_extraction_result",
        _get_extraction_result,
    )
    
    resp = await client.post("/api/v1/documents/doc-9/intelligence")
    assert resp.status_code == 400
    assert "extraction has been completed" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_multiple_simultaneous_issues(client: AsyncClient, mock_intelligence_pipeline):
    """Test multiple issues don't hide each other and aggregate to MISMATCH."""
    fin = Financials(
        taxable_amount=Decimal("1000.00"),
        cgst=Decimal("90.00"), sgst=Decimal("90.00"), igst=Decimal("0"),
        total_tax=Decimal("180.00"),
        grand_total=Decimal("9999.00")  # Math mismatch
    )
    # Seller GSTIN invalid -> GSTIN mismatch
    # Math mismatch -> Math mismatch
    mock_intelligence_pipeline(seller_gstin="INVALID", financials=fin)
    
    resp = await client.post("/api/v1/documents/doc-10/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_status"] == IntelligenceOverallStatus.MISMATCH.value
    
    # We should have BOTH a GSTIN mismatch and a Mathematical mismatch in issues
    issues = data["issues"]
    gstin_mismatches = [i for i in issues if i["category"] == "GSTIN" and i["status"] == "MISMATCH"]
    math_mismatches = [i for i in issues if "Mathematical" in i["category"] and i["status"] == "MISMATCH"]
    
    assert len(gstin_mismatches) >= 1
    assert len(math_mismatches) >= 1
