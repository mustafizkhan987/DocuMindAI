import pytest
from httpx import AsyncClient, ASGITransport
from app.services.gstin_validation_service import gstin_validation_service
from app.schemas.invoice import CanonicalInvoice, Party, Financials
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# Valid GSTIN: 29ABCDE1234F1Z5
# Let's verify its checksum manually.
# State: 29
# PAN: ABCDE1234F
# Entity: 1
# Fixed: Z
# Checksum for 29ABCDE1234F1Z: W is correct!

def test_service_valid_gstin():
    res = gstin_validation_service.validate("29ABCDE1234F1ZW")
    assert res.is_valid
    assert res.format_valid
    assert res.checksum_valid
    assert len(res.errors) == 0

def test_service_invalid_length():
    res = gstin_validation_service.validate("29ABCDE1234F1Z")
    assert not res.is_valid
    assert "INVALID_LENGTH" in res.errors

def test_service_invalid_characters():
    res = gstin_validation_service.validate("29ABCDE1234F1@5")
    assert not res.is_valid
    assert "INVALID_CHARACTERS" in res.errors

def test_service_invalid_state_code():
    res = gstin_validation_service.validate("90ABCDE1234F1Z5")
    assert not res.is_valid
    assert "INVALID_STATE_CODE" in res.errors
    
def test_service_invalid_pan_structure():
    res = gstin_validation_service.validate("291BCDE1234F1Z5")
    assert not res.is_valid
    assert "INVALID_PAN_STRUCTURE" in res.errors
    
def test_service_invalid_entity_number():
    res = gstin_validation_service.validate("29ABCDE1234F0Z5")
    assert not res.is_valid
    assert "INVALID_ENTITY_NUMBER" in res.errors
    
def test_service_incorrect_z_character():
    res = gstin_validation_service.validate("29ABCDE1234F1A5")
    assert not res.is_valid
    assert "INVALID_FIXED_CHARACTER" in res.errors

def test_service_invalid_checksum():
    res = gstin_validation_service.validate("29ABCDE1234F1Z6")
    assert not res.is_valid
    assert res.format_valid
    assert not res.checksum_valid
    assert "INVALID_CHECKSUM" in res.errors

def test_service_lowercase_handling():
    res = gstin_validation_service.validate("29abcde1234f1zw")
    assert res.is_valid
    assert res.normalized_gstin == "29ABCDE1234F1ZW"
    assert res.gstin == "29abcde1234f1zw"

def test_service_leading_trailing_whitespace():
    res = gstin_validation_service.validate("  29ABCDE1234F1ZW  ")
    assert res.is_valid
    assert res.normalized_gstin == "29ABCDE1234F1ZW"

def test_service_empty_gstin():
    res = gstin_validation_service.validate("")
    assert not res.is_valid
    assert "MISSING_GSTIN" in res.errors

def test_service_none_gstin():
    res = gstin_validation_service.validate(None)
    assert not res.is_valid
    assert "MISSING_GSTIN" in res.errors

@pytest.fixture
def mock_extraction(monkeypatch):
    def _mock(seller_gstin=None, buyer_gstin=None):
        def _get_extraction_result(self, doc_id):
            return CanonicalInvoice(
                document_id=doc_id,
                seller=Party(gstin=seller_gstin),
                buyer=Party(gstin=buyer_gstin),
                financials=Financials()
            )
        monkeypatch.setattr("app.services.extraction_service.ExtractionService.get_extraction_result", _get_extraction_result)
    return _mock

@pytest.mark.asyncio
async def test_api_seller_gstin_only(client: AsyncClient, mock_extraction):
    mock_extraction(seller_gstin="29ABCDE1234F1ZW", buyer_gstin=None)
    response = await client.post("/api/v1/documents/doc-123/validate-gstin")
    assert response.status_code == 200
    data = response.json()
    assert data["seller_gstin"]["is_valid"] is True
    assert data["buyer_gstin"]["is_valid"] is False
    assert "MISSING_GSTIN" in data["buyer_gstin"]["errors"]

@pytest.mark.asyncio
async def test_api_buyer_gstin_only(client: AsyncClient, mock_extraction):
    mock_extraction(seller_gstin=None, buyer_gstin="29ABCDE1234F1ZW")
    response = await client.post("/api/v1/documents/doc-123/validate-gstin")
    assert response.status_code == 200
    data = response.json()
    assert data["buyer_gstin"]["is_valid"] is True
    assert data["seller_gstin"]["is_valid"] is False

@pytest.mark.asyncio
async def test_api_both_valid(client: AsyncClient, mock_extraction):
    mock_extraction(seller_gstin="29ABCDE1234F1ZW", buyer_gstin="29ABCDE1234F1ZW")
    response = await client.post("/api/v1/documents/doc-123/validate-gstin")
    assert response.status_code == 200
    data = response.json()
    assert data["seller_gstin"]["is_valid"] is True
    assert data["buyer_gstin"]["is_valid"] is True

@pytest.mark.asyncio
async def test_api_seller_valid_buyer_invalid(client: AsyncClient, mock_extraction):
    mock_extraction(seller_gstin="29ABCDE1234F1ZW", buyer_gstin="29ABCDE1234F1Z6")
    response = await client.post("/api/v1/documents/doc-123/validate-gstin")
    assert response.status_code == 200
    data = response.json()
    assert data["seller_gstin"]["is_valid"] is True
    assert data["buyer_gstin"]["is_valid"] is False
    assert "INVALID_CHECKSUM" in data["buyer_gstin"]["errors"]

@pytest.mark.asyncio
async def test_api_both_invalid(client: AsyncClient, mock_extraction):
    mock_extraction(seller_gstin="29ABC", buyer_gstin="29ABC")
    response = await client.post("/api/v1/documents/doc-123/validate-gstin")
    assert response.status_code == 200
    data = response.json()
    assert data["seller_gstin"]["is_valid"] is False
    assert data["buyer_gstin"]["is_valid"] is False

@pytest.mark.asyncio
async def test_api_no_mutation(client: AsyncClient, mock_extraction):
    original = "  29abcde1234f1zw  "
    mock_extraction(seller_gstin=original, buyer_gstin=None)
    response = await client.post("/api/v1/documents/doc-123/validate-gstin")
    assert response.status_code == 200
    data = response.json()
    assert data["seller_gstin"]["gstin"] == original
    assert data["seller_gstin"]["normalized_gstin"] == "29ABCDE1234F1ZW"
