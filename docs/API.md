# API Documentation (API.md) — BhagvadMood Journal Web Services

> **Protocol:** HTTP / HTTPS  
> **Primary Flask Base URL:** `http://127.0.0.1:5000` (Local Development) / `http://0.0.0.0:5000` (Docker Container)  
> **FastAPI Microservice Base URL:** `http://127.0.0.1:8000`  
> **Data Interchange Format:** JSON (`application/json`), CSV (`text/csv`), & HTML5 Forms (`application/x-www-form-urlencoded`)

---

## 1. REST API Endpoints (Flask Web Platform)

### 1.1 Health Check Endpoint
- **URL:** `/api/health`
- **Method:** `GET`
- **Description:** Verifies service uptime and operational status for container orchestration and health probes.
- **Success Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "service": "BhagvadMood Platform API",
    "version": "2.1.0"
  }
  ```

---

### 1.2 Sentiment Analysis & Wisdom Reframing
- **URL:** `/api/sentiment`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Description:** Evaluates textual reflections, computing multi-dimensional affect polarity, subjectivity, 30-mood neural classification, situational context, crisis probability, and paired Bhagavad Gita Shloka.
- **Request Body:**
  ```json
  {
    "text": "I feel completely overwhelmed by upcoming university exams and fear I will fail everyone."
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "mood": "overwhelmed",
    "polarity": -0.65,
    "subjectivity": 0.82,
    "is_crisis": false,
    "crisis_probability": 0.08,
    "context": "Academic Stress",
    "shlok": "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।",
    "shlok_meaning": "Balance in eating, recreation, and actions brings peace. Regulate your efforts step by step.",
    "reframing": "Focus on the steady effort rather than agonizing over future grading outcomes.",
    "affirmation": "I take one mindful step at a time with confidence."
  }
  ```

---

### 1.3 Period Journal CSV Export
- **URL:** `/api/period/export`
- **Method:** `GET`
- **Auth Required:** Yes (Authenticated Student/User)
- **Description:** Generates and streams an RFC 4180 compliant CSV export containing all historical menstrual cycle start/end dates, cycle lengths, flow intensities, and recorded emotional/physical symptoms.
- **Headers Returned:**
  ```http
  Content-Type: text/csv; charset=utf-8
  Content-Disposition: attachment; filename=sarathi_period_journal_export_1.csv
  ```
- **Response Format:**
  ```csv
  timestamp,mood,symptoms,flow,energy,sleep,gratitude,notes
  2026-10-27 14:30:00,calm,cramps,medium,normal,restful,grateful for hot tea,first day of cycle
  ```

---

### 1.4 Gita Verses Directory Endpoint
- **URL:** `/api/gita/verses`
- **Method:** `GET`
- **Description:** Returns the catalog of authenticated Bhagavad Gita Shlokas categorized by psychological themes (Anxiety, Anger, Duty, Peace, Resilience).
- **Success Response (200 OK):**
  ```json
  {
    "total": 18,
    "verses": [
      {
        "chapter": 2,
        "verse": 47,
        "theme": "Duty over Outcome",
        "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        "transliteration": "karmany-evadhikaras te ma phaleshu kadachana",
        "meaning": "You have a right to perform your prescribed duties, but are not entitled to the fruits of actions."
      }
    ]
  }
  ```

---

### 1.5 Complete Mini-Goal Endpoint
- **URL:** `/api/complete-minigoal`
- **Method:** `POST`
- **Auth Required:** Yes
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "reward": 25,
    "goal_text": "Square Breathing (4-4-4-4)"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "success": true,
    "points_awarded": 25,
    "total_points": 175
  }
  ```

---

## 2. FastAPI Asynchronous Microservice Endpoints (Port 8000)

| Endpoint | Method | Input Model | Output Model | Description |
| :--- | :---: | :--- | :--- | :--- |
| `/api/v1/health` | `GET` | None | `{"status": "healthy"}` | Fast ASGI uptime heartbeat |
| `/api/v1/analyze` | `POST` | `{"text": str}` | Sentiment, Mood, Context, Gita Reframing | Asynchronous low-latency text classification |
| `/api/v1/chat` | `POST` | `{"message": str}` | Conversational reply, crisis status, shlok | Mindful conversational agent response |
| `/api/v1/recommend-tier`| `POST` | `{"age": int, "gender": str, "phq9": int, "gad7": int, "polarity": float}` | `{"tier": int, "probabilities": list}` | Asynchronous ML resource triage |

---

## 3. Web Application Controller Routes

| Route | HTTP Method | Auth Required | Role | Description |
| :--- | :---: | :---: | :---: | :--- |
| `/` | `GET` | No | Public | Responsive landing page introducing Sarathi features |
| `/login` | `GET`, `POST` | No | Public | Multi-persona login supporting Daylight, Amber, Midnight themes |
| `/register` | `GET`, `POST` | No | Public | User and counselor registration with clinical condition capture |
| `/logout` | `GET` | Yes | All | Clears session cookies and redirects to `/login` |
| `/dashboard` | `GET` | Yes | Student | Main journal dashboard, 30-mood ambient glow, analytics |
| `/journal/submit` | `POST` | Yes | Student | Processes reflection, executes NLP, logs to MySQL |
| `/screenings` | `GET`, `POST` | Yes | Student | Interactive PHQ-9 & GAD-7 psychometrics scoring |
| `/resources` | `GET` | Yes | Student | Resource portal, Gita PDF reader, grounding exercises |
| `/forum` | `GET`, `POST` | Yes | Student | Peer support community with category & live query filter |
| `/booking` | `GET`, `POST` | Yes | Student | Counselor appointment scheduling & slot reservation |
| `/period` | `GET`, `POST` | Yes | Student | Menstrual cycle logger, cycle forecast, and symptom tracker |
| `/todo` | `GET`, `POST` | Yes | Student | Actionable task manager awarding Mindful Points |
| `/spinwheel` | `GET`, `POST` | Yes | Student | Daily affirmation spin wheel with cognitive reframing |
| `/counselor/dashboard` | `GET`, `POST` | Yes | Counselor | Counselor appointment review and calendar slot generator |
| `/admin/dashboard` | `GET` | Yes | Admin | Unified governance console with live search across all tables |
| `/admin/delete_counselor/<id>`| `POST` | Yes | Admin | Deletes counselor profile and associated slot records |
| `/admin/delete_slot/<id>` | `POST` | Yes | Admin | Cancels and deletes counselor availability slots |
| `/admin/delete_user/<id>` | `POST` | Yes | Admin | Deletes user accounts and cleans up relational records |
| `/login/student` | `GET` | No | Public | Dedicated Student & General User login portal |
| `/login/counselor` | `GET` | No | Public | Dedicated Counselor clinical login portal |
| `/login/admin` | `GET` | No | Public | Dedicated Enterprise Administrator login gateway |
| `/register/counselor` | `GET`, `POST` | No | Public | Dedicated Counselor registration portal |
| `/api/profile/add` | `POST` | Yes | Student | Adds a managed profile (daughter, wife, sister, dependent) |
| `/api/profile/switch/<id>`| `GET` | Yes | Student | Switches active profile context |
| `/api/permissions/grant` | `POST` | Yes | Student | Grants time-bounded clinical access to counselor until custom date |
| `/api/permissions/revoke/<id>`| `POST`| Yes | Student | Revokes counselor access permission immediately |
| `/counselor/client/<id>`| `GET` | Yes | Counselor/Admin | Counselor clinical review of permitted client history |
| `/api/period/screener/pmdd`| `POST`| Yes | Student | Evaluates DSM-5 PMDD criteria, records assessment score & advice |
| `/api/period/screener/pcos`| `POST`| Yes | Student | Evaluates Rotterdam PCOS criteria, records clinical risk indicators |
| `/api/period/cycle/edit/<id>`| `POST`| Yes | Student | Updates cycle dates, conditions, pain score, flow texture, and notes |
| `/api/period/cycle/delete/<id>`| `POST`| Yes | Student | Deletes an individual cycle record |
| `/api/period/wellness/edit/<id>`| `POST`| Yes | Student | Updates daily wellness check-in (mood, symptoms, energy, sleep, notes) |

---

## 4. Error Handling & Status Codes

| HTTP Status Code | Description | Standard System Action |
| :---: | :--- | :--- |
| `200 OK` | Request succeeded | Returns JSON or renders requested view template |
| `302 Found` | Redirection | Unauthenticated users redirected to `/login`; submissions redirect to view |
| `400 Bad Request` | Missing or invalid payload | Returns JSON error message or flashes validation alert |
| `403 Forbidden` | Access control violation | User attempting to access `/admin/dashboard` or `/counselor/dashboard` without credentials |
| `404 Not Found` | Route does not exist | Renders standard error view |
| `500 Server Error` | Unhandled database or backend exception | Logs exception to stderr and falls back to safe defaults |
