# Project Implementation Details (IMPLEMENTATION.md) — BhagvadMood Platform

> **Document Version:** 2.1.0  
> **Core Technologies:** Python 3.11+, Tkinter, Flask, FastAPI, MySQL Connector, PyTorch / NumPy, TextBlob, PyMuPDF  
> **Key Implementation Modules:** `Main.py`, `app.py`, `fastapi_app.py`, `cognitive_reframer.py`, `wellness_ml.py`, `database_setup.py`

---

## 1. Codebase Architecture & Modular Organization

The project is structured into modular execution paths providing dual client interfaces while sharing identical business rules, algorithmic models, and persistence schemas.

```
                    ┌────────────────────────────┐
                    │     User / Client Request  │
                    └──────────────┬─────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               ▼                   ▼                   ▼
    ┌──────────────────────┐┌──────────────────────┐┌──────────────────────┐
    │ Desktop Client (GUI) ││ Web Client (Flask)   ││ Microservice(FastAPI)│
    │ Main.py (27 Frames)  ││ app.py (Jinja2 Web)  ││ fastapi_app.py (:8000│
    └──────────┬───────────┘└──────────┬───────────┘└──────────┬───────────┘
               │                       │                       │
               └───────────────────┬───┴───────────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │  NLP & Cognitive Reframer  │
                    │  cognitive_reframer.py     │
                    │  - Negation Inversions     │
                    │  - 30-Mood Classification  │
                    │  - Contextual Gita Shlokas │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │  Dual-Engine Machine Learn │
                    │  wellness_ml.py            │
                    │  - PyTorch Deep Models     │
                    │  - NumPy He-Init Networks  │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │  Persistence & Storage     │
                    │  MySQL 8 (sarathi_sih_db)  │
                    └────────────────────────────┘
```

---

## 2. Core Implementation Walkthrough

### 2.1 The Cognitive Reframer Engine (`cognitive_reframer.py`)
Provides deterministic lexical affect extraction, negation-aware polarity adjustments, and contextual Shloka pairings:
- **Compound Negation Inversion:** Transforms counter-intuitive polarity scores:
  - *"not bad"* $\to$ inverted from negative to mildly positive ($+0.30$).
  - *"not happy"* $\to$ inverted from positive to moderately negative ($-0.40$).
- **30-Mood Extractor (`extract_nuanced_mood`):** Regex taxonomy parser resolving 30 granular states (`ecstatic`, `peaceful`, `burned_out`, `resilient`, `devastated`, `serene`, `anxious`, etc.).

### 2.2 The Machine Learning Dual-Engine (`wellness_ml.py`)
To guarantee uninterrupted execution in locked-down environments (e.g., enterprise systems with AppLocker blocking `torch_python.dll`), `wellness_ml.py` is implemented with a dual-engine architecture:
- **PyTorch Feedforward Models:** When available, `TextPyTorchModel` processes bag-of-words vectors on CPU/CUDA.
- **NumPy Analytical Networks:** When PyTorch fails, `NumPySequential` and `TextNeuralNetwork` load pre-computed He-initialized weights from JSON files (`nlp_mood_weights.json`, `nlp_crisis_weights.json`, `wellness_model_weights.json`), achieving $<15\text{ms}$ local inference.

### 2.3 Period Journal & Menstrual Cycle Math (`app.py`)
The menstrual cycle logging and prediction module computes interval statistics across historical cycle records:
```python
# Calculate interval lengths between consecutive cycle start dates
if len(cycles) > 1:
    for i in range(len(cycles) - 1):
        diff = (cycles[i][0] - cycles[i+1][0]).days
        if diff > 0:
            intervals.append(diff)
    if intervals:
        avg_interval = f"{sum(intervals) / len(intervals):.1f} Days"

# Forecast next cycle date
est_interval = int(round(sum(intervals) / len(intervals))) if intervals else 28
est_next_date = latest_start + timedelta(days=est_interval)
next_period_estimate = est_next_date.strftime('%b %d, %Y')
```
For RFC 4180 CSV export (`/api/period/export`), the records are formatted using Python's `csv.writer` with `io.StringIO` and returned with MIME type `text/csv; charset=utf-8`.

### 2.4 Tri-Theme Visual Engine & Dynamic Ambient Canvas (`static/css/main.css`, `static/js/main.js`)
- **Theme Variables:** CSS custom properties (`--bg-color`, `--card-bg`, `--text-primary`) are bound to root attributes `data-theme="daylight"`, `data-theme="amber"`, or `data-theme="night"`.
- **Theme Persistence:** Client preference is cached in `localStorage.getItem('sarathi_theme')` and applied before DOM rendering to prevent visual flicker.
- **Dynamic 30-Mood Ambient Canvas:** Viewport background is enhanced by `#mood-ambient-glow` with smooth 1.2s CSS ease transitions matching the Desktop GUI.

### 2.5 Enterprise Admin Governance Console (`templates/admin_dashboard.html`)
- **Live Search (`filterAdminTable`):** Real-time client-side search across tables (`usersTable`, `counselorsTable`, `slotsTable`, `logsTable`, `screeningsTable`) without triggering server round-trips.
- **Active Tab Persistence:** The active tab index is preserved across page refreshes via `sessionStorage.getItem('sarathi_active_admin_tab')`.
- **Entity Lifecycle Controllers:** Dedicated POST routes for counselor removal, slot deletion, and user cleanup.
