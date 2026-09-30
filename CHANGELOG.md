# Changelog

All notable changes to DocuMind AI are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
