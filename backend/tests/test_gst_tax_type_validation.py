"""Tests for GST Tax Type Validation (Task 13).

Validates that the tax COMPONENT TYPE (CGST+SGST vs IGST) is consistent
with seller/buyer jurisdiction.  Does NOT test tax rates, amounts, or
invoice arithmetic — those belong to Task 14.
"""

import copy
from decimal import Decimal

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.invoice import CanonicalInvoice, Financials, Party
from app.schemas.state_detection import JurisdictionRelationship
from app.schemas.tax_type_validation import (
    ExpectedTaxType,
    GSTTaxTypeValidationResult,
    TaxTypeValidationStatus,
)
from app.services.gst_tax_type_validation_service import GSTTaxTypeValidationService

svc = GSTTaxTypeValidationService()
DOC = "tax-type-test"

# Valid GSTINs (same checksums used by test_state_detection.py)
GSTIN_KARNATAKA = "29ABCDE1234F1ZW"   # state 29
GSTIN_MAHARASHTRA = "27ABCDE1234F1Z0"  # state 27


# ── fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
def mock_tax_pipeline(monkeypatch):
    """Mock classification (INVOICE) + extraction with configurable financials."""
    from app.schemas.classification import ClassificationResult, DocumentType

    def _mock(
        seller_gstin=GSTIN_KARNATAKA,
        buyer_gstin=GSTIN_KARNATAKA,
        cgst=None, sgst=None, igst=None,
    ):
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
                seller=Party(gstin=seller_gstin),
                buyer=Party(gstin=buyer_gstin),
                financials=Financials(cgst=cgst, sgst=sgst, igst=igst),
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

def _fin(cgst=None, sgst=None, igst=None) -> Financials:
    return Financials(cgst=cgst, sgst=sgst, igst=igst)


def _validate(jurisdiction, cgst=None, sgst=None, igst=None):
    return svc.validate(DOC, jurisdiction, _fin(cgst, sgst, igst))


# =====================================================================
# SAME-STATE SCENARIOS
# =====================================================================

def test_same_state_cgst_sgst():
    """Example 1 — CGST+SGST present, IGST zero → CONSISTENT."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("100"), sgst=Decimal("100"), igst=Decimal("0"))
    assert r.expected_tax_type == ExpectedTaxType.CGST_SGST
    assert r.is_consistent is True
    assert r.status == TaxTypeValidationStatus.CONSISTENT
    assert r.errors == []


def test_same_state_igst_mismatch():
    """Same-state but only IGST present → MISMATCH."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("0"), sgst=Decimal("0"), igst=Decimal("200"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.MISMATCH
    assert any("CGST expected" in e for e in r.errors)
    assert any("SGST expected" in e for e in r.errors)
    assert any("IGST present" in e for e in r.errors)


def test_same_state_cgst_only():
    """Same-state with CGST but no SGST → MISMATCH (incomplete pair)."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("100"), sgst=Decimal("0"), igst=Decimal("0"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.MISMATCH
    assert any("SGST expected" in e for e in r.errors)


def test_same_state_sgst_only():
    """Same-state with SGST but no CGST → MISMATCH."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("0"), sgst=Decimal("100"), igst=Decimal("0"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.MISMATCH
    assert any("CGST expected" in e for e in r.errors)


def test_same_state_all_three():
    """Same-state with all three positive → MISMATCH (IGST shouldn't be there)."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("50"), sgst=Decimal("50"), igst=Decimal("100"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.MISMATCH
    assert any("IGST present" in e for e in r.errors)


def test_same_state_all_zero():
    """Same-state with all zeros → REVIEW_REQUIRED."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("0"), sgst=Decimal("0"), igst=Decimal("0"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.REVIEW_REQUIRED
    assert any("zero" in w.lower() for w in r.warnings)


def test_same_state_missing_tax_fields():
    """Same-state with all fields None → REVIEW_REQUIRED."""
    r = _validate(JurisdictionRelationship.SAME_STATE)
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.REVIEW_REQUIRED
    assert any("missing" in w.lower() for w in r.warnings)


# =====================================================================
# DIFFERENT-STATE SCENARIOS
# =====================================================================

def test_different_state_igst():
    """Example 2 — IGST present, CGST/SGST zero → CONSISTENT."""
    r = _validate(JurisdictionRelationship.DIFFERENT_STATE,
                  cgst=Decimal("0"), sgst=Decimal("0"), igst=Decimal("200"))
    assert r.expected_tax_type == ExpectedTaxType.IGST
    assert r.is_consistent is True
    assert r.status == TaxTypeValidationStatus.CONSISTENT


def test_different_state_cgst_sgst_mismatch():
    """Example 3 — different-state but CGST+SGST → MISMATCH."""
    r = _validate(JurisdictionRelationship.DIFFERENT_STATE,
                  cgst=Decimal("100"), sgst=Decimal("100"), igst=Decimal("0"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.MISMATCH
    assert any("IGST expected" in e for e in r.errors)
    assert any("CGST present" in e for e in r.errors)
    assert any("SGST present" in e for e in r.errors)


def test_different_state_all_three():
    """Different-state with all three positive → MISMATCH."""
    r = _validate(JurisdictionRelationship.DIFFERENT_STATE,
                  cgst=Decimal("50"), sgst=Decimal("50"), igst=Decimal("200"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.MISMATCH
    assert any("CGST present" in e for e in r.errors)
    assert any("SGST present" in e for e in r.errors)


def test_different_state_all_zero():
    """Different-state with all zeros → REVIEW_REQUIRED."""
    r = _validate(JurisdictionRelationship.DIFFERENT_STATE,
                  cgst=Decimal("0"), sgst=Decimal("0"), igst=Decimal("0"))
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.REVIEW_REQUIRED


def test_different_state_missing_tax_fields():
    """Different-state with all fields None → REVIEW_REQUIRED."""
    r = _validate(JurisdictionRelationship.DIFFERENT_STATE)
    assert r.is_consistent is False
    assert r.status == TaxTypeValidationStatus.REVIEW_REQUIRED


# =====================================================================
# JURISDICTION UNAVAILABLE SCENARIOS
# =====================================================================

def test_seller_state_unavailable():
    r = _validate(JurisdictionRelationship.SELLER_STATE_UNAVAILABLE,
                  cgst=Decimal("100"), sgst=Decimal("100"))
    assert r.status == TaxTypeValidationStatus.JURISDICTION_UNAVAILABLE
    assert r.expected_tax_type == ExpectedTaxType.UNKNOWN
    assert r.is_consistent is False


def test_buyer_state_unavailable():
    r = _validate(JurisdictionRelationship.BUYER_STATE_UNAVAILABLE,
                  igst=Decimal("200"))
    assert r.status == TaxTypeValidationStatus.JURISDICTION_UNAVAILABLE


def test_both_states_unavailable():
    r = _validate(JurisdictionRelationship.BOTH_STATES_UNAVAILABLE)
    assert r.status == TaxTypeValidationStatus.JURISDICTION_UNAVAILABLE
    assert r.expected_tax_type == ExpectedTaxType.UNKNOWN


# =====================================================================
# API ENDPOINT TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_api_non_invoice_rejected(client: AsyncClient, monkeypatch):
    """Non-invoice documents must be rejected with HTTP 400."""
    from app.schemas.classification import ClassificationResult, DocumentType

    def _classify_receipt(self, doc_id):
        return ClassificationResult(
            document_id=doc_id,
            document_type=DocumentType.RECEIPT,
            confidence=0.90,
            signals=["RECEIPT"],
        )

    monkeypatch.setattr(
        "app.services.classification_service.ClassificationService.classify_document",
        _classify_receipt,
    )

    resp = await client.post("/api/v1/documents/receipt-doc/validate-tax-type")
    assert resp.status_code == 400
    assert "only available for documents classified as Invoice" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_api_response_schema(client: AsyncClient, mock_tax_pipeline):
    """API returns all expected fields for an invoice document."""
    mock_tax_pipeline(
        seller_gstin=GSTIN_KARNATAKA,
        buyer_gstin=GSTIN_KARNATAKA,
        cgst=Decimal("100"),
        sgst=Decimal("100"),
        igst=Decimal("0"),
    )
    resp = await client.post("/api/v1/documents/doc-tax-1/validate-tax-type")
    assert resp.status_code == 200
    body = resp.json()
    assert "document_id" in body
    assert "jurisdiction_relationship" in body
    assert "expected_tax_type" in body
    assert "actual_tax_components" in body
    assert "is_consistent" in body
    assert "status" in body
    assert "errors" in body
    assert "warnings" in body


@pytest.mark.asyncio
async def test_api_same_state_consistent(client: AsyncClient, mock_tax_pipeline):
    """Same-state with correct CGST+SGST through API."""
    mock_tax_pipeline(
        seller_gstin=GSTIN_KARNATAKA,
        buyer_gstin=GSTIN_KARNATAKA,
        cgst=Decimal("100"),
        sgst=Decimal("100"),
        igst=Decimal("0"),
    )
    resp = await client.post("/api/v1/documents/doc-tax-2/validate-tax-type")
    assert resp.status_code == 200
    data = resp.json()
    assert data["expected_tax_type"] == "CGST_SGST"
    assert data["is_consistent"] is True
    assert data["status"] == "CONSISTENT"


@pytest.mark.asyncio
async def test_api_different_state_mismatch(client: AsyncClient, mock_tax_pipeline):
    """Different-state with CGST+SGST through API → MISMATCH."""
    mock_tax_pipeline(
        seller_gstin=GSTIN_KARNATAKA,
        buyer_gstin=GSTIN_MAHARASHTRA,
        cgst=Decimal("100"),
        sgst=Decimal("100"),
        igst=Decimal("0"),
    )
    resp = await client.post("/api/v1/documents/doc-tax-3/validate-tax-type")
    assert resp.status_code == 200
    data = resp.json()
    assert data["expected_tax_type"] == "IGST"
    assert data["is_consistent"] is False
    assert data["status"] == "MISMATCH"


@pytest.mark.asyncio
async def test_api_jurisdiction_unavailable(client: AsyncClient, mock_tax_pipeline):
    """Missing seller GSTIN → JURISDICTION_UNAVAILABLE."""
    mock_tax_pipeline(
        seller_gstin=None,
        buyer_gstin=GSTIN_MAHARASHTRA,
        cgst=Decimal("100"),
        sgst=Decimal("100"),
    )
    resp = await client.post("/api/v1/documents/doc-tax-4/validate-tax-type")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "JURISDICTION_UNAVAILABLE"
    assert data["expected_tax_type"] == "UNKNOWN"


# =====================================================================
# DECIMAL / IMMUTABILITY / SAFETY TESTS
# =====================================================================

def test_decimal_preservation():
    """Decimal values must pass through without float conversion."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("100.50"), sgst=Decimal("100.50"), igst=Decimal("0"))
    assert r.actual_tax_components.cgst == Decimal("100.50")
    assert r.actual_tax_components.sgst == Decimal("100.50")
    assert r.actual_tax_components.igst == Decimal("0")


def test_canonical_invoice_not_mutated():
    """The service must not mutate the Financials passed in."""
    fin = _fin(cgst=Decimal("100"), sgst=Decimal("100"), igst=Decimal("0"))
    original = copy.deepcopy(fin)
    svc.validate(DOC, JurisdictionRelationship.SAME_STATE, fin)
    assert fin == original


def test_no_tax_amount_calculation():
    """Result must not contain computed tax amounts or totals."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("100"), sgst=Decimal("100"), igst=Decimal("0"))
    result_dict = r.model_dump()
    for key in result_dict:
        assert key != "computed_tax"
        assert key != "tax_total"
        assert key != "calculated_amount"


def test_no_tax_rate_validation():
    """No percentage or rate fields appear in the result."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("100"), sgst=Decimal("100"))
    result_dict = r.model_dump()
    for key in result_dict:
        assert "rate" not in key.lower()
        assert "percent" not in key.lower()


# =====================================================================
# NONE vs ZERO DISTINCTION
# =====================================================================

def test_none_vs_zero_cgst():
    """None CGST is handled differently from zero CGST."""
    r_none = _validate(JurisdictionRelationship.SAME_STATE,
                       cgst=None, sgst=Decimal("100"), igst=Decimal("0"))
    r_zero = _validate(JurisdictionRelationship.SAME_STATE,
                       cgst=Decimal("0"), sgst=Decimal("100"), igst=Decimal("0"))
    # Both should fail, but the actual_tax_components should reflect the difference
    assert r_none.actual_tax_components.cgst is None
    assert r_zero.actual_tax_components.cgst == Decimal("0")
    assert r_none.is_consistent is False
    assert r_zero.is_consistent is False


def test_same_state_cgst_sgst_igst_none():
    """CGST+SGST positive with IGST=None → consistent (None means not extracted)."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("100"), sgst=Decimal("100"), igst=None)
    assert r.is_consistent is True
    assert r.status == TaxTypeValidationStatus.CONSISTENT


def test_different_state_igst_positive_cgst_sgst_none():
    """IGST positive with CGST/SGST=None → consistent."""
    r = _validate(JurisdictionRelationship.DIFFERENT_STATE,
                  cgst=None, sgst=None, igst=Decimal("200"))
    assert r.is_consistent is True
    assert r.status == TaxTypeValidationStatus.CONSISTENT


def test_mixed_zero_and_none():
    """Same-state: CGST=0, SGST=None, IGST=None → all-zero branch."""
    r = _validate(JurisdictionRelationship.SAME_STATE,
                  cgst=Decimal("0"), sgst=None, igst=None)
    assert r.status == TaxTypeValidationStatus.REVIEW_REQUIRED
