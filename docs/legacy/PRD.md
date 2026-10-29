# Product Requirements Document (PRD) — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Target Product:** BhagvadMood Journal — AI-Powered Mental Wellness & Reflective Journaling Platform  
> **Author & Lead Developer:** Chahat Modi  
> **Target Audience:** Individuals seeking private mental wellness tracking, clinical psychology researchers, academic evaluators  

---

## 1. Executive Summary & Vision

**BhagvadMood Journal** is a privacy-first, offline-capable desktop mental wellness platform engineered to bridge critical diagnostic and sentiment classification gaps identified across 5+ clinical psychology studies. Unlike commercial cloud-based wellness applications that upload intimate thoughts to remote servers and rely on superficial social-media-trained sentiment classifiers, BhagvadMood Journal operates with zero external telemetry, local relational data persistence (MySQL/SQLite), context-aware Natural Language Processing (NLP), evidence-backed cognitive reframing, and time-tested philosophical guidance derived from Vedic wisdom.

---

## 2. Problem Statement & Research Motivation

### 2.1 The Clinical Gap
1. **Misclassification of Nuanced Affect:** Standard sentiment algorithms (e.g., standard VADER or naive polarity models) misclassify complex clinical emotional text. For instance, statements such as *"I am not feeling terribly unhappy today"* or *"Everything seems quiet, almost too quiet"* are routinely misclassified.
2. **Privacy Vulnerability & Data Sovereignty:** Mental health reflections are among the most sensitive personal data. Commercial SaaS wellness apps introduce data leak liabilities, commercial profiling, and third-party tracking.
3. **Absence of Actionable Cognitive Reframing:** Basic journaling apps merely record text without assisting users in untangling cognitive distortions (e.g., catastrophizing, black-and-white thinking, emotional reasoning).
4. **Disconnection from Cultural & Philosophical Grounding:** Most modern digital therapeutics adopt strictly Western therapeutic frameworks, ignoring the profound psychological resilience principles documented in ancient Indian philosophical literature (Bhagavad Gita's concepts of *Sthitaprajna*, *Karma Yoga*, and emotional equanimity).

---

## 3. User Personas

| Persona | Role / Context | Primary Struggle | BhagvadMood Solution |
| :--- | :--- | :--- | :--- |
| **Aarav S.** | University Student (21) | Academic burnout, acute exam anxiety, fear of failure | Daily journaling with automatic stress vector scoring and Gita-aligned perspective shifts on duty vs. outcome. |
| **Meera K.** | Tech Professional (28) | Privacy-conscious, imposter syndrome, chronic stress | 100% offline journaling; local MySQL storage; zero cloud leaks; visual mood trajectory over 30 days. |
| **Dr. R. Verma** | Clinical Psychology Researcher | Needs objective sentiment scoring and structured sentiment metrics | Quantitative NLP feature extraction, negation handling, and reproducible affective intensity indices. |

---

## 4. Key Functional Requirements

### 4.1 Journaling & Natural Language Preprocessing
- **FR-1.1:** Real-time text entry with automated lexical analysis on demand.
- **FR-1.2:** Context-aware sentiment scoring computing Polarity ([-1.0, +1.0]) and Subjectivity ([0.0, 1.0]).
- **FR-1.3:** Custom negation-handling heuristics ensuring negation words ("not", "never", "barely") invert and scale affective polarities correctly.
- **FR-1.4:** Affective multi-dimensional vector computation (Stress, Hope, Anxiety, Contentment, Melancholy, Neutral).

### 4.2 Vedic Wisdom & Cognitive Reframing Engine
- **FR-2.1:** Semantic mapping between diagnosed emotional states and corresponding Sanskrit Shlokas from the Bhagavad Gita with English translations and psychological commentaries.
- **FR-2.2:** Cognitive Reframing Prompts encouraging self-inquiry (e.g., distinguishing what is within one's control vs. what is external).
- **FR-2.3:** Optional local or API-assisted generative synthesis providing empathetic, non-judgmental guidance.

### 4.3 Crisis Detection & Harm Prevention
- **FR-3.1:** Rule-based and keyword-weighted high-priority crisis detection algorithm scanning for suicide ideation, self-harm, and acute helplessness triggers.
- **FR-3.2:** Immediate emergency intervention modal providing national helpline directories (Tele-MANAS: 14416, KIRAN: 1800-599-0019) with zero judgment.

### 4.4 Analytics & Mood Trajectory Visualization
- **FR-4.1:** Interactive historical chart generation using Matplotlib embedded in Tkinter.
- **FR-4.2:** Rolling 7-day and 30-day sentiment averages, emotion distribution pie charts, and streak tracker.

---

## 5. Non-Functional Requirements

- **NFR-1 (Privacy & Security):** Zero unconsented network calls; database encrypted at rest or password-protected.
- **NFR-2 (Performance):** Sentiment analysis execution time < 150ms for entries up to 2,000 words.
- **NFR-3 (Portability):** Runs smoothly across Windows 10/11, macOS, and Linux with Python 3.10+.
- **NFR-4 (Reliability):** Automatic local backup and graceful fallback to SQLite if MySQL service is unavailable.
