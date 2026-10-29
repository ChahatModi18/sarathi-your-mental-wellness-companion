# Product Requirements Document (PRD) — BhagvadMood Journal (Sarathi)

> **Document Version:** 2.0.0  
> **Product Name:** BhagvadMood Journal / Sarathi Mental Wellness Platform  
> **Author & Lead Developer:** Chahat Modi  
> **Academic Scope:** Minor Project / Mental Health Monitoring & Action (MHMA) Framework  
> **Deployment Target:** Cross-platform Desktop (Tkinter) & Web Platform (Flask / Docker)

---

## 1. Executive Summary & Product Vision

**BhagvadMood Journal** is a privacy-first, dual-client (Desktop GUI and Responsive Web) mental wellness and reflective journaling ecosystem. It integrates clinical cognitive-behavioral diagnostic methodologies (PHQ-9, GAD-7) with evidence-backed cognitive reframing and ancient Vedic wisdom from the *Bhagavad Gita* to foster psychological resilience (*Sthitaprajna* and emotional equanimity).

Unlike conventional commercial mental health applications that compromise privacy by transmitting vulnerable reflections to cloud servers, BhagvadMood Journal provides **100% data sovereignty**, local relational persistence (MySQL 8), context-aware Natural Language Processing (NLP), dual-engine neural networks (PyTorch with portable NumPy fallback), and automated crisis intervention with zero external telemetry required.

```mermaid
graph TD
    User([User / Patient]) --> ClientChoice{Interface Selection}
    ClientChoice -->|Desktop Tkinter| DesktopApp[Main.py GUI - 27 Frames]
    ClientChoice -->|Web Browser| WebApp[Flask Web App - HTML5/CSS3]
    DesktopApp --> LogicEngine[NLP Sentiment & Context Engine]
    WebApp --> LogicEngine
    LogicEngine --> DBNN{Neural Engine}
    DBNN -->|PyTorch if Available| TorchModel[PyTorch Deep Neural Nets]
    DBNN -->|Fallback Mode| NumpyModel[NumPy He-Initialized Sequential Networks]
    LogicEngine --> RelationalDB[(MySQL 8 Database: sarathi_sih_db)]
    LogicEngine --> VedicWisdom[Bhagavad Gita Knowledge Base]
    LogicEngine --> CrisisGuard[Crisis Detection & Tele-MANAS/KIRAN Intervention]
```

---

## 2. Problem Statement & Research Foundation

Clinical studies indicate four foundational deficits in existing digital mental health tools:

1. **Superficial Sentiment Misclassification:** Standard lexicon models (e.g., standard VADER) fail on complex clinical affect, double negations, and nuanced expressions (*"I am not entirely miserable today"*).
2. **Absence of Actionable Cognitive Reframing:** Conventional journaling apps merely store passive text without helping users identify and untangle cognitive distortions (catastrophizing, emotional reasoning).
3. **Data Exploitation & Privacy Risks:** Commercial SaaS wellness tools aggregate intimate behavioral patterns for advertising and commercial profiling.
4. **Cultural & Philosophical Disconnect:** Modern digital therapeutics almost exclusively employ Western cognitive models, ignoring the profound psychological equanimity principles formulated in Indian Vedic psychology.

---

## 3. User Personas

| Persona | Demographics | Core Needs & Frustrations | BhagvadMood Feature Mappings |
| :--- | :--- | :--- | :--- |
| **Aarav S.** | University Student (Age 20) | Academic burnout, exam anxiety, fear of failure, financial constraints | Student Persona login, PHQ-9 & GAD-7 tracking, Gita Shlokas on duty vs. outcome (*Nishkama Karma*), anonymous peer forum. |
| **Meera K.** | Tech Professional (Age 29) | Imposter syndrome, chronic workplace stress, severe privacy concerns | Professional Persona login, 100% offline local storage, visual mood trajectory charts, time-boxed mini-goals. |
| **Dr. R. Verma** | Clinical Counselor | Managing client appointments, reviewing longitudinal mood trends | Counselor Dashboard, slot scheduling, booking approval workflow, risk tier categorization. |
| **System Admin** | Institutional Evaluator | System security, audit logging, aggregate user statistics | Admin Dashboard, user management, counselor credentialing, audit trail. |

---

## 4. Key Functional Requirements (FR)

### FR-1: Multimodal User Management & Role-Based Access
- **FR-1.1:** Support separate user personas: Student, Professional, Non-Professional, Counselor, and Administrator.
- **FR-1.2:** Secure authentication using SHA-256 with user-specific salting and server pepper.
- **FR-1.3:** Password recovery workflow via email verification codes.

### FR-2: Reflective Journaling & Emotion Analysis
- **FR-2.1:** Freeform journal composition with real-time text analysis.
- **FR-2.2:** Multi-dimensional sentiment scoring: Polarity ($-1.0$ to $+1.0$), Subjectivity ($0.0$ to $1.0$), and Discrete Mood Classification (20 granular emotional states).
- **FR-2.3:** Automatic situational context categorization: Academic Stress, Career/Work, Relationships, Health & Body, Financial Pressure, Self-Esteem, Loss & Grief, General Wellbeing.
- **FR-2.4:** Contextual Sanskrit Shloka pairing from the *Bhagavad Gita* with authentic English translations and philosophical guidance.

### FR-3: Machine Learning & Crisis Intervention
- **FR-3.1:** High-priority regex and neural crisis screening detecting suicide ideation, self-harm, and severe medical emergencies.
- **FR-3.2:** Immediate, unclosable alert modal with verified national helplines: Tele-MANAS (`14416`), KIRAN (`1800-599-0019`), and Emergency (`112`).
- **FR-3.3:** Personalized resource recommendation model taking age, gender, PHQ-9 score, GAD-7 score, and polarity to classify optimal intervention levels (Self-Care, Community Support, Professional Therapy, Crisis Intervention).

### FR-4: Clinical Psychometric Screenings
- **FR-4.1:** Standard 9-question PHQ-9 Depression assessment with automatic scoring ($0-27$) and clinical severity tiering.
- **FR-4.2:** Standard 7-question GAD-7 Anxiety assessment with automatic scoring ($0-21$) and clinical severity tiering.
- **FR-4.3:** Longitudinal historical trend storage linked to the user's relational profile.

### FR-5: Counselor Booking & Session Scheduling
- **FR-5.1:** Counselor slot creation and availability management.
- **FR-5.2:** User booking interface with specialization filtering and reason submission.
- **FR-5.3:** Automated SMTP confirmation notifications.

### FR-6: Community & Holistic Wellness
- **FR-6.1:** Moderated anonymous peer support forum with keyword sentiment filtering.
- **FR-6.2:** Menstrual cycle logging and hormone-correlated mood tracking.
- **FR-6.3:** Interactive Spin-the-Wheel for daily positive affirmations and cognitive shifts.
- **FR-6.4:** To-Do and action task manager rewarding Mindful Points (MP) upon completion.
- **FR-6.5:** In-app Bhagavad Gita tri-lingual PDF reader (Sanskrit, Hindi, English).

---

## 5. Non-Functional Requirements (NFR)

- **NFR-1 (Privacy & Sovereignty):** All user journal entries, credentials, and screening histories must remain stored locally on MySQL; no unencrypted telemetry or cloud offloading.
- **NFR-2 (Resilience & Portability):** The application must function fully even if PyTorch, CUDA, or specialized C-compilers are unavailable, seamlessly utilizing NumPy neural networks and offline JSON weights.
- **NFR-3 (Performance):** Sentiment analysis, context detection, and neural inference must complete in under 150ms per entry on standard consumer hardware.
- **NFR-4 (Security):** All passwords must be hashed before persistence; SQL queries must use parameterized prepared statements to eliminate SQL injection vulnerabilities.

