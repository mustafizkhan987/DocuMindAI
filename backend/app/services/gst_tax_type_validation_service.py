"""GST Tax Type Validation Service.

Determines whether an invoice's tax COMPONENT TYPE (CGST+SGST vs IGST)
is consistent with the seller/buyer jurisdiction relationship established
by Task 12.

This service does NOT:
- validate tax rates or percentages
- calculate tax amounts
- verify mathematical totals
- contact any government API

Those responsibilities belong to Task 14 and beyond.
"""

from decimal import Decimal
from typing import Optional

from app.schemas.invoice import Financials
from app.schemas.state_detection import JurisdictionRelationship
from app.schemas.tax_type_validation import (
    ActualTaxComponents,
    ExpectedTaxType,
    GSTTaxTypeValidationResult,
    TaxTypeValidationStatus,
)


def _is_positive(value: Optional[Decimal]) -> bool:
    """True if the value is not None and strictly greater than zero."""
    return value is not None and value > 0


def _is_zero(value: Optional[Decimal]) -> bool:
    """True if the value is not None and exactly zero."""
    return value is not None and value == 0


def _is_missing(value: Optional[Decimal]) -> bool:
    """True if the value was never extracted (None)."""
    return value is None


class GSTTaxTypeValidationService:

    def validate(
        self,
        document_id: str,
        jurisdiction: JurisdictionRelationship,
        financials: Financials,
    ) -> GSTTaxTypeValidationResult:
        """Compare expected tax structure with extracted tax components."""

        actual = ActualTaxComponents(
            cgst=financials.cgst,
            sgst=financials.sgst,
            igst=financials.igst,
        )

        # ------------------------------------------------------------------
        # 1. Jurisdiction unavailable → cannot determine expected tax type
        # ------------------------------------------------------------------
        if jurisdiction not in (
            JurisdictionRelationship.SAME_STATE,
            JurisdictionRelationship.DIFFERENT_STATE,
        ):
            return GSTTaxTypeValidationResult(
                document_id=document_id,
                jurisdiction_relationship=jurisdiction,
                expected_tax_type=ExpectedTaxType.UNKNOWN,
                actual_tax_components=actual,
                is_consistent=False,
                status=TaxTypeValidationStatus.JURISDICTION_UNAVAILABLE,
                warnings=["Jurisdiction could not be determined; tax-type validation skipped."],
            )

        # ------------------------------------------------------------------
        # 2. Determine expected tax type
        # ------------------------------------------------------------------
        if jurisdiction == JurisdictionRelationship.SAME_STATE:
            expected = ExpectedTaxType.CGST_SGST
        else:
            expected = ExpectedTaxType.IGST

        # ------------------------------------------------------------------
        # 3. Check if all tax fields are missing
        # ------------------------------------------------------------------
        all_missing = (
            _is_missing(financials.cgst)
            and _is_missing(financials.sgst)
            and _is_missing(financials.igst)
        )
        if all_missing:
            return GSTTaxTypeValidationResult(
                document_id=document_id,
                jurisdiction_relationship=jurisdiction,
                expected_tax_type=expected,
                actual_tax_components=actual,
                is_consistent=False,
                status=TaxTypeValidationStatus.REVIEW_REQUIRED,
                warnings=["All tax fields are missing from the extracted invoice."],
            )

        # ------------------------------------------------------------------
        # 4. Check if all tax fields are zero
        # ------------------------------------------------------------------
        all_zero = (
            _is_zero(financials.cgst) or _is_missing(financials.cgst)
        ) and (
            _is_zero(financials.sgst) or _is_missing(financials.sgst)
        ) and (
            _is_zero(financials.igst) or _is_missing(financials.igst)
        )
        # But at least one must be explicitly zero (not all missing, handled above)
        has_any_zero = (
            _is_zero(financials.cgst)
            or _is_zero(financials.sgst)
            or _is_zero(financials.igst)
        )
        if all_zero and has_any_zero:
            return GSTTaxTypeValidationResult(
                document_id=document_id,
                jurisdiction_relationship=jurisdiction,
                expected_tax_type=expected,
                actual_tax_components=actual,
                is_consistent=False,
                status=TaxTypeValidationStatus.REVIEW_REQUIRED,
                warnings=[
                    "All extracted tax amounts are zero or missing. "
                    "This may indicate an exempt supply or an extraction gap."
                ],
            )

        # ------------------------------------------------------------------
        # 5. Apply tax-type structure rules
        # ------------------------------------------------------------------
        errors = []
        warnings = []
        
        has_missing = (
            _is_missing(financials.cgst) or
            _is_missing(financials.sgst) or
            _is_missing(financials.igst)
        )

        if expected == ExpectedTaxType.CGST_SGST:
            # Same-state: expect CGST>0 AND SGST>0, IGST absent or zero
            if has_missing:
                return GSTTaxTypeValidationResult(
                    document_id=document_id,
                    jurisdiction_relationship=jurisdiction,
                    expected_tax_type=expected,
                    actual_tax_components=actual,
                    is_consistent=False,
                    status=TaxTypeValidationStatus.REVIEW_REQUIRED,
                    warnings=["One or more tax components are missing, manual review required."],
                )
                
            consistent = True

            if _is_zero(financials.cgst):
                consistent = False
                errors.append("CGST expected for same-state transaction but is explicitly zero.")

            if _is_zero(financials.sgst):
                consistent = False
                errors.append("SGST expected for same-state transaction but is explicitly zero.")

            if _is_positive(financials.igst):
                consistent = False
                errors.append("IGST present in a same-state transaction where CGST+SGST is expected.")

        else:  # IGST
            # Different-state: expect IGST>0, CGST/SGST absent or zero
            if has_missing:
                return GSTTaxTypeValidationResult(
                    document_id=document_id,
                    jurisdiction_relationship=jurisdiction,
                    expected_tax_type=expected,
                    actual_tax_components=actual,
                    is_consistent=False,
                    status=TaxTypeValidationStatus.REVIEW_REQUIRED,
                    warnings=["One or more tax components are missing, manual review required."],
                )
                
            consistent = True

            if _is_zero(financials.igst):
                consistent = False
                errors.append("IGST expected for different-state transaction but is explicitly zero.")

            if _is_positive(financials.cgst):
                consistent = False
                errors.append("CGST present in a different-state transaction where only IGST is expected.")

            if _is_positive(financials.sgst):
                consistent = False
                errors.append("SGST present in a different-state transaction where only IGST is expected.")

        status = (
            TaxTypeValidationStatus.CONSISTENT
            if consistent
            else TaxTypeValidationStatus.MISMATCH
        )

        return GSTTaxTypeValidationResult(
            document_id=document_id,
            jurisdiction_relationship=jurisdiction,
            expected_tax_type=expected,
            actual_tax_components=actual,
            is_consistent=consistent,
            status=status,
            errors=errors,
            warnings=warnings,
        )


gst_tax_type_validation_service = GSTTaxTypeValidationService()
