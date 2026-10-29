# System Architecture Document — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. High-Level Architecture Overview

BhagvadMood Journal follows a decoupled, 3-tier Layered Architecture designed for local desktop execution with high privacy isolation:

```
+-------------------------------------------------------------+
|                 PRESENTATION LAYER (UI)                     |
|  - Tkinter / TTK GUI (Main.py / app.py)                     |
|  - Matplotlib Canvas Embedding (FigureCanvasTkAgg)          |
|  - Custom Dialogs & Modal Controllers                       |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|                   BUSINESS LOGIC LAYER                      |
|  - Sentiment Analysis Engine (TextBlob + Custom Heuristics) |
|  - Emotional Vector Classifier (wellness_ml.py)             |
|  - Vedic Wisdom Matching Engine (Corpus Dispatcher)         |
|  - Crisis Detection & Severity Filter (Rule Engine)         |
|  - Cognitive Reframing Generator                            |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|                     DATA ACCESS LAYER                       |
|  - Database Adapter (MySQL Connector / SQLite Fallback)     |
|  - Schema Initializer & Migration Utility (database_setup)  |
|  - Local JSON Model Weights (nlp_mood_weights.json)         |
|  - Static Vedic Shloka Corpus JSON                          |
+-------------------------------------------------------------+
```

---

## 2. Component Descriptions

### 2.1 Sentiment & NLP Processing Engine
- **Preprocessing:** Tokenization, lowercase normalization, stop-word filtering, and punctuation separation.
- **Negation Resolution:** Scans windows of 3 words preceding adjectives and verbs to flip polarities and dampen intensifiers.
- **Emotion Vectorization:** Projects text onto 6 orthogonal emotional dimensions: Stress, Hope, Anxiety, Contentment, Melancholy, and Clarity.

### 2.2 Vedic Scripture Mapper
- Implements an exact-and-fuzzy keyword correlation matrix linking identified cognitive distortions with Chapter and Verse numbers from the Bhagavad Gita.
- Extracts curated philosophical passages that focus on equanimity (*Samatvam*), detachment from outcome (*Nishkama Karma*), and mastery of the mind (*Atma Samyama*).

### 2.3 Persistence Engine
- Primary target: Local MySQL database running on `localhost:3306`.
- Auto-failover: If MySQL daemon is absent, dynamically switches to embedded SQLite (`bhagvadmood.db`) without crashing the application.
