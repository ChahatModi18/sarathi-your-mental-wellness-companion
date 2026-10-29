"""
Test suite for PHQ-9 (Depression) and GAD-7 (Anxiety) Psychometric Screenings.
"""

import pytest
from Main import PHQ9_QUESTIONS, GAD7_QUESTIONS, PHQ9_SCORES, GAD7_SCORES

def test_phq9_questions_count():
    assert len(PHQ9_QUESTIONS) == 9

def test_gad7_questions_count():
    assert len(GAD7_QUESTIONS) == 7

def test_phq9_score_mapping():
    # Helper to resolve score
    def get_phq_risk(score):
        for (low, high), risk in PHQ9_SCORES.items():
            if low <= score <= high:
                return risk
        return "Unknown"

    assert "Minimal Depression" in get_phq_risk(3)
    assert "Mild Depression" in get_phq_risk(7)
    assert "Moderate Depression" in get_phq_risk(12)
    assert "Moderately Severe" in get_phq_risk(17)
    assert "Severe Depression" in get_phq_risk(24)

def test_gad7_score_mapping():
    def get_gad_risk(score):
        for (low, high), risk in GAD7_SCORES.items():
            if low <= score <= high:
                return risk
        return "Unknown"

    assert "Minimal Anxiety" in get_gad_risk(2)
    assert "Mild Anxiety" in get_gad_risk(7)
    assert "Moderate Anxiety" in get_gad_risk(11)
    assert "Severe Anxiety" in get_gad_risk(18)

