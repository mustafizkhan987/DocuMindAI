# Changelog

All notable changes to DocuMind AI are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.8.6] — 2026-09-30

### Task 8.5B — Visual Redesign

#### Changed
- **Complete Visual Overhaul**: Completely redesigned the UI to match professional business applications (e.g. Google Drive) moving away from developer/dark-mode dashboards.
- **Light Theme Enforced**: Replaced Dark Theme defaults and disabled Android 12+ dynamic colors to strictly enforce the brand identity (Deep Navy, Muted Teal, Light Backgrounds).
- **Redesigned Screens**: Rebuilt `HomeScreen`, `DocumentsScreen`, `UploadScreen`, `ProcessingScreen`, `DocumentResultScreen`, and `AboutScreen`.
- **Removed Technical Information**: Removed all mentions of internal statuses (FastAPI, backend routes, Task names) from the user-facing interface.

#### Fixed
- **Restored Upload Integration**: Re-wired the `UploadScreen` to trigger the actual `DocumentsViewModel` upload flow developed in Task 5, restoring real `Retrofit` networking and dynamic document ID parsing.
- **Disabled Mock UI**: Removed fake `mock_doc_id_12345` flows. The Processing screen is now exclusively triggered when the FastAPI backend confirms a successful document upload.

---

## [0.9.0] — 2026-09-30

### Task 9: Invoice Information Extraction
#### Added
- **Invoice Schema**: Created `InvoiceExtractionResult` and `LineItem` models in `backend/app/schemas/invoice.py`.
- **Extraction Service**: Implemented deterministic heuristic-based regex extraction in `backend/app/services/extraction_service.py` to extract 13+ fields including GSTINs, dates, and amounts.
- **Extraction API**: Exposed `POST /api/v1/documents/{document_id}/extract`.
- **Classification Gate**: Extraction is safely gated to only process documents that return a DocumentType.INVOICE classification.
- **Extraction Storage**: Locally persists JSON extraction results in `storage/extraction_results/`.

---

## [0.8.5B] — 2026-09-30

### Task 8.5 — Professional Android UI & Trust-Centric UX

#### Changed
- **App Theme**: Updated Android Material 3 theme to use a highly professional color palette (`Deep Navy`, `Muted Teal`) replacing the dark "AI demo" aesthetic.
- **UI Architecture**: Implemented full `navigation-compose` flow replacing the static Foundation Screen.
- **Screens**: Redesigned Home, Documents List, Document Review, Upload, Processing, Settings, and About screens to target business-level trust and older demographic accessibility (larger touch targets, clearer typography).
- **Components**: Standardized `StatusBadge`, `DocuMindPrimaryButton`, and `InformationRow` components across the app.

---

## [0.8.0] — 2026-09-30

### Task 8 — Document Classification

#### Added
- **Classification Service**: Created a deterministic Rule-Based TF (Term Frequency) Weighted Scoring algorithm.
- **Classification Endpoint**: Added `POST /api/v1/documents/{document_id}/classify` to evaluate OCR strings against document signatures (Invoice, Receipt, Purchase Order, Bill, Other).
- **OCR Persistence**: Modified OCR pipeline to cache outputs in local JSON files (`storage/ocr_results`), enabling decoupled sequential pipeline steps without redundant deep-learning inferences.

---

## [0.7.0] — 2026-09-30

### Task 7 — OCR Engine

#### Added
- **OCR Service**: Implemented `OCRService` using `easyocr` to extract raw text and confidence scores.
- **OCR API Endpoint**: Added `POST /api/v1/documents/{document_id}/ocr` to trigger extraction on preprocessed images.
- **OCR Tests**: Added mocking and integration tests for OCR processing in `backend/tests/test_ocr.py`.

---

## [0.6.0] — 2026-09-30

### Task 6 — Image Preprocessing

#### Added
- **Preprocessing Pipeline**: Developed `PreprocessingService` utilizing `PyMuPDF` (for PDF rendering) and `OpenCV` (for grayscale, denoising, and adaptive thresholding).
- **Preprocessing Endpoint**: Added `POST /api/v1/documents/{document_id}/preprocess`.
- **Security**: Added isolated `backend/storage/processed/` directory.

---

## [0.5.0] — 2026-09-30

### Task 5 — Document Upload

#### Added
- **Android Document Picker**: Integrated file selection using Android's modern Activity Result API.
- **Multipart Upload Flow**: Implemented Retrofit multipart network call (`MultipartBody.Part`) to upload documents from Android safely.
- **FastAPI Upload Endpoint**: Added `POST /api/v1/documents/upload` for secure file uploads.
- **File Validation**: Enforced file existence, non-emptiness, MIME types (PDF, JPEG, PNG), and max file sizes.
- **Local Storage**: Saved files to `backend/storage/documents` with unique UUID names, avoiding public/static directories and ensuring it is ignored by Git.
- **Upload State & Error Handling**: UI in `DocumentsScreen` dynamically updates to show progress, success, or detailed error messages.
- **Comprehensive Testing**: Validated backend constraints with automated pytest tests including oversized files, invalid types, and empty files.

---

## [0.4.0] — 2026-09-30

### Task 4 — Android ↔ Backend Connection

#### Added
- **Live Integration**:
  - `DocumentRepositoryImpl` modified to execute live API call `getV1Health()` using Retrofit.
  - Mapped JSON responses from FastAPI (`HealthResponseDto`) to internal domain models (`BackendHealth`).
- **Error Handling**:
  - Implemented error handling for network errors and non-successful HTTP responses, emitting appropriate `Result.Error` values.

---

## [0.3.0] — 2026-09-30

### Task 3 — Android Application Foundation

#### Added
- **Compose Navigation**: `AppNavigation`, `Screen`, and `AppBottomNavigation` implemented for multi-screen routing.
- **MVVM Architecture**: Added `HomeViewModel`, `HomeUiState`, and `Result` wrapper for state management and network abstractions.
- **Network Layer**: Added Retrofit `DocuMindApi`, `ApiClient`, and `NetworkModule` in preparation for backend integration.
- **UI Components**: `StatusChip`, `HomeScreen`, `DocumentsScreen`, `SettingsScreen`.

#### Changed
- Removed single-screen placeholder UI in favor of modular MVVM Compose structure.

---

## [0.2.0] — 2026-09-30

### Task 2 — FastAPI Backend Foundation

#### Added
- **Modular FastAPI Architecture**:
  - `backend/app/api/v1/router.py` — Central API v1 router
  - `backend/app/api/v1/endpoints/health.py` — Versioned health check endpoint (`GET /api/v1/health`)
- **Configuration Management**:
  - `backend/app/core/config.py` — Centralized Pydantic Settings with `@lru_cache` helper
- **Database Infrastructure**:
  - `backend/app/core/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, `get_db` dependency, and graceful `check_database_connection()`
  - `backend/app/models/base.py` — Declarative ORM Base model and `TimestampMixin`
- **Centralized Exception & Logging Infrastructure**:
  - `backend/app/core/exceptions.py` — Custom exception classes and global error handlers preventing internal details leakage
  - `backend/app/core/logging.py` — Production-conscious logger with zero secret leakage
- **Docker Setup**:
  - `backend/Dockerfile` — Python 3.13 image configuration for FastAPI API service
  - `docker-compose.yml` — Local development environment with PostgreSQL 16 (`documind-db`) and FastAPI API (`documind-api`)
- **Backend Test Suite Expansion**:
  - `backend/tests/test_health.py` — Tests for `/health` and `/api/v1/health`
  - `backend/tests/test_config.py` — Tests for settings, exceptions, and DB connection check (18 total tests passing)

#### Changed
- Refactored `backend/app/main.py` to use FastAPI's `lifespan` context manager instead of deprecated `on_event` handlers.
- Updated `backend/requirements.txt` with `sqlalchemy==2.1.1` and `psycopg[binary]==3.3.6`.

---

## [0.1.0] — 2026-09-30

### Task 1 — Project Foundation

#### Added

- Complete repository directory structure:
  - `android/` — Android application root
  - `backend/app/{api,services,models,schemas,utils}/` — FastAPI backend structure
  - `ai/{ocr,extraction,validation,models}/` — AI pipeline directories
  - `data/{raw,processed,labeled}/` — Data directories with `.gitkeep`
  - `docs/tasks/` — Task completion reports directory

- **FastAPI application** (`backend/app/main.py`):
  - `GET /` — API root endpoint returning name, version, environment
  - `GET /health` — Health check endpoint
  - Swagger UI at `/docs`
  - ReDoc UI at `/redoc`
  - CORS middleware configured for development
  - Environment variable loading via `python-dotenv`

- **Backend configuration**:
  - `backend/requirements.txt` — Minimal dependencies for Task 1
  - `backend/.env.example` — Environment variable template
  - `backend/pytest.ini` — pytest async configuration

- **Backend test suite** (`backend/tests/test_main.py`):
  - Tests for `GET /` (status, message, version, docs link)
  - Tests for `GET /health` (status, healthy response, version)
  - Tests for `/docs`, `/redoc`, `/openapi.json` accessibility

- **Android application** (`android/DocuMind/`):
  - Kotlin + Jetpack Compose project
  - Foundation screen with app name, subtitle, backend status indicator
  - MVVM architecture skeleton
  - Retrofit + OkHttp dependencies configured
  - Network configuration for emulator and physical device

- **Documentation**:
  - `README.md` — Full project documentation
  - `PROJECT_STATUS.md` — Current project status tracker
  - `CHANGELOG.md` — This file
  - `docs/tasks/TASK_01_PROJECT_FOUNDATION.md` — Task completion report

- **Git configuration**:
  - `.gitignore` — Comprehensive ignore rules for Python, Kotlin, Android, secrets, data
  - `main` branch initialized
  - `develop` branch created
  - `feature/task-01-foundation` branch used for development

#### Changed

- Configured Android `compileSdk` to 37 to support `androidx.core:core-ktx:1.19.0`, while keeping `minSdk` at 27 and `targetSdk` at 36.

#### Fixed

*N/A — Initial release.*

#### Security

- `.env` excluded from version control via `.gitignore`
- `data/raw/*` excluded to prevent accidental commitment of real invoices
- No hardcoded credentials anywhere in the codebase
- `.env.example` contains only placeholder values

---

*DocuMind AI — Understand → Extract → Verify → Explain → Act*
