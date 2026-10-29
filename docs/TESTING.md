# Testing & QA Frameworks (TESTING.md) — BhagvadMood Platform

> **Document Version:** 2.1.0  
> **Testing Framework:** `pytest`  
> **Coverage Target:** Machine Learning, NLP Context, Cryptographic Auth, Psychometrics, Period Journal CSV, Admin Governance, and Flask/FastAPI Web Endpoints  
> **Total Active Automated Tests:** 58 Passed (0 Warnings)

---

## 1. Test Suite Architecture

All automated test suites reside within the dedicated `tests/` directory:

```text
tests/
├── test_auth.py           # Cryptographic hashing & RBAC credentials (3 tests)
├── test_ml.py             # Neural networks, synthetic data, predictions (6 tests)
├── test_nlp.py            # Context tagger, 30 moods & crisis regex scanner (12 tests)
├── test_screenings.py     # PHQ-9 & GAD-7 scoring algorithms (4 tests)
└── test_web.py            # Flask routes, Portals, Caregiver, Permissions & Admin (22 tests)
```

---

## 2. Test Cases Overview (47 Automated Tests)

### 2.1 Machine Learning Suite (`tests/test_ml.py` — 6 Tests)
- `test_generate_synthetic_data`: Verifies sample dimensions ($N \times 5$), normalization constraints ($[0.0, 1.0]$), and one-hot encoding validity ($\sum y_i = 1.0$).
- `test_train_or_load_model`: Verifies dual-engine initialization and weight loading for PyTorch and NumPy Sequential models.
- `test_recommend_resource_output_shape`: Validates that `recommend_resource` outputs an integer class index ($0-3$) and probability vector summing to $1.0$.
- `test_text_to_vector`: Ensures domain vocabulary tokens are converted to correct vector lengths.
- `test_predict_mood`: Validates mood prediction output string and probability distribution over core emotion classes.
- `test_predict_crisis`: Verifies that explicit self-harm inputs trigger `is_crisis == True` with probability $\ge 0.50$.

### 2.2 NLP, Context & Negation Suite (`tests/test_nlp.py` — 12 Tests)
- `test_detect_text_context_academic`: Validates that terms like "exam", "assignment", "semester" tag as `Academic Stress`.
- `test_detect_text_context_career`: Validates that terms like "office", "boss", "salary" tag as `Career / Work`.
- `test_detect_text_context_relationships`: Validates partner/friend conflicts tag as `Relationships`.
- `test_detect_text_context_default`: Validates neutral reflections default safely to `General Wellbeing`.
- `test_detect_text_context_social_anxiety`: Asserts social withdrawal and isolation tag as `Social Anxiety & Loneliness`.
- `test_detect_text_context_burnout`: Asserts exhaustion and chronic work drain tag as `Burnout & Overwork`.
- `test_crisis_keyword_detection_true`: Asserts suicide ideation regex triggers.
- `test_crisis_keyword_detection_physical`: Asserts severe chest pain and medical emergencies trigger.
- `test_crisis_keyword_detection_false`: Asserts healthy everyday text does not false-positive.
- `test_mood_keywords_coverage_30_moods`: Validates presence and non-emptiness of all 30 emotion keywords across the extended taxonomy.
- `test_compound_negation_inversion`: Validates that *"not bad"* flips to positive polarity and *"not happy"* flips to negative polarity.
- `test_extract_nuanced_mood`: Confirms accurate regex extraction for nuanced states (*"burned_out"*, *"resilient"*).

### 2.3 Authentication Suite (`tests/test_auth.py` — 3 Tests)
- `test_hash_password_consistency`: Confirms deterministic SHA-256 output and 64-character hex length.
- `test_hash_password_salt_uniqueness`: Asserts distinct username salts produce distinct hashes for identical passwords.
- `test_hash_password_case_insensitivity_on_username`: Confirms lowercase username canonicalization.

### 2.4 Clinical Screenings Suite (`tests/test_screenings.py` — 4 Tests)
- `test_phq9_questions_count`: Verifies 9 clinical questions.
- `test_gad7_questions_count`: Verifies 7 clinical questions.
- `test_phq9_score_mapping`: Validates clinical risk tiers (Minimal, Mild, Moderate, Moderately Severe, Severe).
- `test_gad7_score_mapping`: Validates anxiety risk tiers (Minimal, Mild, Moderate, Severe).

### 2.5 Web & API Suite (`tests/test_web.py` — 18 Tests)
- `test_root_landing_page`: Asserts HTTP 200 on landing page.
- `test_login_page_renders`: Asserts HTTP 200 on login view with proper theme tokens and Login/Welcome indicators.
- `test_unauthenticated_dashboard_redirect`: Asserts HTTP 302 redirecting to `/login` for unauthenticated requests.
- `test_unauthenticated_resources_redirect`: Asserts HTTP 302 redirecting to `/login`.
- `test_unauthenticated_spinwheel_redirect`: Asserts HTTP 302 redirecting to `/login`.
- `test_api_sentiment_endpoint`: Asserts HTTP 200 and schema validity on `/api/sentiment`.
- `test_api_health_endpoint`: Asserts HTTP 200 on `/api/health`.
- `test_api_gita_verses_endpoint`: Asserts HTTP 200 on `/api/gita/verses`.
- `test_authenticated_routes`: Validates session authentication across dashboard, resources, spinwheel, and mini-goal completion.
- `test_admin_dashboard_portal`: Asserts HTTP 200 and enterprise governance banner on `/admin/dashboard`.
- `test_backend_modular_import`: Verifies clean modular importing from `backend.app`.
- `test_admin_manager_audit`: Validates programmatic platform audit health check.
- `test_fastapi_health`: Asserts HTTP 200 on FastAPI `/api/v1/health`.
- `test_fastapi_analyze`: Asserts HTTP 200 and JSON reframing on FastAPI `/api/v1/analyze`.
- `test_fastapi_chat`: Asserts HTTP 200 on FastAPI `/api/v1/chat`.
- `test_fastapi_chat_crisis_interception`: Verifies suicide ideation triggers crisis intervention on FastAPI `/api/v1/chat`.
- `test_period_export_csv`: Asserts HTTP 200, `text/csv` mime type, and valid headers on `/api/period/export`.
- `test_forum_live_search`: Asserts HTTP 200 and search results filtering on `/forum?q=anxiety`.
- `test_dedicated_login_portals`: Asserts HTTP 200 on `/login/student`, `/login/counselor`, `/login/admin`, and `/register/counselor`.
- `test_male_caregiver_period_access`: Verifies male user accesses `/period` in Caregiver & Ally Mode.
- `test_managed_profile_creation_and_switch`: Asserts HTTP 302 on `/api/profile/add` for dependent profiles.
- `test_counselor_clinical_permission_workflow`: Validates user granting permission on `/api/permissions/grant` and counselor accessing `/counselor/client/<id>`.

---

## 3. Running Automated Tests

```powershell
# Run the complete test suite:
python -m pytest tests/

# Run with verbose test-by-test reporting:
python -m pytest tests/ -v

# Run a specific test suite:
python -m pytest tests/test_web.py
```

Expected output:
```text
============================= 58 passed in 6.91s =============================
```
