from enum import Enum
from typing import Optional
from pydantic import BaseModel


class JurisdictionRelationship(str, Enum):
    SAME_STATE = "SAME_STATE"
    DIFFERENT_STATE = "DIFFERENT_STATE"
    SELLER_STATE_UNAVAILABLE = "SELLER_STATE_UNAVAILABLE"
    BUYER_STATE_UNAVAILABLE = "BUYER_STATE_UNAVAILABLE"
    BOTH_STATES_UNAVAILABLE = "BOTH_STATES_UNAVAILABLE"


class GSTINStateResult(BaseModel):
    gstin: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    detected: bool = False
    error: Optional[str] = None


class DocumentStateDetectionResponse(BaseModel):
    document_id: str
    seller: GSTINStateResult
    buyer: GSTINStateResult
    jurisdiction_relationship: JurisdictionRelationship
