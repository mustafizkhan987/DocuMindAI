# Task 13 — GST Tax Type Validation

## Status
COMPLETED

## Date
2026-09-30

## Objective
Implement deterministic GST tax type validation. Given the seller/buyer jurisdiction relationship (from Task 12) and the extracted tax components (CGST, SGST, IGST), determine whether the invoice's tax COMPONENT TYPE is consistent with the jurisdiction.

## Context
Task 12 established state detection and jurisdiction comparison (SAME_STATE vs DIFFERENT_STATE). Task 13 consumes that relationship to validate whether the correct tax structure was applied:
- **SAME_STATE** → expected CGST + SGST
- **DIFFERENT_STATE** → expected IGST

Task 13 does NOT validate tax rates, amounts, or invoice arithmetic. Those responsibilities belong to Task 14.

## Work Completed
- Created `GSTTaxTypeValidationService` with deterministic tax-type structure comparison.
- Created Pydantic schemas with enums for expected tax type (`CGST_SGST`, `IGST`, `UNKNOWN`) and validation status (`CONSISTENT`, `MISMATCH`, `REVIEW_REQUIRED`, `JURISDICTION_UNAVAILABLE`).
- Added `POST /api/v1/documents/{document_id}/validate-tax-type` endpoint with explicit INVOICE classification gate.
- Wrote 28 comprehensive tests covering all spec scenarios.
- Carefully distinguished `None` (field not extracted) from `Decimal("0")` (field explicitly zero).

## Tax-Type Rules

### Same-State (CGST + SGST expected)
| CGST | SGST | IGST | Result |
|------|------|------|--------|
| >0   | >0   | 0/None | CONSISTENT |
| >0   | 0    | 0/None | MISMATCH (SGST missing) |
| 0    | >0   | 0/None | MISMATCH (CGST missing) |
| 0    | 0    | >0   | MISMATCH (IGST present, CGST/SGST missing) |
| >0   | >0   | >0   | MISMATCH (IGST should not be present) |
| 0    | 0    | 0    | REVIEW_REQUIRED |
| None | None | None | REVIEW_REQUIRED |

### Different-State (IGST expected)
| CGST | SGST | IGST | Result |
|------|------|------|--------|
| 0/None | 0/None | >0 | CONSISTENT |
| >0   | >0   | 0/None | MISMATCH (CGST/SGST present, IGST missing) |
| >0   | >0   | >0   | MISMATCH (CGST/SGST should not be present) |
| 0    | 0    | 0    | REVIEW_REQUIRED |
| None | None | None | REVIEW_REQUIRED |

### Jurisdiction Unavailable
Any unavailable jurisdiction → `JURISDICTION_UNAVAILABLE` with `expected_tax_type = UNKNOWN`.

## Files Created
- `backend/app/schemas/tax_type_validation.py`
- `backend/app/services/gst_tax_type_validation_service.py`
- `backend/tests/test_gst_tax_type_validation.py`
- `docs/tasks/TASK_13_GST_TAX_TYPE_VALIDATION.md`

## Files Modified
- `backend/app/api/v1/endpoints/documents.py`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

## Files Deleted
None

## Dependencies Added
None

## Architecture Changes
- `GSTTaxTypeValidationService` consumes the `JurisdictionRelationship` enum from Task 12 and `Financials` from the canonical invoice schema. It is independently testable with pure functions.
- The service uses three helper functions (`_is_positive`, `_is_zero`, `_is_missing`) to carefully distinguish between None, zero, and positive Decimal values.

## API Changes
Added `POST /api/v1/documents/{document_id}/validate-tax-type`.
The endpoint:
1. Checks classification == INVOICE (rejects non-invoices with HTTP 400).
2. Loads the canonical extraction.
3. Detects seller and buyer states via Task 12 state detection.
4. Compares jurisdictions.
5. Validates tax component type against jurisdiction.
6. Returns structured `GSTTaxTypeValidationResult`.

## Database Changes
None. Database persistence is reserved for Task 16.

## AI/ML Changes
None.

## UI Changes
None.

## Security Changes
None. Uses only synthetic test data.

## Testing Performed
- **Run**: `cd backend && pytest tests/ -v`
- Same-state: CGST+SGST (consistent), IGST only (mismatch), CGST only (mismatch), SGST only (mismatch), all three (mismatch), all zero (review), all missing (review).
- Different-state: IGST (consistent), CGST+SGST (mismatch), all three (mismatch), all zero (review), all missing (review).
- Jurisdiction unavailable: seller, buyer, both.
- API tests: non-invoice rejection, response schema, same-state consistent, different-state mismatch, jurisdiction unavailable.
- Decimal preservation, canonical invoice immutability, no tax amount/rate fields in result.
- None vs zero distinction for CGST, SGST, IGST.
- All existing Tasks 1–12 tests remain green.

## Test Results
123 passed, 11 warnings in 34.00s

## Known Issues
None.

## Limitations
- Tax type validation depends on jurisdiction availability. If jurisdiction cannot be determined, no tax-type conclusion is drawn.
- Zero-tax invoices produce REVIEW_REQUIRED rather than a definitive pass or fail, to avoid false positives for exempt supplies.
- The service does not validate tax rates or amounts.

## Decisions Made
- `None` (not extracted) is treated differently from `Decimal("0")` (explicitly zero). A missing IGST field does not count as "IGST present" — only a positive value does.
- All-zero tax fields produce REVIEW_REQUIRED rather than MISMATCH, since zero-tax may indicate exempt supplies or extraction gaps.
- The `REVIEW_REQUIRED` status is used conservatively for ambiguous situations where the validator cannot make a definitive determination.
- Errors are descriptive strings explaining each specific violation, not generic codes.

## Things NOT Implemented
- Tax-rate validation (5%, 12%, 18%, 28%)
- Tax percentage calculation
- Tax amount calculation
- Taxable amount validation
- Grand-total validation
- CGST + SGST mathematical equality
- Invoice arithmetic
- GST government API verification
- HSN validation
- e-Invoice verification
- Duplicate detection
- Database persistence
- Android UI changes

## Current Project State
Upload → Preprocessing → OCR → Classification → Extraction → Canonical Schema → GSTIN Validation → State Detection → **GST Tax Type Validation**

## Next Task
Task 14 — Invoice Mathematical Validation

## Instructions For Next Developer/Agent
Task 13 provides `GSTTaxTypeValidationResult` with `is_consistent` and `status`. Task 14 should implement mathematical validation (CGST + SGST = total_tax, taxable_amount × rate, grand_total checks) without duplicating the tax-type structure checks done here. The tax-type service is read-only and does not mutate the canonical invoice.

## Git Commit
`feat: add gst tax type validation`

## Handoff Summary
Task 13 establishes deterministic GST tax type validation. The service compares the expected tax structure (CGST+SGST for same-state, IGST for different-state) against the actually extracted tax components. It carefully distinguishes None from zero, handles jurisdiction unavailability, and produces structured results with descriptive errors. No tax rates, amounts, or arithmetic are validated — those belong to Task 14.
