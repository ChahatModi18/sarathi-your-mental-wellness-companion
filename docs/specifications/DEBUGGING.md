# Troubleshooting & Debugging Guides (DEBUGGING.md) — BhagvadMood Platform

> **Document Version:** 2.0.0  
> **Target Audience:** Developers, System Administrators, Evaluators

---

## 1. Quick Diagnostic Checklist

Before diving into specific issues, run these diagnostic commands to verify the environment health:

```powershell
# 1. Verify Python version
python --version

# 2. Check MySQL Service status
Get-Service *mysql*

# 3. Test Database Connection
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password='your_password'); print('MySQL OK')"

# 4. Run automated test suite
python -m pytest tests/
```

---

## 2. Common Issues & Root Cause Resolutions

### Issue 1: `ImportError: cannot import name '_regex' from partially initialized module 'regex'`
- **Symptom:** Running `python Main.py` or importing `textblob` crashes with an `_regex` circular import or DLL mismatch.
- **Root Cause:** A hardcoded `sys.path.insert(0, "Lib/site-packages")` was prepending the virtual environment's site-packages to Python's search path. Because the venv in the project was built using Python 3.14 with `_regex.cp314-win_amd64.pyd`, running with Python 3.11 attempted to load incompatible Python 3.14 binary extensions.
- **Resolution:** [Main.py](Main.py#L3-L6) now guards the injection:
  ```python
  venv_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib", "site-packages")
  if sys.version_info[:2] == (3, 14) and os.path.isdir(venv_site) and venv_site not in sys.path:
      sys.path.insert(0, venv_site)
  ```
  This allows standard Python 3.11 and venv Python 3.14 to use their own matching native binaries seamlessly.

---

### Issue 2: `[WinError 4551] An Application Control policy has blocked this file ... torch_python.dll`
- **Symptom:** Startup prints a warning regarding PyTorch or AppLocker blocking `torch_python.dll`.
- **Root Cause:** Windows Defender Application Control (WDAC) or AppLocker policies in enterprise or managed university environments block unsigned third-party PyTorch C++ binaries.
- **Resolution:** The platform's machine learning engine (`wellness_ml.py`) is engineered with a **zero-dependency fallback**:
  1. The code catches `WinError 4551` and general exceptions during `import torch`.
  2. Sets `USE_REAL_TORCH = False`.
  3. Seamlessly activates `NumPySequential` and `TextNeuralNetwork` with weights loaded from `wellness_model_weights.json`, `nlp_mood_weights.json`, and `nlp_crisis_weights.json`.
  4. All predictions, sentiment scoring, and resource recommendations continue working without crashing.

---

### Issue 3: `mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied for user 'root'@'localhost'`
- **Symptom:** App fails to start with database access denied.
- **Root Cause:** The default password (`chahat`) does not match the local MySQL root password on your system.
- **Resolution:** Set the `DB_PASSWORD` environment variable in PowerShell or in `.env`:
  ```powershell
  # Set environment variable in PowerShell:
  $env:DB_PASSWORD="your_actual_mysql_password"

  # Then launch:
  python database_setup.py
  python Main.py
  ```

---

### Issue 4: `mysql.connector.errors.ProgrammingError: 1054 (42S22): Unknown column 'username' in 'field list'`
- **Symptom:** `database_setup.py` or `/forum` crashes with unknown column `username` or `message`.
- **Root Cause:** An older version of the `forum_posts` table existed with legacy column names (`author` and `content`).
- **Resolution:** Run `database_setup.py`. It includes safe idempotent migrations:
  ```sql
  ALTER TABLE forum_posts ADD COLUMN username VARCHAR(100) NOT NULL DEFAULT 'Anonymous';
  ALTER TABLE forum_posts ADD COLUMN message TEXT;
  ```

---

### Issue 5: Port 5000 Already in Use (Web Client)
- **Symptom:** Running `app.py` gives `OSError: [Errno 10048] Only one usage of each socket address is normally permitted`.
- **Root Cause:** Another process (e.g. an earlier Flask process or Docker container) is holding port 5000.
- **Resolution:**
  ```powershell
  # Identify the process listening on port 5000:
  netstat -ano | findstr :5000

  # Terminate the process (replace <PID> with process ID found):
  taskkill /PID <PID> /F
  ```
  Or change the port in `app.py`:
  ```python
  app.run(port=5050, debug=True)
  ```

---

### Issue 6: Tkinter GUI Fails in Headless or SSH Environment
- **Symptom:** `_tkinter.TclError: no display name and no $DISPLAY environment variable`.
- **Root Cause:** Desktop Tkinter requires an active X-server or Windows desktop session.
- **Resolution:** In remote or headless server environments, use the web client (`app.py`), which runs independently of graphical display drivers:
  ```bash
  python app.py
  ```

