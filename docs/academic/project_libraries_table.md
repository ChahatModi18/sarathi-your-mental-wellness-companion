# Reference Guide: Imported Libraries and Modules

This document outlines all external frameworks, standard libraries, and helper modules used throughout the BhagvadMood Journal codebase (`Main.py`, `app.py`, `database_setup.py`, and `wellness_ml.py`).

| Library / Module Name | Core Import Example | Domain | Purpose & Functionality |
| :--- | :--- | :--- | :--- |
| **PyTorch (`torch`)** | `import torch`<br>`import torch.nn as nn`<br>`import torch.optim as optim`<br>`from torch.utils.data import DataLoader` | Machine Learning | Deep Learning backend. Defines neural layers, initializes parameters, sets up optimizer loops (SGD/Adam), constructs data loaders, and saves weights (`.pth`). |
| **NumPy (`numpy`)** | `import numpy as np` | Data Science / Math | Vectorized array operations. Used as the main mathematical computation engine for the local fallback models when PyTorch is not available. |
| **Flask (`flask`)** | `from flask import Flask, render_template, request, session, jsonify, flash` | Web Server / Router | Web application framework. Manages routes, renders Jinja2 HTML templates, tracks session states, handles authentication redirects, and returns JSON APIs. |
| **MySQL Connector (`mysql.connector`)** | `import mysql.connector` | Database | Establishes connections to local MySQL instances, maps records, and executes SQL commands (queries, inserts, updates, and deletes). |
| **TextBlob (`textblob`)** | `from textblob import TextBlob` | NLP / Sentiment | Performs natural language processing. Analyzes user journal logs to determine mood polarity (range $[-1.0, 1.0]$) and subjectivity. |
| **PyMuPDF (`fitz`)** | `import fitz` | File Parser | Opens, renders, and extracts text content from PDF documents (used for scripture rendering and document parsing). |
| **Tkinter (`tkinter`)** | `import tkinter as tk`<br>`from tkinter import messagebox, ttk` | Desktop GUI | Core graphical user interface framework for the legacy desktop platform (`Main.py`). Renders dialog windows, input prompts, and widgets. |
| **Matplotlib (`matplotlib`)** | `from matplotlib.figure import Figure`<br>`from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg` | Visualization | Renders data visualizations (pie charts, trend lines) inside the Tkinter dashboard. |
| **tkinterPdfViewer** | `from tkinterPdfViewer import tkinterPdfViewer` | GUI widget | Custom third-party library to load and display chapters of the Gita PDF directly inside a Tkinter scrollable frame. |
| **OpenAI Client (`openai`)** | `from openai import OpenAI` | LLM Integration | Integrates with GPT-3.5-turbo/GPT-4 to generate conversational CBT reframing dialogues when an API key is available. |
| **Hashlib (`hashlib`)** | `import hashlib` | Security | Computes SHA-256 cryptographic hashes with a local pepper key to protect user and counselor passwords. |
| **Datetime (`datetime`)** | `from datetime import datetime, timedelta, date` | Time / Scheduling | Manages slot assignments, session schedules, journal entry timestamps, cycle lengths, and consecutive daily streak logs. |
| **Regular Expressions (`re`)** | `import re` | String Parsing | Implements pattern matching. Critical for safety regexes (crisis detection) and forum moderation filters. |
| **System Interface (`sys`)** | `import sys` | System Utilities | Alters system paths (`sys.path.insert`) to manually load libraries from `Lib/site-packages` when default site modules are disabled. |
| **OS Module (`os`)** | `import os` | System Environment | Accesses system path structures, resolves local files, and retrieves secret keys or database passwords from environment variables. |
| **Random (`random`)** | `import random` | Utilities | Generates randomized numbers (used to select Gita shlokas and compute spin wheel rewards). |
| **JSON (`json`)** | `import json` | File Serialization | Parses and saves model configuration and weight matrices in JSON text files for NumPy fallback loops. |
| **CSV (`csv`)** | `import csv` | Data Storage | Reads and exports user records, diagnostics, or datasets to structured CSV spreadsheets. |
| **Webbrowser (`webbrowser`)** | `import webbrowser` | OS Navigation | Opens the system's default internet browser to direct users to specific self-care recommendations (such as YouTube videos). |
| **I/O Engine (`io`)** | `import io` | Stream Utility | Handles text data streams as memory buffers (used for CSV data generation and exports). |
