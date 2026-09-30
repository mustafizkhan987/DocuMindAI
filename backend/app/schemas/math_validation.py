from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class MathCheckStatus(str, Enum):
    PASS = "PASS"
    MISMATCH = "MISMATCH"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_CHECKED = "NOT_CHECKED"

class OverallMathStatus(str, Enum):
    CONSISTENT = "CONSISTENT"
    MISMATCH = "MISMATCH"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

class MathCheckResult(BaseModel):
    check_name: str
    status: MathCheckStatus
    expected: Optional[Decimal] = None
    actual: Optional[Decimal] = None
    difference: Optional[Decimal] = None
    tolerance: Optional[Decimal] = None
    message: str

class InvoiceMathValidationResult(BaseModel):
    document_id: str
    status: OverallMathStatus
    overall_consistent: bool
    checks: Dict[str, MathCheckResult] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
