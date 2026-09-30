# Task 10 — Structured Invoice Schema

## Status
COMPLETED

## Date
2026-09-30

## Objective
Establish one canonical, structured invoice data contract that will be consumed by all future downstream tasks (e.g. GSTIN validation, Math validation). The schema must remain distinct from validation operations.

## Context
Task 9 extracted raw values and mapped them into a flat `InvoiceExtractionResult` structure. Moving into tasks 11-15, which will perform complex validations, the system requires a well-structured canonical domain model (Party, Financials, etc.). This ensures consistency across components.

## Work Completed
- Evolved `InvoiceExtractionResult` into a nested domain structure: `CanonicalInvoice`
- Created sub-models: `Party` (for seller and buyer) and `Financials`
- Updated the Extraction Service to cleanly map its parsed values into the new nested canonical model.
- Persisted the existing HTTP endpoint behavior and updated test suites to assert against the canonical JSON response.
- Preserved precise `Decimal` usage across all monetary values to prevent loss of floating-point precision.

## Files Created
- `docs/tasks/TASK_10_STRUCTURED_INVOICE_SCHEMA.md`

## Files Modified
- `backend/app/schemas/invoice.py`
- `backend/app/services/extraction_service.py`
- `backend/tests/test_extraction.py`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

## Files Deleted
None

## Dependencies Added
None

## Architecture Changes
Introduced a canonical domain model for invoice data (`CanonicalInvoice`), clearly decoupling the *shape* of the data from its *validity*.

## API Changes
The extraction endpoint `POST /api/v1/documents/{document_id}/extract` response shape transitioned from a flat JSON model to a cleaner nested structure (containing `seller`, `buyer`, `financials` blocks) without breaking the logical contract. 

## Database Changes
None. Database persistence is reserved for Task 16.

## AI/ML Changes
None

## UI Changes
None. The Android UI was left untouched.

## Security Changes
None. Did not introduce sensitive data or log outputs. Maintained proper UUID validation guarding against path traversal, which was introduced at the end of Task 9.

## Testing Performed
### Run
`pytest tests/ -v`

### Results
48 tests passed. No regressions were observed. Coverage encompasses missing variables resolving to `null`, preventing the fabrication of fields, preserving exact string representations of `Decimal`, and ensuring that `CanonicalInvoice` successfully handles all previously flat attributes correctly mapped to nested fields.

## Build Status
N/A (Android code was untouched).

## Known Issues
No issues identified.

## Limitations
- Extraction heuristic accuracy still inherits the limitations from Task 9.
- No database persistence.
- Line items are initialized as an empty list (table parsing is not yet implemented).

## Decisions Made
- Created nested components `Party` and `Financials` while maintaining backward compatibility by aliasing `CanonicalInvoice` back to `InvoiceExtractionResult` inside the internal app codebase to minimize refactor overhead.
- Used `Optional` models for handling nullability without fabricating string responses like "N/A" or "Unknown".

## Things NOT Implemented
- GSTIN validation
- GST state-code/PAN relationship validation
- Math and tax calculations validation
- PostgreSQL database schemas

## Current Project State
The backend document pipeline successfully proceeds from Upload → Preprocessing → OCR → Classification → Invoice Extraction → Canonical Invoice Schema representation.

## Next Task
Task 11 — GSTIN Validation

## Instructions For Next Developer/Agent
Task 10 has set up the fundamental `CanonicalInvoice` structure in `app/schemas/invoice.py`. Proceed to Task 11 to begin validation rules by adding a validation service that inspects `CanonicalInvoice.seller.gstin` and `CanonicalInvoice.buyer.gstin`. Do not attempt to merge the validation logic *inside* the schema itself. 

## Git Commit
`feat: establish canonical structured invoice schema`

## Handoff Summary
The domain schema is now highly robust and cleanly structured. All monetary values use Decimals, avoiding floating-point precision flaws. It sets a clean slate for building independent business rule validators.
