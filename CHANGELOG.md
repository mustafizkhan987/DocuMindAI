# Changelog

All notable changes to DocuMind AI are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

*Future tasks will be recorded here before release.*

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

*N/A — Initial release.*

#### Fixed

*N/A — Initial release.*

#### Security

- `.env` excluded from version control via `.gitignore`
- `data/raw/*` excluded to prevent accidental commitment of real invoices
- No hardcoded credentials anywhere in the codebase
- `.env.example` contains only placeholder values

---

*DocuMind AI — Understand → Extract → Verify → Explain → Act*
