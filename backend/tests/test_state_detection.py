import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.state_detection_service import state_detection_service
from app.schemas.state_detection import JurisdictionRelationship
from app.schemas.invoice import CanonicalInvoice, Party, Financials
from app.utils.gst_state_codes import GST_STATE_CODES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
def mock_invoice_pipeline(monkeypatch):
    """Mock classification (INVOICE) + extraction for API tests."""
    from app.schemas.classification import ClassificationResult, DocumentType

    def _mock(seller_gstin=None, buyer_gstin=None):
        def _classify(self, doc_id):
            return ClassificationResult(
                document_id=doc_id,
                document_type=DocumentType.INVOICE,
                confidence=0.95,
                signals=["TAX INVOICE"]
            )

        def _get_extraction_result(self, doc_id):
            return CanonicalInvoice(
                document_id=doc_id,
                seller=Party(gstin=seller_gstin),
                buyer=Party(gstin=buyer_gstin),
                financials=Financials()
            )

        monkeypatch.setattr(
            "app.services.classification_service.ClassificationService.classify_document",
            _classify
        )
        monkeypatch.setattr(
            "app.services.extraction_service.ExtractionService.get_extraction_result",
            _get_extraction_result
        )
    return _mock


# ---------------------------------------------------------------------------
# Valid GSTINs with correct checksums for specific states
# (computed deterministically using the Modulo‑36 algorithm)
# ---------------------------------------------------------------------------
GSTIN_KARNATAKA    = "29ABCDE1234F1ZW"  # state 29
GSTIN_MAHARASHTRA  = "27ABCDE1234F1Z0"  # state 27
GSTIN_TAMIL_NADU   = "33ABCDE1234F1Z7"  # state 33
GSTIN_TELANGANA    = "36ABCDE1234F1Z1"  # state 36
GSTIN_KERALA       = "32ABCDE1234F1Z9"  # state 32
GSTIN_DELHI        = "07ABCDE1234F1Z2"  # state 07
GSTIN_UP           = "09ABCDE1234F1ZY"  # state 09
GSTIN_GUJARAT      = "24ABCDE1234F1Z6"  # state 24


# ===========================================================================
# Unit tests — StateDetectionService.detect_state
# ===========================================================================

def test_detect_karnataka():
    r = state_detection_service.detect_state(GSTIN_KARNATAKA)
    assert r.detected is True
    assert r.state_code == "29"
    assert r.state_name == "Karnataka"

def test_detect_maharashtra():
    r = state_detection_service.detect_state(GSTIN_MAHARASHTRA)
    assert r.detected is True
    assert r.state_code == "27"
    assert r.state_name == "Maharashtra"

def test_detect_tamil_nadu():
    r = state_detection_service.detect_state(GSTIN_TAMIL_NADU)
    assert r.detected is True
    assert r.state_code == "33"
    assert r.state_name == "Tamil Nadu"

def test_detect_telangana():
    r = state_detection_service.detect_state(GSTIN_TELANGANA)
    assert r.detected is True
    assert r.state_code == "36"
    assert r.state_name == "Telangana"

def test_detect_kerala():
    r = state_detection_service.detect_state(GSTIN_KERALA)
    assert r.detected is True
    assert r.state_code == "32"
    assert r.state_name == "Kerala"

def test_detect_delhi():
    r = state_detection_service.detect_state(GSTIN_DELHI)
    assert r.detected is True
    assert r.state_code == "07"
    assert r.state_name == "Delhi"

def test_detect_uttar_pradesh():
    r = state_detection_service.detect_state(GSTIN_UP)
    assert r.detected is True
    assert r.state_code == "09"
    assert r.state_name == "Uttar Pradesh"

def test_detect_gujarat():
    r = state_detection_service.detect_state(GSTIN_GUJARAT)
    assert r.detected is True
    assert r.state_code == "24"
    assert r.state_name == "Gujarat"


def test_all_mapped_state_codes_are_present():
    """Verify the mapping covers codes 01–38 plus specials."""
    for code_int in range(1, 39):
        code = f"{code_int:02d}"
        assert code in GST_STATE_CODES, f"Missing state code {code}"
    assert "97" in GST_STATE_CODES
    assert "99" in GST_STATE_CODES


# ===========================================================================
# Invalid / missing GSTIN
# ===========================================================================

def test_detect_invalid_gstin():
    """Structurally invalid GSTIN must NOT produce a detected state."""
    r = state_detection_service.detect_state("29ABCDE1234F1Z6")  # bad checksum
    assert r.detected is False
    assert r.state_code is None
    assert r.error is not None
    assert "INVALID_CHECKSUM" in r.error

def test_detect_malformed_gstin():
    r = state_detection_service.detect_state("NOTAVALIDGSTIN!")
    assert r.detected is False

def test_detect_missing_gstin_none():
    r = state_detection_service.detect_state(None)
    assert r.detected is False
    assert r.error is not None

def test_detect_missing_gstin_empty():
    r = state_detection_service.detect_state("")
    assert r.detected is False
    assert r.error is not None


# ===========================================================================
# Jurisdiction comparison
# ===========================================================================

def test_compare_same_state():
    s = state_detection_service.detect_state(GSTIN_KARNATAKA)
    b = state_detection_service.detect_state(GSTIN_KARNATAKA)
    assert state_detection_service.compare_jurisdictions(s, b) == JurisdictionRelationship.SAME_STATE

def test_compare_different_state():
    s = state_detection_service.detect_state(GSTIN_KARNATAKA)
    b = state_detection_service.detect_state(GSTIN_MAHARASHTRA)
    assert state_detection_service.compare_jurisdictions(s, b) == JurisdictionRelationship.DIFFERENT_STATE

def test_compare_seller_unavailable():
    s = state_detection_service.detect_state(None)
    b = state_detection_service.detect_state(GSTIN_MAHARASHTRA)
    assert state_detection_service.compare_jurisdictions(s, b) == JurisdictionRelationship.SELLER_STATE_UNAVAILABLE

def test_compare_buyer_unavailable():
    s = state_detection_service.detect_state(GSTIN_KARNATAKA)
    b = state_detection_service.detect_state(None)
    assert state_detection_service.compare_jurisdictions(s, b) == JurisdictionRelationship.BUYER_STATE_UNAVAILABLE

def test_compare_both_unavailable():
    s = state_detection_service.detect_state(None)
    b = state_detection_service.detect_state(None)
    assert state_detection_service.compare_jurisdictions(s, b) == JurisdictionRelationship.BOTH_STATES_UNAVAILABLE


# ===========================================================================
# Verify NO tax conclusions appear in the result
# ===========================================================================

def test_no_tax_conclusion_in_result():
    """Ensure the service does not embed IGST/CGST/SGST conclusions."""
    s = state_detection_service.detect_state(GSTIN_KARNATAKA)
    b = state_detection_service.detect_state(GSTIN_MAHARASHTRA)
    rel = state_detection_service.compare_jurisdictions(s, b)
    assert rel == JurisdictionRelationship.DIFFERENT_STATE
    # Must NOT contain tax keywords
    result_text = f"{s} {b} {rel}"
    for forbidden in ("IGST", "CGST", "SGST", "TAX"):
        assert forbidden not in result_text


# ===========================================================================
# API integration tests
# ===========================================================================

@pytest.mark.asyncio
async def test_api_same_state(client: AsyncClient, mock_invoice_pipeline):
    mock_invoice_pipeline(seller_gstin=GSTIN_KARNATAKA, buyer_gstin=GSTIN_KARNATAKA)
    resp = await client.post("/api/v1/documents/doc-1/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["seller"]["detected"] is True
    assert data["seller"]["state_code"] == "29"
    assert data["seller"]["state_name"] == "Karnataka"
    assert data["buyer"]["detected"] is True
    assert data["jurisdiction_relationship"] == "SAME_STATE"

@pytest.mark.asyncio
async def test_api_different_state(client: AsyncClient, mock_invoice_pipeline):
    mock_invoice_pipeline(seller_gstin=GSTIN_KARNATAKA, buyer_gstin=GSTIN_MAHARASHTRA)
    resp = await client.post("/api/v1/documents/doc-2/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["seller"]["state_name"] == "Karnataka"
    assert data["buyer"]["state_name"] == "Maharashtra"
    assert data["jurisdiction_relationship"] == "DIFFERENT_STATE"

@pytest.mark.asyncio
async def test_api_seller_only(client: AsyncClient, mock_invoice_pipeline):
    mock_invoice_pipeline(seller_gstin=GSTIN_KARNATAKA, buyer_gstin=None)
    resp = await client.post("/api/v1/documents/doc-3/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["seller"]["detected"] is True
    assert data["buyer"]["detected"] is False
    assert data["jurisdiction_relationship"] == "BUYER_STATE_UNAVAILABLE"

@pytest.mark.asyncio
async def test_api_buyer_only(client: AsyncClient, mock_invoice_pipeline):
    mock_invoice_pipeline(seller_gstin=None, buyer_gstin=GSTIN_MAHARASHTRA)
    resp = await client.post("/api/v1/documents/doc-4/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["seller"]["detected"] is False
    assert data["buyer"]["detected"] is True
    assert data["jurisdiction_relationship"] == "SELLER_STATE_UNAVAILABLE"

@pytest.mark.asyncio
async def test_api_both_missing(client: AsyncClient, mock_invoice_pipeline):
    mock_invoice_pipeline(seller_gstin=None, buyer_gstin=None)
    resp = await client.post("/api/v1/documents/doc-5/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["jurisdiction_relationship"] == "BOTH_STATES_UNAVAILABLE"

@pytest.mark.asyncio
async def test_api_non_invoice_rejected(client: AsyncClient, monkeypatch):
    from app.schemas.classification import ClassificationResult, DocumentType

    def _classify_receipt(self, doc_id):
        return ClassificationResult(
            document_id=doc_id,
            document_type=DocumentType.RECEIPT,
            confidence=0.90,
            signals=["RECEIPT"]
        )

    monkeypatch.setattr(
        "app.services.classification_service.ClassificationService.classify_document",
        _classify_receipt
    )

    resp = await client.post("/api/v1/documents/receipt-doc/detect-state")
    assert resp.status_code == 400
    assert "only available for documents classified as Invoice" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_api_invalid_gstin_no_state(client: AsyncClient, mock_invoice_pipeline):
    """Invalid GSTIN must not produce a detected state through the API."""
    mock_invoice_pipeline(seller_gstin="29ABCDE1234F1Z6", buyer_gstin=GSTIN_MAHARASHTRA)
    resp = await client.post("/api/v1/documents/doc-6/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["seller"]["detected"] is False
    assert data["buyer"]["detected"] is True
    assert data["jurisdiction_relationship"] == "SELLER_STATE_UNAVAILABLE"

@pytest.mark.asyncio
async def test_api_response_schema(client: AsyncClient, mock_invoice_pipeline):
    """Verify the top-level response keys."""
    mock_invoice_pipeline(seller_gstin=GSTIN_KARNATAKA, buyer_gstin=GSTIN_MAHARASHTRA)
    resp = await client.post("/api/v1/documents/doc-schema/detect-state")
    assert resp.status_code == 200
    data = resp.json()
    assert "document_id" in data
    assert "seller" in data
    assert "buyer" in data
    assert "jurisdiction_relationship" in data
    # Seller sub-keys
    for key in ("gstin", "state_code", "state_name", "detected"):
        assert key in data["seller"]
