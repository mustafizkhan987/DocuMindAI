from pydantic import BaseModel, Field
from datetime import datetime, timezone

def get_utc_now():
    return datetime.now(timezone.utc)

class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the uploaded document")
    original_filename: str = Field(..., description="Original name of the uploaded file")
    stored_filename: str = Field(..., description="Safe filename used for local storage")
    content_type: str = Field(..., description="MIME type of the document")
    size_bytes: int = Field(..., description="Size of the document in bytes")
    upload_timestamp: datetime = Field(default_factory=get_utc_now, description="Time of upload")
    status: str = Field(default="uploaded", description="Status of the document")
