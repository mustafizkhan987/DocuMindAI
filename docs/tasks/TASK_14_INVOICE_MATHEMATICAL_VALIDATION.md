# Task 14 — Invoice Mathematical Validation

## Status
COMPLETED

## Date
2026-09-30

## Objective
Implement deterministic invoice mathematical validation. This checks whether extracted financial amounts on an invoice are mathematically consistent with each other, focusing strictly on arithmetic without duplicating tax-type/jurisdictional validation.

## Context
While Task 13 determines whether the *type* of tax components (e.g. CGST vs IGST) is consistent with the state jurisdiction, Task 14 verifies whether the numbers themselves add up. The service computes checks based on the `Financials` and `LineItem` models in the canonical invoice schema. Missing data results in a `REVIEW_REQUIRED` status instead of forcing mathematical assumptions.

## Work Completed
- Created `MathValidationService` to perform deterministic mathematical checks.
- Implemented three primary checks:
  1. **Tax Total**: `CGST + SGST + IGST == total_tax`
  2. **Grand Total**: `taxable_amount + total_tax == grand_total`
  3. **Line Items**: `quantity * unit_price == line_total`
- Created dedicated schema (`InvoiceMathValidationResult` and `MathCheckResult`) to yield structured, explainable responses.
- Added API endpoint `POST /api/v1/documents/{document_id}/validate-math`.
- Added comprehensive pytest suite with 19 tests covering all logic branches.

## Files Created
- `backend/app/schemas/math_validation.py`
- `backend/app/services/math_validation_service.py`
- `backend/tests/test_math_validation.py`
- `docs/tasks/TASK_14_INVOICE_MATHEMATICAL_VALIDATION.md`

## Files Modified
- `backend/app/api/v1/endpoints/documents.py`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

## Files Deleted
None.

## Dependencies Added
No new dependencies added. Python's built-in `decimal` library is exclusively used for calculations.

## Architecture Changes
- Introduced mathematical validation stage. The `MathValidationService` operates entirely on the `CanonicalInvoice` and is independent of previous stages like `GSTTaxTypeValidationService` or `StateDetectionService`. It is stateless and does not mutate input artifacts.

## API Changes
Added `POST /api/v1/documents/{document_id}/validate-math`:
- Verifies document is classified as `INVOICE`.
- Retrives canonical invoice extraction.
- Returns `InvoiceMathValidationResult` containing overall status and detailed check results.

## Database Changes
None. Database persistence is reserved for Task 16.

## AI/ML Changes
None.

## UI Changes
None.

## Security Changes
No new security concerns introduced. Endpoint retains standard classifications constraints. Standard document access controls remain in place.

## Mathematical Checks
- **Check A (Tax Total)**: Confirms the sum of extracted CGST, SGST, and IGST matches the extracted total tax. 
- **Check B (Grand Total)**: Confirms the sum of the taxable amount and total tax matches the grand total.
- **Check C (Line Items)**: Verifies that quantity multiplied by unit price matches the line item total for each line item that contains all three fields.

## Rounding / Tolerance Policy
A strict, configurable tolerance of `Decimal("0.01")` is applied to all mathematical comparisons to gracefully handle valid rounding discrepancies commonly found in real-world monetary systems. Any difference larger than `0.01` yields a `MISMATCH`.

## Missing Data Policy
Missing data (`None`) is strictly distinguished from explicitly zero values (`Decimal("0.00")`). 
- If any required component for a specific check is missing, the check is marked `REVIEW_REQUIRED`. The service does not attempt to "guess" or "invent" missing values. 
- If an invoice possesses zero values across its taxes (e.g., `CGST=0`, `SGST=0`, `IGST=0`, `total_tax=0`), the math still calculates as `0 == 0`, and the check will cleanly `PASS`.

## Testing Performed
- Validated individual checks (passing and failing).
- Verified missing data scenarios for individual checks.
- Confirmed precision of the `Decimal` type without floating-point errors.
- Verified line item logic, incomplete line item handling.
- Ensured non-invoice documents are rejected by the API.
- Confirmed CanonicalInvoice immutability.
- Run complete regression suite.

### Test 1
Command: `pytest tests/test_math_validation.py -v`
Result: 19 passed.

### Test 2
Command: `pytest tests/ -v`
Result: 142 passed (Complete regression).

## Build Status
All 142 tests passing.

## Known Issues
None.

## Limitations
- Mathematical validation cannot verify the *authenticity* or *legal compliance* of an invoice. It strictly verifies whether the extracted numbers physically balance.

## Decisions Made
- Chose `Decimal("0.01")` as the hardcoded default tolerance since standard Indian accounting primarily rounds to the nearest paisa.
- Used a comprehensive output model returning individual statuses for every mathematical check performed to provide extreme explainability. 

## Things NOT Implemented
- Tax-rate calculation (e.g. 18% calculation from taxable amount).
- GSTIN verification via government portals.
- HSN code logic.
- Anomaly detection / Fraud detection.
- Database persistence.

## Current Project State
Upload → Preprocessing → OCR → Classification → Extraction → Canonical Schema → GSTIN Validation → State Detection → GST Tax Type Validation → **Invoice Mathematical Validation**

## Next Task
Task 15 (if specified) or Task 16 (Persistence)

## Instructions For Next Developer/Agent
Task 14 provides mathematical validity results which are now completely segregated from Task 13's Tax-Type validity. When generating analytical summaries or persistence layers, combine the output of `validate-tax-type` and `validate-math` to determine overall invoice health.

## Git Commit
`feat: add invoice mathematical validation`

## Handoff Summary
Task 14 implements deterministic mathematical validation focusing on arithmetic consistency between extracted fields. It safely handles decimals, manages a 0.01 tolerance policy, and respects missing data without forcing calculations. Full regression tests remain green. No unnecessary features were built.
