# UI/UX & System Design Document — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Design Philosophy & Aesthetic Strategy

BhagvadMood Journal adheres to a **Mindful Serenity** design paradigm. The graphical user interface is constructed using Python's native `tkinter` and `tkinter.ttk` themed widgets, augmented with custom PIL image renderings, calming palettes, and clear visual hierarchy.

### 1.1 Color Palette
- **Primary Deep Slate:** `#1E293B` — Used for main navigation, window chrome, and structural headers.
- **Vedic Saffron Accent:** `#D97706` / `#F59E0B` — Represents illumination, wisdom, and cognitive clarity.
- **Soothing Sage Green:** `#059669` / `#10B981` — Positive sentiment, resilience, and recovery indicators.
- **Reflective Lavender:** `#6366F1` — Introspective prompts and philosophical wisdom cards.
- **Alert Coral:** `#EF4444` — Crisis warning and urgent helpline triggers.
- **Background Soft Cream / Off-White:** `#F8FAFC` (Light) / `#0F172A` (Dark).

---

## 2. Information Architecture & Screen Flow

```
[Main Application Window]
  ├── [1. Journal Entry Workspace]
  │     ├── Rich Text Area (Entry Title, Mood Tag, Text Box)
  │     ├── Real-time Word Counter & Reading Time
  │     └── Action Bar: [Analyze Entry] [Save Entry] [Clear]
  │
  ├── [2. Sentiment & Reframing Output Panel]
  │     ├── Polarity Gauge & Subjectivity Gauge
  │     ├── Identified Emotional Dimension Badges
  │     └── Vedic Wisdom Card (Sanskrit Shloka + English Reframe)
  │
  ├── [3. Emotional Analytics Dashboard]
  │     ├── Matplotlib Mood Trend Line (7-Day / 30-Day)
  │     ├── Emotional Distribution Radar/Bar Chart
  │     └── Daily Consistency Calendar
  │
  ├── [4. Vedic Corpus Explorer]
  │     ├── Search by Emotion (Anxiety, Anger, Grief, Indecision)
  │     └── Shloka Reader with Sanskrit Text, Transliteration & Meaning
  │
  └── [5. Crisis Intervention Modal (Trigger-Activated)]
        ├── Empathetic Acknowledgment Banner
        └── Direct Helpline Numbers (Tele-MANAS, Vandrevala, KIRAN)
```

---

## 3. Component Design & Interactions

1. **Card Containers:** Custom canvas-drawn rounded frames with subtle borders to prevent visual fatigue.
2. **Typography Hierarchy:** Clean modern sans-serif typography (`Segoe UI` / `Helvetica Neue` / `Inter`).
3. **Status Feedback:** Non-intrusive bottom status bar providing instant confirmation for save and export operations.
