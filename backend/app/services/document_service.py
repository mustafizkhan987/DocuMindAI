import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
from app.schemas.document import DocumentUploadResponse

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}

class DocumentService:
    def validate_file(self, file: UploadFile) -> tuple[str, str]:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        
        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
            
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
            
        return file.content_type, ALLOWED_MIME_TYPES[file.content_type]

    def save_upload_file(self, upload_file: UploadFile) -> DocumentUploadResponse:
        mime_type, extension = self.validate_file(upload_file)
        
        storage_dir = Path(settings.STORAGE_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        document_id = str(uuid.uuid4())
        stored_filename = f"{document_id}{extension}"
        stored_filepath = storage_dir / stored_filename
        
        upload_file.file.seek(0, os.SEEK_END)
        size_bytes = upload_file.file.tell()
        upload_file.file.seek(0)
        
        with open(stored_filepath, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return DocumentUploadResponse(
            document_id=document_id,
            original_filename=upload_file.filename or "unknown",
            stored_filename=stored_filename,
            content_type=mime_type,
            size_bytes=size_bytes,
        )

document_service = DocumentService()
