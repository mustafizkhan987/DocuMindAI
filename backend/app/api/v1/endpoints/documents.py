from fastapi import APIRouter, File, UploadFile, status
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import document_service

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document securely.
    """
    return document_service.save_upload_file(file)

from app.services.preprocessing_service import PreprocessingService
preprocessing_service = PreprocessingService()

@router.post("/{document_id}/preprocess")
async def preprocess_document(document_id: str):
    """
    Preprocess a document for OCR.
    """
    path, mime_type = document_service.get_document_path_and_mime_type(document_id)
    return preprocessing_service.process_document(document_id, str(path), mime_type)

from app.services.ocr_service import ocr_service
from app.schemas.ocr import OCRDocumentResult

@router.post("/{document_id}/ocr", response_model=OCRDocumentResult)
async def extract_text(document_id: str):
    """
    Extract raw text from a preprocessed document using OCR.
    Requires preprocessing to have been completed.
    """
    return ocr_service.extract_text(document_id)

from app.services.classification_service import classification_service
from app.schemas.classification import ClassificationResult

@router.post("/{document_id}/classify", response_model=ClassificationResult)
async def classify_document(document_id: str):
    """
    Classify a document type based on its extracted OCR text.
    Requires OCR to have been completed.
    """
    return classification_service.classify_document(document_id)

from app.services.extraction_service import extraction_service
from app.schemas.invoice import InvoiceExtractionResult

@router.post("/{document_id}/extract", response_model=InvoiceExtractionResult)
async def extract_invoice(document_id: str):
    """
    Extract structured invoice information from an OCR'd and classified document.
    Requires classification result to be INVOICE.
    """
    return extraction_service.extract_invoice(document_id)

from app.services.gstin_validation_service import gstin_validation_service
from app.schemas.validation import DocumentGSTINValidationResponse
from app.schemas.classification import DocumentType
from fastapi import HTTPException

@router.post("/{document_id}/validate-gstin", response_model=DocumentGSTINValidationResponse)
async def validate_gstin(document_id: str):
    """
    Validate GSTIN format and checksum for seller and buyer from the extracted invoice.
    Requires classification as INVOICE and extraction to have been completed.
    Note: This performs structural/checksum validation, not government registration verification.
    """
    # Explicit invoice classification gate
    classification_result = classification_service.classify_document(document_id)
    if classification_result.document_type != DocumentType.INVOICE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GSTIN validation is only available for documents classified as Invoice."
        )

    invoice = extraction_service.get_extraction_result(document_id)

    seller_gstin = invoice.seller.gstin if invoice.seller else None
    buyer_gstin = invoice.buyer.gstin if invoice.buyer else None

    return DocumentGSTINValidationResponse(
        document_id=document_id,
        seller_gstin=gstin_validation_service.validate(seller_gstin),
        buyer_gstin=gstin_validation_service.validate(buyer_gstin)
    )

from app.services.state_detection_service import state_detection_service
from app.schemas.state_detection import DocumentStateDetectionResponse

@router.post("/{document_id}/detect-state", response_model=DocumentStateDetectionResponse)
async def detect_state(document_id: str):
    """
    Detect seller and buyer state/jurisdiction from their GSTINs.
    Requires classification as INVOICE and extraction to have been completed.
    Returns state codes, names, and whether parties are in the same or different state.
    Does NOT draw any tax conclusions (CGST/SGST/IGST).
    """
    # Explicit invoice classification gate
    classification_result = classification_service.classify_document(document_id)
    if classification_result.document_type != DocumentType.INVOICE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State detection is only available for documents classified as Invoice."
        )

    invoice = extraction_service.get_extraction_result(document_id)

    seller_gstin = invoice.seller.gstin if invoice.seller else None
    buyer_gstin = invoice.buyer.gstin if invoice.buyer else None

    seller_state = state_detection_service.detect_state(seller_gstin)
    buyer_state = state_detection_service.detect_state(buyer_gstin)
    relationship = state_detection_service.compare_jurisdictions(seller_state, buyer_state)

    return DocumentStateDetectionResponse(
        document_id=document_id,
        seller=seller_state,
        buyer=buyer_state,
        jurisdiction_relationship=relationship
    )

from app.services.gst_tax_type_validation_service import gst_tax_type_validation_service
from app.schemas.tax_type_validation import GSTTaxTypeValidationResult

@router.post("/{document_id}/validate-tax-type", response_model=GSTTaxTypeValidationResult)
async def validate_tax_type(document_id: str):
    """
    Validate the GST tax component type (CGST+SGST vs IGST) against the
    seller/buyer jurisdiction relationship.
    Requires classification as INVOICE and extraction to have been completed.
    Does NOT validate tax rates, amounts, or invoice arithmetic.
    """
    # Explicit invoice classification gate
    classification_result = classification_service.classify_document(document_id)
    if classification_result.document_type != DocumentType.INVOICE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax type validation is only available for documents classified as Invoice."
        )

    invoice = extraction_service.get_extraction_result(document_id)

    # Obtain jurisdiction via Task 12
    seller_gstin = invoice.seller.gstin if invoice.seller else None
    buyer_gstin = invoice.buyer.gstin if invoice.buyer else None
    seller_state = state_detection_service.detect_state(seller_gstin)
    buyer_state = state_detection_service.detect_state(buyer_gstin)
    relationship = state_detection_service.compare_jurisdictions(seller_state, buyer_state)

    return gst_tax_type_validation_service.validate(
        document_id=document_id,
        jurisdiction=relationship,
        financials=invoice.financials,
    )

from app.services.math_validation_service import math_validation_service
from app.schemas.math_validation import InvoiceMathValidationResult

@router.post("/{document_id}/validate-math", response_model=InvoiceMathValidationResult)
async def validate_math(document_id: str):
    """
    Validate deterministic arithmetic relationships within the invoice.
    Requires classification as INVOICE and extraction to have been completed.
    Does NOT validate tax-type rules, tax rates, or GSTINs.
    """
    # Explicit invoice classification gate
    classification_result = classification_service.classify_document(document_id)
    if classification_result.document_type != DocumentType.INVOICE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mathematical validation is only available for documents classified as Invoice."
        )

    invoice = extraction_service.get_extraction_result(document_id)

    return math_validation_service.validate(invoice)
