# API & Service Interface Specification — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Type:** Internal Python Service APIs & External Optional Connectors  

---

## 1. Internal Python Service APIs

### 1.1 `SentimentAnalyzer`
```python
class SentimentAnalyzer:
    def analyze_text(self, text: str) -> dict:
        """
        Performs NLP preprocessing, negation handling, and sentiment extraction.
        Returns:
            {
                "polarity": float,      # [-1.0 to 1.0]
                "subjectivity": float,  # [0.0 to 1.0]
                "primary_emotion": str, # e.g., 'Anxiety', 'Hope', 'Stress'
                "emotion_vector": dict  # breakdown of affective dimensions
            }
        """
        pass
```

### 1.2 `CrisisDetector`
```python
class CrisisDetector:
    def evaluate_risk(self, text: str, polarity: float) -> dict:
        """
        Evaluates risk factors and returns emergency intervention status.
        Returns:
            {
                "is_crisis": bool,
                "confidence": float,
                "triggered_keywords": list[str],
                "recommended_action": str
            }
        """
        pass
```

### 1.3 `VedicEngine`
```python
class VedicEngine:
    def get_philosophical_guidance(self, emotion: str, polarity: float) -> dict:
        """
        Queries local Vedic corpus and returns psychological reframing passage.
        Returns:
            {
                "chapter": int,
                "verse": int,
                "sanskrit": str,
                "transliteration": str,
                "translation": str,
                "reframe_prompt": str
            }
        """
        pass
```

---

## 2. Optional External Connectors (OpenAI Integration)

When configured with an optional API key in `.env`:
- **Endpoint:** `POST https://api.openai.com/v1/chat/completions`
- **Model:** `gpt-4o-mini` / `gpt-3.5-turbo`
- **System Prompt:** Provides empathetic, non-clinical supportive reflections grounded in cognitive behavioral coaching and mindful acceptance.
