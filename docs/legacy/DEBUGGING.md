# Debugging & Troubleshooting Playbook — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Common Issues & Solutions

### Issue 1: `mysql.connector.errors.InterfaceError: Can't connect to MySQL server`
- **Cause:** Local MySQL service is stopped or wrong credentials in `.env`.
- **Solution:** Verify service status via `Get-Service MySQL*`. Ensure `DB_USER` and `DB_PASSWORD` are valid. If not running, the application will fallback to SQLite.

### Issue 2: `LookupError: Resource punkt not found`
- **Cause:** NLTK data dependencies not downloaded on current machine.
- **Solution:** Run in terminal:
  ```powershell
  python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
  ```

### Issue 3: `ModuleNotFoundError: No module named 'tkinterPdfViewer'`
- **Cause:** Optional PDF viewer dependency missing.
- **Solution:** `pip install tkinterPdfViewer Pillow` or view PDF references via external default viewer.
