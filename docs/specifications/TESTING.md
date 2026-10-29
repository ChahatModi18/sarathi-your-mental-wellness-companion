# Testing & QA Frameworks (TESTING.md) — BhagvadMood Platform

> **Document Version:** 2.0.0  
> **Testing Framework:** `pytest`  
> **Coverage Target:** Machine Learning, NLP Context, Cryptographic Auth, Psychometrics, and Flask Web Endpoints  
> **Total Active Automated Tests:** 32

---

## 1. Test Suite Architecture

All automated test suites reside within the dedicated `tests/` directory:

```text
tests/
├── test_auth.py           # Cryptographic hashing & RBAC credentials (3 tests)
├── test_ml.py             # Neural networks, synthetic data, predictions (6 tests)
├── test_nlp.py            # Context tagger & crisis regex scanner (8 tests)
├── test_screenings.py     # PHQ-9 & GAD-7 scoring algorithms (4 tests)
├── test_web.py            # Flask routes, modular imports, and REST API (11 tests)
└── [legacy test scripts: test_booking.py, test_slots_ui.py, test_ml_diagnostics.py]
```

---

## 2. Test Cases Overview

### 2.1 Machine Learning Suite (`tests/test_ml.py`)
- `test_generate_synthetic_data`: Verifies sample dimensions ($N \times 5$), normalization constraints ($[0.0, 1.0]$), and one-hot encoding validity ($\sum y_i = 1.0$).
- `test_train_or_load_model`: Verifies dual-engine initialization and weight loading for PyTorch and NumPy Sequential models.
- `test_recommend_resource_output_shape`: Validates that `recommend_resource` outputs an integer class index ($0-3$) and probability vector summing to $1.0$.
- `test_text_to_vector`: Ensures domain vocabulary tokens are converted to correct vector lengths.
- `test_predict_mood`: Validates mood prediction output string and probability distribution over all 6 core emotion classes.
- `test_predict_crisis`: Verifies that explicit self-harm inputs trigger `is_crisis == True` with probability $\ge 0.50$.

### 2.2 NLP & Context Analysis Suite (`tests/test_nlp.py`)
- `test_detect_text_context_academic`: Validates that terms like "exam", "assignment", "semester" tag as `Academic Stress`.
- `test_detect_text_context_career`: Validates that terms like "office", "boss", "salary" tag as `Career / Work`.
- `test_detect_text_context_relationships`: Validates partner/friend conflicts tag as `Relationships`.
- `test_detect_text_context_default`: Validates neutral reflections default safely to `General Wellbeing`.
- `test_crisis_keyword_detection_true`: Asserts suicide ideation regex triggers.
- `test_crisis_keyword_detection_physical`: Asserts severe chest pain and medical emergencies trigger.
- `test_crisis_keyword_detection_false`: Asserts healthy everyday text does not false-positive.
- `test_mood_keywords_coverage`: Validates presence and depth of emotion dictionary sets.

### 2.3 Authentication Suite (`tests/test_auth.py`)
- `test_hash_password_consistency`: Confirms deterministic SHA-256 output and 64-character hex length.
- `test_hash_password_salt_uniqueness`: Asserts distinct salts produce distinct hashes for identical passwords across usernames.
- `test_hash_password_case_insensitivity_on_username`: Confirms lowercase username canonicalization.

### 2.4 Clinical Screenings Suite (`tests/test_screenings.py`)
- `test_phq9_questions_count`: Verifies 9 clinical questions.
- `test_gad7_questions_count`: Verifies 7 clinical questions.
- `test_phq9_score_mapping`: Validates clinical risk tiers (Minimal, Mild, Moderate, Moderately Severe, Severe).
- `test_gad7_score_mapping`: Validates anxiety risk tiers (Minimal, Mild, Moderate, Severe).

### 2.5 Web Application Suite (`tests/test_web.py`)
- `test_root_landing_page`: Asserts HTTP 200 on landing page.
- `test_login_page_renders`: Asserts HTTP 200 on login view.
- `test_unauthenticated_dashboard_redirect`: Asserts HTTP 302 redirecting to `/login` for unauthenticated requests.
- `test_api_sentiment_endpoint`: Asserts HTTP 200 on `/api/sentiment` with valid mood and paired Shloka JSON.

---

## 3. How to Run the Test Suite

Execute pytest across the workspace:
```powershell
python -m pytest tests/
```

For verbose output with execution times:
```powershell
python -m pytest tests/ -v --durations=5
```

Expected output:
```text
tests/test_auth.py::test_hash_password_consistency PASSED
tests/test_auth.py::test_hash_password_salt_uniqueness PASSED
tests/test_auth.py::test_hash_password_case_insensitivity_on_username PASSED
tests/test_ml.py::test_generate_synthetic_data PASSED
tests/test_ml.py::test_train_or_load_model PASSED
tests/test_ml.py::test_recommend_resource_output_shape PASSED
tests/test_ml.py::test_text_to_vector PASSED
tests/test_ml.py::test_predict_mood PASSED
tests/test_ml.py::test_predict_crisis PASSED
tests/test_nlp.py::test_detect_text_context_academic PASSED
tests/test_nlp.py::test_detect_text_context_career PASSED
tests/test_nlp.py::test_detect_text_context_relationships PASSED
tests/test_nlp.py::test_detect_text_context_default PASSED
tests/test_nlp.py::test_crisis_keyword_detection_true PASSED
tests/test_nlp.py::test_crisis_keyword_detection_physical PASSED
tests/test_nlp.py::test_crisis_keyword_detection_false PASSED
tests/test_nlp.py::test_mood_keywords_coverage PASSED
tests/test_screenings.py::test_phq9_questions_count PASSED
tests/test_screenings.py::test_gad7_questions_count PASSED
tests/test_screenings.py::test_phq9_score_mapping PASSED
tests/test_screenings.py::test_gad7_score_mapping PASSED
tests/test_web.py::test_root_landing_page PASSED
tests/test_web.py::test_login_page_renders PASSED
tests/test_web.py::test_unauthenticated_dashboard_redirect PASSED
tests/test_web.py::test_api_sentiment_endpoint PASSED

======================== 25 passed in 12.89s ========================
```

