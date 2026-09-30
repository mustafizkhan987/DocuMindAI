# Task 11 — GSTIN Validation

## Status
COMPLETED

## Date
2026-09-30

## Objective
Implement deterministic GSTIN validation for extracted GSTIN values. The service validates whether the extracted GSTIN satisfies the syntactic and structural GSTIN rules implemented by DocuMind AI.

## Context
Following Task 10's implementation of the structured domain schema (`CanonicalInvoice`), Task 11 builds the first step of the independent validation rules engine. The system needs to analyze extracted GSTIN fields (for both buyer and seller) and assess their compliance with Indian GST structural constraints and Modulo 36 checksum algorithms, without modifying the underlying extraction data or persisting it to the database yet.

## Work Completed
- Created `GSTINValidationService` to implement deterministic, isolated GSTIN structural and checksum validations.
- Developed the `GSTINValidationResult` and `DocumentGSTINValidationResponse` schemas to clearly represent validation success, errors (e.g., `INVALID_CHECKSUM`, `INVALID_STATE_CODE`), and normalize data without modifying original extraction outputs.
- Extended the `ExtractionService` to allow reloading extracted `CanonicalInvoice` objects locally.
- Added a dedicated validation API endpoint: `POST /api/v1/documents/{document_id}/validate-gstin`.
- Wrote extensive independent and integration tests in `test_gstin_validation.py`.

## Files Created
- `docs/tasks/TASK_11_GSTIN_VALIDATION.md`
- `backend/app/schemas/validation.py`
- `backend/app/services/gstin_validation_service.py`
- `backend/tests/test_gstin_validation.py`

## Files Modified
- `backend/app/api/v1/endpoints/documents.py`
- `backend/app/services/extraction_service.py`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

## Files Deleted
None

## Dependencies Added
None

## Architecture Changes
- Introduced an independent `validation.py` schema distinct from extraction heuristics.
- Set a precedent for separate validation endpoints taking document IDs, reading the canonical representation, and returning deterministic structural validation metrics.

## API Changes
Added `POST /api/v1/documents/{document_id}/validate-gstin`.
The endpoint first verifies the document is classified as `INVOICE` via the existing Task 8 classification gate. Non-invoice documents (RECEIPT, PURCHASE_ORDER, BILL, OTHER) are rejected with HTTP 400 before any GSTIN logic runs.
For valid invoices, it loads the canonical extraction and returns `DocumentGSTINValidationResponse` with structured validation metrics for both `seller_gstin` and `buyer_gstin`.

Key behavioral distinction:
- **Non-invoice document** → HTTP 400 rejection ("GSTIN validation is only available for documents classified as Invoice.")
- **Invoice with missing GSTIN** → HTTP 200, validation proceeds, result contains `MISSING_GSTIN` in errors. This is distinct from a malformed GSTIN.

*(NOTE: This returns structural check responses. It makes NO claim of government verification).*

## Database Changes
None. Persistence is reserved for Task 16.

## AI/ML Changes
None.

## UI Changes
None.

## Security Changes
Data validation occurs locally. Validations perform deterministic algorithmic checking, avoiding third-party API exposure of extracted identifiers.

## GSTIN Validation Rules
The service checks the following sequential constraints on normalized 15-character GSTINs:
1. **Length**: Exactly 15 characters.
2. **Character Set**: Alphanumeric only.
3. **State Code**: First 2 digits (valid standard codes 01–38 and 97–99).
4. **PAN Structure**: Next 10 characters must follow `[A-Z]{5}[0-9]{4}[A-Z]{1}`.
5. **Entity Number**: 13th character must be alphanumeric 1-9 or A-Z.
6. **Z Character**: 14th character must be exactly `Z`.
7. **Checksum**: Modulo 36 calculation of the first 14 characters must match the 15th.

## Checksum Algorithm
- Characters `0-9` map to values 0-9.
- Characters `A-Z` map to values 10-35.
- The iteration factor alternates between 1 (odd indices, 1-based) and 2 (even indices, 1-based).
- Checksum result corresponds to `(36 - (total_sum % 36)) % 36` mapped back to the character dictionary.

## Testing Performed
- **Run**: `cd backend && pytest tests/ -v`
- Tested valid, invalid length, invalid structure, invalid characters, invalid fixed chars, invalid checksums.
- Tested lowercase handling and whitespace normalization logic (proving original variables aren't mutated).
- Handled empty / null / absent GSTIN logic (reporting as `MISSING_GSTIN` instead of malformed syntax).
- Tested API for mixed scenarios (e.g. Seller Valid / Buyer Invalid).
- **Regression**: Non-invoice classification (RECEIPT) → rejected with HTTP 400.
- **Regression**: Invoice + missing GSTIN → proceeds with HTTP 200 and reports `MISSING_GSTIN`.

## Test Results
- 68 tests executed and PASSED.
- 100% success on the GSTIN validation suite.

## Known Issues
None.

## Limitations
- Checksum valid != Government active. The validation algorithm proves structural compliance, not active government registration or legal identity verification.

## Decisions Made
- Added a `get_extraction_result` function to the `ExtractionService` instead of directly embedding local file-reads in the router.
- `GSTINValidationResult` maintains an `errors` list (e.g. `['INVALID_CHECKSUM']`) instead of a single boolean, vastly improving API client observability.
- The validate-gstin endpoint explicitly checks classification == INVOICE before proceeding, matching the pattern used by the extraction endpoint. Missing extraction artifacts are not relied upon as an indirect document-type gate.

## Things NOT Implemented
- State detection (Extracting state from GSTIN).
- Tax calculations or Mathematical verifications (Tasks 12/13).
- Postgres DB schemas (Task 16).
- Verification via Government APIs.

## Current Project State
Upload → Preprocessing → OCR → Classification → Extraction → Canonical Schema → **GSTIN Validation**

## Next Task
Task 12

## Instructions For Next Developer/Agent
Proceed to Task 12 (likely involving state detection or invoice mathematical/tax validations). The GSTIN validation logic is self-contained. Ensure any future validations (like State cross-checks) leverage the logic built in `gstin_validation_service.py` where applicable.

## Git Commit
`feat: add gstin validation`

## Handoff Summary
Task 11 adds an extremely robust Modulo-36 structural GSTIN validator. The project pipeline architecture correctly partitions data structuralization (Task 10) from data validation (Task 11), returning deterministic logic that avoids false-positive government verification claims.
