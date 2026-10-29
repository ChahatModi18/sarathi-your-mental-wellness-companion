# Dataset Requirements & Guidelines

This document details the requirements and data specifications for the machine learning models utilized in the **Bhagvad Mood Journal** application. 

The application utilizes three neural network models for wellness recommendations and sentiment classification. If you wish to retrain these models on your own real-world data rather than the synthetic/boilerplate datasets, ensure your data conforms to the following guidelines.

---

## 1. Resource Recommendation Model Dataset

The Resource Recommendation Model predicts the level of care a user requires (one of 4 classes) based on demographic and mental wellness metrics.

### File Format
- **Preferred Format**: CSV (Comma Separated Values) or database extracts (MySQL tables).
- **Structure**: Each row represents a single user assessment snapshot.

### Feature Specifications (Inputs)

Your dataset must include the following 5 columns, normalized to a $[0.0, 1.0]$ range before training:

| Column Name | Description | Original Value Range | Normalization Formula | Input Representation |
| :--- | :--- | :--- | :--- | :--- |
| **Age** | User's age in years | $15$ to $100$ | $x / 100.0$ | Continuous value between $[0.15, 1.0]$ |
| **Gender** | Numerical mapping of user's gender | Categorical | Female $\rightarrow 0.0$, Male $\rightarrow 0.5$, Other $\rightarrow 1.0$ | Discrete float value |
| **PHQ-9** | Depression screening score | $0$ to $27$ | $x / 27.0$ | Continuous value between $[0.0, 1.0]$ |
| **GAD-7** | Anxiety screening score | $0$ to $21$ | $x / 21.0$ | Continuous value between $[0.0, 1.0]$ |
| **Sentiment** | Rolling journal entry mood polarity | $-1.0$ to $1.0$ | $(x + 1.0) / 2.0$ | Continuous value between $[0.0, 1.0]$ where $0.5$ is neutral |

### Target Label Specifications (Outputs)

The output must be structured as a **One-Hot Encoded Vector** of size $4$, corresponding to the recommendation classes:

| Class Index | Label | Meaning & Recommended Resources |
| :---: | :--- | :--- |
| `0` | Self-Care / Info Guides | Stable metrics. Recommend breathing exercises, stress management guides, etc. |
| `1` | Stress Videos | Slightly elevated stress (e.g. young adults). Recommend expert video guides. |
| `2` | Counselor Booking | Elevated anxiety/depression, low sentiment. Recommend booking a wellness counselor. |
| `3` | Crisis Support | Severe anxiety/depression or explicit crisis indicators. Recommend immediate helpline numbers. |

**Example Row (CSV)**:
```csv
age_norm,gender_norm,phq_norm,gad_norm,sentiment_norm,class_0,class_1,class_2,class_3
0.20,0.0,0.66,0.76,0.10,0.0,0.0,0.0,1.0
```

---

## 2. NLP Text Classification Datasets

The application employs two natural language processing models to classify raw journal entries:
1. **Crisis Detection Model** (Binary Classification)
2. **Mood Classification Model** (Multi-class Classification)

Both models extract feature vectors based on a custom vocabulary list of $75$ mood/crisis terms.

### File Format
- **Preferred Format**: Structured text lists, JSON structures, or tabular CSV files containing `(text, label)` pairs.

### Model 1: Crisis Detection (Binary)
- **Inputs**: Raw string inputs (representing sentences, paragraphs, or thoughts).
- **Labels**: 
  - `0`: Safe / Normal journal text (e.g., *"I am anxious about my exam tomorrow"*).
  - `1`: Crisis indicator requiring immediate intervention (e.g., *"I want to end my life"*, *"He is having a heart attack and cannot breathe"*).

**CSV Structure**:
```csv
text,label
"I want to kill myself",1
"I am feeling a bit sad today",0
```

### Model 2: Mood Classification (6 Classes)
- **Inputs**: Raw string inputs of student journal thoughts.
- **Labels**:
  - `0`: **Happy / Positive** (words like: happy, good, excited, content, peaceful, grateful)
  - `1`: **Sad** (words like: sad, depressed, cry, lonely, grieving, heartbroken)
  - `2`: **Anxious** (words like: anxious, worry, panic, scared, nervous, tense)
  - `3`: **Angry** (words like: angry, mad, hate, irritated, annoyed, rage)
  - `4`: **Neutral** (words like: fine, okay, normal, average, meh)
  - `5`: **Stressed / Overwhelmed** (words like: overwhelmed, exhausted, burned out)

**CSV Structure**:
```csv
text,label
"I am so excited and happy about my results",0
"I feel so overwhelmed with homework, I am completely exhausted",5
```

---

## 3. Best Practices for Preparing Training Data

1. **Class Balance**: 
   Ensure that each target class is represented relatively equally. For example, if you have 10,000 entries for class `0` but only 10 entries for class `3`, the model will struggle to recognize class `3` scenarios. Aim for at least $50\text{--}100$ examples per class.
2. **Text Cleanliness**:
   - Lowercase the text.
   - Do not remove words that carry strong emotion (like "not", "no", "hate").
   - Ensure spelling variations are minimized or represented in the vocabulary lists.
3. **Generalization**:
   Include negative/neutral examples for the NLP models. Ensure that simple keywords (like "life") do not trigger false positives for crisis detection unless accompanied by explicit crisis context (like "end my life").
