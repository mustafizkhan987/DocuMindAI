# Task 06 — Image Preprocessing

## Status
COMPLETED

## Date
2026-09-30

## Objective
Build a modular OCR-preparation preprocessing pipeline for uploaded documents. Convert inputs (images and PDFs) into enhanced, high-contrast grayscale images optimized for OCR, without altering the original uploaded files.

## Context
Before passing documents to an OCR engine, they must be standardized and cleaned. This ensures maximum accuracy when handling noisy mobile-camera photos, thermal receipts, and varying illumination. Task 6 lays the groundwork for Task 7 by creating a modular `PreprocessingService` that handles resizing, denoising, and contrast enhancement (adaptive thresholding) using OpenCV, and translates PDFs into OCR-ready images using PyMuPDF.

## Work Completed
- Added `opencv-python-headless` for image transformations.
- Added `pymupdf` (fitz) for rendering PDF pages into images at 300 DPI without relying on external system dependencies like poppler.
- Added `PROCESSED_DIR` to `config.py` (`backend/storage/processed/`) for isolated storage of output files.
- Created `PreprocessingService` containing logic for:
  - Validating and loading the input file.
  - Converting to Grayscale.
  - Denoising using Non-Local Means Denoising.
  - Adaptive Gaussian Thresholding to enhance contrast across regions with uneven lighting.
  - Writing the output pages to the `processed_dir` with the format `<document_id>_page_<X>.png`.
- Created `/api/v1/documents/{document_id}/preprocess` API endpoint.
- Developed comprehensive automated tests simulating document uploads and validating the preprocessing pipeline.
- Verified that original files are perfectly preserved and path traversal/data corruption is avoided.

## Files Created
- `backend/app/services/preprocessing_service.py`
- `backend/tests/test_preprocessing.py`
- `docs/tasks/TASK_06_IMAGE_PREPROCESSING.md`

## Files Modified
- `backend/requirements.txt`
- `backend/app/core/config.py`
- `backend/app/api/v1/endpoints/documents.py`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

## Files Deleted
None

## Dependencies Added
- `opencv-python-headless==4.11.0.86`
- `pymupdf==1.25.3`

## Architecture Changes
- Added a `PreprocessingService` to isolate image manipulation from routing.
- The pipeline supports multi-page PDFs, generating multiple independent page images.

## API Changes
- Added `POST /api/v1/documents/{document_id}/preprocess`
- Response returns metadata including original dimensions, processed dimensions, status, and the list of output images created.

## Database Changes
- None (Local file storage in `backend/storage/processed/`)

## AI/ML Changes
- None (OCR is next).

## UI Changes
- None (Android continues to upload documents without directly invoking preprocessing. The preprocessing pipeline is a backend capability that will eventually be linked dynamically or via a queue in future tasks.)

## Security Changes
- Added `storage/processed` (the default storage processed dir) fallback logic in configuration.
- Validates the existence of the source `document_id` safely using internal helper methods.

## Testing Performed
### Test 1
Command: `pytest backend/tests/ -v`
Result: PASSED. Verified valid image processing, invalid ID rejection, and corrupted image detection. Verified that the original image is preserved perfectly.

### Test 2
Command: `./gradlew assembleDebug`
Result: PASSED (Android codebase remains intact).

## Build Status
Success

## Known Issues
None.

## Limitations
- OCR readability depends on input resolution; extremely low-resolution inputs will still be challenging even with adaptive thresholding.
- PDFs are rendered at 300 DPI which uses memory scaling with the page count.

## Decisions Made
- Used OpenCV `fastNlMeansDenoising` and `adaptiveThreshold` as they handle mobile photos heavily impacted by shadows much better than simple global thresholds.
- Used `pymupdf` instead of `pdf2image` to avoid forcing a system-level `poppler-utils` dependency, improving cross-platform stability.

## Things NOT Implemented
- OCR
- PaddleOCR
- Tesseract
- LLM / RAG

## Current Project State
The platform can now accept documents from Android, store them securely, and run them through an advanced preprocessing pipeline to generate clean, high-contrast, OCR-ready images stored safely in an isolated directory.

## Next Task
TASK 7 — OCR

## Instructions For Next Developer/Agent
The Preprocessing Pipeline is fully operational. Begin Task 7 by taking the clean, preprocessed images from the `PROCESSED_DIR` and running them through an OCR engine (e.g., Tesseract or PaddleOCR).

## Git Commit
`feat: add document image preprocessing pipeline`

## Handoff Summary
Task 6 completed successfully. A modular PreprocessingService is active using OpenCV and PyMuPDF, providing robust OCR-ready image inputs. Tests pass perfectly, original documents are untouched, and the Android application continues to build.
