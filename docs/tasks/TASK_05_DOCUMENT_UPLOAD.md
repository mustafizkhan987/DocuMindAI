# Task 05 — Document Upload

## Status
COMPLETED

## Date
2026-09-30

## Objective
Implement the first real Document Pipeline capability to allow secure document uploading from the Android application to the FastAPI backend.

## Context
Task 5 establishes a clean and secure document-upload pipeline. It includes selecting a file in the Android UI, uploading it via multipart/form-data to the FastAPI endpoint, validating the file structure (size, MIME type), and securely persisting it locally with a UUID-based filename. This provides the necessary foundation for OCR and extraction in upcoming tasks.

## Work Completed
- Added `python-multipart` integration in FastAPI.
- Configured max upload limits and secure local storage directory in `config.py`.
- Created `DocumentService` to handle secure file validation (MIME types: PDF/JPG/PNG, size limit, non-empty) and UUID-based secure persistence.
- Created `/api/v1/documents/upload` endpoint and added it to the main router.
- Tested all backend upload constraints thoroughly with `pytest`.
- Updated Android `DocuMindApi` and `DocumentRepositoryImpl` to support Retrofit `MultipartBody` networking.
- Implemented `DocumentsViewModel` to handle reading Android `ContentResolver` file bytes securely.
- Updated `DocumentsScreen` with modern Android Document Picker (`rememberLauncherForActivityResult`) and detailed upload progress/error UI.
- Prevented git from tracking uploaded documents via `.gitignore`.

## Files Created
- `backend/app/schemas/document.py`
- `backend/app/services/document_service.py`
- `backend/app/api/v1/endpoints/documents.py`
- `backend/tests/test_documents.py`
- `app/src/main/java/com/documind/ai/data/remote/dto/DocumentUploadResponseDto.kt`
- `app/src/main/java/com/documind/ai/ui/screens/documents/DocumentsUiState.kt`
- `app/src/main/java/com/documind/ai/ui/screens/documents/DocumentsViewModel.kt`
- `docs/tasks/TASK_05_DOCUMENT_UPLOAD.md`

## Files Modified
- `backend/app/core/config.py`
- `backend/app/api/v1/router.py`
- `app/src/main/java/com/documind/ai/data/remote/api/DocuMindApi.kt`
- `app/src/main/java/com/documind/ai/domain/repository/DocumentRepository.kt`
- `app/src/main/java/com/documind/ai/data/repository/DocumentRepositoryImpl.kt`
- `app/src/main/java/com/documind/ai/ui/screens/documents/DocumentsScreen.kt`
- `.gitignore`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

## Files Deleted
None

## Dependencies Added
- None (python-multipart was already in requirements)

## Architecture Changes
- Added `/documents` router to FastAPI.
- Added `DocumentsViewModel` to Android MVVM structure.

## API Changes
- Added `POST /api/v1/documents/upload` accepting `multipart/form-data`.
- Response schema: `DocumentUploadResponse`

## Database Changes
- None (Local development file storage used)

## AI/ML Changes
- None (OCR starts in Task 6/7)

## UI Changes
- `DocumentsScreen` heavily modified to include upload button, file picker, loading indicator, and success/error status display.

## Security Changes
- Files are saved with UUID identifiers instead of original user filenames to prevent path traversal.
- File types restricted strictly to `application/pdf`, `image/jpeg`, and `image/png`.
- Empty files and files exceeding `MAX_UPLOAD_SIZE_MB` (10MB default) are strictly rejected.
- File bytes and PII are not logged.

## Testing Performed
### Test 1
Command: `pytest backend/tests/test_documents.py -v`
Result: PASSED (Tested successful PDF upload, empty file rejection, unsupported file rejection, and oversized file rejection)

### Test 2
Command: `./gradlew assembleDebug`
Result: PASSED

## Build Status
Success (Both Python pytest and Android Gradle build pass).

## Known Issues
None.

## Limitations
- Storage is purely local filesystem at the moment, which will be expanded or modified in Phase 4 (Persistence).

## Decisions Made
- Chose `ByteArrayOutputStream` for reading URIs into byte arrays for Retrofit to minimize dependencies and correctly deal with `ContentResolver` on modern Android versions without assuming `java.io.File` absolute paths.
- Enforced strict backend file limits directly in a `DocumentService` rather than putting logic inside the routing layer.

## Things NOT Implemented
- OCR (Tesseract / PaddleOCR)
- Image preprocessing
- Postgres Database Persistence
- e-Invoice scanning

## Current Project State
The project now allows a user to pick a document on the Android app, safely upload it, validate it on the FastAPI backend, save it securely, and reflect the success state in the Android UI.

## Next Task
TASK 6 — IMAGE PREPROCESSING

## Instructions For Next Developer/Agent
The secure document upload pipeline is fully implemented. The uploaded document is stored safely, and its ID is returned to the Android app. Start Task 6 by taking these uploaded documents and preparing them via OpenCV image preprocessing pipelines before OCR begins.

## Git Commit
`feat: add secure document upload pipeline`

## Handoff Summary
Task 5 completed successfully. Android document picker, multi-part networking, FastAPI upload endpoints, file validation, and secure storage have all been successfully implemented and tested.
