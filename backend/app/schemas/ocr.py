from typing import List, Optional
from pydantic import BaseModel, Field

class OCRPageResult(BaseModel):
    page_number: int = Field(..., description="The page number (1-indexed)")
    text: str = Field(..., description="The raw extracted text for this page")
    confidence: Optional[float] = Field(None, description="Average confidence score for this page's text")

class OCRDocumentResult(BaseModel):
    document_id: str = Field(..., description="Unique identifier of the document")
    page_count: int = Field(..., description="Total number of pages processed")
    text: str = Field(..., description="Combined text from all pages")
    pages: List[OCRPageResult] = Field(..., description="Detailed page-by-page OCR results")
