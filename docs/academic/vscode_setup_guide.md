# VS Code Environment & Project Setup Guide

This guide details the step-by-step instructions to configure, run, and develop this application inside **Visual Studio Code (VS Code)**. It covers virtual environments, package installations, running Jupyter notebooks, and hosting the Flask server.

---

## Step 1: Install VS Code Extensions

For the best development experience, open VS Code and install the following extensions from the Extensions Marketplace (Ctrl+Shift+X):

1. **Python** (by Microsoft) - Enables code linting, debugging, and environment selection.
2. **Jupyter** (by Microsoft) - Allows opening, editing, and running `.ipynb` notebook files directly inside VS Code.

---

## Step 2: Open Project and Activate the Virtual Environment

1. Open VS Code, select **File > Open Folder...**, and select the folder:
   `c:\Users\Lenovo\Desktop\Minor Project, python (.venv)`
2. Open a new terminal in VS Code: **Terminal > New Terminal** (or press Ctrl+\`).
3. Make sure you are using the Windows PowerShell environment. Activate the existing virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(If you get a script execution permission error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` in the terminal first).*

---

## Step 3: Install Required Packages

To support PyTorch (our advanced ML engine) and Flask/Jinja2 (our web UI), install the necessary packages. Run the following command inside your activated virtual environment terminal:

```powershell
# Install PyTorch (CPU-only version is ideal and lightweight for wellness models)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install Flask for Web UI hosting
pip install flask
```

Ensure all other original dependencies are installed:
```powershell
pip install -r requirements.txt
```

---

## Step 4: Run the Jupyter Notebook in VS Code

1. In the VS Code file explorer (left panel), click on [wellness_ml.ipynb](file:///c:/Users/Lenovo/Desktop/Minor%20Project,%20python%20%28.venv%29/wellness_ml.ipynb).
2. The Jupyter interface will load.
3. In the top-right corner of the editor, click **Select Kernel**.
4. Choose **Python Environments...** and select the `.venv` interpreter (`.venv/Scripts/python.exe`).
5. You can now run individual cells by clicking the **Play** button next to each cell, or click **Run All** in the top bar to train and evaluate the PyTorch models.

---

## Step 5: Launch the Flask Web Application

1. Open the file [app.py](file:///c:/Users/Lenovo/Desktop/Minor%20Project,%20python%20%28.venv%29/app.py) (we will create this in the next step).
2. Ensure your local MySQL server is running.
3. If you have an OpenAI API key, configure it in your terminal environment:
   ```powershell
   $env:OPENAI_API_KEY="your_api_key_here"
   ```
4. Start the Flask application by running:
   ```powershell
   python app.py
   ```
5. Click the link in the terminal output (usually `http://127.0.0.1:5000`) or open your browser and navigate to that address to view the stunning new Web GUI.

---

## Step 6: Verify with Diagnostic Tests

Run the following test script inside the terminal to confirm PyTorch model training, loading, and inference work seamlessly:
```powershell
python test_ml_diagnostics.py
```
This script will output classification probabilities using the PyTorch backend, verifying that the integration was successful.
