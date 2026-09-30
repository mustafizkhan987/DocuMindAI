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
