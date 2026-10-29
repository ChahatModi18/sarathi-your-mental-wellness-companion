# Project Implementation Walkthrough — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Repository Layout & Module Breakdown

- `Main.py` / `Main_Advanced.py`: Primary application entry point; initializes Tkinter graphical loop, window layouts, navigation tabs, and event binders.
- `app.py`: Alternative lightweight launcher and web/service interface adapter.
- `wellness_ml.py`: Custom machine learning and heuristic sentiment scoring pipeline, emotional intensity computation, and model weight loaders.
- `database_setup.py`: Database initialization script creating MySQL tables, default test user credentials, and seeding initial Vedic verses.
- `nlp_mood_weights.json`: Calibrated emotion-keyword weight matrix mapping tokens to clinical valence.
- `nlp_crisis_weights.json`: High-priority keyword dictionaries and emergency triggers.
- `BhagavadGita_Tri-lingual.pdf`: Canonical reference text utilized for corpus verification and Sanskrit citation accuracy.

---

## 2. Key Implementation Details

1. **Lightweight ML Architecture:** Engineered without heavyweight dependencies (TensorFlow/PyTorch) so the application launches instantly on student laptops with under 150MB RAM footprint.
2. **Tkinter Dynamic Threading:** Long computations and database transactions run via asynchronous threading to keep the graphical interface silky smooth at 60 FPS without UI freezes.
3. **Robust Fallbacks:** Implements structured exception handling around database connections, falling back to local file/SQLite storage if MySQL server daemon is uncontactable.
