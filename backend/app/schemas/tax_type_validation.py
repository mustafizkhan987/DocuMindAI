from enum import Enum
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel

from app.schemas.state_detection import JurisdictionRelationship


class ExpectedTaxType(str, Enum):
    """The tax structure expected based on seller/buyer jurisdiction."""
    CGST_SGST = "CGST_SGST"
    IGST = "IGST"
    UNKNOWN = "UNKNOWN"


class TaxTypeValidationStatus(str, Enum):
    """Overall result status of the tax-type validation."""
    CONSISTENT = "CONSISTENT"
    MISMATCH = "MISMATCH"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    JURISDICTION_UNAVAILABLE = "JURISDICTION_UNAVAILABLE"


class ActualTaxComponents(BaseModel):
    """Snapshot of the tax components extracted from the canonical invoice.

    Uses Optional[Decimal] to preserve the critical distinction between
    a field that was never extracted (None) and a field that was
    explicitly extracted as zero (Decimal("0")).
    """
    cgst: Optional[Decimal] = None
    sgst: Optional[Decimal] = None
    igst: Optional[Decimal] = None


class GSTTaxTypeValidationResult(BaseModel):
    document_id: str
    jurisdiction_relationship: JurisdictionRelationship
    expected_tax_type: ExpectedTaxType
    actual_tax_components: ActualTaxComponents
    is_consistent: bool = False
    status: TaxTypeValidationStatus
    errors: List[str] = []
    warnings: List[str] = []
