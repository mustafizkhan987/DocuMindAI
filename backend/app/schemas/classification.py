from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    BILL = "BILL"
    OTHER = "OTHER"

class ClassificationResult(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the document")
    document_type: DocumentType = Field(..., description="The predicted class of the document")
    confidence: float = Field(..., description="Confidence score normalized between 0.0 and 1.0")
    signals: List[str] = Field(default_factory=list, description="List of matched keywords or signals justifying the decision")
