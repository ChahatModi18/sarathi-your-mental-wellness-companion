# Setup & Installation Guide — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Prerequisites

- **Python:** Version 3.10, 3.11, or 3.12 (Recommended: Python 3.11)
- **Database:** MySQL Community Server 8.0+ (Optional: SQLite is used as auto-fallback)
- **OS:** Windows 10/11, macOS, or Ubuntu Linux

---

## 2. Step-by-Step Installation

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "c:\Users\Lenovo\Desktop\RECENT\Minor Project, python (.venv)"
```

### Step 2: Set Up Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Download NLP Tokenizer Data (One-Time)
```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### Step 5: Configure Database & Environment
Copy or create `.env`:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=bhagvadmood
OPENAI_API_KEY=optional_key_here
```

Run database initialization:
```powershell
python database_setup.py
```

### Step 6: Launch BhagvadMood Journal
```powershell
python Main.py
```
