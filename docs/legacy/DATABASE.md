# Database Architecture & Schema Specification — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Engine:** MySQL 8.0+ / SQLite 3 Fallback  

---

## 1. Entity Relationship Overview

The schema is normalized to 3NF, ensuring minimal data redundancy, atomic transactions, and swift retrieval for analytics.

```
+------------------+         1:N         +--------------------+
|      USERS       | ------------------> |   JOURNAL_ENTRIES  |
+------------------+                     +--------------------+
| id (PK)          |                     | id (PK)            |
| username         |                     | user_id (FK)       |
| password_hash    |                     | title              |
| created_at       |                     | content            |
+------------------+                     | polarity_score     |
                                         | subjectivity_score |
                                         | primary_emotion    |
                                         | created_at         |
                                         +--------------------+
                                                   │
                                                   │ 1:1
                                                   ▼
                                         +--------------------+
                                         | VEDIC_REFLECTIONS  |
                                         +--------------------+
                                         | id (PK)            |
                                         | entry_id (FK)      |
                                         | chapter            |
                                         | verse              |
                                         | sanskrit_text      |
                                         | english_meaning    |
                                         +--------------------+
```

---

## 2. Table Definitions (DDL)

### 2.1 `users`
```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.2 `journal_entries`
```sql
CREATE TABLE IF NOT EXISTS journal_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    polarity_score DECIMAL(4,3) NOT NULL,
    subjectivity_score DECIMAL(4,3) NOT NULL,
    primary_emotion VARCHAR(32) NOT NULL,
    crisis_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.3 `vedic_reflections`
```sql
CREATE TABLE IF NOT EXISTS vedic_reflections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry_id INT NOT NULL,
    chapter INT NOT NULL,
    verse INT NOT NULL,
    sanskrit_shloka TEXT NOT NULL,
    english_translation TEXT NOT NULL,
    reframe_guidance TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
