# 🕉️ Sarathi: Your Mental Wellness Companion [Research Based Project]
### *AI-Guided Cognitive Reframing, Clinical Psychometrics, Hormonal Phase Biofeedback & Vedic Equanimity*

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.1+](https://img.shields.io/badge/web-Flask%203.1+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![FastAPI](https://img.shields.io/badge/microservice-FastAPI%20ASGI-009688.svg)](https://fastapi.tiangolo.com/)
[![Desktop: Tkinter](https://img.shields.io/badge/desktop-Tkinter%20GUI-purple.svg)](https://docs.python.org/3/library/tkinter.html)
[![Database: MySQL 8](https://img.shields.io/badge/database-MySQL%208.0-orange.svg)](https://www.mysql.com/)
[![ML: PyTorch + NumPy](https://img.shields.io/badge/ML-PyTorch%20%7C%20NumPy-red.svg)](https://pytorch.org/)
[![Vercel Deployment](https://img.shields.io/badge/deployment-Vercel%20Serverless-black.svg?logo=vercel)](DEPLOYMENT_GUIDE.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 58 Passed](https://img.shields.io/badge/tests-58%20passed-brightgreen.svg)](tests/)

An offline-first, privacy-centric mental wellness and reflective journaling ecosystem. It integrates clinical cognitive-behavioral assessment methodologies (PHQ-9, GAD-7) with evidence-backed cognitive reframing, multi-dimensional NLP sentiment classification, dual-engine neural networks, real-time voicebot assistance, dynamic ambient emotion theming, and timeless Vedic equanimity principles derived from the *Bhagavad Gita*.

---

## 📚 Complete Technical Documentation Suite

This repository contains comprehensive technical specifications and engineering guides:

| Document | Primary Focus & Domain |
| :--- | :--- |
| 📋 [**PRD.md**](docs/PRD.md) | **Product Requirements Document:** Vision, personas, clinical motivations, functional & non-functional requirements. |
| 🎨 [**DESIGN.md**](docs/DESIGN.md) | **Design Specifications:** UI/UX philosophy, Daylight/Amber/Midnight tri-theme engine, 30-mood ambient palette, responsive layout. |
| 🏛️ [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | **System Architecture:** Dual-client layered design, FastAPI microservices, sequence diagrams, ML pipelines, and data flows. |
| 🗄️ [**DATABASE.md**](docs/DATABASE.md) | **Database Schema & Models:** MySQL ER diagram, 10 table data dictionaries (including `period_logs`), foreign keys, and migrations. |
| 🔌 [**API.md**](docs/API.md) | **API Documentation:** REST endpoints (`/api/health`, `/api/sentiment`, `/api/period/export`), FastAPI endpoints, request/response contracts. |
| 🤖 [**AGENTS.md**](AGENTS.md) | **AI Agents & LLM Workflows:** Multi-agent pipeline (Crisis Guardian, Mood Classifier, Context Tagger, Vedic Reframer, Voicebot). |
| 💻 [**IMPLEMENTATION.md**](docs/IMPLEMENTATION.md) | **Project Implementation:** Codebase walkthrough, cognitive reframing, negation logic, neural fallbacks, and state management. |
| ⚙️ [**SETUP.md**](docs/SETUP.md) | **Setup & Installation:** Quickstart for Windows, Linux, macOS, Docker containers, FastAPI, and environment variables. |
| 🚀 [**FEATURES.md**](docs/FEATURES.md) | **Feature Roadmap:** Phase 1-4 capabilities, completed milestones, and menstrual cycle tracking. |
| 🔒 [**AUTH.md**](docs/AUTH.md) | **Authentication & Security:** SHA-256 salted/peppered hashing, role-based access control (Student, Counselor, Admin), privacy safeguards. |
| 🌐 [**MCP.md**](docs/MCP.md) | **Model Context Protocol:** MCP server and client integrations for AI agents and developer workflows. |
| 🔗 [**INTEGRATIONS.md**](docs/INTEGRATIONS.md) | **Third-Party Integrations:** Web Speech API, OpenAI API, Tele-MANAS/KIRAN hotlines, SMTP email, PyMuPDF, Matplotlib. |
| 🧪 [**TESTING.md**](docs/TESTING.md) | **Testing & QA Framework:** Test suite architecture, 58 automated unit & integration tests, pytest automated verification. |
| 🛠️ [**DEBUGGING.md**](docs/DEBUGGING.md) | **Troubleshooting & Playbook:** Root cause analyses, route registration fixes, contrast tokens, DLL AppLocker fixes, environment diagnosis. |
| 🚀 [**DEPLOYMENT_GUIDE.md**](DEPLOYMENT_GUIDE.md) | **GitHub & Vercel Deployment Guide:** Complete tabular commands for repository creation, sanitized git push, and Vercel serverless deployment. |

---

## 🌟 Key Functional Pillars

### 🛡️ Multi-Persona Access, Clinical Consent & Caregiver Theming
- **Dedicated & Unified Portals:** Unified `/login` with 3-role switcher, plus dedicated portals (`/login/student`, `/login/counselor`, `/login/admin`) and counselor onboarding (`/register/counselor`).
- **Role-Based Visibility (RBAC):** Admin has full visibility into all platform dashboards and tools; Counselors access clinical queues and permitted clients; Students/General Users access only self-care and journaling tools.
- **Male Ally & Caregiver Mode:** When male users log into `/period`, the platform activates Caregiver Mode, allowing them to track cycles, log symptoms, and view mindful support tips for multiple women in their lives (Wife, Daughter, Sister).
- **Time-Bounded Clinical Consent:** Users can grant temporary clinical access to counselors with custom expiration dates (`allowed_until`), enabling counselors to review reflections and psychometrics at `/counselor/client/<id>`.
- **Multi-Account / Dependent Management:** Users can manage and switch between multiple linked profiles (Self, Children, Dependents, Spouses).


1. **Dual Client Flexibility (Desktop & Web) + FastAPI Microservice:**
   - **Desktop UI (`Main.py` / `gui_desktop/Main.py`):** 27 Tkinter views featuring interactive Matplotlib mood charts, in-app Gita PDF reader, and spinning affirmation wheel.
   - **Web UI (`app.py` / `frontend/`):** Responsive HTML5/CSS3 interface with Daylight (Sage), Warm Amber, and Midnight Cosmic tri-theme engine, REST APIs, and full accessibility contrast compliance.
   - **FastAPI Microservice (`fastapi_app.py`):** High-throughput asynchronous ASGI microservice running on port 8000 for low-latency sentiment scoring and cognitive reframing.
2. **Tri-Theme Visual System & Dynamic 30-Mood Ambient Canvas (Desktop Parity):**
   - Universal theme switcher allowing users to toggle between **Daylight (Sage Natural Theme)**, **Warm Amber**, and **Midnight Cosmic**.
   - Identical to the Tkinter desktop GUI, reflections dynamically illuminate the viewport background with 30 distinct mood colors (`#mood-ambient-glow`), providing immediate visual biofeedback.
3. **Context-Aware Sentiment & Negation Classifier:**
   - Evaluates polarity ($-1.0$ to $+1.0$) and subjectivity ($0.0$ to $1.0$).
   - Custom negation-resolution heuristics ensuring compound phrases (*"not bad"*, *"never satisfied"*) are scored with clinical accuracy.
   - Categorizes situational drivers: *Academic Stress*, *Career / Work*, *Relationships*, *Health & Body*, *Financial Pressure*, *Self-Esteem*, *Loss & Grief*, *Burnout & Overwork*, *Social Anxiety & Loneliness*, and *General Wellbeing*.
4. **Advanced Period Journal, Hormonal Biofeedback & Clinical Diagnostics:**
   - **Clinical Condition Tracking:** Ingests and monitors symptoms for **PCOS / PCOD**, **PMDD (Premenstrual Dysphoric Disorder)**, **PMS**, and **Endometriosis & Chronic Dysmenorrhea**.
   - **Biological Cycle Phase Biofeedback:** Maps daily cycle days to 5 biological phases (Menstrual / Inner Winter, Follicular / Inner Spring, Ovulatory / Inner Summer, Early Luteal, and Late Luteal PMDD vulnerability window) with targeted hormonal trajectory, nutrition, movement, and Vedic wisdom.
   - **Standardized Diagnostic Self-Screeners:**
     - **DSM-5 PMDD Diagnostic Screener (`/api/period/screener/pmdd`):** Evaluates 11 clinical criteria including core affective lability, irritability, and despair.
     - **Rotterdam PCOS Risk Screener (`/api/period/screener/pcos`):** Evaluates cycle irregularity, hyperandrogenism, metabolic markers, and ovarian imaging history.
   - **VAS Pain Severity Tracking (0-10):** Visual Analog Scale for cramping, lower back pain, pelvic ache, and radiating discomfort.
   - **Caregiver & Male Ally Portal:** Dedicated support mode allowing men and family caregivers to log cycles, record pain, and receive actionable compassion tips for multiple women in their lives (Wife, Daughter, Sister, Mother).
   - **Medical-Grade RFC 4180 CSV Export (`/api/period/export`):** Formats comprehensive cycle records, condition tags, pain scores, and clinical notes for physician review.
5. **Sarathi Voice Bot & Conversational AI Companion:**
   - Interactive conversational drawer providing real-time voice recognition and voice synthesis via the Web Speech API.
   - Multimodal agent providing compassionate active listening, cognitive distortion identification, and calming breathing guidance.
   - Intelligently scoped to non-authentication views to protect privacy and eliminate visual distraction during login.
6. **Enterprise Admin Governance Console:**
   - Unified administrative dashboard (`/admin/dashboard`) offering real-time live search across users, counselors, booking slots, and psychometric screening logs.
   - Full administrative lifecycle management: counselor account approval/deletion, slot cancellation, and user moderation.
7. **Dual-Engine Neural Networks (PyTorch + NumPy Fallback):**
   - Seamlessly executes deep learning PyTorch models if available.
   - Automatically switches to He-initialized NumPy sequential networks and portable JSON weights when PyTorch is unavailable or blocked by security policies.
8. **Crisis Guardian & Real-Time Harm Prevention:**
   - Automated keyword and neural crisis scanning detecting suicide ideation and acute medical distress.
   - Triggers an immediate intervention screen providing national 24/7 helplines (**Tele-MANAS: 14416**, **KIRAN: 1800-599-0019**, **Emergency: 112**).
9. **Clinical Psychometric Inventories:**
   - Built-in standardized PHQ-9 (Depression, 9 questions) and GAD-7 (Anxiety, 7 questions) screening tools with automatic clinical severity scoring and historical trend logging.
10. **Counselor Scheduling & Anonymous Peer Forum:**
    - Counselor slot creation and user booking workflow with SMTP email confirmation.
    - Moderated peer forum categorized by student life, professional work, physical health, and mental wellbeing with real-time keyword search.

---

## 🔑 Default Demonstration Accounts

The platform includes pre-seeded demonstration accounts for immediate local or cloud evaluation:

| Persona / Role | Username | Password | Access Scope & Demonstration Features |
| :--- | :---: | :---: | :--- |
| **Student / General User** | `chahat` | `chahat` | Full personal dashboard, **seeded period cycles (5 cycles)**, daily wellness check-ins, clinical screenings, cycle phase biofeedback, and cycle editing/deletion. |
| **System Administrator** | `admin` | `admin` | Full governance console (`/admin/dashboard`), real-time search across all tables, counselor approvals, slot moderation, user audit. |
| **Verified Counselor** | `dr_sharma` | `counselor123` | Counselor clinical portal (`/counselor/dashboard`), slot creation, client appointments, permitted user psychometrics review. |

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.11+ (or Python 3.14)
- MySQL 8.0+ running on `localhost:3306` (or Docker)

### 2. Setup & Installation
```powershell
# Clone or navigate to the repository
cd "Minor Project, python (.venv)"

# Install dependencies
pip install -r requirements.txt

# Initialize MySQL Database (creates tables & seed accounts)
python database_setup.py
```

### 3. Launching Applications

#### Option A: Run the Desktop GUI Application
```powershell
# Run using the Windows batch launcher:
.\run_desktop.bat

# Or run directly via Python:
python Main.py
```

#### Option B: Run the Flask Web Platform
```powershell
# Run using the Windows batch launcher:
.\run_web.bat

# Or run directly via Python:
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

#### Option C: Run the FastAPI Microservice
```powershell
# Run directly via Python:
python fastapi_app.py

# Or run using Uvicorn:
uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 --reload
```
Open interactive Swagger API docs at `http://127.0.0.1:8000/docs`.

#### Option D: Run via Docker Compose
```bash
docker-compose up --build
```

#### Option E: Deploy to Vercel (Cloud Serverless)
Follow the step-by-step instructions in [**DEPLOYMENT_GUIDE.md**](DEPLOYMENT_GUIDE.md):
```powershell
# Authenticate and link project
npx vercel login
npx vercel link

# Deploy production release
npx vercel --prod
```


---

## 🧪 Running Automated Tests

A comprehensive **58-test suite** covers authentication, machine learning inference, NLP context tagging, psychometrics, modular backend architecture, FastAPI endpoints, Period Journal CSV export, and web API endpoints:

```powershell
# Run with system Python
python -m pytest tests/

# Or run with virtual environment Python
.\Scripts\python.exe -m pytest tests/
```

Expected output:
```text
============================= 58 passed in 11.28s =============================
```

---

## 📁 Repository Directory Structure

The repository is organized into dedicated modular folders for frontend, backend, admin, desktop GUI, and documentation, while retaining primary entry points at the root for seamless execution:

```text
├── frontend/                       # Web Client Presentation Layer
│   ├── templates/                  # Responsive HTML5 Jinja2 Templates (12 templates)
│   │   ├── base.html               # Global glassmorphism navigation, tri-theme switcher & sidebar
│   │   ├── dashboard.html          # Journal reflection stream, 30-mood ambient glow & analytics
│   │   ├── resources.html          # Resource hub, Gita explorer & 5-4-3-2-1 grounding
│   │   ├── spinwheel.html          # Universal affirmation wheel & Gita verse pairings
│   │   ├── login.html              # Tri-theme multi-persona authentication portal
│   │   ├── screenings.html         # Interactive PHQ-9 & GAD-7 psychometrics
│   │   ├── booking.html            # Verified counselor scheduling & slots
│   │   ├── forum.html              # Anonymous peer support forum with live search
│   │   ├── todo.html               # Actionable wellness task manager
│   │   ├── period.html             # Menstrual symptom & cycle tracker with CSV export
│   │   ├── admin_dashboard.html    # Enterprise governance console & live table search
│   │   └── counselor_dashboard.html# Counselor appointment reviews & slot generator
│   └── static/                     # Web Styles & Interactive Client Utilities
│       ├── css/main.css            # Daylight/Amber/Midnight tokens, high-contrast & glow rules
│       └── js/main.js              # Sarathi Voicebot, Web Speech API, theme manager & confetti
│
├── services/                       # Modular Service Layer (Separation of Concerns)
│   ├── period_service.py           # Biological cycle phase biofeedback, DSM-5 PMDD & Rotterdam PCOS diagnostics
│   └── __init__.py                 # Services package marker
│
├── backend/                        # Web API & Core Application Server
│   ├── app.py                      # Flask REST API, authentication & cognitive reframing
│   ├── fastapi_app.py              # High-throughput asynchronous ASGI microservice
│   ├── cognitive_reframer.py       # Standalone NLP, negation inversion & 30-mood extractor
│   ├── database_setup.py           # MySQL connection pool, table schema & migrations
│   ├── wellness_ml.py              # Dual-Engine ML (PyTorch & NumPy Sequential fallback)
│   ├── wellness_ml.ipynb           # Model development & training experiments
│   └── models/                     # Deep learning weights & portable JSON matrices
│       ├── nlp_mood_weights.json   # Text mood classification weights
│       ├── nlp_crisis_weights.json # Text crisis detection weights
│       └── wellness_model_weights.json # Resource recommendation weights
│
├── admin/                          # Administrative Tooling & System Governance
│   ├── admin_manager.py            # CLI management tool (audit, users, slots, screenings)
│   ├── seed_data.py                # Database demonstration seed script
│   ├── seed_full_database.py       # Extended seed generator for counselors & users
│   └── __init__.py                 # Admin package marker
│
├── gui_desktop/                    # Desktop Client Applications (Tkinter)
│   ├── Main.py                     # Primary 27-frame desktop GUI application
│   ├── Main_Advanced.py            # Advanced CustomTkinter desktop variant
│   ├── run_desktop.bat             # Folder-local batch launcher
│   └── assets/                     # Desktop bundled assets
│       ├── BhagavadGita_Tri-lingual.pdf # Complete tri-lingual reference text
│       └── gita_preview.png        # Gita thumbnail preview asset
│
├── docs/                           # Documentation Library
│   ├── PRD.md                      # Product Requirements Document
│   ├── DESIGN.md                   # Design System & UI/UX Guidelines
│   ├── ARCHITECTURE.md             # System Architecture & Multi-Client Data Flows
│   ├── DATABASE.md                 # MySQL ER Diagrams & Schema Data Dictionaries
│   ├── API.md                      # REST API Endpoints & Request/Response Contracts
│   ├── AGENTS.md                   # Multi-Agent Ecosystem Specifications
│   ├── IMPLEMENTATION.md           # Implementation Details & Codebase Walkthrough
│   ├── SETUP.md                    # Environment Setup & Deployment Guide
│   ├── FEATURES.md                 # Feature Roadmap & Milestone Matrix
│   ├── AUTH.md                     # Cryptographic Security & RBAC Protocols
│   ├── MCP.md                      # Model Context Protocol Specification
│   ├── INTEGRATIONS.md             # Third-Party Integrations & Hotline Services
│   ├── TESTING.md                  # Test Suite & Quality Assurance Documentation
│   ├── DEBUGGING.md                # Troubleshooting Playbook & Diagnoses
│   ├── README.md                   # Master Project Overview
│   ├── academic/                   # Minor project thesis, synopsis & research reports
│   └── legacy/                     # Historical markdown drafts & notes
│
├── tests/                          # Automated Pytest Regression Test Suite (58 tests)
│   ├── test_auth.py                # SHA-256 salted/peppered hashing tests (3 tests)
│   ├── test_ml.py                  # Machine learning & neural network tests (6 tests)
│   ├── test_nlp.py                 # Context detection, 30 moods & crisis regex (12 tests)
│   ├── test_screenings.py          # PHQ-9 & GAD-7 scoring validation tests (4 tests)
│   ├── test_period_advanced.py     # PMDD/PCOS screeners, cycle phases, CSV buffer, edit/delete, 404 (11 tests)
│   └── test_web.py                 # Flask/FastAPI routes, Portals, Caregiver, Permissions (22 tests)
│
├── templates/                      # Root Jinja2 Templates (synchronized with frontend)
├── static/                         # Root Static Assets (synchronized with frontend)
├── Dockerfile                      # Container Deployment Definition
├── docker-compose.yml              # Multi-Service Orchestration (Web + MySQL)
├── pytest.ini                      # Pytest Configuration & Warning Filters
├── requirements.txt                # Unified Python Dependencies
├── run_web.bat                     # Windows Batch Launcher for Web Platform
├── run_desktop.bat                 # Windows Batch Launcher for Desktop GUI
├── app.py                          # Primary Flask Web Server Entry Point
├── fastapi_app.py                  # Primary FastAPI Microservice Entry Point
├── Main.py                         # Primary Desktop GUI Entry Point
└── database_setup.py               # Primary Database Initializer Entry Point

---

## 👤 Author & Academic Credits

- **Author & Lead Developer:** Chahat Modi  
- **Project Role:** Minor Project / Mental Health Monitoring & Action (MHMA) Framework  
- **Supervision & Review:** Department of Computer Science & Engineering  
- **License:** MIT License — Open for academic and research evaluation
