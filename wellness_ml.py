import os
import numpy as np
import json

USE_REAL_KERAS = False
model = None

# Custom NumPy fallback sequential model for Resource Recommendations
class NumPySequential:
    def __init__(self):
        # 5 inputs -> 8 hidden -> 4 outputs
        # Using He initialization
        self.W1 = np.random.randn(5, 8) * np.sqrt(2.0 / 5)
        self.b1 = np.zeros((1, 8))
        self.W2 = np.random.randn(8, 4) * np.sqrt(2.0 / 8)
        self.b2 = np.zeros((1, 4))
        
    def relu(self, x):
        return np.maximum(0, x)
        
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        
    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
        
    def fit(self, X, y, epochs=100, lr=0.1):
        N = X.shape[0]
        for epoch in range(epochs):
            a2 = self.forward(X)
            dz2 = (a2 - y) / N
            dW2 = self.a1.T @ dz2
            db2 = np.sum(dz2, axis=0, keepdims=True)
            
            da1 = dz2 @ self.W2.T
            dz1 = da1 * (self.z1 > 0)
            dW1 = X.T @ dz1
            db1 = np.sum(dz1, axis=0, keepdims=True)
            
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2
            
    def save(self, filepath):
        data = {
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist()
        }
        with open(filepath, "w") as f:
            json.dump(data, f)
            
    def load(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
            self.W1 = np.array(data["W1"])
            self.b1 = np.array(data["b1"])
            self.W2 = np.array(data["W2"])
            self.b2 = np.array(data["b2"])
            return True
        return False

def _import_keras_if_available():
    global USE_REAL_KERAS
    try:
        import keras
        return keras
    except Exception:
        try:
            from tensorflow import keras
            return keras
        except Exception:
            return None

keras = _import_keras_if_available()
if keras is not None:
    try:
        model_test = keras.Sequential([
            keras.layers.Input(shape=(5,)),
            keras.layers.Dense(8, activation="relu"),
            keras.layers.Dense(4, activation="softmax")
        ])
        USE_REAL_KERAS = True
    except Exception as e:
        print(f"[ML INFO] Keras initialization deferred or failed: {e}. Falling back to NumPy Sequential model.")
        USE_REAL_KERAS = False
else:
    print("[ML INFO] Keras import not available. Falling back to NumPy Sequential model.")
    USE_REAL_KERAS = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), "wellness_model.keras")
WEIGHTS_PATH_JSON = os.path.join(os.path.dirname(__file__), "wellness_model_weights.json")

def generate_synthetic_data(num_samples=400):
    X = []
    y = []
    np.random.seed(42)
    for _ in range(num_samples):
        age = np.random.randint(15, 80)
        gender_val = np.random.choice([0.0, 0.5, 1.0])
        phq = np.random.randint(0, 28)
        gad = np.random.randint(0, 22)
        polarity = np.random.uniform(-1.0, 1.0)
        
        age_norm = age / 100.0
        phq_norm = phq / 27.0
        gad_norm = gad / 21.0
        pol_norm = (polarity + 1.0) / 2.0
        
        if phq >= 15 or gad >= 15 or (phq >= 10 and polarity < -0.6):
            label = 3
        elif polarity < -0.3 and gad >= 8:
            label = 2
        elif age <= 25 and gad >= 7:
            label = 1
        else:
            label = 0
            
        X.append([age_norm, gender_val, phq_norm, gad_norm, pol_norm])
        one_hot = [0.0] * 4
        one_hot[label] = 1.0
        y.append(one_hot)
        
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

def train_or_load_model():
    global model, USE_REAL_KERAS
    X_train, y_train = generate_synthetic_data()
    
    if USE_REAL_KERAS:
        try:
            model = keras.Sequential([
                keras.layers.Input(shape=(5,)),
                keras.layers.Dense(8, activation="relu"),
                keras.layers.Dense(4, activation="softmax")
            ])
            model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
            if os.path.exists(MODEL_PATH):
                model.load_weights(MODEL_PATH)
            else:
                model.fit(X_train, y_train, epochs=25, batch_size=16, verbose=0)
                model.save_weights(MODEL_PATH)
            return "Keras Sequential"
        except Exception as e:
            print(f"[ML WARNING] Failed to train with Keras: {e}. Falling back to NumPySequential.")
            USE_REAL_KERAS = False
            
    model = NumPySequential()
    if os.path.exists(WEIGHTS_PATH_JSON):
        loaded = model.load(WEIGHTS_PATH_JSON)
        if loaded:
            return "NumPy Sequential (Loaded)"
            
    model.fit(X_train, y_train, epochs=150, lr=0.1)
    model.save(WEIGHTS_PATH_JSON)
    return "NumPy Sequential (Trained)"

def recommend_resource(age, gender_str, phq_score, gad_score, mood_polarity):
    global model
    if model is None:
        train_or_load_model()
        
    age_norm = float(age) / 100.0
    g_map = {"female": 0.0, "male": 0.5}
    gender_val = g_map.get(gender_str.lower(), 1.0)
    phq_norm = float(phq_score) / 27.0
    gad_norm = float(gad_score) / 21.0
    pol_norm = (float(mood_polarity) + 1.0) / 2.0
    
    X_input = np.array([[age_norm, gender_val, phq_norm, gad_norm, pol_norm]], dtype=np.float32)
    
    if USE_REAL_KERAS:
        try:
            preds = model.predict(X_input, verbose=0)
            class_idx = int(np.argmax(preds[0]))
            return class_idx, preds[0].tolist()
        except Exception as e:
            pass
            
    preds = model.forward(X_input)
    class_idx = int(np.argmax(preds[0]))
    return class_idx, preds[0].tolist()


# ==============================================================================
# --- NEW: NLP TEXT CLASSIFIER FOR CRISIS DETECTION AND MOOD CLASSIFICATION ---
# ==============================================================================

VOCABULARY = [
    # Crisis indicators
    "suicide", "suicidal", "kill", "die", "death", "overdose", "harm", "cut", "bleed",
    "stroke", "choke", "accident", "chest", "breathe", "emergency", "poison", "heart attack",
    "end my life", "ending it", "cannot go on", "myself", "life",
    # Anxious
    "anxious", "worry", "panic", "scared", "fear", "nervous", "tense", "stress", "restless",
    # Sad
    "sad", "depressed", "cry", "lonely", "hopeless", "useless", "worthless", "hurt", "grief",
    "devastated", "heartbroken",
    # Angry
    "angry", "mad", "furious", "hate", "irritate", "annoy", "frustrate", "rage",
    # Happy/Positive
    "happy", "good", "great", "glad", "awesome", "excited", "content", "peaceful", "grateful", "hopeful",
    # Neutral
    "fine", "okay", "neutral", "normal", "average", "meh",
    # Stressed/Overwhelmed
    "overwhelmed", "exhausted", "burned out", "burn out"
]

def text_to_vector(text):
    text_lower = text.lower()
    vector = np.zeros(len(VOCABULARY), dtype=np.float32)
    for idx, word in enumerate(VOCABULARY):
        if word in text_lower:
            vector[idx] = 1.0
    return vector

class TextNeuralNetwork:
    def __init__(self, input_dim, output_dim):
        # Neural Net with input_dim inputs -> 12 hidden nodes -> output_dim outputs
        self.W1 = np.random.randn(input_dim, 12) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros((1, 12))
        self.W2 = np.random.randn(12, output_dim) * np.sqrt(2.0 / 12)
        self.b2 = np.zeros((1, output_dim))
        
    def relu(self, x):
        return np.maximum(0, x)
        
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        
    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
        
    def fit(self, X, y, epochs=200, lr=0.1):
        N = X.shape[0]
        for epoch in range(epochs):
            a2 = self.forward(X)
            dz2 = (a2 - y) / N
            dW2 = self.a1.T @ dz2
            db2 = np.sum(dz2, axis=0, keepdims=True)
            da1 = dz2 @ self.W2.T
            dz1 = da1 * (self.z1 > 0)
            dW1 = X.T @ dz1
            db1 = np.sum(dz1, axis=0, keepdims=True)
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2

    def save(self, filepath):
        data = {
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist()
        }
        with open(filepath, "w") as f:
            json.dump(data, f)
            
    def load(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                W1 = np.array(data["W1"])
                b1 = np.array(data["b1"])
                W2 = np.array(data["W2"])
                b2 = np.array(data["b2"])
                if W1.shape == self.W1.shape and W2.shape == self.W2.shape:
                    self.W1 = W1
                    self.b1 = b1
                    self.W2 = W2
                    self.b2 = b2
                    return True
            except Exception:
                pass
        return False

CRISIS_TRAINING_PAIRS = [
    # Crisis (1)
    ("I want to end my life", 1),
    ("I am thinking of suicide", 1),
    ("I want to kill myself", 1),
    ("I will overdose on pills", 1),
    ("I want to die today", 1),
    ("I cannot go on anymore, ending it", 1),
    ("He is having a sudden stroke and collapsed", 1),
    ("She has severe chest pain and cannot breathe", 1),
    ("There is uncontrollable bleeding from the cut", 1),
    ("Having a heart attack, call an ambulance", 1),
    ("I am choking on something", 1),
    ("Had a major car accident, bleeding", 1),
    
    # Non-Crisis (0)
    ("I am feeling a bit sad today", 0),
    ("I am anxious about my upcoming exam tomorrow", 0),
    ("It was a normal, okay day", 0),
    ("I am so angry at my brother", 0),
    ("We had a great time walking in the park", 0),
    ("I am happy and content", 0),
    ("Feeling stressed out by homework", 0),
    ("Nothing special happened today, just fine", 0),
    
    # All-zero/Unknown inputs should map to safe (0)
    ("", 0),
    ("I am walking", 0),
    ("The sky is blue", 0),
    ("Hello how are you", 0)
]

MOOD_TRAINING_PAIRS = [
    # 0: Happy/Positive
    ("I am very happy and joyful", 0),
    ("It is a great day, I feel content", 0),
    ("I am peaceful, calm and relaxed", 0),
    ("I feel grateful and blessed", 0),
    ("Feeling hopeful about the future", 0),
    ("Awesome news, I am so excited", 0),
    
    # 1: Sad
    ("I am feeling very sad and down", 1),
    ("I feel depressed and lonely", 1),
    ("I want to cry, everything is empty", 1),
    ("I am devastated and heartbroken", 1),
    ("I feel worthless and useless", 1),
    
    # 2: Anxious
    ("I am feeling extremely anxious and nervous", 2),
    ("I am scared and worried about the outcome", 2),
    ("My panic is rising, I feel tense", 2),
    ("I am restless and jittery today", 2),
    
    # 3: Angry
    ("I am so angry and mad", 3),
    ("I hate this situation, feeling furious", 3),
    ("I am irritated and annoyed by them", 3),
    ("This makes me rage, so frustrated", 3),
    
    # 4: Neutral
    ("I feel okay and fine", 4),
    ("Just a normal day, average", 4),
    ("meh, nothing special", 4),
    
    # All-zero/Unknown inputs should map to neutral (4)
    ("", 4),
    ("I am walking", 4),
    ("The sky is blue", 4),
    ("Hello how are you", 4),
    
    # 5: Stressed/Overwhelmed
    ("I am overwhelmed by too much work", 5),
    ("I am so stressed out and exhausted", 5),
    ("burned out and swamped", 5)
]

crisis_model = None
mood_model = None

CRISIS_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "nlp_crisis_weights.json")
MOOD_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "nlp_mood_weights.json")

def train_or_load_nlp_models():
    global crisis_model, mood_model
    vocab_len = len(VOCABULARY)
    crisis_model = TextNeuralNetwork(vocab_len, 2)
    mood_model = TextNeuralNetwork(vocab_len, 6)
    
    if os.path.exists(CRISIS_WEIGHTS_PATH) and os.path.exists(MOOD_WEIGHTS_PATH):
        c_ok = crisis_model.load(CRISIS_WEIGHTS_PATH)
        m_ok = mood_model.load(MOOD_WEIGHTS_PATH)
        if c_ok and m_ok:
            return "NLP Models Loaded"
            
    X_c, y_c = [], []
    for text, label in CRISIS_TRAINING_PAIRS:
        vec = text_to_vector(text)
        X_c.append(vec)
        one_hot = [0.0, 0.0]
        one_hot[label] = 1.0
        y_c.append(one_hot)
    X_c = np.array(X_c, dtype=np.float32)
    y_c = np.array(y_c, dtype=np.float32)
    
    X_m, y_m = [], []
    for text, label in MOOD_TRAINING_PAIRS:
        vec = text_to_vector(text)
        X_m.append(vec)
        one_hot = [0.0] * 6
        one_hot[label] = 1.0
        y_m.append(one_hot)
    X_m = np.array(X_m, dtype=np.float32)
    y_m = np.array(y_m, dtype=np.float32)
    
    crisis_model.fit(X_c, y_c, epochs=250, lr=0.15)
    mood_model.fit(X_m, y_m, epochs=250, lr=0.15)
    
    crisis_model.save(CRISIS_WEIGHTS_PATH)
    mood_model.save(MOOD_WEIGHTS_PATH)
    return "NLP Models Trained"

def predict_crisis(text):
    global crisis_model
    if crisis_model is None:
        train_or_load_nlp_models()
    vec = text_to_vector(text)
    X_input = np.array([vec], dtype=np.float32)
    probs = crisis_model.forward(X_input)[0]
    return probs[1] >= 0.5, float(probs[1])

def predict_mood(text):
    global mood_model
    if mood_model is None:
        train_or_load_nlp_models()
    vec = text_to_vector(text)
    X_input = np.array([vec], dtype=np.float32)
    probs = mood_model.forward(X_input)[0]
    class_idx = int(np.argmax(probs))
    idx_to_mood = {
        0: "happy",
        1: "sad",
        2: "anxious",
        3: "angry",
        4: "neutral",
        5: "overwhelmed"
    }
    return idx_to_mood.get(class_idx, "neutral"), probs.tolist()
