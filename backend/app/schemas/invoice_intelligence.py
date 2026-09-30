from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.classification import ClassificationResult, DocumentType
from app.schemas.invoice import CanonicalInvoice
from app.schemas.validation import DocumentGSTINValidationResponse
from app.schemas.state_detection import DocumentStateDetectionResponse
from app.schemas.tax_type_validation import GSTTaxTypeValidationResult
from app.schemas.math_validation import InvoiceMathValidationResult


class IntelligenceOverallStatus(str, Enum):
    INFORMATION_FOUND = "INFORMATION_FOUND"
    CONSISTENT = "CONSISTENT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    MISMATCH = "MISMATCH"


class IntelligenceIssueStatus(str, Enum):
    MISMATCH = "MISMATCH"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    INFO = "INFO"


class IntelligenceIssue(BaseModel):
    category: str
    status: IntelligenceIssueStatus
    field: Optional[str] = None
    explanation: str
    recommendation: Optional[str] = None


class InvoiceIntelligenceResult(BaseModel):
    document_id: str
    document_type: DocumentType
    overall_status: IntelligenceOverallStatus
    summary: str
    
    classification: ClassificationResult
    extraction: Optional[CanonicalInvoice] = None
    gstin_validation: Optional[DocumentGSTINValidationResponse] = None
    state_detection: Optional[DocumentStateDetectionResponse] = None
    tax_type_validation: Optional[GSTTaxTypeValidationResult] = None
    mathematical_validation: Optional[InvoiceMathValidationResult] = None
    
    issues: List[IntelligenceIssue] = Field(default_factory=list)
