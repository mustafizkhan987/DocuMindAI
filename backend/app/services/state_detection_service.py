from typing import Optional

from app.schemas.state_detection import (
    GSTINStateResult,
    DocumentStateDetectionResponse,
    JurisdictionRelationship,
)
from app.services.gstin_validation_service import gstin_validation_service
from app.utils.gst_state_codes import GST_STATE_CODES


class StateDetectionService:
    """Deterministic GSTIN state / jurisdiction detection.

    Given a GSTIN string this service:
    1. Delegates structural validation to GSTINValidationService (Task 11).
    2. Extracts the two-digit state code from a *valid* GSTIN.
    3. Maps the code to the canonical state name via GST_STATE_CODES.

    It deliberately does NOT draw any tax conclusions
    (e.g. IGST vs CGST+SGST).  Those belong to Task 13.
    """

    def detect_state(self, gstin: Optional[str]) -> GSTINStateResult:
        """Detect the state from a single GSTIN string."""
        result = GSTINStateResult(gstin=gstin)

        if not gstin or not str(gstin).strip():
            result.error = "GSTIN not provided"
            return result

        # Delegate to Task 11 for structural validation
        validation = gstin_validation_service.validate(gstin)

        if not validation.is_valid:
            result.error = (
                "State detection requires a structurally valid GSTIN. "
                f"Validation errors: {', '.join(validation.errors)}"
            )
            return result

        # Extract state code from the validated, normalized GSTIN
        normalized = validation.normalized_gstin
        state_code = normalized[:2]
        state_name = GST_STATE_CODES.get(state_code)

        if state_name is None:
            result.error = f"Unknown state code: {state_code}"
            return result

        result.state_code = state_code
        result.state_name = state_name
        result.detected = True
        return result

    def compare_jurisdictions(
        self,
        seller_result: GSTINStateResult,
        buyer_result: GSTINStateResult,
    ) -> JurisdictionRelationship:
        """Determine the relationship between seller and buyer jurisdictions."""
        seller_ok = seller_result.detected
        buyer_ok = buyer_result.detected

        if not seller_ok and not buyer_ok:
            return JurisdictionRelationship.BOTH_STATES_UNAVAILABLE
        if not seller_ok:
            return JurisdictionRelationship.SELLER_STATE_UNAVAILABLE
        if not buyer_ok:
            return JurisdictionRelationship.BUYER_STATE_UNAVAILABLE

        if seller_result.state_code == buyer_result.state_code:
            return JurisdictionRelationship.SAME_STATE
        return JurisdictionRelationship.DIFFERENT_STATE


state_detection_service = StateDetectionService()
