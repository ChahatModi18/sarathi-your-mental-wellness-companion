"""
Test suite for wellness_ml machine learning engine.
Verifies NumPy sequential neural networks, PyTorch fallbacks,
mood prediction, crisis detection, and resource recommendations.
"""

import pytest
import numpy as np
import wellness_ml

def test_generate_synthetic_data():
    X, y = wellness_ml.generate_synthetic_data(num_samples=50)
    assert X.shape == (50, 5)
    assert y.shape == (50, 4)
    assert np.all((X >= 0.0) & (X <= 1.0))
    # Each row in y should be one-hot encoded
    assert np.allclose(np.sum(y, axis=1), 1.0)

def test_train_or_load_model():
    status = wellness_ml.train_or_load_model()
    assert status in ["PyTorch Model (Trained)", "PyTorch Model (Loaded)", "NumPy Sequential (Trained)", "NumPy Sequential (Loaded)"]
    assert wellness_ml.model is not None

def test_recommend_resource_output_shape():
    wellness_ml.train_or_load_model()
    class_idx, probs = wellness_ml.recommend_resource(
        age=22,
        gender_str="Female",
        phq_score=14,
        gad_score=12,
        mood_polarity=-0.5
    )
    assert isinstance(class_idx, int)
    assert 0 <= class_idx < 4
    assert len(probs) == 4
    assert np.isclose(sum(probs), 1.0, atol=1e-2)

def test_text_to_vector():
    vec = wellness_ml.text_to_vector("I am feeling very happy and good today")
    assert len(vec) == len(wellness_ml.VOCABULARY)
    assert any(v > 0 for v in vec)

def test_predict_mood():
    wellness_ml.train_or_load_nlp_models()
    mood, probs = wellness_ml.predict_mood("Everything is peaceful and happy")
    assert isinstance(mood, str)
    assert mood in ["happy", "sad", "anxious", "angry", "neutral", "overwhelmed"]
    assert len(probs) == 6

def test_predict_crisis():
    wellness_ml.train_or_load_nlp_models()
    is_crisis, prob = wellness_ml.predict_crisis("I want to end my life, kill myself")
    assert isinstance(is_crisis, bool)
    assert 0.0 <= prob <= 1.0
    assert is_crisis is True
    assert prob >= 0.5

