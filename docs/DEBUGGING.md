# Troubleshooting & Debugging Guides (DEBUGGING.md) — BhagvadMood Platform

> **Document Version:** 2.1.0  
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

# 4. Run automated test suite (all 43 tests must pass)
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

### Issue 5: Port 5000 or Port 8000 Already in Use
- **Symptom:** `OSError: [Errno 10048] Only one usage of each socket address is normally permitted`.
- **Root Cause:** A lingering Python background process is holding port 5000 (Flask) or port 8000 (FastAPI).
- **Resolution:**
  ```powershell
  # Identify process on port 5000:
  netstat -ano | findstr :5000
  # Terminate by PID:
  taskkill /PID <PID> /F
  ```

---

### Issue 6: `werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'api_period_export'. Did you mean 'period' instead?`
- **Symptom:** Visiting `/period` raises a Flask 500 BuildError stating that endpoint `'api_period_export'` was not found.
- **Root Cause:** The route decorator `@app.route('/api/period/export')` was inadvertently placed below the `if __name__ == '__main__': app.run(...)` block in `app.py`. When `app.py` is executed via WSGI or imported by the test client, code below `if __name__ == '__main__':` is never evaluated, causing the endpoint to remain unregistered.
- **Resolution:** Repositioned the route definition into module global scope above `if __name__ == '__main__':` in both `app.py` and `backend/app.py`.

---

### Issue 7: Login View Dark Viewport & Unstyled Voicebot Drawer Collision
- **Symptom:** When navigating to `/login`, the right viewport displayed a pitch-black background despite Daylight mode being active, and the Sarathi Voicebot floating drawer mounted unstyled over the login form.
- **Root Cause:** `templates/login.html` did not link `static/css/main.css`, contained hardcoded background `#080614` in its private `<style>` tag, and `static/js/main.js` automatically injected the voicebot drawer on every DOMContentLoaded event without checking the current route.
- **Resolution:**
  1. Linked `static/css/main.css` to `login.html` and bound body background to `var(--bg-page)`.
  2. Integrated the floating universal theme selector (`Daylight`, `Amber`, `Midnight`).
  3. Styled flash alert boxes with high-contrast text and border tokens (`#047857` and `#be123c`).
  4. Added a route exclusion guard in `initSarathiVoiceBot()`:
     ```javascript
     if (window.location.pathname === '/login' || window.location.pathname === '/register') return;
     ```

---

### Issue 8: PyMuPDF Deprecation Warning (`import fitz`)
- **Symptom:** Running tests or importing document extraction utilities triggered `DeprecationWarning: PyMuPDF: The module 'fitz' has been renamed to 'pymupdf'`.
- **Root Cause:** Upgraded versions of PyMuPDF deprecate the historical `fitz` namespace in favor of `pymupdf`.
- **Resolution:** Updated imports to `import pymupdf as fitz` and registered `filterwarnings = ignore::DeprecationWarning` in `pytest.ini`. 0 warnings remain.
