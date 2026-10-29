import os
import sys
# Inject the virtual environment's site packages path only if using a compatible Python 3.14 interpreter
venv_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib", "site-packages")
if sys.version_info[:2] == (3, 14) and os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)
import numpy as np

def run_diagnostics():
    print("=" * 60)
    print("RUNNING MACHINE LEARNING MODEL DIAGNOSTICS")
    print("=" * 60)
    
    # Check if wellness_ml can be imported
    try:
        import wellness_ml
        print("[SUCCESS] wellness_ml successfully imported.")
    except Exception as e:
        print(f"[ERROR] Failed to import wellness_ml: {e}")
        return

    # Check weights files
    weights_files = [
        "wellness_model_weights.json",
        "nlp_crisis_weights.json",
        "nlp_mood_weights.json"
    ]
    
    print("\n--- Checking Local Weight Files ---")
    for wf in weights_files:
        path = os.path.join(os.path.dirname(wellness_ml.__file__), wf)
        exists = os.path.exists(path)
        status = "EXISTS" if exists else "NOT FOUND (Will be auto-generated during training)"
        print(f"File: {wf:<30} | Status: {status}")

    # Test initialization/training loading
    print("\n--- Testing Model Initialization / Training ---")
    try:
        model_type = wellness_ml.train_or_load_model()
        print(f"[SUCCESS] Resource Recommendation Model loaded: {model_type}")
    except Exception as e:
        print(f"[ERROR] Failed to train or load Resource Recommendation model: {e}")

    try:
        nlp_status = wellness_ml.train_or_load_nlp_models()
        print(f"[SUCCESS] NLP Models loaded/trained: {nlp_status}")
    except Exception as e:
        print(f"[ERROR] Failed to train or load NLP models: {e}")

    # Test Resource Recommendation
    print("\n--- Testing Resource Recommendations ---")
    test_cases_recommend = [
        {"age": 20, "gender": "female", "phq": 18, "gad": 16, "pol": -0.8, "desc": "Severe depression & anxiety"},
        {"age": 45, "gender": "male", "phq": 3, "gad": 2, "pol": 0.5, "desc": "Minimal symptoms, positive mood"},
        {"age": 22, "gender": "female", "phq": 11, "gad": 8, "pol": -0.4, "desc": "Moderate symptoms, young adult"},
    ]

    for i, tc in enumerate(test_cases_recommend):
        try:
            class_idx, probs = wellness_ml.recommend_resource(
                tc["age"], tc["gender"], tc["phq"], tc["gad"], tc["pol"]
            )
            print(f"Case {i+1} ({tc['desc']}):")
            print(f"  Input: Age={tc['age']}, Gender={tc['gender']}, PHQ={tc['phq']}, GAD={tc['gad']}, Polarity={tc['pol']}")
            print(f"  Output: Recommend Class={class_idx} | Probabilities={np.round(probs, 4)}")
        except Exception as e:
            print(f"  [ERROR] Failed to run recommend_resource for case {i+1}: {e}")

    # Test Crisis Detection
    print("\n--- Testing NLP Crisis Detection ---")
    test_cases_crisis = [
        "I want to end my life right now.",
        "I am thinking of suicide today.",
        "Just having a regular day at work, doing fine.",
        "I am anxious about my exam tomorrow."
    ]

    for i, text in enumerate(test_cases_crisis):
        try:
            is_crisis, prob = wellness_ml.predict_crisis(text)
            status = "CRISIS ALERT" if is_crisis else "SAFE/NORMAL"
            print(f"Text {i+1}: \"{text}\"")
            print(f"  Output: {status} (Crisis probability: {prob:.4f})")
        except Exception as e:
            print(f"  [ERROR] Failed to run predict_crisis for text {i+1}: {e}")

    # Test Mood Classification
    print("\n--- Testing NLP Mood Classification ---")
    test_cases_mood = [
        "I am so happy and excited about this new project!",
        "Feeling down, lonely and want to cry.",
        "Everything makes me angry and furious.",
        "This is so overwhelming, I am completely stressed and burned out.",
        "I feel fine, just an average day."
    ]

    for i, text in enumerate(test_cases_mood):
        try:
            mood, probs = wellness_ml.predict_mood(text)
            print(f"Text {i+1}: \"{text}\"")
            print(f"  Output: Mood='{mood}' | Probs={np.round(probs, 4)}")
        except Exception as e:
            print(f"  [ERROR] Failed to run predict_mood for text {i+1}: {e}")

    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_diagnostics()
