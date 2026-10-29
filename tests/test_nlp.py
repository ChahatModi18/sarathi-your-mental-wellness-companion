"""
Test suite for Natural Language Processing (NLP), Context Tagger,
Affect Inversion, and Crisis Detection algorithms.
Supports 30 discrete emotional moods and 15 distinct contextual life domains.
"""

import pytest
import re
from Main import detect_text_context, CRISIS_KEYWORDS, _matches_any, mood_keywords
from cognitive_reframer import analyze_text_affect, extract_nuanced_mood

def test_detect_text_context_academic():
    text = "I have an upcoming exam and semester deadline that is stressing me out."
    context = detect_text_context(text)
    assert context == "Academic Stress"

def test_detect_text_context_career():
    text = "My boss gave me a huge workload at the office and I feel burnout."
    context = detect_text_context(text)
    assert context == "Career / Work"

def test_detect_text_context_relationships():
    text = "I had a terrible argument with my friend and partner today."
    context = detect_text_context(text)
    assert context == "Relationships"

def test_detect_text_context_default():
    text = "Just sitting on the balcony watching the sky."
    context = detect_text_context(text)
    assert context == "General Wellbeing"

def test_detect_text_context_social_anxiety():
    text = "I feel lonely and isolated, and social anxiety makes parties awkward."
    context = detect_text_context(text)
    assert context == "Social Anxiety & Loneliness"

def test_detect_text_context_burnout():
    text = "I am exhausted and drained from non-stop overwork."
    context = detect_text_context(text)
    assert context == "Burnout & Overwork"

def test_crisis_keyword_detection_true():
    distress_text = "I cannot take it anymore and want to kill myself."
    assert _matches_any(CRISIS_KEYWORDS, distress_text) is True

def test_crisis_keyword_detection_physical():
    chest_pain_text = "I have severe chest pain and can't breathe."
    assert _matches_any(CRISIS_KEYWORDS, chest_pain_text) is True

def test_crisis_keyword_detection_false():
    calm_text = "Today was a productive study session with no worries."
    assert _matches_any(CRISIS_KEYWORDS, calm_text) is False

def test_mood_keywords_coverage_30_moods():
    # Verify core and extended taxonomy
    expected_moods = [
        "positive", "very_happy", "negative", "pessimistic", "optimistic",
        "neutral", "overwhelmed", "anxious", "peaceful", "restless",
        "very_sad", "sad", "discouraged", "devastated", "ecstatic",
        "content", "angry", "happy", "grateful", "hopeful",
        "lonely", "burned_out", "guilty", "insecure", "confused",
        "envious", "grief_stricken", "serene", "inspired", "resilient"
    ]
    for m in expected_moods:
        assert m in mood_keywords, f"Mood {m} missing from mood_keywords"
        assert len(mood_keywords[m]) > 0, f"Mood {m} has no keywords"

def test_compound_negation_inversion():
    not_bad = analyze_text_affect("Today was not bad at all.")
    assert not_bad["polarity"] > 0, "not bad should be converted to positive polarity"

    not_happy = analyze_text_affect("I am not happy with how things turned out.")
    assert not_happy["polarity"] < 0, "not happy should be converted to negative polarity"

def test_extract_nuanced_mood():
    assert extract_nuanced_mood("I feel completely burned out and drained") == "burned_out"
    assert extract_nuanced_mood("I am standing strong and persevering") == "resilient"
