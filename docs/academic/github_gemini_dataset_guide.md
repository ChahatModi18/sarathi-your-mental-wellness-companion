# GitHub, VS Code, Gemini API & Dataset Integration Guide

This guide details the step-by-step instructions for managing the BhagvadMood Journal codebase on GitHub, setting it up in VS Code, integrating the Google Gemini API, and loading custom datasets for model training.

---

## 1. Pushing the Codebase to GitHub

To store the project securely on GitHub without leaking sensitive local virtual environments, database credentials, trained weights, or API keys, follow these steps:

### Step 1: Create a `.gitignore` File
Create a `.gitignore` file in the root of the project to exclude local system files and configurations. Copy and paste the following content:

```text
# Virtual Environments
venv/
.venv/
Scripts/
Lib/
Include/
pyvenv.cfg

# Python Cache & Compiled Files
__pycache__/
*.py[cod]
*$py.class

# Local Databases & Server Configurations
instance/
.webassets-cache
database_setup.py

# Trained Weights Cache
*.pth
*.json
!wellness_ml.ipynb # Keep jupyter notebook

# Environment Variables and Secret Keys
.env
secret_key.txt

# VS Code Configurations
.vscode/
```

### Step 2: Initialize Git and Push to GitHub
Open your terminal inside the project root directory and run the following Git commands:

```bash
# Initialize local git repository
git init

# Stage all files except those in .gitignore
git add .

# Create initial commit
git commit -m "Initial commit - PyTorch and Flask Migration"

# Rename branch to main
git branch -M main

# Link to your remote GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/BhagvadMood-Journal.git

# Push changes
git push -u origin main
```

---

## 2. Importing and Running the Code in VS Code

If you or another developer clones this repository on a new machine, follow these steps to configure VS Code and the execution environment:

### Step 1: Clone and Open the Project
Clone the repository and open it in VS Code:
```bash
git clone https://github.com/YOUR_USERNAME/BhagvadMood-Journal.git
cd BhagvadMood-Journal
code .
```

### Step 2: Create a Python Virtual Environment
Initialize a clean local virtual environment:
```bash
# On Windows:
python -m venv .venv

# On macOS/Linux:
python3 -m venv .venv
```

### Step 3: Create a `requirements.txt` File
Create a `requirements.txt` file in the root directory to hold dependencies:
```text
torch --index-url https://download.pytorch.org/whl/cpu
flask
mysql-connector-python
textblob
pymupdf
```

Then install the packages:
```bash
# Activate the virtual environment
# On Windows:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 4: Select Python Interpreter in VS Code
Tell VS Code to use the newly created virtual environment interpreter:
1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on Mac) to open the Command Palette.
2. Search for **Python: Select Interpreter**.
3. Select the interpreter pointing to the virtual environment (e.g., `.\.venv\Scripts\python.exe`).

### Step 5: Handling Python 3.14 Site Decoding Issues
If Python 3.14 fails to load with a `Fatal Python error: init_import_site`, disable the default site scanning by passing the `-S` flag when launching scripts, and manually add `site-packages` to `sys.path`. 

Create a `.vscode/launch.json` file to automate this in VS Code:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Flask App (Safe Site)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/app.py",
            "pythonArgs": ["-S"],
            "console": "integratedTerminal"
        },
        {
            "name": "Run Diagnostics (Safe Site)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/test_ml_diagnostics.py",
            "pythonArgs": ["-S"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## 3. Integrating the Google Gemini API

To replace or augment the existing sentiment/reframing logic with the **Google Gemini API**, use the modern **Google GenAI SDK** (`google-genai` library).

### Step 1: Install the Google GenAI Library
Install the SDK in your activated virtual environment:
```bash
pip install google-genai
```

### Step 2: Obtain and Set the Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Create API Key** and copy the generated key.
3. Define the key in your local system environment variables:
   * **On Windows (PowerShell)**:
     ```powershell
     $env:GEMINI_API_KEY="your_api_key_here"
     ```
   * **On Windows (Command Prompt)**:
     ```cmd
     set GEMINI_API_KEY=your_api_key_here
     ```
   * **On macOS/Linux**:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```

### Step 3: Code Integration in `app.py`
Replace the rule-based reframing matrices or OpenAI calls inside [app.py](file:///c:/Users/Lenovo/Desktop/Minor%20Project, python (.venv)/app.py) with the following client integration code:

```python
import os
from google import genai
from google.genai import types

# Initialize Gemini Client if API key is present
gemini_client = None
if os.environ.get("GEMINI_API_KEY"):
    try:
        # The new SDK automatically resolves the GEMINI_API_KEY from environment
        gemini_client = genai.Client()
        print("[INFO] Gemini Client initialized successfully.")
    except Exception as e:
        print(f"[WARNING] Gemini initialization failed: {e}")

def get_gemini_reframe(user_thought, detected_mood):
    """
    Sends the user thought and mood to Gemini to obtain a Gita shlok-aligned cognitive reframe.
    """
    if not gemini_client:
        return None, None, None
        
    prompt = f"""
    The user wrote the following journal reflection: "{user_thought}"
    Our NLP system classified their emotional state as: "{detected_mood}".
    
    Act as a wise, empathetic mental wellness companion. 
    1. Identify a relevant Sanskrit Shlok from the Bhagavad Gita that speaks directly to their state.
    2. Provide its English translation.
    3. Write a supportive, CBT-based reframing explanation showing how to apply the verse's wisdom to resolve their struggles.
    
    Response format (strict JSON):
    {{
        "shlok": "Sanskrit Shlok text here",
        "translation": "English translation here",
        "insight": "Empathetic CBT-based reframing explanation here"
    }}
    """
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        # Parse JSON output
        import json
        result = json.loads(response.text)
        return result.get("shlok"), result.get("translation"), result.get("insight")
    except Exception as e:
        print(f"[ERROR] Gemini request failed: {e}")
        return None, None, None
```

Integrate this function into your Flask route `/journal_submit`:
```python
# In app.py /journal_submit route:
shlok, meaning, insight = None, None, None

# Try Gemini first
if os.environ.get("GEMINI_API_KEY"):
    shlok, meaning, insight = get_gemini_reframe(thought, mood)

# Fallback to local rule-based matrix if Gemini fails or is not configured
if not shlok:
    shlok, meaning = get_shlok_by_mood(mood)
    insight = analyze_and_reframe(thought)
```

---

## 4. Customizing and Training the Dataset

If you want to train the models on your own datasets (e.g., custom mood labels or demographics data):

### Step 1: Format Your CSV Files
Format your local dataset files matching [dataset_requirements.md](file:///c:/Users/Lenovo/Desktop/Minor%20Project,%20python%20%28.venv%29/dataset_requirements.md):
* **Recommendation Dataset (`recommendation_data.csv`)**: Must contain headers `age`, `gender`, `phq9`, `gad7`, `polarity`, and `recommended_resource` (values $0$ to $3$).
* **Mood Dataset (`mood_dataset.csv`)**: Must contain headers `text` and `mood` (labels: happy, sad, angry, anxious, neutral, overwhelmed).

### Step 2: Adjust Paths and Run Training
Load the dataset paths in [wellness_ml.py](file:///c:/Users/Lenovo/Desktop/Minor%20Project,%20python%20%28.venv%29/wellness_ml.py) and execute the model's training loop:

```python
# To load and train on custom data, run this in python:
import pandas as pd
import torch
import wellness_ml

# Load your custom CSVs
rec_df = pd.read_csv("path/to/your/recommendation_data.csv")

# Extract inputs and target labels
X = rec_df[['age', 'gender', 'phq9', 'gad7', 'polarity']].values
y = rec_df['recommended_resource'].values

# Preprocess and normalize inputs
# (Follow formulas in wellness_ml.py)

# Initialize PyTorch Model
model = wellness_ml.WellnessPyTorchModel()

# Train
wellness_ml.train_recommendation_model(model, X, y, epochs=150)

# Save the trained weights file
torch.save(model.state_dict(), "wellness_model.pth")
```

Alternatively, run the visual training cells in [wellness_ml.ipynb](file:///c:/Users/Lenovo/Desktop/Minor%20Project,%20python%20%28.venv%29/wellness_ml.ipynb) using VS Code's Jupyter Notebook interface.
