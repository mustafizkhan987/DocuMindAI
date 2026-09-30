# Task 12 — State Detection

## Status
COMPLETED

## Date
2026-09-30

## Objective
Implement deterministic GSTIN state/jurisdiction detection. Given an extracted GSTIN, extract the two-digit state code and map it to the corresponding Indian state or Union Territory. Determine whether the seller and buyer are in the same or different jurisdiction. This information will be consumed by Task 13 for CGST/SGST/IGST validation.

## Context
Task 11 established structural and checksum validation for GSTINs. Task 12 builds on that foundation by extracting the state code from *validated* GSTINs and mapping them to canonical state names. It deliberately draws NO tax conclusions — that responsibility belongs to Task 13.

## Work Completed
- Created a centralized, authoritative GST state-code mapping (`gst_state_codes.py`) covering codes 01–38 plus special codes 97 and 99.
- Created `StateDetectionService` that delegates GSTIN validation to the existing Task 11 service and only infers states from structurally valid GSTINs.
- Created Pydantic schemas for state detection results, including a `JurisdictionRelationship` enum with five explicit states.
- Added `POST /api/v1/documents/{document_id}/detect-state` endpoint with an explicit INVOICE classification gate.
- Wrote comprehensive unit and integration tests.

## Files Created
- `backend/app/utils/gst_state_codes.py`
- `backend/app/schemas/state_detection.py`
- `backend/app/services/state_detection_service.py`
- `backend/tests/test_state_detection.py`
- `docs/tasks/TASK_12_STATE_DETECTION.md`

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
- Introduced a centralized state-code mapping module (`gst_state_codes.py`) in `app/utils/` to serve as the single source of truth.
- State detection delegates GSTIN structural validation to the existing `GSTINValidationService` (Task 11), avoiding any duplication of checksum logic.
- The `StateDetectionService` is independently testable with pure functions.

## API Changes
Added `POST /api/v1/documents/{document_id}/detect-state`.
The endpoint:
1. Checks classification == INVOICE (rejects non-invoices with HTTP 400).
2. Loads the canonical extraction.
3. Detects seller and buyer states from their GSTINs.
4. Compares jurisdictions.
5. Returns a structured `DocumentStateDetectionResponse`.

## Database Changes
None. Database persistence is reserved for Task 16.

## AI/ML Changes
None.

## UI Changes
None.

## Security Changes
None. Uses only synthetic test data. No real GSTIN datasets committed.

## State Code Mapping
Codes 01–38 covering all Indian states and UTs, plus special codes:
- 97: Other Territory
- 99: Centre Jurisdiction

The mapping is centralized in `backend/app/utils/gst_state_codes.py`.

## Testing Performed
- **Run**: `cd backend && pytest tests/ -v`
- Unit tests for individual state detection (Karnataka, Maharashtra, Tamil Nadu, Telangana, Kerala, Delhi, Uttar Pradesh, Gujarat).
- Verification that all 38 standard codes plus specials are present in the mapping.
- Invalid GSTIN (bad checksum) does NOT produce a detected state.
- Malformed GSTIN returns `detected=False`.
- Missing/None/empty GSTIN returns `detected=False` with an error.
- Same-state and different-state comparison.
- Seller-only, buyer-only, both-unavailable comparisons.
- Non-invoice classification → rejected with HTTP 400.
- API response schema validation.
- No tax conclusions appear anywhere in the result.
- All existing Tasks 1–11 tests remain green.

## Test Results
All tests passed. See final report for exact count.

## Known Issues
None.

## Limitations
- State detection depends on Task 11 structural validation. If the GSTIN is invalid, no state is inferred.
- The mapping is static and may require updates if GST jurisdiction codes change in the future.
- State code 28 and 37 both map to "Andhra Pradesh" (pre/post bifurcation), which is the correct GST convention.

## Decisions Made
- State detection refuses to infer a state from structurally invalid GSTINs. This avoids false positives where first two characters coincidentally resemble a valid state code.
- The `JurisdictionRelationship` enum uses descriptive values (`SAME_STATE`, `DIFFERENT_STATE`, etc.) rather than tax-implication values.
- The state mapping is kept in a dedicated utility module rather than embedded in the service, to allow reuse by future tasks.

## Things NOT Implemented
- CGST/SGST/IGST validation (Task 13)
- Tax-rate validation
- Invoice mathematical validation
- Government API verification
- Database persistence
- Android UI changes

## Current Project State
Upload → Preprocessing → OCR → Classification → Extraction → Canonical Schema → GSTIN Validation → **State Detection**

## Next Task
Task 13 — GST Tax Type Validation (CGST/SGST/IGST)

## Instructions For Next Developer/Agent
Task 12 provides the `JurisdictionRelationship` needed by Task 13 to determine whether CGST+SGST or IGST should apply. Use `state_detection_service.detect_state()` and `state_detection_service.compare_jurisdictions()` to obtain the relationship, then apply tax-type rules in Task 13. Do NOT modify the state detection service to embed tax conclusions.

## Git Commit
`feat: add gstin state detection`

## Handoff Summary
Task 12 establishes deterministic state/jurisdiction detection from GSTIN state codes. The service cleanly delegates validation to Task 11, refuses to infer states from invalid GSTINs, and returns a structured relationship enum without drawing any tax conclusions. The centralized state-code mapping covers all 38 standard GST jurisdiction codes plus special codes 97 and 99.
