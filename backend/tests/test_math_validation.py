"""Tests for Invoice Mathematical Validation (Task 14).

Validates deterministic arithmetic relationships within the invoice, such as:
- CGST + SGST + IGST == total_tax
- taxable_amount + total_tax == grand_total
- line item quantity * unit_price == total
"""
import copy
from decimal import Decimal

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.invoice import CanonicalInvoice, Financials, LineItem, Party
from app.schemas.math_validation import MathCheckStatus, OverallMathStatus
from app.services.math_validation_service import math_validation_service

DOC = "math-test-doc"

# ── fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
def mock_math_pipeline(monkeypatch):
    """Mock classification (INVOICE) + extraction with configurable financials."""
    from app.schemas.classification import ClassificationResult, DocumentType

    def _mock(financials: Financials, line_items=None):
        def _classify(self, doc_id):
            return ClassificationResult(
                document_id=doc_id,
                document_type=DocumentType.INVOICE,
                confidence=0.95,
                signals=["TAX INVOICE"],
            )

        def _get_extraction_result(self, doc_id):
            return CanonicalInvoice(
                document_id=doc_id,
                seller=Party(name="Seller"),
                buyer=Party(name="Buyer"),
                financials=financials,
                line_items=line_items or []
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


# ── helpers ──────────────────────────────────────────────────────────

def _validate(financials: Financials, line_items=None):
    invoice = CanonicalInvoice(
        document_id=DOC,
        financials=financials,
        line_items=line_items or []
    )
    return math_validation_service.validate(invoice)


# =====================================================================
# A. Tax total passes
# =====================================================================
def test_tax_total_passes():
    """A: CGST + SGST + IGST == total_tax -> PASS"""
    fin = Financials(
        cgst=Decimal("900.00"),
        sgst=Decimal("900.00"),
        igst=Decimal("0.00"),
        total_tax=Decimal("1800.00")
    )
    res = _validate(fin)
    assert res.checks["tax_total"].status == MathCheckStatus.PASS


# =====================================================================
# B. Tax total mismatch
# =====================================================================
def test_tax_total_mismatch():
    """B: CGST + SGST + IGST != total_tax -> MISMATCH"""
    fin = Financials(
        cgst=Decimal("900.00"),
        sgst=Decimal("900.00"),
        igst=Decimal("0.00"),
        total_tax=Decimal("1900.00")
    )
    res = _validate(fin)
    assert res.checks["tax_total"].status == MathCheckStatus.MISMATCH


# =====================================================================
# C. Grand total passes
# =====================================================================
def test_grand_total_passes():
    """C: taxable_amount + total_tax == grand_total -> PASS"""
    fin = Financials(
        taxable_amount=Decimal("10000.00"),
        total_tax=Decimal("1800.00"),
        grand_total=Decimal("11800.00")
    )
    res = _validate(fin)
    assert res.checks["grand_total"].status == MathCheckStatus.PASS


# =====================================================================
# D. Grand total mismatch
# =====================================================================
def test_grand_total_mismatch():
    """D: taxable_amount + total_tax != grand_total -> MISMATCH"""
    fin = Financials(
        taxable_amount=Decimal("10000.00"),
        total_tax=Decimal("1800.00"),
        grand_total=Decimal("11850.00")
    )
    res = _validate(fin)
    assert res.checks["grand_total"].status == MathCheckStatus.MISMATCH


# =====================================================================
# E. Both checks pass
# =====================================================================
def test_both_checks_pass_consistent():
    """E: Both checks pass -> CONSISTENT"""
    fin = Financials(
        cgst=Decimal("900.00"),
        sgst=Decimal("900.00"),
        igst=Decimal("0.00"),
        total_tax=Decimal("1800.00"),
        taxable_amount=Decimal("10000.00"),
        grand_total=Decimal("11800.00")
    )
    res = _validate(fin)
    assert res.status == OverallMathStatus.CONSISTENT
    assert res.overall_consistent is True


# =====================================================================
# F, G, H, I: Missing data -> REVIEW_REQUIRED
# =====================================================================
def test_missing_taxable_amount():
    """F: Missing taxable amount -> REVIEW_REQUIRED"""
    fin = Financials(
        total_tax=Decimal("1800.00"),
        grand_total=Decimal("11800.00"),
        cgst=Decimal("900"), sgst=Decimal("900"), igst=Decimal("0")
    )
    res = _validate(fin)
    assert res.checks["grand_total"].status == MathCheckStatus.REVIEW_REQUIRED
    assert res.status == OverallMathStatus.REVIEW_REQUIRED


def test_missing_total_tax():
    """G: Missing total_tax -> REVIEW_REQUIRED for both checks"""
    fin = Financials(
        taxable_amount=Decimal("10000.00"),
        grand_total=Decimal("11800.00"),
        cgst=Decimal("900"), sgst=Decimal("900"), igst=Decimal("0")
    )
    res = _validate(fin)
    assert res.checks["tax_total"].status == MathCheckStatus.REVIEW_REQUIRED
    assert res.checks["grand_total"].status == MathCheckStatus.REVIEW_REQUIRED
    assert res.status == OverallMathStatus.REVIEW_REQUIRED


def test_missing_grand_total():
    """H: Missing grand_total -> REVIEW_REQUIRED"""
    fin = Financials(
        taxable_amount=Decimal("10000.00"),
        total_tax=Decimal("1800.00"),
        cgst=Decimal("900"), sgst=Decimal("900"), igst=Decimal("0")
    )
    res = _validate(fin)
    assert res.checks["grand_total"].status == MathCheckStatus.REVIEW_REQUIRED
    assert res.status == OverallMathStatus.REVIEW_REQUIRED


def test_missing_individual_tax_component():
    """I: Missing CGST -> REVIEW_REQUIRED for tax total"""
    fin = Financials(
        sgst=Decimal("900.00"),
        igst=Decimal("0.00"),
        total_tax=Decimal("1800.00"),
        taxable_amount=Decimal("10000.00"),
        grand_total=Decimal("11800.00")
    )
    res = _validate(fin)
    assert res.checks["tax_total"].status == MathCheckStatus.REVIEW_REQUIRED
    assert res.checks["grand_total"].status == MathCheckStatus.PASS
    assert res.status == OverallMathStatus.REVIEW_REQUIRED


# =====================================================================
# J. Decimal precision / no float conversion
# =====================================================================
def test_decimal_precision_retained():
    """J: Explicitly prove Decimal is retained and no float conversion occurs."""
    fin = Financials(
        cgst=Decimal("900.00"),
        sgst=Decimal("900.00"),
        igst=Decimal("0.00"),
        total_tax=Decimal("1800.00")
    )
    res = _validate(fin)
    # Check A
    assert isinstance(res.checks["tax_total"].expected, Decimal)
    assert isinstance(res.checks["tax_total"].actual, Decimal)
    assert isinstance(res.checks["tax_total"].difference, Decimal)


# =====================================================================
# K. Tolerance (0.01)
# =====================================================================
def test_tolerance_accepted():
    """K: Difference exactly 0.01 -> PASS"""
    fin = Financials(
        taxable_amount=Decimal("1180.00"),
        total_tax=Decimal("0.00"),
        grand_total=Decimal("1180.01")  # Diff 0.01
    )
    res = _validate(fin)
    assert res.checks["grand_total"].status == MathCheckStatus.PASS


def test_tolerance_mismatch():
    """K: Difference 0.02 -> MISMATCH"""
    fin = Financials(
        taxable_amount=Decimal("1180.00"),
        total_tax=Decimal("0.00"),
        grand_total=Decimal("1180.02")  # Diff 0.02
    )
    res = _validate(fin)
    assert res.checks["grand_total"].status == MathCheckStatus.MISMATCH


# =====================================================================
# L, M: Line items
# =====================================================================
def test_line_item_validation_passes():
    """L: Line item validation where schema provides enough info."""
    items = [
        LineItem(quantity=Decimal("2"), unit_price=Decimal("50.00"), total=Decimal("100.00")),
        LineItem(quantity=Decimal("3"), unit_price=Decimal("10.00"), total=Decimal("30.00")),
    ]
    res = _validate(Financials(), line_items=items)
    assert res.checks["line_items"].status == MathCheckStatus.PASS


def test_line_item_validation_mismatch():
    items = [
        LineItem(quantity=Decimal("2"), unit_price=Decimal("50.00"), total=Decimal("100.00")),
        LineItem(quantity=Decimal("3"), unit_price=Decimal("10.00"), total=Decimal("40.00")), # Mismatch
    ]
    res = _validate(Financials(), line_items=items)
    assert res.checks["line_items"].status == MathCheckStatus.MISMATCH


def test_incomplete_line_items():
    """M: Incomplete line items -> REVIEW_REQUIRED."""
    items = [
        LineItem(quantity=Decimal("2"), unit_price=None, total=Decimal("100.00")),
    ]
    res = _validate(Financials(), line_items=items)
    assert res.checks["line_items"].status == MathCheckStatus.REVIEW_REQUIRED


# =====================================================================
# N: API Tests (Non-invoice document)
# =====================================================================
@pytest.mark.asyncio
async def test_api_non_invoice_rejected(client: AsyncClient, monkeypatch):
    """N: Non-invoice document -> rejected with HTTP 400."""
    from app.schemas.classification import ClassificationResult, DocumentType
    def _classify_receipt(self, doc_id):
        return ClassificationResult(
            document_id=doc_id, document_type=DocumentType.RECEIPT, confidence=0.9
        )
    monkeypatch.setattr(
        "app.services.classification_service.ClassificationService.classify_document",
        _classify_receipt,
    )
    resp = await client.post("/api/v1/documents/receipt-doc/validate-math")
    assert resp.status_code == 400
    assert "only available for documents classified as Invoice" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_api_math_validation_success(client: AsyncClient, mock_math_pipeline):
    """API endpoint returns structured validation results."""
    fin = Financials(
        cgst=Decimal("900.00"),
        sgst=Decimal("900.00"),
        igst=Decimal("0.00"),
        total_tax=Decimal("1800.00"),
        taxable_amount=Decimal("10000.00"),
        grand_total=Decimal("11800.00")
    )
    mock_math_pipeline(financials=fin)
    
    resp = await client.post("/api/v1/documents/doc-math-1/validate-math")
    assert resp.status_code == 200
    body = resp.json()
    assert body["document_id"] == "doc-math-1"
    assert body["status"] == "CONSISTENT"
    assert body["overall_consistent"] is True
    assert "tax_total" in body["checks"]
    assert "grand_total" in body["checks"]
    assert body["checks"]["tax_total"]["status"] == "PASS"


# =====================================================================
# P: Canonical invoice is not mutated
# =====================================================================
def test_canonical_invoice_not_mutated():
    """P: Service must not mutate the canonical invoice."""
    fin = Financials(cgst=Decimal("100"), sgst=Decimal("100"), igst=Decimal("0"))
    invoice = CanonicalInvoice(document_id=DOC, financials=fin)
    original = copy.deepcopy(invoice)
    math_validation_service.validate(invoice)
    assert invoice == original


# =====================================================================
# Q: All-zero tax arithmetic
# =====================================================================
def test_all_zero_tax_arithmetic():
    """Q: All-zero tax arithmetic passes cleanly."""
    fin = Financials(
        cgst=Decimal("0"), sgst=Decimal("0"), igst=Decimal("0"),
        total_tax=Decimal("0"),
        taxable_amount=Decimal("1000.00"),
        grand_total=Decimal("1000.00")
    )
    res = _validate(fin)
    assert res.checks["tax_total"].status == MathCheckStatus.PASS
    assert res.checks["grand_total"].status == MathCheckStatus.PASS
    assert res.status == OverallMathStatus.CONSISTENT
