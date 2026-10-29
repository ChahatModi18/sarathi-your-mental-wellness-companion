# Testing & Quality Assurance Plan — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Test Suite Organization

- `test_ml_diagnostics.py`: Evaluates sentiment analysis accuracy across positive, negative, mixed, and negated sentences.
- `test_booking.py` / `test_slots_ui.py`: Verifies calendar picker widgets and entry date filtering.

---

## 2. Key Test Cases

| Test ID | Category | Scenario / Input | Expected Result |
| :--- | :--- | :--- | :--- |
| **TC-NLP-01** | Negation | "I am not feeling depressed today" | Polarity > 0 (Recognizes negation flip) |
| **TC-NLP-02** | Crisis Flag | "I don't want to live anymore" | `is_crisis == True`, Helpline modal triggers |
| **TC-DB-01** | Failover | MySQL service offline | Graceful switch to SQLite, zero crash |
| **TC-SEC-01** | SQL Injection | `Robert'; DROP TABLE users;--` | Sanitized; input treated as literal string |
