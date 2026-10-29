# API Documentation (API.md) — BhagvadMood Journal Web Services

> **Protocol:** HTTP / HTTPS  
> **Base URL:** `http://127.0.0.1:5000` (Local Development) / `http://0.0.0.0:5000` (Docker Container)  
> **Data Interchange Format:** JSON (`application/json`) & HTML5 Forms (`application/x-www-form-urlencoded`)

---

## 1. REST API Endpoints

### 1.1 Health Check Endpoint
- **URL:** `/api/health`
- **Method:** `GET`
- **Description:** Verifies service uptime and operational status for container orchestration and health probes.
- **Success Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "service": "BhagvadMood Platform API",
    "version": "1.0.0"
  }
  ```

---

### 1.2 Sentiment Analysis & Wisdom Reframing
- **URL:** `/api/sentiment`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Description:** Evaluates textual reflections, computing multi-dimensional affect polarity, subjectivity, neural mood classification, crisis probability, and paired Bhagavad Gita Shloka.
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
    "shlok": "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।",
    "shlok_meaning": "Balance in eating, recreation, and actions brings peace. Regulate your efforts step by step."
  }
  ```
- **Error Response (400 Bad Request):**
  ```json
  {
    "error": "No text provided"
  }
  ```

---

## 2. Web Application Routes & Controller Endpoints

| Route | HTTP Method | Auth Required | Description |
| :--- | :---: | :---: | :--- |
| `/` | `GET` | No | Public landing page introducing BhagvadMood capabilities |
| `/login` | `GET`, `POST` | No | Authentication form handling Student, Professional, Counselor & Admin logins |
| `/register` | `GET`, `POST` | No | Registration interface capturing username, password, age, and gender |
| `/logout` | `GET` | Yes | Clears session cookie and redirects to `/login` |
| `/dashboard` | `GET` | Yes | Master user dashboard showing mood history, streak, and quick action cards |
| `/journal/submit` | `POST` | Yes | Ingests journal reflections, runs NLP analysis, stores entry in MySQL |
| `/screenings` | `GET`, `POST` | Yes | Renders and evaluates PHQ-9 (Depression) and GAD-7 (Anxiety) inventories |
| `/resources` | `GET` | Yes | Displays curated wellness guides, Gita reader, and helpline directories |
| `/forum` | `GET`, `POST` | Yes | Anonymous peer support forum with category filters (`Student Life`, `Mental Health`, etc.) |
| `/booking` | `GET`, `POST` | Yes | Appointment booking interface for counselor sessions |
| `/period` | `GET`, `POST` | Yes | Menstrual cycle logger and symptom/mood tracker |
| `/todo` | `GET`, `POST` | Yes | Mindful to-do list manager awarding Mindful Points upon task completion |
| `/spinwheel` | `GET`, `POST` | Yes | Interactive affirmation spin wheel offering instant cognitive reframing |
| `/export` | `GET` | Yes | Exports the authenticated user's journal entries into a downloadable CSV |
| `/counselor/dashboard` | `GET`, `POST` | Counselor | Counselor appointment review, approval, rejection, and slot creator |
| `/admin/dashboard` | `GET`, `POST` | Admin | Administrative metrics, system user lists, and audit summaries |

---

## 3. Error Handling & Status Codes

| HTTP Status Code | Description | Standard System Action |
| :---: | :--- | :--- |
| `200 OK` | Request succeeded | Returns JSON or renders requested view template |
| `302 Found` | Redirection | Unauthenticated users redirected to `/login`; successful submissions redirect to `/dashboard` |
| `400 Bad Request` | Missing or invalid payload | Returns JSON error message or flashes form validation prompt |
| `403 Forbidden` | Access control violation | User attempting to access `/admin/dashboard` or `/counselor/dashboard` without role credentials |
| `404 Not Found` | Route does not exist | Renders standard error view |
| `500 Server Error` | Unhandled database or backend exception | Logs exception to stdout and falls back to safe defaults |

