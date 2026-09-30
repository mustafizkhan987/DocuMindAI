"""Invoice Mathematical Validation Service.

Validates deterministic arithmetic relationships within the invoice, such as:
- CGST + SGST + IGST == total_tax
- taxable_amount + total_tax == grand_total
- line item quantity * unit_price == line_total

This service relies strictly on Decimal arithmetic and requires an explicitly defined tolerance.
"""
from decimal import Decimal
from typing import List, Tuple

from app.schemas.invoice import CanonicalInvoice
from app.schemas.math_validation import (
    InvoiceMathValidationResult,
    MathCheckResult,
    MathCheckStatus,
    OverallMathStatus,
)

# Deterministic tolerance for floating/rounding issues
TOLERANCE = Decimal("0.01")


class MathValidationService:

    def validate(self, invoice: CanonicalInvoice) -> InvoiceMathValidationResult:
        """Perform mathematical validation on the canonical invoice."""
        
        checks = {}
        errors = []
        warnings = []
        
        # ------------------------------------------------------------------
        # CHECK A: Tax Total (CGST + SGST + IGST == total_tax)
        # ------------------------------------------------------------------
        cgst = invoice.financials.cgst
        sgst = invoice.financials.sgst
        igst = invoice.financials.igst
        total_tax = invoice.financials.total_tax
        
        if cgst is None or sgst is None or igst is None or total_tax is None:
            checks["tax_total"] = MathCheckResult(
                check_name="Tax Total",
                status=MathCheckStatus.REVIEW_REQUIRED,
                message="One or more tax components (CGST, SGST, IGST, total_tax) are missing."
            )
            warnings.append("Tax total check skipped due to missing tax components.")
        else:
            expected_tax = cgst + sgst + igst
            diff = abs(expected_tax - total_tax)
            if diff <= TOLERANCE:
                checks["tax_total"] = MathCheckResult(
                    check_name="Tax Total",
                    status=MathCheckStatus.PASS,
                    expected=expected_tax,
                    actual=total_tax,
                    difference=diff,
                    tolerance=TOLERANCE,
                    message="Tax components sum correctly to total tax."
                )
            else:
                checks["tax_total"] = MathCheckResult(
                    check_name="Tax Total",
                    status=MathCheckStatus.MISMATCH,
                    expected=expected_tax,
                    actual=total_tax,
                    difference=diff,
                    tolerance=TOLERANCE,
                    message=f"Tax components sum ({expected_tax}) does not match total tax ({total_tax})."
                )
                errors.append(checks["tax_total"].message)

        # ------------------------------------------------------------------
        # CHECK B: Grand Total (taxable_amount + total_tax == grand_total)
        # ------------------------------------------------------------------
        taxable_amount = invoice.financials.taxable_amount
        grand_total = invoice.financials.grand_total
        
        if taxable_amount is None or total_tax is None or grand_total is None:
            checks["grand_total"] = MathCheckResult(
                check_name="Grand Total",
                status=MathCheckStatus.REVIEW_REQUIRED,
                message="One or more components (taxable_amount, total_tax, grand_total) are missing."
            )
            warnings.append("Grand total check skipped due to missing components.")
        else:
            expected_grand_total = taxable_amount + total_tax
            diff = abs(expected_grand_total - grand_total)
            if diff <= TOLERANCE:
                checks["grand_total"] = MathCheckResult(
                    check_name="Grand Total",
                    status=MathCheckStatus.PASS,
                    expected=expected_grand_total,
                    actual=grand_total,
                    difference=diff,
                    tolerance=TOLERANCE,
                    message="Taxable amount and total tax sum correctly to grand total."
                )
            else:
                checks["grand_total"] = MathCheckResult(
                    check_name="Grand Total",
                    status=MathCheckStatus.MISMATCH,
                    expected=expected_grand_total,
                    actual=grand_total,
                    difference=diff,
                    tolerance=TOLERANCE,
                    message=f"Taxable amount + total tax ({expected_grand_total}) does not match grand total ({grand_total})."
                )
                errors.append(checks["grand_total"].message)

        # ------------------------------------------------------------------
        # CHECK C: Line Item Arithmetic (quantity * unit_price == total)
        # ------------------------------------------------------------------
        if not invoice.line_items:
            checks["line_items"] = MathCheckResult(
                check_name="Line Items",
                status=MathCheckStatus.NOT_CHECKED,
                message="No line items found."
            )
        else:
            line_items_missing_data = False
            line_item_mismatch = False
            mismatch_details = []
            
            for idx, item in enumerate(invoice.line_items):
                if item.quantity is None or item.unit_price is None or item.total is None:
                    line_items_missing_data = True
                    continue
                
                expected_total = item.quantity * item.unit_price
                diff = abs(expected_total - item.total)
                if diff > TOLERANCE:
                    line_item_mismatch = True
                    mismatch_details.append(
                        f"Line {idx+1}: {item.quantity} * {item.unit_price} = {expected_total} != {item.total}"
                    )
            
            if line_item_mismatch:
                checks["line_items"] = MathCheckResult(
                    check_name="Line Items",
                    status=MathCheckStatus.MISMATCH,
                    message="One or more line items have mismatched quantity * unit_price totals.",
                    tolerance=TOLERANCE,
                )
                errors.extend(mismatch_details)
            elif line_items_missing_data:
                checks["line_items"] = MathCheckResult(
                    check_name="Line Items",
                    status=MathCheckStatus.REVIEW_REQUIRED,
                    message="Some line items lacked quantity, unit_price, or total for validation."
                )
                warnings.append(checks["line_items"].message)
            else:
                checks["line_items"] = MathCheckResult(
                    check_name="Line Items",
                    status=MathCheckStatus.PASS,
                    message="All line items with quantity and unit price match their totals.",
                    tolerance=TOLERANCE,
                )

        # ------------------------------------------------------------------
        # OVERALL STATUS LOGIC
        # ------------------------------------------------------------------
        has_mismatch = any(c.status == MathCheckStatus.MISMATCH for c in checks.values())
        has_review_required = any(c.status == MathCheckStatus.REVIEW_REQUIRED for c in checks.values())
        
        if has_mismatch:
            overall_status = OverallMathStatus.MISMATCH
            overall_consistent = False
        elif has_review_required:
            overall_status = OverallMathStatus.REVIEW_REQUIRED
            overall_consistent = False
        else:
            overall_status = OverallMathStatus.CONSISTENT
            overall_consistent = True

        return InvoiceMathValidationResult(
            document_id=invoice.document_id,
            status=overall_status,
            overall_consistent=overall_consistent,
            checks=checks,
            errors=errors,
            warnings=warnings,
        )

math_validation_service = MathValidationService()
