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

