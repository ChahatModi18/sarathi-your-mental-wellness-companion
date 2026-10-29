# Environment Setup & Installation Guide (SETUP.md) — BhagvadMood

> **Document Version:** 2.1.0  
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
Create or edit your `.env` file based on `.env.example`:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=chahat
DB_NAME=sarathi_sih_db
```
*(If your local MySQL root password differs from `chahat`, update `DB_PASSWORD=your_actual_password`).*

### Step 4: Initialize the Database
```powershell
python database_setup.py
```
Expected output:
```text
Database sarathi_sih_db created/verified and populated successfully.
```

### Step 5: Launching Applications

#### Option A: Launch Desktop GUI
```powershell
.\run_desktop.bat
# or: python Main.py
```

#### Option B: Launch Flask Web Platform
```powershell
.\run_web.bat
# or: python app.py
```
Open your browser at `http://127.0.0.1:5000`.

#### Option C: Launch FastAPI Asynchronous Microservice
```powershell
python fastapi_app.py
# or using Uvicorn:
uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 --reload
```
Access interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

---

## 3. Running Automated Tests

Verify that your installation is fully operational by executing the 43 automated unit and integration tests:

```powershell
python -m pytest tests/
```

Expected result:
```text
============================= 43 passed in 6.84s =============================
```

---

## 4. Docker Container Deployment

To launch the complete containerized stack (Flask Web Application + MySQL 8 Database) with zero manual database configuration:

```bash
# Build and run containers
docker-compose up --build

# Run in background
docker-compose up -d

# Check service logs
docker-compose logs -f web

# Tear down environment
docker-compose down
```
When running via Docker, the web application is accessible at `http://localhost:5000`.
