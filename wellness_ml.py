import os
import numpy as np
import json

USE_REAL_TORCH = False
torch = None
nn = None
optim = None
device = None

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

# Custom NumPy fallback sequential model for Text Classification
class TextNeuralNetwork:
    def __init__(self, input_dim, output_dim):
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


# Try importing PyTorch
def _import_torch_if_available():
    global USE_REAL_TORCH, torch, nn, optim, device
    try:
        import torch as t
        import torch.nn as n
        import torch.optim as o
        torch = t
        nn = n
        optim = o
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        USE_REAL_TORCH = True
        print(f"[ML INFO] PyTorch imported successfully. Running on device: {device}")
    except Exception as e:
        print(f"[ML INFO] PyTorch not available: {e}. Falling back to NumPy Sequential models.")
        USE_REAL_TORCH = False

_import_torch_if_available()

# PyTorch Model Classes
if USE_REAL_TORCH:
    class WellnessPyTorchModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(5, 8)
            self.fc2 = nn.Linear(8, 4)
            
        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = torch.softmax(self.fc2(x), dim=-1)
            return x

    class TextPyTorchModel(nn.Module):
        def __init__(self, input_dim, output_dim):
            super().__init__()
            self.fc1 = nn.Linear(input_dim, 12)
            self.fc2 = nn.Linear(12, output_dim)
            
        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = torch.softmax(self.fc2(x), dim=-1)
            return x

# Paths
def _find_weight_file(filename, subfolder=""):
    candidates = [
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join(os.path.dirname(__file__), subfolder, filename) if subfolder else "",
        os.path.join(os.path.dirname(__file__), "models", filename),
        os.path.join(os.path.dirname(__file__), "..", filename),
        os.path.join(os.path.dirname(__file__), "..", "models", filename),
        os.path.join(os.path.dirname(__file__), "..", "backend", "models", filename),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    return os.path.join(os.path.dirname(__file__), filename)

MODEL_PATH_PTH = _find_weight_file("wellness_model.pth", "models")
CRISIS_MODEL_PATH_PTH = _find_weight_file("nlp_crisis_model.pth", "models")
MOOD_MODEL_PATH_PTH = _find_weight_file("nlp_mood_model.pth", "models")

WEIGHTS_PATH_JSON = _find_weight_file("wellness_model_weights.json")
CRISIS_WEIGHTS_PATH = _find_weight_file("nlp_crisis_weights.json")
MOOD_WEIGHTS_PATH = _find_weight_file("nlp_mood_weights.json")

# Compatibility with existing files referencing old paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), "wellness_model.keras")

# Global instances (will hold either PyTorch models or NumPy sequentially executed models)
model = None
crisis_model = None
mood_model = None


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


def train_pytorch_model(pytorch_model, X_train, y_train, epochs=100, batch_size=16, lr=0.01):
    pytorch_model.to(device)
    optimizer = optim.Adam(pytorch_model.parameters(), lr=lr)
    inputs = torch.tensor(X_train, dtype=torch.float32).to(device)
    targets = torch.tensor(y_train, dtype=torch.float32).to(device)
    
    dataset = torch.utils.data.TensorDataset(inputs, targets)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    pytorch_model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            preds = pytorch_model(batch_x)
            # Categorical crossentropy loss
            loss = -torch.mean(torch.sum(batch_y * torch.log(preds + 1e-15), dim=-1))
            loss.backward()
            optimizer.step()


def train_or_load_model():
    global model, USE_REAL_TORCH
    X_train, y_train = generate_synthetic_data()
    
    if USE_REAL_TORCH:
        try:
            model = WellnessPyTorchModel()
            if os.path.exists(MODEL_PATH_PTH):
                model.load_state_dict(torch.load(MODEL_PATH_PTH, map_location=device))
                model.to(device)
                return "PyTorch Sequential (Loaded)"
            else:
                train_pytorch_model(model, X_train, y_train, epochs=100, batch_size=16, lr=0.01)
                torch.save(model.state_dict(), MODEL_PATH_PTH)
                return "PyTorch Sequential (Trained)"
        except Exception as e:
            print(f"[ML WARNING] Failed to train/load with PyTorch: {e}. Falling back to NumPySequential.")
            USE_REAL_TORCH = False
            
    # NumPy Fallback
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
    
    if USE_REAL_TORCH:
        try:
            model.eval()
            with torch.no_grad():
                tensor_input = torch.tensor(X_input, dtype=torch.float32).to(device)
                preds = model(tensor_input).cpu().numpy()
                class_idx = int(np.argmax(preds[0]))
                return class_idx, preds[0].tolist()
        except Exception as e:
            print(f"[ML WARNING] PyTorch prediction failed: {e}. Falling back to NumPy Sequential.")
            
    # NumPy Fallback Prediction
    preds = model.forward(X_input)
    class_idx = int(np.argmax(preds[0]))
    return class_idx, preds[0].tolist()


# ==============================================================================
# --- NLP TEXT CLASSIFIER FOR CRISIS DETECTION AND MOOD CLASSIFICATION ---
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


def train_or_load_nlp_models():
    global crisis_model, mood_model, USE_REAL_TORCH
    vocab_len = len(VOCABULARY)
    
    if USE_REAL_TORCH:
        try:
            crisis_model = TextPyTorchModel(vocab_len, 2)
            mood_model = TextPyTorchModel(vocab_len, 6)
            
            if os.path.exists(CRISIS_MODEL_PATH_PTH) and os.path.exists(MOOD_MODEL_PATH_PTH):
                crisis_model.load_state_dict(torch.load(CRISIS_MODEL_PATH_PTH, map_location=device))
                mood_model.load_state_dict(torch.load(MOOD_MODEL_PATH_PTH, map_location=device))
                crisis_model.to(device)
                mood_model.to(device)
                return "NLP PyTorch Models Loaded"
            else:
                # Prepare training data
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
                
                train_pytorch_model(crisis_model, X_c, y_c, epochs=250, batch_size=8, lr=0.01)
                train_pytorch_model(mood_model, X_m, y_m, epochs=250, batch_size=8, lr=0.01)
                
                torch.save(crisis_model.state_dict(), CRISIS_MODEL_PATH_PTH)
                torch.save(mood_model.state_dict(), MOOD_MODEL_PATH_PTH)
                return "NLP PyTorch Models Trained"
        except Exception as e:
            print(f"[ML WARNING] Failed to train/load NLP models with PyTorch: {e}. Falling back to NumPy.")
            USE_REAL_TORCH = False
            
    # NumPy Fallback
    crisis_model = TextNeuralNetwork(vocab_len, 2)
    mood_model = TextNeuralNetwork(vocab_len, 6)
    
    if os.path.exists(CRISIS_WEIGHTS_PATH) and os.path.exists(MOOD_WEIGHTS_PATH):
        c_ok = crisis_model.load(CRISIS_WEIGHTS_PATH)
        m_ok = mood_model.load(MOOD_WEIGHTS_PATH)
        if c_ok and m_ok:
            return "NLP NumPy Models Loaded"
            
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
    return "NLP NumPy Models Trained"


def predict_crisis(text):
    global crisis_model, USE_REAL_TORCH
    if crisis_model is None:
        train_or_load_nlp_models()
        
    vec = text_to_vector(text)
    X_input = np.array([vec], dtype=np.float32)
    
    if USE_REAL_TORCH:
        try:
            crisis_model.eval()
            with torch.no_grad():
                tensor_input = torch.tensor(X_input, dtype=torch.float32).to(device)
                probs = crisis_model(tensor_input).cpu().numpy()[0]
                return bool(probs[1] >= 0.5), float(probs[1])
        except Exception as e:
            print(f"[ML WARNING] NLP crisis prediction with PyTorch failed: {e}. Falling back to NumPy.")
            
    # NumPy Fallback
    probs = crisis_model.forward(X_input)[0]
    return bool(probs[1] >= 0.5), float(probs[1])


def predict_mood(text):
    global mood_model, USE_REAL_TORCH
    if mood_model is None:
        train_or_load_nlp_models()
        
    vec = text_to_vector(text)
    X_input = np.array([vec], dtype=np.float32)
    
    if USE_REAL_TORCH:
        try:
            mood_model.eval()
            with torch.no_grad():
                tensor_input = torch.tensor(X_input, dtype=torch.float32).to(device)
                probs = mood_model(tensor_input).cpu().numpy()[0]
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
        except Exception as e:
            print(f"[ML WARNING] NLP mood prediction with PyTorch failed: {e}. Falling back to NumPy.")
            
    # NumPy Fallback
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
