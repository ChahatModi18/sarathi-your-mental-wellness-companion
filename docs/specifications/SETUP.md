# Environment Setup & Installation Guide (SETUP.md) — BhagvadMood

> **Document Version:** 2.0.0  
> **Supported OS:** Windows 10/11, Ubuntu 20.04/22.04 LTS, macOS Monterey+  
> **Python Compatibility:** Python 3.11.x, Python 3.12.x, Python 3.14.x  
> **Database:** MySQL Server 8.0+ / MariaDB 10.5+

---

## 1. System Prerequisites

1. **Python:** 3.11 or later installed. Verify via:
   ```bash
   python --version
   ```
2. **MySQL Server:** Version 8.0 running locally on port 3306.
   - On Windows: Verify the service is running (`Get-Service *mysql*`).
   - On Linux/macOS: Verify with `sudo systemctl status mysql`.
3. **Git (Optional):** For version control and cloning.

---

## 2. Installation on Windows

### Step 1: Open Terminal in Workspace
```powershell
cd "c:\Users\Lenovo\Desktop\RECENT\Minor Project, python (.venv)"
```

### Step 2: Install Dependencies
```powershell
# Using the pre-configured virtual environment:
.\Scripts\python.exe -m pip install -r requirements.txt

# Or using the system Python interpreter:
python -m pip install -r requirements.txt
```

### Step 3: Configure Database Credentials
Create a `.env` file based on `.env.example`:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=chahat
DB_NAME=sarathi_sih_db
```
*(If your MySQL root password differs from `chahat`, set `DB_PASSWORD=your_password` in your `.env` or set it in your environment).*

### Step 4: Initialize the Database
```powershell
python database_setup.py
```
Expected output:
```text
Database sarathi_sih_db created/verified and populated successfully.
```

### Step 5: Launch the Application
- **To launch the Desktop GUI:**
  ```powershell
  .\run_desktop.bat
  # or: python Main.py
  ```
- **To launch the Web Platform:**
  ```powershell
  .\run_web.bat
  # or: python app.py
  ```
  Open `http://127.0.0.1:5000` in your web browser.

---

## 3. Installation on Linux / macOS

```bash
# 1. Create a fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Initialize MySQL Database
export DB_HOST="localhost"
export DB_USER="root"
export DB_PASSWORD="your_mysql_password"
python3 database_setup.py

# 4. Run the Web Application
python3 app.py
```

---

## 4. Containerized Deployment (Docker & Docker Compose)

To spin up both MySQL 8 and the BhagvadMood Web Platform in isolated containers with zero manual configuration:

```bash
# Build and start services
docker-compose up --build -d

# View real-time container logs
docker-compose logs -f web

# Verify health status
curl http://localhost:5000/api/health
```

To shut down services while preserving database data:
```bash
docker-compose down
```

---

## 5. Verification & Test Suite

Verify that your environment is fully operational by executing the automated test suite:

```bash
python -m pytest tests/
```
All 25 tests should pass.

