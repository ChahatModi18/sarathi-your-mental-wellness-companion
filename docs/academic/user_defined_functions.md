# Developer Reference: User-Defined Functions (UDF)

This document provides a comprehensive list of all custom classes and user-defined functions developed within the BhagvadMood Journal codebase.

---

## 1. Machine Learning Core (`wellness_ml.py`)

### `WellnessPyTorchModel(nn.Module)` (Class)
* **Constructor**: `__init__(self, input_dim=5, output_dim=4)`
* **Forward Pass**: `forward(self, x)`
* **Purpose**: Maps user demographics (Age, Gender) and clinical scores (PHQ-9, GAD-7, Mood Polarity) to 4 support resource categories using feedforward linear layers with Dropout.

### `TextPyTorchModel(nn.Module)` (Class)
* **Constructor**: `__init__(self, input_dim=200, output_dim=2)`
* **Forward Pass**: `forward(self, x)`
* **Purpose**: Classifies text reflections (represented as a 200-dimensional bag-of-words vector) for crisis identification (binary) and mood classification (6 categories).

### `NumPySequential` (Class)
* **Constructor**: `__init__(self, weights_dict)`
* **Methods**: `forward(self, x)`
* **Purpose**: Executes feedforward calculations using weight matrices and bias vectors stored in JSON files. Bypasses PyTorch dependencies during offline fallbacks.

### `TextNeuralNetwork` (Class)
* **Constructor**: `__init__(self, weights_dict)`
* **Methods**: `forward(self, x)`
* **Purpose**: A NumPy-only neural network representing the bag-of-words text classifier, used to determine crisis or mood outputs without PyTorch installed.

### `get_sentiment(text)`
* **Inputs**: `text` (String)
* **Outputs**: Polarity (Float between $-1.0$ and $1.0$), Subjectivity (Float between $0.0$ and $1.0$)
* **Purpose**: Uses TextBlob to compute polarity score metrics for journal reflections.

### `detect_crisis_regex(text)`
* **Inputs**: `text` (String)
* **Outputs**: Boolean (True if matching risk words, False otherwise)
* **Purpose**: Scans entries for self-harm keywords, providing a safety override system that executes before the machine learning models.

### `get_shlok_by_mood(mood)`
* **Inputs**: `mood` (String)
* **Outputs**: Tuple: `(shlok_sanskrit, english_meaning)`
* **Purpose**: Selects and returns a relevant Sanskrit verse from the Bhagavad Gita based on the user's detected emotional state.

### `train_recommendation_model(model, X, y, epochs=150)`
* **Inputs**: `model` (WellnessPyTorchModel), `X` (NumPy Array), `y` (NumPy Array), `epochs` (Int)
* **Outputs**: Trained model weights (saved to `wellness_model.pth` and `wellness_model_weights.json`)
* **Purpose**: Trains the feedforward recommendation model using CrossEntropyLoss and SGD optimization.

### `train_text_model(model, texts, labels, num_classes, epochs=10)`
* **Inputs**: `model` (TextPyTorchModel), `texts` (List of Strings), `labels` (List of Ints), `num_classes` (Int), `epochs` (Int)
* **Outputs**: Saves trained weights to `.pth` and `.json` files.
* **Purpose**: Fits the text classifier to training samples, converting words into a vocabulary bag-of-words index.

### `get_recommendation(age, gender, phq9, gad7, journal_polarity)`
* **Inputs**: `age` (Int), `gender` (String), `phq9` (Int), `gad7` (Int), `journal_polarity` (Float)
* **Outputs**: Dictionary: `{"type": ResourceType, "title": ResourceTitle, "desc": ResourceDescription}` and probabilities list
* **Purpose**: Preprocesses parameters, runs predictions through the active recommendation model (PyTorch or NumPy fallback), and returns the suggested resource.

### `classify_text_crisis(text)`
* **Inputs**: `text` (String)
* **Outputs**: Boolean (True for crisis, False for safe) and float probability
* **Purpose**: Analyzes input text to determine crisis risk, checking regex safety rules first before running neural network inferences.

### `classify_text_mood(text)`
* **Inputs**: `text` (String)
* **Outputs**: String mood label and list of class probabilities
* **Purpose**: Classifies journal entries into one of the 6 emotional categories.

---

## 2. Database Initializations (`database_setup.py`)

### `hash_password(password, username="")`
* **Inputs**: `password` (String), `username` (String)
* **Outputs**: Hex String SHA-256
* **Purpose**: Combines a password, a local pepper key, and the user's lowercase username to generate a secure cryptographic hash.

### `init_db()`
* **Inputs**: None
* **Outputs**: Database initialization log
* **Purpose**: Connects to the local MySQL server, creates the `sarathi_sih_db` database, establishes tables with foreign key constraints, and seeds default counselors and forum posts.

---

## 3. Web Server Controller (`app.py`)

### `get_db_connection()`
* **Inputs**: None
* **Outputs**: MySQL connection object
* **Purpose**: Connects to the local MySQL server using environment credentials.

### `login()` & `register()`
* **Inputs**: HTTP POST form details
* **Outputs**: Rendered portals or dashboard redirects
* **Purpose**: Handles authentication routes and role-based checks for Students, Counselors, and Admins.

### `dashboard()` & `journal_submit()`
* **Inputs**: Form thought inputs (AJAX/Fetch)
* **Outputs**: JSON details containing mood parameters, shloka information, CBT reframes, points won, and streak stats
* **Purpose**: Processes daily journal inputs. Runs safety filters and mood models, fetches verses, updates streaks and mindful points, and logs entries in the database.

### `screenings()`
* **Inputs**: Selected responses to GAD-7 / PHQ-9 questions
* **Outputs**: Scores logged to the database and page redirects
* **Purpose**: Logs clinical assessment scores and returns history metrics.

### `resources()`
* **Inputs**: HTTP GET/POST requests
* **Outputs**: Rendered recommendations templates
* **Purpose**: Processes PyTorch classification probabilities and displays relevant self-care recommendations.

### `forum()`
* **Inputs**: Category filter parameters and post form fields
* **Outputs**: Filtered discussion board threads
* **Purpose**: Manages anonymous peer support postings, checking for bad words before logging entries.

### `booking()`
* **Inputs**: Selection options for counselors, specialization fields, and time slots
* **Outputs**: Redirects to booking pages
* **Purpose**: Manages appointment bookings and schedules availability slots.

### `period()`
* **Inputs**: Start date, end date, and symptom notes
* **Outputs**: Logged cycle parameters and statistical analytics
* **Purpose**: Tracks menstrual cycles for female users, calculating average cycle lengths and intervals.

### `todo()`
* **Inputs**: Task definitions
* **Outputs**: Task lists and mindful points (+15 MP)
* **Purpose**: Renders to-do checklists and manages task completion.

### `spinwheel()`
* **Inputs**: HTTP POST requests
* **Outputs**: JSON details containing points won and updated user totals
* **Purpose**: Processes spin wheel rewards (10 to 50 MP) once a day.

### `counselor_dashboard()` & `admin_dashboard()`
* **Inputs**: Action updates
* **Outputs**: Rendered dashboard panels
* **Purpose**: Counselor interface for slot approvals and Admin console for system oversight.

---

## 4. Desktop Client Logic (`Main.py`)

### `detect_text_context(text)`
* **Inputs**: `text` (String)
* **Outputs**: Intensity multipliers (Float), negation adjustments (Float)
* **Purpose**: Enhances TextBlob sentiment analysis by scanning for intensifiers (e.g., "very", "extremely") and negations (e.g., "not", "no").

### `get_sentiment_enhanced(text)`
* **Inputs**: `text` (String)
* **Outputs**: Adjusted mood polarity (Float)
* **Purpose**: Computes sentiment polarity, adjusting results based on negations and intensifiers.

### `check_risk_escalation(user_id)`
* **Inputs**: `user_id` (Int)
* **Outputs**: String alerts or None
* **Purpose**: Checks the user's recent journal entries. Generates warning alerts if the user logs three consecutive negative entries or shows high risk indicators.

### `analyze_and_reframe(text)`
* **Inputs**: `text` (String)
* **Outputs**: CBT cognitive restructuring reframe (String)
* **Purpose**: Scans user reflections for cognitive distortions (e.g., black-and-white thinking, personalization) and suggests positive alternatives.
