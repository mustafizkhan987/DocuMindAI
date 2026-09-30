from typing import List, Optional, Dict
from pydantic import BaseModel

class GSTINValidationResult(BaseModel):
    gstin: Optional[str] = None
    normalized_gstin: Optional[str] = None
    is_valid: bool = False
    format_valid: bool = False
    checksum_valid: bool = False
    errors: List[str] = []
    warnings: List[str] = []

class DocumentGSTINValidationResponse(BaseModel):
    document_id: str
    seller_gstin: GSTINValidationResult
    buyer_gstin: GSTINValidationResult
