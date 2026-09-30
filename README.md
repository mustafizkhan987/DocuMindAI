# DocuMind AI

> **AI-Powered GST-Aware Document & Invoice Intelligence Platform**

[![Platform](https://img.shields.io/badge/Platform-Android-green.svg)](https://developer.android.com)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Language](https://img.shields.io/badge/Language-Kotlin%20%7C%20Python-blue.svg)](https://kotlinlang.org)
[![Status](https://img.shields.io/badge/Status-Phase%201%20%E2%80%94%20Foundation-yellow.svg)](PROJECT_STATUS.md)

---

## What is DocuMind AI?

DocuMind AI is an Android-first intelligent document and invoice processing platform designed specifically for Indian businesses.

The platform goes far beyond simple OCR scanning. It **understands** documents, **extracts** structured information, **verifies** GST compliance, **detects** issues, and **explains** every finding in plain language.

```
Camera Photo / Image / PDF
         ↓
  Image Preprocessing
         ↓
         OCR
         ↓
Document Classification
         ↓
 Information Extraction
         ↓
GST / Financial Validation
         ↓
    Issue Detection
         ↓
  Explainable Results
         ↓
History / Analytics / Q&A
```

---

## The Problem We're Solving

Businesses across India receive hundreds of documents daily:

- Invoices
- Receipts
- Purchase Orders
- Quotations
- Tax Documents
- Bills
- Delivery Documents

The traditional workflow is entirely manual:

```
Open document → Read → Enter data → Calculate → Check errors → Store
```

This creates:
- **Manual data-entry errors** that cost time and money
- **Slow processing** that creates bottlenecks
- **Duplicate invoices** going undetected
- **Calculation mistakes** in tax amounts
- **Difficulty searching** historical documents
- **No vendor spending intelligence**

DocuMind AI **automates** this entire workflow and adds intelligence that no manual process can match.

---

## Core Value Proposition

> **Understand → Extract → Verify → Explain → Act**

DocuMind AI is **not** positioned as "an OCR invoice scanner." OCR is only one component.

The primary differentiator is **India-specific invoice intelligence**:

### GSTIN Intelligence
- Extract GSTIN from documents
- Format validation (15-character structure)
- State code validation (01–37)
- PAN relationship validation
- Checksum validation

### GST Structure Validation
- Detect seller and buyer states
- Determine if CGST+SGST or IGST applies
- Flag wrong tax component usage

### Mathematical Validation
- Independent calculation: `Qty × Unit Price → Line Total → Subtotal → Tax → Total`
- Compare calculated total vs. invoice total
- Flag discrepancies with explanation

### HSN Intelligence
- Extract HSN codes from line items
- Validate HSN code format

### e-Invoice QR Processing
- Read QR code data from e-invoices
- Compare with extracted invoice data
- Flag mismatches

---

## Target Users

| User Type | Use Case |
|-----------|----------|
| Small Businesses | Automate invoice processing, reduce errors |
| Shop Owners | Quick receipt and invoice capture |
| Accountants | Batch document processing with validation |
| CA Offices | Compliance checking for client documents |
| Freelancers | Track invoices and payments |
| University / Organization Accounts | Process vendor invoices at scale |

---

## Document Types Supported

### Current (MVP)
- Invoice
- Receipt
- Purchase Order
- Quotation
- Utility Bill
- Other

### Future
- Bank Statement
- Tax Document
- Contract
- Delivery Document
- Application Form

---

## Technology Stack

### Android Application
| Component | Technology |
|-----------|-----------|
| Language | Kotlin |
| UI Framework | Jetpack Compose |
| Architecture | MVVM / Clean Architecture |
| HTTP Client | Retrofit + OkHttp |
| Async | Coroutines |

### Backend
| Component | Technology |
|-----------|-----------|
| Language | Python 3.13+ |
| Framework | FastAPI |
| Server | Uvicorn |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy / SQLModel |

### Database
| Component | Technology |
|-----------|-----------|
| Primary | PostgreSQL |
| Vector Search (future) | pgvector |

### AI / ML
| Component | Technology |
|-----------|-----------|
| OCR | PaddleOCR |
| Image Processing | OpenCV |
| ML | scikit-learn, XGBoost |
| Anomaly Detection | Isolation Forest |
| Embeddings (future) | sentence-transformers |
| Document AI (future) | Layout-aware models |

### Development
| Component | Technology |
|-----------|-----------|
| Version Control | Git / GitHub |
| Containerization | Docker |
| Testing (Backend) | pytest |
| Testing (Android) | JUnit + Compose UI Tests |
| API Testing | Postman / Bruno |
| IDE | Android Studio + VS Code |

---

## Architecture

```
                    ANDROID APP
               Kotlin + Jetpack Compose
                         │
                         │ HTTPS / REST
                         ▼
                    FASTAPI API
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
          Document    Validation  Analytics
          Service      Service     Service
              │
              ▼
        AI Processing
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
      OCR    NLP     ML
       │      │      │
       └──────┼──────┘
              ▼
          PostgreSQL
```

---

## Repository Structure

```
DocuMindAI/
│
├── android/                          # Android application (Kotlin + Compose)
│   └── DocuMind/
│
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/                      # API route handlers
│   │   ├── services/                 # Business logic
│   │   ├── models/                   # Database models (SQLAlchemy)
│   │   ├── schemas/                  # Pydantic schemas
│   │   └── utils/                    # Utility functions
│   │
│   ├── tests/                        # pytest test suite
│   ├── requirements.txt              # Python dependencies
│   ├── pytest.ini                    # pytest configuration
│   └── .env.example                  # Environment variable template
│
├── ai/                               # AI/ML pipelines (future tasks)
│   ├── ocr/                          # OCR pipeline (Task 7)
│   ├── extraction/                   # Invoice extraction (Task 9)
│   ├── validation/                   # Validation logic (Tasks 11–15)
│   └── models/                       # Trained model files
│
├── data/                             # Data directory
│   ├── raw/                          # Raw documents (NEVER commit real docs)
│   ├── processed/                    # Preprocessed documents
│   └── labeled/                      # Labeled training data
│
├── docs/                             # Project documentation
│   └── tasks/                        # Task completion reports
│       └── TASK_01_PROJECT_FOUNDATION.md
│
├── README.md                         # This file
├── PROJECT_STATUS.md                 # Current project status (always up to date)
├── CHANGELOG.md                      # Change log
└── .gitignore                        # Git ignore rules
```

---

## Development Setup

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Java | 17+ |
| Android Studio | Latest |
| Android SDK | API 33+ |
| Git | Latest |
| PostgreSQL | 15+ (for Task 16+) |

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/mustafizkhan987/DocuMind-AI.git
cd DocuMind-AI

# 2. Create a Python virtual environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env
# Edit .env with your actual values

# 5. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Backend is Running

```bash
# Test root endpoint
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/health

# Open Swagger UI in browser
http://localhost:8000/docs

# Open ReDoc in browser
http://localhost:8000/redoc
```

### Running Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Android Setup

```bash
# 1. Open Android Studio
# 2. Open: android/DocuMind/
# 3. Let Gradle sync complete
# 4. Update backend URL in NetworkConfig:
#    - Emulator: http://10.0.2.2:8000
#    - Physical device: http://<your-machine-ip>:8000
# 5. Run the application
```

---

## API Endpoints

### Current (Task 1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and version |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

### Planned (Future Tasks)

| Method | Endpoint | Task | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/documents/upload` | Task 5 | Upload document |
| GET | `/api/v1/documents/{id}` | Task 5 | Get document |
| POST | `/api/v1/ocr/process` | Task 7 | Run OCR |
| POST | `/api/v1/extract/invoice` | Task 9 | Extract invoice fields |
| POST | `/api/v1/validate/gstin` | Task 11 | Validate GSTIN |
| GET | `/api/v1/documents/history` | Task 17 | Document history |
| GET | `/api/v1/analytics/vendors` | Task 20 | Vendor analytics |
| POST | `/api/v1/search` | Task 27 | Natural-language search |
| POST | `/api/v1/qa` | Task 30 | Document Q&A |

---

## Project Roadmap

| Phase | Tasks | Description |
|-------|-------|-------------|
| **Phase 1 — Foundation** | 1–4 | Project setup, backend, Android, connection |
| **Phase 2 — Document Pipeline** | 5–9 | Upload, preprocessing, OCR, classification, extraction |
| **Phase 3 — Invoice Intelligence** | 10–15 | Schema, GSTIN, state detection, GST validation, math, explanations |
| **Phase 4 — Persistence** | 16–18 | PostgreSQL, history, correction system |
| **Phase 5 — Intelligence** | 19–22 | Duplicate detection, vendor analytics, payment tracking |
| **Phase 6 — Advanced India** | 23–26 | e-Invoice QR, HSN, multilingual, anomaly detection |
| **Phase 7 — AI Assistant** | 27–30 | NL search, embeddings, RAG, Q&A |
| **Phase 8 — Production** | 31–38 | Security, performance, testing, deployment, pilot |

---

## Security & Privacy

DocuMind AI processes sensitive business documents. Key security principles:

- ❌ **Never commit real invoices** to version control
- ❌ **Never log raw invoice text** in production
- ❌ **Never expose uploaded files** publicly
- ❌ **Never hard-code credentials**
- ❌ **Never send private documents** to third-party AI without authorization
- ✅ Environment variables for all secrets
- ✅ Input validation on all endpoints
- ✅ Proper CORS configuration
- ✅ Data anonymization before training

---

## Current Status

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the latest project status.

**Currently working:**
- `GET /` — API root
- `GET /health` — Health check
- `/docs` — Swagger UI
- `/redoc` — ReDoc UI
- Android foundation screen (Task 3 — in queue)

---

## Contributing

This project follows a strict task-based development protocol. Before contributing:

1. Read [PROJECT_STATUS.md](PROJECT_STATUS.md)
2. Read the latest task report in `docs/tasks/`
3. Follow the task lifecycle defined in the Master Project Protocol
4. Create a task completion report before committing

---

## License

MIT License — see LICENSE file for details.

---

*DocuMind AI — Understand → Extract → Verify → Explain → Act*

