import os
import sys
# Ensure parent repository and backend directory are accessible
_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent not in sys.path:
    sys.path.insert(0, _parent)
_backend = os.path.abspath(os.path.join(_parent, "backend"))
if _backend not in sys.path:
    sys.path.insert(0, _backend)
import sqlite3
import random
import re
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

# Inject site-packages
# Inject the virtual environment's site packages path only if using a compatible Python 3.14 interpreter
venv_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib", "site-packages")
if sys.version_info[:2] == (3, 14) and os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

import customtkinter as ctk

# Try importing wellness_ml
try:
    import wellness_ml
except Exception as e:
    wellness_ml = None
    print(f"[ML INFO] wellness_ml import failed on startup: {e}")

# Try importing mysql.connector
try:
    import mysql.connector
except ImportError:
    mysql = None

# Optional for stats window
matplotlib_available = False
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    matplotlib_available = True
except ImportError:
    pass

# Try importing tkcalendar
tkcalendar_available = False
try:
    from tkcalendar import DateEntry
    tkcalendar_available = True
except ImportError:
    pass

# Try importing pdf viewer
pdf_viewer_available = False
try:
    from tkinterPdfViewer import tkinterPdfViewer as pdf
    pdf_viewer_available = True
except ImportError:
    class DummyPdfViewer:
        def ShowPdf(self):
            return self
        def pdf_view(self, master, pdf_location, width, height):
            lbl = ctk.CTkLabel(master, text="PDF Viewer not available.\nPlease install 'tkinterPdfViewer'.", text_color="red")
            lbl.pack(pady=20)
            return tk.Frame(master)
    pdf = DummyPdfViewer()

# --- DATABASE SETUP ---
conn = None
cursor = None
IS_SQLITE = False

def init_db():
    global conn, cursor, IS_SQLITE
    # Try MySQL first
    mysql_success = False
    if mysql is not None:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=os.environ.get("chahat", "chahat")
            )
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS sarathi_sih_db")
            cursor.execute("USE sarathi_sih_db")
            print("[DB INFO] Connected to MySQL successfully.")
            mysql_success = True
        except Exception as e:
            print(f"[DB WARNING] MySQL connection failed ({e}). Falling back to SQLite.")
    
    if not mysql_success:
        IS_SQLITE = True
        conn = sqlite3.connect("sarathi_local.db", check_same_thread=False)
        cursor = conn.cursor()
        print("[DB INFO] Connected to local SQLite successfully.")

    # Create Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT DEFAULT NULL,
            gender TEXT DEFAULT NULL,
            age INTEGER DEFAULT NULL,
            diagnosed_conditions TEXT DEFAULT NULL,
            journal_streak INTEGER DEFAULT 0,
            last_journal_date TEXT DEFAULT NULL,
            mindful_points INTEGER DEFAULT 0
        )
    """ if IS_SQLITE else """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(255) DEFAULT NULL,
            gender VARCHAR(20) DEFAULT NULL,
            age INT DEFAULT NULL,
            diagnosed_conditions TEXT DEFAULT NULL,
            journal_streak INT DEFAULT 0,
            last_journal_date DATE DEFAULT NULL,
            mindful_points INT DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            mood TEXT NOT NULL,
            thought TEXT,
            shlok TEXT,
            shlok_meaning TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """ if IS_SQLITE else """
        CREATE TABLE IF NOT EXISTS journal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            username VARCHAR(100) NOT NULL,
            mood VARCHAR(50) NOT NULL,
            thought TEXT,
            shlok TEXT,
            shlok_meaning TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

init_db()

# DB query wrappers
def db_query(query, params=None):
    global cursor, IS_SQLITE
    if IS_SQLITE:
        query = query.replace("%s", "?")
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()

def db_execute(query, params=None):
    global conn, cursor, IS_SQLITE
    if IS_SQLITE:
        query = query.replace("%s", "?")
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return False

# --- COMPASSIONATE DATA ---
shloks = {
    "positive": [("कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।", "You have a right to perform your duties, but never to the fruits of those actions.")],
    "negative": [("श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।", "It is better to fail in one's own duty than to succeed in another’s.")],
    "neutral": [("योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।", "Perform your duty equipoised, abandoning all attachment to success or failure.")],
    "anxious": [("मा ते संगोऽस्त्वकर्मणि।", "Do not be attached to inaction.")],
    "peaceful": [("शान्तिमाप्नोति नैष्ठिकीम्।", "One attains supreme peace.")],
    "angry": [("क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः।", "From anger comes delusion, from delusion the loss of memory.")],
    "very_happy": [("न हि कश्चित्क्षणमपि जातु तिष्ठत्यकर्मकृत्।", "No one can remain without action even for a moment.")],
    "pessimistic": [("मात्मानं अवसादयेत्।", "Do not allow yourself to sink into despair.")],
    "optimistic": [("मां अनन्याश्चिन्तयन्तो ye जनाः पर्युपासते।", "Those who worship me with unwavering devotion — I carry what they lack.")],
    "overwhelmed": [("समं सर्वेषु भूतेषु तिष्ठन्तं परमेश्वरम्।", "See the Lord equally present in all beings.")],
    "restless": [("चञ्चलं हि मनः कृष्ण", "The mind is restless, turbulent, obstinate, and very strong.")],
    "very_sad": [("न जायते म्रियते वा कदाचित्।", "The soul is eternal; it neither dies nor is born. — BG 2.20")],
    "sad": [("जातस्य हि ध्रुवो मृत्युर्ध्रुवं जन्म मृतस्य च।", "Do not grieve for the living or the dead. — BG 2.27")],
    "discouraged": [("यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता।", "Just as a lamp in a windless place does not flicker, remain steady.")],
    "devastated": [("नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः।", "Weapons do not cut the soul, fire does not burn it.")],
    "ecstatic": [("हृष्यन्ति पश्यतां सर्वे लोकाः।", "All worlds rejoice beholding the divine form.")],
    "content": [("सन्तुष्टः सततं योगी यथा लभते तिष्ठति।", "The yogi who is always content remains steady.")],
    "happy": [("सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ।", "Treating happiness and distress, gain and loss, victory and defeat alike.")]
}

MINI_GOALS = {
    "anxious": {"goal": "Complete a 3-minute breath exercise (e.g., Square Breathing).", "reward": 25},
    "stressed": {"goal": "Do one thing on your to-do list for 15 minutes.", "reward": 20},
    "sad": {"goal": "Reach out to one trusted friend or family member.", "reward": 15},
    "angry": {"goal": "Do 10 minutes of light physical stretching.", "reward": 30},
}

uplifting_messages = [
    "Every day is a new beginning.",
    "You are stronger than you think.",
    "This too shall pass.",
    "Believe in yourself and all that you are.",
    "Small steps lead to big changes.",
    "Be kind to yourself today; you are doing your best."
]

# Color Tokens for CustomTkinter
bg_color = ("#F5F6F8", "#0B0F19")
card_color = ("#FFFFFF", "#151E2E")
sidebar_color = ("#EAECEF", "#0F172A")
primary_accent = ("#2D6A4F", "#52B788")
accent_hover = ("#1B4332", "#74C69D")
text_primary = ("#0F172A", "#F1F5F9")
text_secondary = ("#475569", "#94A3B8")

class SarathiAdvancedApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sārathi - Advanced Wellness & Mindfulness Desktop")
        self.geometry("1180x750")
        
        # Set theme behavior
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")
        
        # State
        self.user_id = None
        self.username = None
        self.mindful_points = 0
        self.journal_streak = 0
        
        # Window configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, fg_color=bg_color)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (WelcomeFrame, LoginFrame, DashboardFrame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("WelcomeFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_raise"):
            frame.on_raise()

# --- WELCOME FRAME ---
class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=bg_color)
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left Panel (Text & Proceed)
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(5, weight=1)
        
        self.logo_lbl = ctk.CTkLabel(self.left_panel, text="🧘 Sārathi", font=("Georgia", 40, "bold"), text_color=primary_accent)
        self.logo_lbl.grid(row=1, column=0, sticky="w", pady=(10,20))
        
        self.title_lbl = ctk.CTkLabel(self.left_panel, text="Your AI-Powered Wellness &\nMindfulness Companion", font=("Helvetica", 24, "bold"), text_color=text_primary, justify="left")
        self.title_lbl.grid(row=2, column=0, sticky="w", pady=10)
        
        self.desc_lbl = ctk.CTkLabel(self.left_panel, text="Feeling lost? Your inner peace awaits. Start journaling, chat with our wellness model, and find clarity with timeless scriptural wisdom.", font=("Helvetica", 14), text_color=text_secondary, justify="left", wraplength=450)
        self.desc_lbl.grid(row=3, column=0, sticky="w", pady=(10,30))
        
        self.btn_proceed = ctk.CTkButton(self.left_panel, text="Proceed to Login", font=("Helvetica", 14, "bold"), height=45, fg_color=primary_accent, hover_color=accent_hover, text_color="white", command=lambda: app.show_frame("LoginFrame"))
        self.btn_proceed.grid(row=4, column=0, sticky="w", pady=10)
        
        # Right Panel (Book image / Quote Card)
        self.right_panel = ctk.CTkFrame(self, fg_color=card_color, corner_radius=20, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.right_panel.grid(row=0, column=1, padx=40, pady=60, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(3, weight=1)
        
        # Book Image Loading
        self.img_lbl = ctk.CTkLabel(self.right_panel, text="")
        self.img_lbl.grid(row=1, column=0, padx=20, pady=20, sticky="center")
        try:
            pil_img = Image.open("gita_preview.png")
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 290))
            self.img_lbl.configure(image=ctk_img)
        except Exception:
            self.img_lbl.configure(text="📖\n[Bhagavad Gita Tri-lingual Preview]")
            self.img_lbl.configure(font=("Georgia", 16, "italic"), text_color=text_secondary)
            
        self.quote_lbl = ctk.CTkLabel(self.right_panel, text="\"Perform your duty equipoised, abandoning all attachment to success or failure.\"\n— Bhagavad Gita", font=("Georgia", 14, "italic"), text_color=primary_accent, wraplength=350, justify="center")
        self.quote_lbl.grid(row=2, column=0, padx=30, pady=(10,30), sticky="center")
        self.right_panel.grid_columnconfigure(0, weight=1)

# --- LOGIN FRAME ---
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=bg_color)
        self.app = app
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Centered Login Card
        self.card = ctk.CTkFrame(self, fg_color=card_color, corner_radius=20, width=420, height=520, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.card.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.card.grid_propagate(False)
        self.card.grid_columnconfigure(0, weight=1)
        
        self.title_lbl = ctk.CTkLabel(self.card, text="Welcome Back", font=("Helvetica", 24, "bold"), text_color=text_primary)
        self.title_lbl.pack(pady=(40, 10))
        
        self.subtitle_lbl = ctk.CTkLabel(self.card, text="Sign in to resume your wellness journey", font=("Helvetica", 13), text_color=text_secondary)
        self.subtitle_lbl.pack(pady=(0, 30))
        
        # User input fields
        self.username_inp = ctk.CTkEntry(self.card, placeholder_text="Username", width=300, height=45, corner_radius=8, border_color=("#CBD5E1", "#334155"))
        self.username_inp.pack(pady=10)
        
        self.password_inp = ctk.CTkEntry(self.card, placeholder_text="Password", show="*", width=300, height=45, corner_radius=8, border_color=("#CBD5E1", "#334155"))
        self.password_inp.pack(pady=10)
        
        self.btn_login = ctk.CTkButton(self.card, text="Login", font=("Helvetica", 14, "bold"), width=300, height=45, corner_radius=8, fg_color=primary_accent, hover_color=accent_hover, command=self.perform_login)
        self.btn_login.pack(pady=(25, 10))
        
        self.btn_reg_switch = ctk.CTkButton(self.card, text="Don't have an account? Sign Up", font=("Helvetica", 12), text_color=primary_accent, fg_color="transparent", hover=False, command=self.perform_registration)
        self.btn_reg_switch.pack(pady=5)
        
        self.btn_back = ctk.CTkButton(self.card, text="Back to Home", font=("Helvetica", 12), text_color=text_secondary, fg_color="transparent", hover=False, command=lambda: app.show_frame("WelcomeFrame"))
        self.btn_back.pack(pady=(15, 0))

    def perform_login(self):
        username = self.username_inp.get().strip()
        password = self.password_inp.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
            
        # Select user
        rows = db_query("SELECT id, username, mindful_points, journal_streak FROM users WHERE username = %s AND password = %s", (username, password))
        if rows:
            self.app.user_id = rows[0][0]
            self.app.username = rows[0][1]
            self.app.mindful_points = rows[0][2]
            self.app.journal_streak = rows[0][3]
            
            messagebox.showinfo("Login Success", f"Welcome back, {self.app.username}!")
            self.app.show_frame("DashboardFrame")
        else:
            # Check if there is any user in database at all (for quick demo helper)
            existing_users = db_query("SELECT COUNT(*) FROM users")
            if existing_users[0][0] == 0:
                # Automake account for easy testing
                db_execute("INSERT INTO users (username, password, mindful_points, journal_streak) VALUES (%s, %s, 100, 3)", (username, password))
                rows = db_query("SELECT id, username, mindful_points, journal_streak FROM users WHERE username = %s AND password = %s", (username, password))
                self.app.user_id = rows[0][0]
                self.app.username = rows[0][1]
                self.app.mindful_points = rows[0][2]
                self.app.journal_streak = rows[0][3]
                messagebox.showinfo("Demo Mode", f"Created new demo user '{username}' and logged in!")
                self.app.show_frame("DashboardFrame")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

    def perform_registration(self):
        username = self.username_inp.get().strip()
        password = self.password_inp.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in Username and Password first to register.")
            return
            
        rows = db_query("SELECT id FROM users WHERE username = %s", (username,))
        if rows:
            messagebox.showerror("Registration Error", "Username already exists.")
            return
            
        if db_execute("INSERT INTO users (username, password, mindful_points, journal_streak) VALUES (%s, %s, 50, 1)", (username, password)):
            messagebox.showinfo("Success", "Registration complete! You can now login.")
        else:
            messagebox.showerror("Error", "Could not complete registration.")

# --- DASHBOARD FRAME ---
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=bg_color)
        self.app = app
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Viewport
        
        # Navigation Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=sidebar_color, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(6, weight=1) # spacer
        self.sidebar.grid_rowconfigure(9, weight=0)
        
        # User details card
        self.profile_card = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.profile_card.grid(row=0, column=0, padx=15, pady=(30, 20), sticky="ew")
        
        self.username_lbl = ctk.CTkLabel(self.profile_card, text="Hi, Guest", font=("Helvetica", 16, "bold"), text_color=text_primary, anchor="w")
        self.username_lbl.pack(fill="x")
        
        self.points_lbl = ctk.CTkLabel(self.profile_card, text="Points: 0 MP  |  Streak: 0 🔥", font=("Helvetica", 12), text_color=primary_accent, anchor="w")
        self.points_lbl.pack(fill="x", pady=(2, 0))
        
        # Sidebar Menu Items
        self.menu_buttons = []
        menus = [
            ("Home / Mini-Goals", "home"),
            ("Wellness Chatbot", "chatbot"),
            ("Gita Thought Journal", "journal"),
            ("Read Gita PDF", "pdf_reader"),
            ("Analytics & Moods", "stats")
        ]
        
        for idx, (label, code) in enumerate(menus):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=label, 
                font=("Helvetica", 13, "bold"),
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=text_secondary,
                hover_color=bg_color,
                command=lambda c=code: self.select_tab(c)
            )
            btn.grid(row=idx+1, column=0, padx=12, pady=5, sticky="ew")
            self.menu_buttons.append((code, btn))
            
        # Theme / Appearance Toggle
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar, values=["System", "Dark", "Light"], command=self.change_theme_event, fg_color=primary_accent, button_color=primary_accent, button_hover_color=accent_hover, text_color="white")
        self.theme_menu.grid(row=7, column=0, padx=15, pady=10, sticky="ew")
        
        # Logout
        self.logout_btn = ctk.CTkButton(self.sidebar, text="Logout", font=("Helvetica", 12, "bold"), fg_color="transparent", border_width=1, border_color=text_secondary, text_color=text_secondary, hover_color=("#F1F5F9", "#1E293B"), command=self.logout)
        self.logout_btn.grid(row=8, column=0, padx=15, pady=(0, 30), sticky="ew")
        
        # Right Viewport tabs
        self.tabs = {}
        
        self.tab_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.tab_container.grid_rowconfigure(0, weight=1)
        self.tab_container.grid_columnconfigure(0, weight=1)
        
        for TabClass in (HomeTab, ChatbotTab, JournalTab, PdfTab, StatsTab):
            tab = TabClass(self.tab_container, self)
            self.tabs[tab.code] = tab
            tab.grid(row=0, column=0, sticky="nsew")
            
        self.select_tab("home")
        
    def on_raise(self):
        self.username_lbl.configure(text=f"Hi, {self.app.username or 'Guest'}")
        self.points_lbl.configure(text=f"Points: {self.app.mindful_points} MP  |  Streak: {self.app.journal_streak} 🔥")
        self.select_tab("home")

    def select_tab(self, tab_code):
        for code, tab in self.tabs.items():
            if code == tab_code:
                tab.tkraise()
                if hasattr(tab, "on_active"):
                    tab.on_active()
            else:
                pass
                
        # Highlight active sidebar item
        for code, btn in self.menu_buttons:
            if code == tab_code:
                btn.configure(fg_color=primary_accent, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=text_secondary)

    def change_theme_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def logout(self):
        self.app.user_id = None
        self.app.username = None
        self.app.show_frame("WelcomeFrame")

# --- TAB INTERFACE BASE ---
class TabBase(ctk.CTkFrame):
    def __init__(self, parent, dashboard):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        self.app = dashboard.app
        self.code = None

# --- HOME / MINI-GOALS TAB ---
class HomeTab(TabBase):
    def __init__(self, parent, dashboard):
        super().__init__(parent, dashboard)
        self.code = "home"
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Header Banner
        self.header = ctk.CTkFrame(self, fg_color=card_color, height=80, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.header.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(self.header, text="✨ Mindfulness Center", font=("Helvetica", 20, "bold"), text_color=primary_accent, padx=20, pady=25)
        self.header_title.pack(side="left")
        
        # Left Dashboard Side: Streak & Daily goals
        self.left_side = ctk.CTkFrame(self, fg_color="transparent")
        self.left_side.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.left_side.grid_columnconfigure(0, weight=1)
        
        # Streak Card
        self.streak_card = ctk.CTkFrame(self.left_side, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.streak_card.pack(fill="x", pady=(0, 15), ipady=15)
        
        self.streak_title = ctk.CTkLabel(self.streak_card, text="🔥 Current Streak", font=("Helvetica", 14, "bold"), text_color=text_primary, padx=15)
        self.streak_title.pack(anchor="w", pady=(10, 5))
        
        self.streak_val = ctk.CTkLabel(self.streak_card, text="3 Days", font=("Helvetica", 32, "bold"), text_color=primary_accent, padx=15)
        self.streak_val.pack(anchor="w")
        
        # Progress Mindful points
        self.points_progress_lbl = ctk.CTkLabel(self.streak_card, text="Mindfulness Level Progress", font=("Helvetica", 12), text_color=text_secondary, padx=15)
        self.points_progress_lbl.pack(anchor="w", pady=(10, 2))
        
        self.points_progress = ctk.CTkProgressBar(self.streak_card, height=10, fg_color=bg_color[0], progress_color=primary_accent[1])
        self.points_progress.pack(fill="x", padx=15, pady=(2, 5))
        self.points_progress.set(0.35)
        
        # Goals Card
        self.goals_card = ctk.CTkFrame(self.left_side, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.goals_card.pack(fill="both", expand=True, ipady=15)
        
        self.goals_title = ctk.CTkLabel(self.goals_card, text="🎯 Today's Mini-Goals", font=("Helvetica", 16, "bold"), text_color=text_primary, padx=15)
        self.goals_title.pack(anchor="w", pady=(15, 10))
        
        self.goals_box = ctk.CTkFrame(self.goals_card, fg_color="transparent")
        self.goals_box.pack(fill="both", expand=True, padx=15)
        
        # Right Dashboard Side: Spin Wheel Game
        self.right_side = ctk.CTkFrame(self, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.right_side.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        self.right_side.grid_columnconfigure(0, weight=1)
        self.right_side.grid_rowconfigure(0, weight=0)
        self.right_side.grid_rowconfigure(1, weight=1)
        
        self.wheel_title = ctk.CTkLabel(self.right_side, text="🎡 Wheel of Gita Wisdom", font=("Helvetica", 16, "bold"), text_color=text_primary)
        self.wheel_title.grid(row=0, column=0, pady=(20, 10))
        
        self.canvas = tk.Canvas(self.right_side, width=280, height=280, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=1, column=0, pady=20)
        
        self.spin_btn = ctk.CTkButton(self.right_side, text="Spin for Wisdom", font=("Helvetica", 14, "bold"), fg_color=primary_accent, hover_color=accent_hover, command=self.spin_wheel)
        self.spin_btn.grid(row=2, column=0, pady=(10, 30))
        
        self.wheel_result = ctk.CTkLabel(self.right_side, text="Press the button to spin the wheel!", font=("Georgia", 13, "italic"), text_color=primary_accent, justify="center", wraplength=250)
        self.wheel_result.grid(row=3, column=0, pady=(0, 20))
        
        self.draw_static_wheel()
        
    def on_active(self):
        self.streak_val.configure(text=f"{self.app.journal_streak} Days")
        progress_val = (self.app.mindful_points % 500) / 500.0
        self.points_progress.set(progress_val)
        
        # Load mini goals
        for widget in self.goals_box.winfo_children():
            widget.destroy()
            
        demo_goals = [
            ("Write in Gita Thought Journal", 25, True),
            ("Explore Gita verses in PDF viewer", 15, False),
            ("Do a quick breathing exercise", 20, False)
        ]
        
        for desc, reward, completed in demo_goals:
            item_frame = ctk.CTkFrame(self.goals_box, fg_color="transparent", height=40)
            item_frame.pack(fill="x", pady=6)
            
            cb = ctk.CTkCheckBox(item_frame, text=f"{desc} (+{reward} MP)", font=("Helvetica", 13), state="normal" if not completed else "disabled")
            cb.pack(side="left")
            if completed:
                cb.select()

    def draw_static_wheel(self):
        self.canvas.delete("all")
        colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#1A535C", "#A29BFE", "#FD79A8"]
        angles = [0, 60, 120, 180, 240, 300]
        for i, color in enumerate(colors):
            self.canvas.create_arc(10, 10, 270, 270, start=angles[i], extent=60, fill=color, outline="#F1F5F9", width=2)
            
        self.canvas.create_oval(125, 125, 155, 155, fill="white", outline=primary_accent[1], width=4)
        self.canvas.create_polygon(135, 120, 145, 120, 140, 95, fill="black")

    def spin_wheel(self):
        def rotate(count):
            if count > 0:
                self.canvas.delete("all")
                offset = count * 15
                colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#1A535C", "#A29BFE", "#FD79A8"]
                angles = [0, 60, 120, 180, 240, 300]
                for i, color in enumerate(colors):
                    self.canvas.create_arc(10, 10, 270, 270, start=angles[i]+offset, extent=60, fill=color, outline="#F1F5F9", width=2)
                self.canvas.create_oval(125, 125, 155, 155, fill="white", outline=primary_accent[1], width=4)
                self.canvas.create_polygon(135, 120, 145, 120, 140, 95, fill="black")
                self.canvas.after(40, lambda: rotate(count - 1))
            else:
                flat_list = []
                for k, v in shloks.items():
                    flat_list.extend(v)
                verse, meaning = random.choice(flat_list)
                self.wheel_result.configure(text=f"📜 {verse}\n\n💡 {meaning}")
                self.app.mindful_points += 15
                db_execute("UPDATE users SET mindful_points = %s WHERE id = %s", (self.app.mindful_points, self.app.user_id))
                self.dashboard.points_lbl.configure(text=f"Points: {self.app.mindful_points} MP  |  Streak: {self.app.journal_streak} 🔥")
                
        rotate(12)

# --- WELLNESS CHATBOT TAB ---
class ChatbotTab(TabBase):
    def __init__(self, parent, dashboard):
        super().__init__(parent, dashboard)
        self.code = "chatbot"
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        self.msg_area = ctk.CTkScrollableFrame(self, fg_color=bg_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.msg_area.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.entry_msg = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message to Sārathi...", height=45, corner_radius=8, border_color=("#CBD5E1", "#334155"))
        self.entry_msg.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda e: self.send_message())
        
        self.btn_send = ctk.CTkButton(self.input_frame, text="Send", font=("Helvetica", 14, "bold"), width=80, height=45, corner_radius=8, fg_color=primary_accent, hover_color=accent_hover, command=self.send_message)
        self.btn_send.grid(row=0, column=1)

        self.append_bubble("Sārathi", "Hare Krishna! I am Sārathi, your spiritual and emotional wellness companion. How are you feeling today?", is_user=False)
        
    def append_bubble(self, sender, text, is_user=True):
        bubble_frame = ctk.CTkFrame(self.msg_area, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=6, padx=5)
        
        card_bg = ("#D8F3DC", "#1B4332") if is_user else (card_color[0], card_color[1])
        bubble = ctk.CTkFrame(bubble_frame, fg_color=card_bg, corner_radius=12, border_width=1 if not is_user else 0, border_color=("#E2E8F0", "#1E293B"))
        
        if is_user:
            bubble.pack(side="right", anchor="e")
        else:
            bubble.pack(side="left", anchor="w")
            
        lbl_msg = ctk.CTkLabel(bubble, text=text, font=("Helvetica", 13), text_color=text_primary, justify="left", wraplength=480, padx=15, pady=10)
        lbl_msg.pack()
        
        self.msg_area._parent_canvas.yview_moveto(1.0)

    def send_message(self):
        msg = self.entry_msg.get().strip()
        if not msg:
            return
            
        self.entry_msg.delete(0, tk.END)
        self.append_bubble(self.app.username or "You", msg, is_user=True)
        self.after(600, lambda: self.process_bot_response(msg))

    def process_bot_response(self, text):
        is_crisis = False
        if wellness_ml is not None:
            is_crisis, _ = wellness_ml.predict_crisis(text)
            
        if is_crisis:
            response = "⚠️ [System Notice] Our model has detected indicators of a high-stress crisis state. Please remember you are not alone. Consider reaching out to professionals or support helplines (AASRA Helpline: +91-9820466726)."
        else:
            matched = False
            lowered = text.lower()
            response = ""
            for key, val in shloks.items():
                if key in lowered:
                    verse, meaning = random.choice(val)
                    response = f"I hear you. Here is a calming Gita verse to reflect on:\n\n📜 {verse}\n💡 {meaning}"
                    matched = True
                    break
            
            if not matched:
                response = f"Thank you for sharing. Remember: {random.choice(uplifting_messages)}"
                
        self.append_bubble("Sārathi", response, is_user=False)

# --- GITA THOUGHT JOURNAL TAB ---
class JournalTab(TabBase):
    def __init__(self, parent, dashboard):
        super().__init__(parent, dashboard)
        self.code = "journal"
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.left_side = ctk.CTkFrame(self, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.left_side.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        self.left_side.grid_columnconfigure(0, weight=1)
        
        self.write_lbl = ctk.CTkLabel(self.left_side, text="🖊️ Jot Down Your Thoughts", font=("Helvetica", 16, "bold"), text_color=text_primary, padx=20)
        self.write_lbl.pack(anchor="w", pady=(20, 10))
        
        self.textbox = ctk.CTkTextBox(self.left_side, font=("Helvetica", 13), border_width=1, border_color=("#CBD5E1", "#334155"), corner_radius=8)
        self.textbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.mood_lbl = ctk.CTkLabel(self.left_side, text="Select Your Primary Mood", font=("Helvetica", 13, "bold"), text_color=text_primary, padx=20)
        self.mood_lbl.pack(anchor="w", pady=(10, 5))
        
        self.mood_frame = ctk.CTkFrame(self.left_side, fg_color="transparent")
        self.mood_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        mood_options = [("😊 Happy", "happy"), ("😔 Sad", "sad"), ("😰 Anxious", "anxious"), ("😡 Angry", "angry"), ("🧘 Peaceful", "peaceful")]
        
        self.mood_selector = ctk.CTkSegmentedButton(self.mood_frame, values=[opt[0] for opt in mood_options], height=35)
        self.mood_selector.pack(fill="x")
        self.mood_selector.set("🧘 Peaceful")
        
        self.btn_submit = ctk.CTkButton(self.left_side, text="Reflect & Save Entry", font=("Helvetica", 14, "bold"), height=40, fg_color=primary_accent, hover_color=accent_hover, command=self.submit_journal)
        self.btn_submit.pack(fill="x", padx=20, pady=(0, 20))
        
        self.right_side = ctk.CTkFrame(self, fg_color="transparent")
        self.right_side.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        self.insight_card = ctk.CTkFrame(self.right_side, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.insight_card.pack(fill="both", expand=True)
        
        self.insight_title = ctk.CTkLabel(self.insight_card, text="🧘 Spiritual Reframing", font=("Helvetica", 16, "bold"), text_color=text_primary, padx=20)
        self.insight_title.pack(anchor="w", pady=(20, 10))
        
        self.shloka_box = ctk.CTkFrame(self.insight_card, fg_color=bg_color, corner_radius=10, border_width=1, border_color=primary_accent)
        self.shloka_box.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.shloka_lbl = ctk.CTkLabel(self.shloka_box, text="Your spiritual reframe card will appear here after reflection.", font=("Georgia", 13, "italic"), text_color=primary_accent, justify="center", wraplength=350, padx=20, pady=40)
        self.shloka_lbl.pack(fill="both", expand=True)

    def submit_journal(self):
        thought = self.textbox.get("1.0", tk.END).strip()
        selected_mood_label = self.mood_selector.get()
        
        mood_options = [("😊 Happy", "happy"), ("😔 Sad", "sad"), ("😰 Anxious", "anxious"), ("😡 Angry", "angry"), ("🧘 Peaceful", "peaceful")]
        mood_code = "peaceful"
        for opt, code in mood_options:
            if opt == selected_mood_label:
                mood_code = code
                break
                
        if not thought:
            messagebox.showwarning("Warning", "Please write down some thoughts first.")
            return
            
        predicted_mood = mood_code
        verse_list = shloks.get(predicted_mood, shloks["neutral"])
        verse, meaning = random.choice(verse_list)
        
        self.shloka_lbl.configure(
            text=f"✨ Daily Reframe Insight:\n\n📜 \"{verse}\"\n\n💡 Meaning:\n{meaning}",
            font=("Georgia", 14, "italic"),
            text_color=text_primary
        )
        
        db_execute(
            "INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.app.user_id, self.app.username, predicted_mood, thought, verse, meaning)
        )
        
        self.app.mindful_points += 30
        self.app.journal_streak += 1
        db_execute("UPDATE users SET mindful_points = %s, journal_streak = %s WHERE id = %s", (self.app.mindful_points, self.app.journal_streak, self.app.user_id))
        self.dashboard.points_lbl.configure(text=f"Points: {self.app.mindful_points} MP  |  Streak: {self.app.journal_streak} 🔥")
        
        messagebox.showinfo("Mindfulness Points", "Journal saved! +30 Mindfulness Points awarded. 🔥")

# --- GITA PDF VIEWER TAB ---
class PdfTab(TabBase):
    def __init__(self, parent, dashboard):
        super().__init__(parent, dashboard)
        self.code = "pdf_reader"
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.card = ctk.CTkFrame(self, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(0, weight=0)
        self.card.grid_rowconfigure(1, weight=1)
        
        self.title_lbl = ctk.CTkLabel(self.card, text="📖 Bhagavad Gita PDF Reader", font=("Georgia", 18, "bold"), text_color=primary_accent)
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.viewer_frame = ctk.CTkFrame(self.card, fg_color=bg_color, corner_radius=8)
        self.viewer_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.viewer_frame.grid_columnconfigure(0, weight=1)
        self.viewer_frame.grid_rowconfigure(0, weight=1)
        
        self.fallback_lbl = ctk.CTkLabel(self.viewer_frame, text="Loading PDF or manual viewer falls here...", justify="center")
        self.fallback_lbl.grid(row=0, column=0)
        
    def on_active(self):
        pdf_location = "BhagavadGita_Tri-lingual.pdf"
        
        for w in self.viewer_frame.winfo_children():
            w.destroy()
            
        if os.path.exists(pdf_location) and pdf_viewer_available:
            try:
                pdf_frame = tk.Frame(self.viewer_frame, bg="#ffffff")
                pdf_frame.pack(fill="both", expand=True)
                pdf.ShowPdf().pdf_view(pdf_frame, pdf_location=pdf_location, width=90, height=80)
            except Exception as e:
                lbl = ctk.CTkLabel(self.viewer_frame, text=f"Error displaying PDF natively:\n{e}\n\nFalling back to manual browser option.", text_color=text_secondary)
                lbl.pack(pady=20)
                btn = ctk.CTkButton(self.viewer_frame, text="Open PDF in Browser / System Reader", fg_color=primary_accent, hover_color=accent_hover, command=lambda: os.startfile(pdf_location))
                btn.pack(pady=10)
        else:
            lbl = ctk.CTkLabel(self.viewer_frame, text=f"Gita PDF Document ('{pdf_location}') not found or PDF viewer unavailable.\nVerify the file is in your project directory.", text_color=text_secondary)
            lbl.pack(pady=20)
            if os.path.exists(pdf_location):
                btn = ctk.CTkButton(self.viewer_frame, text="Open PDF directly", fg_color=primary_accent, hover_color=accent_hover, command=lambda: os.startfile(pdf_location))
                btn.pack(pady=10)

# --- ANALYTICS / MOODS TAB ---
class StatsTab(TabBase):
    def __init__(self, parent, dashboard):
        super().__init__(parent, dashboard)
        self.code = "stats"
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.card = ctk.CTkFrame(self, fg_color=card_color, corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(0, weight=0)
        self.card.grid_rowconfigure(1, weight=1)
        
        self.title_lbl = ctk.CTkLabel(self.card, text="📊 Your Mood Analytics", font=("Helvetica", 18, "bold"), text_color=primary_accent)
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.chart_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
    def on_active(self):
        for w in self.chart_frame.winfo_children():
            w.destroy()
            
        rows = db_query("SELECT mood, COUNT(*) FROM journal WHERE user_id = %s GROUP BY mood", (self.app.user_id,))
        moods = [r[0] for r in rows]
        counts = [r[1] for r in rows]
        
        if not rows:
            lbl = ctk.CTkLabel(self.chart_frame, text="No journal entries logged yet.\nWrite in your thought journal to see analytical charts here!", font=("Helvetica", 14), text_color=text_secondary)
            lbl.pack(pady=60)
            return
            
        if matplotlib_available:
            fig = Figure(figsize=(6, 4), dpi=100)
            is_dark = ctk.get_appearance_mode() == "Dark"
            bg_color_hex = "#151E2E" if is_dark else "#FFFFFF"
            text_color_hex = "#F1F5F9" if is_dark else "#0F172A"
            
            fig.patch.set_facecolor(bg_color_hex)
            
            ax = fig.add_subplot(111)
            ax.set_facecolor(bg_color_hex)
            
            colors = ["#2D6A4F", "#52B788", "#74C69D", "#95D5B2", "#D8F3DC", "#B7E4C7"]
            wedges, texts, autotexts = ax.pie(
                counts, 
                labels=moods, 
                autopct='%1.1f%%', 
                colors=colors[:len(moods)],
                textprops=dict(color=text_color_hex)
            )
            
            ax.set_title("Logged Mood Distribution", color=text_color_hex, fontname="Helvetica", fontsize=14, fontweight="bold")
            
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            lbl = ctk.CTkLabel(self.chart_frame, text="Matplotlib not installed. Showing raw statistics:\n", font=("Helvetica", 14), text_color=text_primary)
            lbl.pack(pady=(20, 10))
            for mood, count in zip(moods, counts):
                m_lbl = ctk.CTkLabel(self.chart_frame, text=f"• {mood.title()}: {count} entry/entries", font=("Helvetica", 13), text_color=text_secondary)
                m_lbl.pack(pady=2)

if __name__ == "__main__":
    app = SarathiAdvancedApp()
    app.mainloop()
