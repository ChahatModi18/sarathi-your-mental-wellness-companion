# Project Implementation Details (IMPLEMENTATION.md) — BhagvadMood Platform

> **Document Version:** 2.0.0  
> **Core Technologies:** Python 3.11+, Tkinter, Flask, MySQL Connector, PyTorch / NumPy, TextBlob, PyMuPDF  
> **Key Implementation Modules:** `Main.py`, `app.py`, `wellness_ml.py`, `database_setup.py`

---

## 1. Codebase Architecture & Modular Organization

The project is structured into modular execution paths providing dual client interfaces while sharing identical business rules, algorithmic models, and persistence schemas.

```
                    ┌────────────────────────────┐
                    │     User / Client Request  │
                    └──────────────┬─────────────┘
                                   │
               ┌───────────────────┴───────────────────┐
               ▼                                       ▼
    ┌──────────────────────┐               ┌──────────────────────┐
    │ Desktop Client (GUI) │               │ Web Client (Flask)   │
    │ Main.py (27 Frames)  │               │ app.py (Jinja2 Web)  │
    └──────────┬───────────┘               └──────────┬───────────┘
               │                                       │
               └───────────────────┬───────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │  NLP & Sentiment Engine    │
                    │  - TextBlob Polarity/Subj  │
                    │  - Context Tagging Tagger  │
                    │  - Crisis Pattern Scanner  │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │  Dual-Engine Machine Learn │
                    │  wellness_ml.py            │
                    │  - PyTorch Deep Models     │
                    │  - NumPy He-Init Networks  │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │  Persistence & Storage     │
                    │  MySQL 8 (sarathi_sih_db)  │
                    └────────────────────────────┘
```

---

## 2. Core Implementation Walkthrough

### 2.1 The Machine Learning Dual-Engine (`wellness_ml.py`)
To guarantee high performance on high-end developer workstations and uninterrupted fallback resilience on restricted environments, `wellness_ml.py` is implemented with a dual-engine architecture:

#### A. PyTorch Implementation
When PyTorch is accessible, `TextPyTorchModel` executes feedforward inference using CUDA or CPU:
```python
class TextPyTorchModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 12)
        self.fc2 = nn.Linear(12, output_dim)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.softmax(self.fc2(x), dim=-1)
        return x
```

#### B. NumPy Analytical Fallback Implementation
When PyTorch cannot be loaded (e.g. system Application Control policy blocks DLL execution, or running on lightweight systems), `TextNeuralNetwork` executes analytical matrix operations with He-initialization:
```python
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
```

---

### 2.2 Text Context Identification & Sentiment Analysis
Implemented in `Main.py` via `detect_text_context` and `get_sentiment_enhanced`:

```python
def detect_text_context(text):
    text_lower = text.lower()
    context_mapping = {
        "Academic Stress": ["exam", "assignment", "college", "university", "semester", "grades", "deadline", "study"],
        "Career / Work": ["job", "work", "office", "boss", "career", "promotion", "interview", "salary", "burnout"],
        "Relationships": ["relationship", "partner", "girlfriend", "boyfriend", "family", "friend", "marriage"],
        "Health & Body": ["health", "pain", "illness", "doctor", "sleep", "diet", "exercise", "physical"],
        "Financial Pressure": ["money", "debt", "loan", "rent", "bills", "savings", "budget", "finance"],
        "Self-Esteem": ["confidence", "self-worth", "esteem", "worthless", "compare", "body image"],
        "Loss & Grief": ["loss", "grief", "bereavement", "death", "lost", "heartbroken"],
        "General Wellbeing": ["stress", "anxious", "sad", "happy", "overwhelmed", "angry", "tired"]
    }
    for label, keywords in context_mapping.items():
        if any(word in text_lower for word in keywords):
            return label
    return "General Wellbeing"
```

---

### 2.3 Desktop GUI State & Frame Lifecycle (`Main.py`)
`SarathiApp` instantiates 27 frame objects during startup and organizes them inside a central stacking frame:
```python
class SarathiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bhagvad Mood Journal, Your Wellness Companion")
        self.geometry("1200x800")
        self.user_id = None
        self.username = None
        self.user_streak = 0
        self.mindful_points = 0
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (WelcomePage, LoginFrame, RegisterFrame, ChatbotFrame,
                  AdminDashboardFrame, ResourcesFrame, BookingFrame,
                  PeerSupportFrame, EntriesFrame, ExportFrame, SpinWheelFrame,
                  ToDoNotesFrame, PeriodJournalFrame, PeriodLogFrame,
                  PeriodStatsFrame, ScreeningsFrame, RewardsFrame, ...):
            page_name = F.__name__
            frame = F(parent=self.container, app=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("WelcomePage")
```

---

### 2.4 Web Implementation (`app.py`)
The Flask web application mirrors all desktop functionality:
- Uses `session['user_id']` and `session['role']` to guard routes.
- Renders Jinja2 templates located in `templates/`.
- Connects to MySQL with parameterized queries, preventing injection attacks.
- Exposes JSON endpoints (`/api/health`, `/api/sentiment`) for decoupled frontend applications.

