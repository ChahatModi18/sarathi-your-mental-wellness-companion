# Authentication & Security Specification — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Security Architecture & Threat Model

Mental wellness journals contain deeply personal thoughts. The platform enforces strict **Local-First Privacy**:

1. **Zero External Telemetry:** No user journal entries or affective metrics are sent to remote analytics servers.
2. **Password Hashing:** Passwords hashed using standard cryptographic one-way functions (SHA-256 / PBKDF2 with unique salts).
3. **SQL Injection Prevention:** All database operations utilize parameterized queries through `mysql.connector` and `sqlite3`.
4. **Data Isolation:** User records are logically segregated by `user_id` with foreign key cascade deletion constraints.
5. **Sensitive Log Sanitization:** No plaintext journal contents are ever printed to debug logs or terminal stdout.
