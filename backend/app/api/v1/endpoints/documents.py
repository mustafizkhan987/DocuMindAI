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
