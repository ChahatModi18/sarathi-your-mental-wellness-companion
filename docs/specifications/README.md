# 🕉️ BhagvadMood Journal (Sarathi) — AI-Powered Mental Wellness Ecosystem

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.1+](https://img.shields.io/badge/web-Flask%203.1+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Desktop: Tkinter](https://img.shields.io/badge/desktop-Tkinter%20GUI-purple.svg)](https://docs.python.org/3/library/tkinter.html)
[![Database: MySQL 8](https://img.shields.io/badge/database-MySQL%208.0-orange.svg)](https://www.mysql.com/)
[![ML: PyTorch + NumPy](https://img.shields.io/badge/ML-PyTorch%20%7C%20NumPy-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 32 Passed](https://img.shields.io/badge/tests-32%20passed-brightgreen.svg)](tests/)

An offline-first, privacy-centric mental wellness and reflective journaling ecosystem. It integrates clinical cognitive-behavioral assessment methodologies (PHQ-9, GAD-7) with evidence-backed cognitive reframing, multi-dimensional NLP sentiment classification, dual-engine neural networks, and timeless Vedic equanimity principles derived from the *Bhagavad Gita*.

---

## 📚 Complete Technical Documentation Suite

This repository contains comprehensive technical specifications and engineering guides:

| Document | Primary Focus & Domain |
| :--- | :--- |
| 📋 [**PRD.md**](PRD.md) | **Product Requirements Document:** Vision, personas, clinical motivations, functional & non-functional requirements. |
| 🎨 [**DESIGN.md**](DESIGN.md) | **Design Specifications:** UI/UX philosophy, emotion color systems, typography, Tkinter & responsive Web layouts. |
| 🏛️ [**ARCHITECTURE.md**](ARCHITECTURE.md) | **System Architecture:** Dual-client layered design, sequence diagrams, ML pipelines, and data flows. |
| 🗄️ [**DATABASE.md**](DATABASE.md) | **Database Schema & Models:** MySQL ER diagram, 10 table data dictionaries, foreign keys, and migration strategies. |
| 🔌 [**API.md**](API.md) | **API Documentation:** REST endpoints (`/api/health`, `/api/sentiment`), request/response contracts, web routes. |
| 🤖 [**AGENTS.md**](AGENTS.md) | **AI Agents & LLM Workflows:** Multi-agent pipeline (Crisis Guardian, Mood Classifier, Context Tagger, Vedic Reframer). |
| 💻 [**IMPLEMENTATION.md**](IMPLEMENTATION.md) | **Project Implementation:** Codebase walkthrough, negation logic, neural fallbacks, and state management. |
| ⚙️ [**SETUP.md**](SETUP.md) | **Setup & Installation:** Quickstart for Windows, Linux, macOS, Docker containers, and environment variables. |
| 🚀 [**FEATURES.md**](FEATURES.md) | **Feature Roadmap:** Phase 1-4 capabilities, completed milestones, and planned future innovations. |
| 🔒 [**AUTH.md**](AUTH.md) | **Authentication & Security:** SHA-256 salted/peppered hashing, role-based access control, privacy safeguards. |
| 🌐 [**MCP.md**](MCP.md) | **Model Context Protocol:** MCP server and client integrations for AI agents and developer workflows. |
| 🔗 [**INTEGRATIONS.md**](INTEGRATIONS.md) | **Third-Party Integrations:** OpenAI API, Tele-MANAS/KIRAN hotlines, SMTP email, PyMuPDF, Matplotlib. |
| 🧪 [**TESTING.md**](TESTING.md) | **Testing & QA Framework:** Test suite architecture, unit & integration tests, pytest automated verification. |
| 🛠️ [**DEBUGGING.md**](DEBUGGING.md) | **Troubleshooting & Playbook:** Root cause analyses, resolution guides, DLL AppLocker fixes, environment diagnosis. |

---

## 🌟 Key Functional Pillars

1. **Dual Client Flexibility (Desktop & Web):**
   - **Desktop UI (`Main.py`):** 27 Tkinter views featuring interactive Matplotlib mood charts, in-app Gita PDF reader, and spinning affirmation wheel.
   - **Web UI (`app.py`):** Modern glassmorphism HTML5/CSS3 interface with responsive sidebar and REST APIs.
2. **Context-Aware Sentiment & Negation Classifier:**
   - Evaluates polarity ($-1.0$ to $+1.0$) and subjectivity ($0.0$ to $1.0$).
   - Custom negation-resolution heuristics ensuring compound phrases (*"not happy"*, *"never satisfied"*) are scored with clinical accuracy.
   - Categorizes situational drivers: *Academic Stress*, *Career / Work*, *Relationships*, *Health & Body*, *Financial Pressure*, *Self-Esteem*, *Loss & Grief*.
3. **Dual-Engine Neural Networks (PyTorch + NumPy Fallback):**
   - Seamlessly executes deep learning PyTorch models if available.
   - Automatically switches to He-initialized NumPy sequential networks and portable JSON weights when PyTorch is unavailable or blocked by security policies.
4. **Crisis Guardian & Real-Time Harm Prevention:**
   - Automated keyword and neural crisis scanning detecting suicide ideation and acute medical distress.
   - Triggers an immediate intervention screen providing national 24/7 helplines (**Tele-MANAS: 14416**, **KIRAN: 1800-599-0019**, **Emergency: 112**).
5. **Vedic Cognitive Reframing:**
   - Pairs emotional states with authentic Sanskrit Shlokas from the *Bhagavad Gita*, transliterations, English translations, and cognitive reframing prompts.
6. **Clinical Psychometric Inventories:**
   - Built-in standardized PHQ-9 (Depression, 9 questions) and GAD-7 (Anxiety, 7 questions) screening tools with automatic clinical severity scoring and historical trend logging.
7. **Counselor Scheduling & Anonymous Peer Forum:**
   - Counselor slot creation and user booking workflow with SMTP email confirmation.
   - Moderated peer forum categorized by student life, professional work, physical health, and mental wellbeing.

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

#### Option C: Run via Docker Compose
```bash
docker-compose up --build
```

---

## 🧪 Running Automated Tests

A comprehensive 32-test suite covers authentication, machine learning inference, NLP context tagging, psychometrics, modular backend architecture, and web API endpoints:

```powershell
# Run with system Python
python -m pytest tests/

# Or run with virtual environment Python
.\Scripts\python.exe -m pytest tests/
```

Expected output:
```text
======================= 32 passed, 1 warning in 4.95s =======================
```

---

## 📁 Repository Directory Structure

The repository is organized into dedicated modular folders for frontend, backend, admin, desktop GUI, and documentation:

```text
├── frontend/                       # Web Client Presentation Layer
│   ├── templates/                  # Responsive HTML5 Jinja2 Templates (12 templates)
│   │   ├── base.html               # Global glassmorphism navigation & sidebar layout
│   │   ├── dashboard.html          # Journal reflection stream, mini-goals & analytics
│   │   ├── resources.html          # Resource hub, Gita explorer & 5-4-3-2-1 grounding
│   │   ├── spinwheel.html          # Universal affirmation wheel & Gita verse pairings
│   │   ├── login.html              # Multi-persona authentication portal
│   │   ├── screenings.html         # Interactive PHQ-9 & GAD-7 psychometrics
│   │   ├── booking.html            # Verified counselor scheduling & slots
│   │   ├── forum.html              # Anonymous peer support forum
│   │   ├── todo.html               # Actionable wellness task manager
│   │   ├── period.html             # Menstrual symptom & cycle tracker
│   │   ├── admin_dashboard.html    # Administrative overview & statistics
│   │   └── counselor_dashboard.html# Counselor appointment reviews & slot generator
│   └── static/                     # Web Styles & Interactive Client Utilities
│       ├── css/main.css            # Glassmorphism, mandala animations & dark mode
│       └── js/main.js              # TTS speech synthesis, breathing coach & confetti
│
├── backend/                        # Web API & Core Application Server
│   ├── app.py                      # Flask REST API, authentication & cognitive reframing
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
│   ├── specifications/             # 15 Complete Technical Markdown Specifications
│   │   ├── PRD.md                  # Product Requirements Document
│   │   ├── DESIGN.md               # Design System & UI/UX Guidelines
│   │   ├── ARCHITECTURE.md         # System Architecture & Multi-Client Data Flows
│   │   ├── DATABASE.md             # MySQL ER Diagrams & Schema Data Dictionaries
│   │   ├── API.md                  # REST API Endpoints & Request/Response Contracts
│   │   ├── AGENTS.md               # Multi-Agent Ecosystem Specifications
│   │   ├── IMPLEMENTATION.md       # Implementation Details & Codebase Walkthrough
│   │   ├── SETUP.md                # Environment Setup & Deployment Guide
│   │   ├── FEATURES.md             # Feature Roadmap & Milestone Matrix
│   │   ├── AUTH.md                 # Cryptographic Security & RBAC Protocols
│   │   ├── MCP.md                  # Model Context Protocol Specification
│   │   ├── INTEGRATIONS.md         # Third-Party Integrations & Hotline Services
│   │   ├── TESTING.md              # Test Suite & Quality Assurance Documentation
│   │   ├── DEBUGGING.md            # Troubleshooting Playbook & Diagnoses
│   │   └── README.md               # Master Project Overview
│   ├── academic/                   # Minor project thesis, synopsis & research reports
│   └── legacy/                     # Historical markdown drafts & notes
│
├── tests/                          # Automated Pytest Regression Test Suite (32 tests)
│   ├── test_auth.py                # SHA-256 salted/peppered hashing tests
│   ├── test_ml.py                  # Machine learning & neural network tests
│   ├── test_nlp.py                 # Context detection & crisis regex tests
│   ├── test_screenings.py          # PHQ-9 & GAD-7 scoring validation tests
│   └── test_web.py                 # Flask routes, modular imports & REST API tests
│
├── Dockerfile                      # Container Deployment Definition
├── docker-compose.yml              # Multi-Service Orchestration (Web + MySQL)
├── requirements.txt                # Unified Python Dependencies
├── run_web.bat                     # Windows Batch Launcher for Web Platform
├── run_desktop.bat                 # Windows Batch Launcher for Desktop GUI
├── app.py                          # Root Entry Point (forwards to backend.app)
├── Main.py                         # Root Entry Point (forwards to gui_desktop.Main)
└── database_setup.py               # Root Entry Point (forwards to backend.database_setup)

---

## 👤 Author & Academic Credits

- **Author & Lead Developer:** Chahat Modi  
- **Project Role:** Minor Project / Mental Health Monitoring & Action (MHMA) Framework  
- **Supervision & Review:** Department of Computer Science & Engineering  
- **License:** MIT License — Open for academic and research evaluation
