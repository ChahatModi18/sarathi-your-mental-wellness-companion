# Bhagvad Mood Journal

A mental wellness desktop application built with Python, Tkinter, OpenAI, and lightweight machine learning.

## Features

- Mood and journal entry analysis
- Context-aware OpenAI reframing and support suggestions
- Peer support forum UI improvements
- Crisis detection and resource recommendations
- MySQL integration for persistence
- Fallback ML logic for environments without TensorFlow

## Requirements

- Python 3.12+
- `openai`
- `textblob`
- `mysql-connector-python`
- `matplotlib`
- `Pillow`
- `tkcalendar`
- `tkinterPdfViewer`

Install dependencies with:

```powershell
pip install -r requirements.txt
```

## Run

Activate the virtual environment and run:

```powershell
python Main.py
```

## Notes

- Ensure your OpenAI API key is configured in the environment before using mood analysis features.
- If `keras` is installed, the project can use advanced ML support; otherwise the fallback NumPy model is used.
