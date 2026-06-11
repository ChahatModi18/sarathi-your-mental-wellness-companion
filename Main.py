import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext, ttk, filedialog
from textblob import TextBlob
import mysql.connector
from datetime import datetime, timedelta, date
import re, random, csv, os, math, json
import webbrowser
# Optional for stats window
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Import the PDF viewer library
try:
    from tkinterPdfViewer import tkinterPdfViewer as pdf
except ImportError:
    # Dummy class if tkinterPdfViewer is not installed
    class DummyPdfViewer:
        def ShowPdf(self):
            return self
        def pdf_view(self, master, pdf_location, width, height):
            tk.Label(master, text="PDF Viewer not available. Please install 'tkinterPdfViewer'.", fg="red").pack()
            return tk.Frame(master)
    pdf = DummyPdfViewer()

from PIL import Image, ImageTk
import smtplib
from email.message import EmailMessage

# Optional machine learning helpers used for sentiment and crisis detection
try:
    import wellness_ml
except Exception as e:
    wellness_ml = None
    print(f"[ML INFO] wellness_ml import failed on startup: {e}")

# --- REQUIRED IMPORT ---
try:
    from tkcalendar import DateEntry
except ImportError:
    # If tkcalendar is missing, we define a dummy to prevent crashes on startup
    try:
        messagebox.showerror("Import Error", "The 'tkcalendar' library is required for the Date Picker feature. Please install it using: pip install tkcalendar")
    except Exception:
        # If messagebox is not usable (early import), ignore
        pass
    class DateEntry(tk.Entry):
        def __init__(self, master=None, **kw):
            super().__init__(master, **kw)
            self.insert(0, "YYYY-MM-DD")

# ------------------ PASSWORD HASHING HELPER ------------------
import hashlib

def hash_password(password, username=""):
    salt = "sarathi_secure_pepper_1294_$"
    combined = password + salt + username.lower()
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

# ------------------ OPENAI CLIENT SETUP ------------------
import os
from openai import OpenAI

openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    try:
        openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    except Exception as e:
        print(f"[OpenAI Info] Initialization failed: {e}")

# ------------------ DATABASE SETUP ------------------
conn = None
cursor = None
try:
    # Use environment variables for sensitive data
    db_password = os.environ.get("chahat")
    if not "chahat":
        pass

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        # Using a dummy password to allow non-set environment variable run
        password=os.environ.get("chahat", "chahat")
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS sarathi_sih_db")
    cursor.execute("USE sarathi_sih_db")

    # --- USER TABLE (Existing) ---
    cursor.execute("""
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

    # Ensure users has email column if table already existed (safe ALTER)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) DEFAULT NULL")
        conn.commit()
    except mysql.connector.Error:
        pass

    # --- NEW: COUNSELOR TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counselors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            online_status BOOLEAN DEFAULT FALSE,
            last_login DATETIME
        )
    """)
    # Add a default counselor for demonstration if the table is empty
    cursor.execute("SELECT COUNT(*) FROM counselors")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO counselors (username, password, specialization) VALUES (%s, %s, %s)", ('counselor1', hash_password('pass123', 'counselor1'), 'General Wellness'))
        cursor.execute("INSERT INTO counselors (username, password, specialization) VALUES (%s, %s, %s)", ('dr.sharma', hash_password('counsellor', 'dr.sharma'), 'Anxiety/Stress'))
        conn.commit()

    # --- NEW: BOOKINGS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            counselor_id INT,
            booking_time DATETIME NOT NULL,
            slot_id INT DEFAULT NULL,
            specialization_requested VARCHAR(100),
            reason TEXT,
            status VARCHAR(50) DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (counselor_id) REFERENCES counselors(id)
        )
    """)

    # Ensure bookings has slot_id column for linking to counselor_slots (safe ALTER)
    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN slot_id INT DEFAULT NULL")
        conn.commit()
    except mysql.connector.errors.ProgrammingError:
        pass

    # --- NEW: COUNSELOR SLOTS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counselor_slots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            counselor_id INT NOT NULL,
            slot_time DATETIME NOT NULL,
            available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (counselor_id) REFERENCES counselors(id)
        )
    """)

    # --- ADMIN HACK (Admin is a regular user with a specific username/ID) ---
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "adminpass"
    cursor.execute("SELECT id FROM users WHERE username = %s", (ADMIN_USERNAME,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD, ADMIN_USERNAME)))
        conn.commit()
    # --- END ADMIN HACK ---

    # --- EXISTING TABLES ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(100),
            mood VARCHAR(100),
            thought TEXT,
            shlok TEXT,
            shlok_meaning TEXT,
            timestamp DATETIME,
            risk_level VARCHAR(50) DEFAULT 'low',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_cycles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            start_date DATE,
            end_date DATE,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_resources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(100),
            resource_type VARCHAR(50),
            title VARCHAR(255),
            description TEXT,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            timestamp DATETIME,
            tool_name VARCHAR(50),
            score INT,
            risk_level VARCHAR(50),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    # Fix & Enhancement: Ensure user columns are present (repeated from original)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN journal_streak INT DEFAULT 0")
        conn.commit()
    except mysql.connector.errors.ProgrammingError: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_journal_date DATE DEFAULT NULL")
        conn.commit()
    except mysql.connector.errors.ProgrammingError: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN mindful_points INT DEFAULT 0")
        conn.commit()
    except mysql.connector.errors.ProgrammingError: pass
    # --- END FIX & ENHANCEMENT ---

    conn.commit()
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Failed to connect to MySQL database: {err}")
    conn = None
except ValueError as verr:
    messagebox.showerror("Configuration Error", str(verr))
    conn = None

# ------------------ STATIC DATA & HELPER FUNCTIONS ------------------

# ----------------- ENHANCED CRISIS KEYWORDS (Mental & Physical) -----------------
CRISIS_KEYWORDS = [
    r"\bsuicid(?:e|al)\b", r"\bkill (?:myself|me)\b", r"\bend (?:my )?life\b",
    r"\boverdos(?:e|ing)\b", r"\bwant to die\b", r"\bcan'?t go on\b",
    r"\bworthless\b", r"\bnot worth living\b", r"\bcut(ting)? myself\b",
    r"\bharm myself\b", r"\btake my life\b", r"\bend it all\b",
    # Physical Health Crisis Keywords
    r"\bsevere chest pain\b", r"\bcan'?t breathe\b", r"\buncontrollable bleeding\b",
    r"\bhaving a stroke\b", r"\bsudden numbness\b", r"\bcollapsed\b",
    r"\bpoisoning\b", r"\bchoking\b", r"\bheart attack\b", r"\bhigh fever\b",
    r"\bunconsciousness\b", r"\bmajor accident\b"
]

# --- PEER FORUM MODERATION ENHANCEMENT ---
FORUM_BLOCK_KEYWORDS = [
    r"\bidiot\b", r"\bstupid\b", r"\bhate you\b", r"\bfailur[e]?\b",
    r"\bruin[s]?(?: my)? life\b"
]

# PHQ-9 Questions and Scoring (Conceptual for ScreeningsFrame)
PHQ9_QUESTIONS = [
    "1. Little interest or pleasure in doing things?",
    "2. Feeling down, depressed, or hopeless?",
    "3. Trouble falling or staying asleep, or sleeping too much?",
    "4. Feeling tired or having little energy?",
    "5. Poor appetite or overeating?",
    "6. Feeling bad about yourself—or that you are a failure or have let yourself or your family down?",
    "7. Trouble concentrating on things, such as reading the newspaper or watching television?",
    "8. Moving or speaking so slowly that other people could have noticed? Or the opposite—being so fidgety or restless that you have been moving around a lot more than usual?",
    "9. Thoughts that you would be better off dead, or of hurting yourself in some way?"
]
GAD7_QUESTIONS = [
    "1. Feeling nervous, anxious, or on edge?",
    "2. Not being able to stop or control worrying?",
    "3. Worrying too much about different things?",
    "4. Trouble relaxing?",
    "5. Being so restless that it's hard to sit still?",
    "6. Becoming easily annoyed or irritable?",
    "7. Feeling afraid as if something awful might happen?"
]

# Scoring maps (Min-Max score)
PHQ9_SCORES = {
    (0, 4): "Minimal Depression (Low Risk)",
    (5, 9): "Mild Depression (Medium Risk)",
    (10, 14): "Moderate Depression (Medium-High Risk)",
    (15, 19): "Moderately Severe Depression (High Risk)",
    (20, 27): "Severe Depression (Very High Risk)"
}
GAD7_SCORES = {
    (0, 4): "Minimal Anxiety (Low Risk)",
    (5, 9): "Mild Anxiety (Medium Risk)",
    (10, 14): "Moderate Anxiety (Medium-High Risk)",
    (15, 21): "Severe Anxiety (High Risk)"
}

HELPLINES = {
    "IN": {
        "mental_health": [
            {"name": "Tele MANAS (24/7)", "number": "14416 / 1-800-891-4416"},
            {"name": "Vandrevala Foundation (24/7)", "number": "+91 9999666555"},
            {"name": "KIRAN Helpline (24/7)", "number": "1800-599-0019"},
        ],
        "emergency": "112"
    },
    "DEFAULT": {
        "mental_health": [
            {"name": "Local Crisis Line", "number": "Please check local resources or emergency services"}
        ],
        "emergency": "Call your local emergency number"
    }
}

# --- MINDFUL POINTS (MP) REWARD TIERS ---
MP_REWARD_TIERS = {
    50: "Beginner Balancer",
    200: "Mindful Contributor",
    500: "Zen Seeker",
    1000: "Emotional Navigator",
}
STREAK_BADGES = {
    7: "7-Day Consistent",
    30: "Monthly Habit",
    100: "Triple Digit Dedication"
}

# --- MOOD-BASED MINI-GOALS ---
MINI_GOALS = {
    "anxious": {"goal": "Complete a 3-minute breath exercise (e.g., Square Breathing).", "reward": 25},
    "stressed": {"goal": "Do one thing on your to-do list for 15 minutes.", "reward": 20},
    "sad": {"goal": "Reach out to one trusted friend or family member via text.", "reward": 15},
    "angry": {"goal": "Do 10 minutes of light physical activity (e.g., stretching, brisk walk).", "reward": 30},
}
# (Uplifting messages, thought_specific_reframes, mood_specific_reframes, mood_keywords, MOOD_COLORS, shloks remain the same as previous response)

uplifting_messages = [
    "Every day is a new beginning.",
    "You are stronger than you think.",
    "This too shall pass.",
    "Believe in yourself and all that you are.",
    "You are not alone in this journey of life.",
    "Small steps lead to big changes.",
    "Be kind to yourself today; you are doing your best.",
    "Your story isn't over yet. There are brighter chapters ahead.",
    "You possess incredible resilience. Draw on that power.",
    "Progress, not perfection. Celebrate the small victories.",
    "The world is better because you are in it.",
    "You have survived every challenge so far. You can handle this one too.",
    "Rest when you need to, but never give up on yourself.",
    "Just take the next breath. That is enough for this moment.",
    "Let go of what you can't control, and focus on your inner peace.",
    "Find an anchor: a friend, a memory, or a gentle truth.",
    "Your worth is inherent; it's not tied to your productivity or feelings.",
    "A moment of peace can be found in a focused breath.",
    "Hope is a feeling that must be practiced daily. Start now."
]

thought_specific_reframes = {
    "no one cares": "This too shall pass. Believe in yourself and all that you are.",
    "i am useless": "You have value and can contribute positively every day.",
    "i am worthless": "Remember, your existence matters and you are important.",
    "i can't do anything right": "Mistakes are part of learning, and you are improving every day.",
    "i hate myself": "It's okay to feel this way, but you are worthy of love and care.",
    "nobody loves me": "You are loved in ways you may not see yet, and people care about you.",
    "i am a failure": "Failing is just a step towards success. You are growing stronger.",
    "everything is hopeless": "This feeling will pass. Focus on small steps forward.",
    "i am not good enough": "You are enough as you are, and you have unique strengths.",
    "i am alone": "Being alone sometimes is okay, but support and friendship are available to you.",
    "life is unfair": "Even in challenges, you have the power to grow and create positive change.",
    "i am anxious": "Take a deep breath; you are capable of handling this moment.",
    "i am depressed": "It's okay to feel down. You are taking steps to care for yourself.",
    "i feel rejected": "Rejection is part of life, but it doesn't define your worth.",
    "i can't handle this": "You are stronger than you think, and you can take it one step at a time.",
    "i am overwhelmed": "Focus on one thing at a time; you are capable of handling it.",
    "i am stressed": "Take small steps and breathe; things will get better.",
    "i am tired": "Rest will restore your energy and help you move forward.",
    "i feel insecure": "You are unique, valuable, and have qualities that matter.",
    "i feel hopeless": "Even small actions can lead to positive change; hope is always possible."
}

mood_specific_reframes = {
    "sad": [("i'm useless", "I have worth and am learning."), ("i am so sad", "It's okay to feel sad. What is one small thing you can do to be kind to yourself?")] ,
    "anxious": [("i can't do this", "I can take it step by step."), ("i am scared", "It's okay to feel scared. You are safe in this moment. Breathe.")],
    "angry": [("i hate everything", "I acknowledge my feelings but choose calmer actions."), ("i am so angry", "This feeling is valid. How can I release this energy constructively?")] ,
    "stressed": [("too much work", "I can break tasks into small steps."), ("i am so stressed", "Stress is a sign that I care. I will handle one task at a time.")] ,
    "lonely": [("no one cares", "I can reach out, connection is possible."), ("i am so lonely", "Connection is a choice. I can reach out to one person today.")] ,
    "overwhelmed": [("it's too much", "I can handle one step at a time."), ("i feel overwhelmed", "This is a temporary state. I can prioritize one thing to focus on right now.")] ,
    "pessimistic": [("nothing will ever change", "Change starts with small actions. What is one small thing I can improve today?")],
    "discouraged": [("i feel like giving up", "Progress, not perfection. Every small step forward is a victory.")],
    "very_sad": [("life is pointless", "Your life has meaning and purpose. Your presence is a gift to the world.")],
    "devastated": [("i am broken", "You are resilient. Healing is a journey, and you are capable of it.")],
    "restless": [("i can't sit still", "This energy can be channeled. What is one creative or physical activity I can do?")]
}

mood_keywords = {
    "positive": ["positive", "good", "great", "uplifted", "cheerful", "joyful", "excited", "enthusiastic", "motivated", "inspired", "optimistic", "hopeful", "content", "satisfied", "fulfilled", "at peace"],
    "very_happy": ["overjoyed", "elated", "thrilled", "delighted", "blissful", "euphoric", "rapturous", "exuberant", "jubilant", "radiant", "smiling", "glad", "joyous", "exultant", "lighthearted", "surprised"],
    "negative": ["negative", "bad", "awful", "downhearted", "depressed", "disappointed", "frustrated", "unhappy", "dismayed", "discouraged", "demotivated", "hopeless", "despondent", "gloomy", "downcast", "disheartened", "broken", "shattered", "can't do","defeated","worthless","inedequate","failure","incompetent","useless","unloved","unwanted","unworthy","pathetic"],
    "pessimistic": ["pessimistic", "hopeless", "doubtful", "cynical", "skeptical", "defeated", "resigned", "disillusioned", "disappointed", "unenthusiastic", "unmotivated", "unfulfilled", "dispirited", "downcast", "despondent","derogatory","dismissive","doubtful","gloomy","negative"],
    "optimistic": ["optimistic", "hopeful", "confident", "looking forward", "positive", "upbeat", "encouraged", "enthusiastic", "motivated", "inspired", "expectant", "assured", "buoyant", "assured", "encouraged", "enthusiastic", "upbeat"],
    "neutral": ["neutral", "okay", "fine", "meh", "indifferent", "unmoved", "unaffected", "apathetic", "dispassionate", "unbiased", "objective", "calm", "steady", "balanced", "unemotional", "unperturbed", "unfazed", "unflustered"],
    "overwhelmed": ["overwhelmed", "too much", "can't handle", "exhausted", "stressed", "burned out", "overloaded", "swamped", "flooded", "drowning", "overworked", "strained", "pressured", "burdened", "weighed down", "frazzled", "nostalgic","confused"],
    "anxious": ["anxious", "nervous", "worried", "scared", "stressed", "tense", "fearful", "uneasy", "overthinking", "panic", "jittery", "restless", "on edge", "apprehensive", "fidgety", "agitated", "concerned", "distressed", "troubled"],
    "peaceful": ["peaceful", "calm", "serene", "relaxed", "tranquil", "at ease", "untroubled", "content", "harmonious", "balanced", "composed", "unperturbed", "unfazed", "unflustered", "unruffled", "placid", "still", "quiet","restful"," soothing","pacified"," tranquilized"],
    "restless": ["restless", "fidgety", "uneasy", "bored", "jittery", "antsy", "impatient", "agitated", "unsettled", "discontented", "unfulfilled", "disquieted", "unrestful", "unpeaceful", "unrelaxed"," edgy"," nervous","anxious"," unsettled"," uneasy","impatient"," agitated"," disturbed"," pertubed"],
    "very_sad": ["heartbroken", "devastated", "hopeless", "crying", "lonely", "empty", "despairing", "miserable", "dejected", "downcast", "disheartened", "dispirited", "dismal", "gloomy", "forlorn", "woeful", "sorrowful", "grief-stricken"],
    "sad": ["sad", "down", "upset", "low", "disappointed", "unhappy", "blue", "melancholy", "sorrowful", "depressed", "disheartened", "dispirited", "dismal", "gloomy", "forlorn", "woeful", "sorrowful", "grief-stricken", "downcast", "despondent", "mournful"," unhappy"," downhearted"," heartbroken"," tearful"," regretful"," remorseful"," desolate"," bereaved"],
    "discouraged": ["discouraged", "demotivated", "frustrated", "let down", "disheartened", "dispirited", "unmotivated", "downcast", "dejected", "disappointed", "unfulfilled"," disc"," dismayed","dillusioned","disenchanted"," discontented"," disillusioned"," disenchanted"," discontented"," disheartened"," downcast"," dejected"," demoralized"," dispirited"," unmotivated"],
    "devastated": ["devastated", "shattered", "crushed", "broken", "heartbroken", "desolate", "despairing", "distraught", "overwhelmed", "sorrowful", "grief-stricken", "mournful"," bereaved"," inconsolable"," anguished"," forlorn"," woeful"," despondent"," downcast"," disconsolate"," disheartened"," brokenhearted"],
    "ecstatic": ["ecstatic", "blissful", "euphoric", "rapturous", "elated", "overjoyed", "thrilled", "exhilarated", "exuberant", "jubilant", "radiant", "happy vala emotional"],
    "content": ["content", "satisfied", "fulfilled", "at peace", "pleased", "gratified", "happy", "serene", "untroubled", "complacent", "self-satisfied", "pleased", "gratified","fulfilled","at peace"," contented"],
    "angry": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "enraged", "infuriated", "livid", "exasperated", "indignant", "outraged", "incensed", "resentful","cross","irate","wrathful","heated","fuming","seething","raging","stormy","tempestuous","volatile","fierce","ferocious","vicious","savage","belligerent"],
    "happy": ["happy","awesome","fabulous","joyful", "glad", "smiling", "cheerful", "content", "satisfied", "pleased", "delighted", "jovial", "jubilant", "radiant", "exuberant"," merry","sunny","lighthearted","elated","thrilled","euphoric","jocund"],
    "grateful": ["grateful", "thankful", "blessed", "appreciative", "indebted", "obliged","pleased" , " content","satisfied","joyful","happy","cheerful","delighted","jovial","jubilant","radiant","exuberant","thankful","blessed","appreciative","indebted","obliged","pleased","content","satisfied"],
    "hopeful": ["hopeful", "looking forward", "optimistic", "confident", "expectant", "assured", "buoyant", "encouraged", "enthusiastic", "inspired", "positive", "upbeat","expectant"]
}

MOOD_COLORS = {
    "positive": {"primary": "#FFD300", "calm": "#AEE1F9"},   # Bright Yellow → Soft Sky Blue
    "very_happy": {"primary": "#FF914D", "calm": "#6BCBCE"}, # Vibrant Orange → Cool Teal
    "negative": {"primary": "#B23A48", "calm": "#9BF6FF"},   # Sharp Crimson → Seafoam Green
    "pessimistic": {"primary": "#5A189A", "calm": "#FEC89A"},# Dark Purple → Pastel Peach
    "optimistic": {"primary": "#8FD694", "calm": "#CDB4DB"}, # Spring Green → Lavender Mist
    "neutral": {"primary": "#6C757D", "calm": "#FFD56B"},    # Grey-Blue → Golden Yellow
    "overwhelmed": {"primary": "#D1495B", "calm": "#C3B1E1"},# Rusty Red → Cool Lilac
    "anxious": {"primary": "#7209B7", "calm": "#FEC89A"},    # Deep Violet → Soft Peach
    "peaceful": {"primary": "#87CEEB", "calm": "#FFD1BA"},   # Serene Blue → Sunset Peach
    "restless": {"primary": "#FF6F61", "calm": "#A8E6CF"},   # Energetic Coral → Mint Green
    "very_sad": {"primary": "#1D3557", "calm": "#FF9B85"},   # Deep Navy → Warm Coral
    "sad": {"primary": "#457B9D", "calm": "#FFB4A2"},         # Muted Blue → Soft Coral Pink
    "discouraged": {"primary": "#8D6E63", "calm": "#B8F2E6"},# Dusky Brown → Aqua Green
    "devastated": {"primary": "#2B2D42", "calm": "#F4A261"}, # Charcoal Blue → Warm Amber
    "ecstatic": {"primary": "#9D4EDD", "calm": "#B5EAEA"},   # Bright Violet → Powder Blue
    "content": {"primary": "#A7C957", "calm": "#F7A9A8"},    # Sage Green → Rose Quartz
    "angry": {"primary": "#E63946", "calm": "#90E0EF"},       # Fiery Red → Cool Aqua
    "happy": {"primary": "#FFCB77", "calm": "#A0CED9"},       # Warm Golden → Soft Blue
    "grateful": {"primary": "#FF6F91", "calm": "#A8E6CF"},   # Warm Pink → Gentle Mint
    "hopeful": {"primary": "#06D6A0", "calm": "#CDB4DB"}      # Fresh Green → Lavender Mist
}

RELAXING_COLOR = "#F0F0F0" # Neutral background if mood is missing a key

all_moods = list(mood_keywords.keys())

shloks = {
    "positive": [("कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।", "You have a right to perform your duties, but never to the fruits of those actions.")],
    "negative": [("श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।", "It is better to fail in one's own duty than to succeed in another’s.")],
    "neutral": [("योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।", "Perform your duty equipoised, abandoning all attachment to success or failure.")],
    "anxious": [("मा ते संगोऽस्त्वकर्मणि。", "Do not be attached to inaction.")],
    "peaceful": [("शान्तिमाप्नोति नैष्ठिकीम्。", "One attains supreme peace.")],
    "angry": [("क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः。", "From anger comes delusion, from delusion the loss of memory.")],
    "spin_message": [("सर्वं खल्विदं ब्रह्म।", "All this is indeed Brahman. (A reminder of the interconnectedness of all things.)")],
    "very_happy": [("न हि कश्चित्क्षणमपि जातु तिष्ठत्यकर्मकृत्。", "No one can remain without action even for a moment."),("आत्मौपम्येन सर्वत्र समं पश्यति योऽर्जुन。", "That yogi sees all beings with an equal vision, rejoicing in the welfare of all.")],
    "pessimistic": [("मात्मानं अवसादयेत्。", "Do not allow yourself to sink into despair."),("न हि कल्याणकृत्कश्चिद् दुर्गतिं तात गच्छति。", "One who does good, My friend, never comes to grief.")],
    "optimistic": [("मां अनन्याश्चिन्तयन्तो ये जनाः पर्युपासते。", "Those who worship me with unwavering devotion — I carry what they lack."),("न हि कल्याणकृत्कश्चिद् दुर्गतिं taata गच्छति。", "One who does good, My friend, never comes to grief.")],
    "overwhelmed": [("समं सर्वेषु भूतेषु तिष्ठन्तं परमेश्वरम्。", "See the Lord equally present in all beings."),("युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।", "Balance in eating, recreation, and actions brings peace.")],
    "restless": [("चञ्चलं हि मनः कृष्ण", "The mind is restless, turbulent, obstinate, and very strong."),("असंशयं महाबाहो मनो दुर्निग्रहं चलम्。", "Undoubtedly, the mind is restless and hard to control.")],
    "very_sad": [("न जायते म्रियते वा कदाचित्。", "The soul is eternal; it neither dies nor is born. — BG 2.20"),("सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।", "Even the darkest night will end, and the sun will rise. — BG 18.66")],
    "sad": [(" जातस्य हि ध्रुवो मृत्युर्ध्रुवं जन्म मृतस्य च。", "Do not grieve for the living or the dead. — BG 2.27"),("नेहाभिक्रमनाशोऽस्ति प्रत्यवायो न विद्यते。", "Even a little progress on this path protects one from great fear. — BG 2.40")],
    "discouraged": [("यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता。", "Just as a lamp in a windless place does not flicker, remain steady in the self."),("दुःखेष्वनुद्विग्नमनाः सुखेषु विगतस्पृहः", "One who is undisturbed in sorrow and free from desire in happiness is wise.")],
    "devastated": [("नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः。", "Weapons do not cut the soul, fire does not burn it."),("अजो नित्यः शाश्वतोऽयं पुराणो。", "The soul is unborn, eternal, ever-existing, and primeval.")],
    "ecstatic": [("हृष्यन्ति पश्यतां सर्वे लोकाः。", "All worlds rejoice beholding the divine form."),("विस्मयोऽस्मि महात्मन्。", "I am filled with wonder, O great-souled one.")],
    "content": [("सन्तुष्टः सततं योगी यथा लभते तिष्ठति。", "The yogi who is always content remains steady in whatever comes."),("आत्मरतिरेव स्यात् आत्मतृप्तश्च मानवः。", "The person who rejoices in the self and is satisfied in the self is truly content.")],
    "angry": [("क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः。", "From anger comes delusion, from delusion the loss of memory.")],
    "happy": [("सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ。", "Treating happiness and distress, gain and loss, victory and defeat alike."),("सुखं तु नित्यं सुखिनः सदा", "The one who is always happy is truly blessed.")],
    "grateful": [("सन्तुष्टः सततं योगी यथा लभते तिष्ठति。", "The yogi who is always content remains steady in whatever comes."),("आत्मरतिरेव स्यात् आत्मतृप्तश्च मानवः。", "The person who rejoices in the self and is satisfied in the self is truly content.")],
    "hopeful": [("मां अनन्याश्चिन्तयन्तो ये जनाः पर्युपासते。", "Those who worship me with unwavering devotion — I carry what they lack."),("न हि कल्याणकृत्कश्चिद् दुर्गतिं taata गच्छति。", "One who does good, My friend, never comes to grief.")]
}

# New in-memory data for the Peer Support Forum to simulate a database
peer_support_posts = [
    {
        "title": "How do you handle academic stress?",
        "user": "Anonymous Student",
        "category": "Student Life",
        "message": "I often feel overwhelmed by deadlines, exams, and the pressure to perform. Does anyone have a practical routine or mindset tip that helped them manage academic stress?",
        "answers": 4,
        "views": 135,
    },
    {
        "title": "Balancing work and personal life is so tough.",
        "user": "Anonymous Professional",
        "category": "Professional Work",
        "message": "Work hours are so long lately, and I struggle to switch off when I get home. How do you maintain personal time without feeling guilty?",
        "answers": 2,
        "views": 98,
    },
    {
        "title": "I'm feeling really lonely on campus, anyone else?",
        "user": "Anonymous Student",
        "category": "Student Life",
        "message": "I sit in classes and feel disconnected from everyone, even though I want friends. Has anyone found ways to build meaningful connections in college?",
        "answers": 5,
        "views": 146,
    },
    {
        "title": "Tips for better sleep when anxious?",
        "user": "Anonymous User",
        "category": "Physical Health",
        "message": "My mind races at night and I can't sleep. I want healthy habits, not medication. What calming routines have helped you?",
        "answers": 3,
        "views": 112,
    },
    {
        "title": "What's the best way to talk to a friend who is struggling?",
        "user": "Anonymous Peer",
        "category": "Mental Health",
        "message": "A close friend is going through a hard time, but I don't know whether to ask directly or give them space. How can I support them without making things worse?",
        "answers": 6,
        "views": 158,
    },
    {
        "title": "Dealing with chronic pain and mental health.",
        "user": "Anonymous User",
        "category": "Physical Health",
        "message": "Living with pain has made me feel exhausted and low. How do you cope on days when both your body and your mind hurt?",
        "answers": 2,
        "views": 89,
    },
    {
        "title": "Just started my first job, feeling overwhelmed.",
        "user": "Anonymous Professional",
        "category": "Professional Work",
        "message": "The transition from college to a full-time role has been harder than expected. Any advice for managing new expectations and staying calm?",
        "answers": 3,
        "views": 103,
    },
    {
        "title": "How to stay motivated for college applications?",
        "user": "Anonymous Student",
        "category": "Student Life",
        "message": "I keep procrastinating on applications and feel like I can't finish anything. What helped you stay motivated through the process?",
        "answers": 1,
        "views": 74,
    },
    {
        "title": "Body positivity and self-esteem issues.",
        "user": "Anonymous User",
        "category": "Mental Health",
        "message": "I compare myself to others constantly and it impacts my confidence. How can I build a healthier relationship with my body?",
        "answers": 4,
        "views": 121,
    },
]
peer_support_categories = ["All", "Student Life", "Professional Work", "Physical Health", "Mental Health"]

# Full list of moods for UI components
all_moods = list(mood_keywords.keys())

def detect_text_context(text):
    text_lower = text.lower()
    context_mapping = {
        "Academic Stress": ["exam", "assignment", "college", "university", "semester", "grades", "deadline", "study", "class", "tuition"],
        "Career / Work": ["job", "work", "office", "boss", "career", "promotion", "interview", "salary", "deadline", "burnout"],
        "Relationships": ["relationship", "partner", "girlfriend", "boyfriend", "family", "friend", "marriage", "dating", "breakup"],
        "Health & Body": ["health", "pain", "illness", "doctor", "sleep", "diet", "exercise", "body", "physical"],
        "Financial Pressure": ["money", "debt", "loan", "rent", "bills", "savings", "budget", "finance"],
        "Self-Esteem": ["confidence", "self-worth", "esteem", "worthless", "compare", "body image", "appearance"],
        "Loss & Grief": ["loss", "grief", "bereavement", "death", "lost", "heartbroken"],
        "General Wellbeing": ["stress", "anxious", "sad", "happy", "overwhelmed", "angry", "tired"]
    }
    for label, keywords in context_mapping.items():
        if any(word in text_lower for word in keywords):
            return label
    return "General Wellbeing"


def get_sentiment_enhanced(text):
    """Enhanced sentiment analysis to handle negation, sarcasm, and multiple moods using OpenAI if available."""
    global openai_client
    context = detect_text_context(text)

    # 1. Attempt using OpenAI if configured
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a compassionate psychological sentiment analysis assistant. "
                            "Analyze the user's journal text with attention to mood and situation. "
                            "Output a JSON object containing: "
                            "'mood' (one of: positive, very_happy, negative, pessimistic, optimistic, neutral, overwhelmed, anxious, peaceful, restless, very_sad, sad, discouraged, devastated, ecstatic, content, angry, happy, grateful, hopeful), "
                            "'context' (a short label like Academic Stress, Career / Work, Relationships, Health & Body, Financial Pressure, Self-Esteem, Loss & Grief, General Wellbeing), "
                            "'polarity' (float from -1.0 to 1.0), and 'subjectivity' (float from 0.0 to 1.0)."
                        )
                    },
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                timeout=5
            )
            import json
            data = json.loads(response.choices[0].message.content)

            mood = data.get("mood", "").lower()
            if mood not in mood_keywords:
                mood = "neutral"

            context = data.get("context", "").strip() or context
            polarity = float(data.get("polarity", 0.0))
            subjectivity = float(data.get("subjectivity", 0.0))

            shlok = random.choice(shloks.get(mood, [("Be present and mindful.", "— Unknown")]))
            return mood, context, shlok, polarity, subjectivity
        except Exception as e:
            print(f"[OpenAI Warning] Sentiment analysis failed, using fallback: {e}")

    # 2. TextBlob Fallback (Preserves original features)
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    text_lower = text.lower()

    # Predict mood using custom text classification neural network
    import wellness_ml
    overall_mood, _ = wellness_ml.predict_mood(text)

    if overall_mood == "neutral":
        for mood_type, keywords in mood_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                overall_mood = mood_type
                break

        if overall_mood == "neutral" or overall_mood is None:
            if polarity >= 0.9:
                overall_mood = "ecstatic"
            elif polarity >= 0.75:
                overall_mood = "very_happy"
            elif polarity >= 0.55:
                overall_mood = "optimistic"
            elif polarity >= 0.5:
                overall_mood = "hopeful"
            elif polarity >= 0.45:
                overall_mood = "grateful"
            elif polarity >= 0.4:
                overall_mood = "happy"
            elif polarity >= 0.35:
                overall_mood = "content"
            elif polarity >= 0.3:
                overall_mood = "peaceful"
            elif polarity >= 0.15:
                overall_mood = "positive"
            elif polarity <= -0.9:
                overall_mood = "devastated"
            elif polarity <= -0.75:
                overall_mood = "very_sad"
            elif polarity <= -0.55:
                overall_mood = "pessimistic"
            elif polarity <= -0.4:
                overall_mood = "angry"
            elif polarity <= -0.35:
                overall_mood = "discouraged"
            elif polarity <= -0.3:
                overall_mood = "anxious"
            elif polarity <= -0.25:
                overall_mood = "overwhelmed"
            elif polarity < -0.2:
                overall_mood = "sad"
            elif polarity <= -0.15:
                overall_mood = "negative"
            else:
                overall_mood = "neutral"

    shlok = random.choice(shloks.get(overall_mood, [("Be present and mindful.", "— Unknown")]))
    return overall_mood, context, shlok, polarity, subjectivity

def _matches_any(patterns, text):
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False

def _choose_helplines(locale="DEFAULT"):
    """Choose appropriate helplines based on the locale."""
    return HELPLINES.get(locale.upper(), HELPLINES["DEFAULT"])

def create_crisis_message(locale="IN"):
    """Generates the structured crisis message based on the user's request."""

    # Use the appropriate helpline data based on the locale
    helplines = _choose_helplines(locale)

    # Extracting necessary numbers
    emergency_line = helplines.get("emergency", "Call local emergency")
    mh_lines = helplines.get("mental_health", [])

    # The base message structure
    message = (
        "🚨 URGENT CRISIS ALERT 🚨\n"
        "\n"
        "Your recent entries suggest you may be in distress. Please reach out for immediate, "
        "confidential support. You are not alone.\n"
        "\n"
        "---------------------------------------------------\n"
        f"## 📞 CRISIS & MENTAL HEALTH SUPPORT ({locale.upper()})\n"
        "---------------------------------------------------\n"
        f"| Service | Number | Availability |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **National Emergency** | **{emergency_line}** | **Life-Threatening Situations** |\n"
    )

    if mh_lines:
        for h in mh_lines:
            message += f"| {h['name']} | **{h['number']}** | Emotional/Crisis Counseling |\n"

    # Add the universal reassurance and coping text provided by the user
    message += (
        "---------------------------------------------------\n"
        "## 🫂 Reassurance & Consoling\n"
        "Please read this slowly and internalize it:\n"
        "• **You are safe in this moment.** Focus on finding ground beneath your feet.\n"
        "• **This intense feeling is temporary.** Your emotional waves will pass.\n"
        "• **Your life is precious.** Hold on just a little longer.\n\n"
        "## 💡 Immediate Coping Suggestions\n"
        "1.  **5-4-3-2-1 Grounding:** Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, and 1 you taste.\n"
        "2.  **Square Breathing:** Inhale 4, Hold 4, Exhale 4, Hold 4. Repeat 3 times.\n"
        "3.  **Sensory Shift:** Splash cold water on your face or hold an ice cube.\n"
        "4.  **Reach Out:** Call a trusted person immediately, even if it's just to distract you.\n"
        "5.  **Safe Space Visualization:** Close your eyes and picture a place where you feel completely safe.\n\n"
    )
    return message


def send_email_confirmation(to_email, subject, body):
    """Send an email via SMTP using environment configuration. Returns (success, message)."""
    # Try to load settings from local config file first, then fall back to env vars
    cfg = load_smtp_config()
    smtp_host = cfg.get('host') or os.environ.get('SMTP_HOST')
    if not smtp_host:
        return False, "SMTP not configured"
    try:
        smtp_port = int(cfg.get('port') or os.environ.get('SMTP_PORT', '587'))
    except Exception:
        smtp_port = 587
    smtp_user = cfg.get('user') or os.environ.get('SMTP_USER')
    smtp_pass = cfg.get('pass') or os.environ.get('SMTP_PASS')
    from_addr = cfg.get('from') or os.environ.get('EMAIL_FROM', smtp_user)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_email
    msg.set_content(body)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except Exception:
                pass

        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)

        server.send_message(msg)
        server.quit()
        return True, 'Email sent'
    except Exception as e:
        return False, str(e)


# ----------------- SMTP CONFIG & EMAIL TEMPLATES (Local Config File) -----------------
SMTP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'smtp_config.json')

def load_smtp_config():
    try:
        if os.path.exists(SMTP_CONFIG_PATH):
            with open(SMTP_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f).get('smtp', {})
    except Exception:
        pass
    return {}

def save_smtp_config(cfg: dict):
    data = {}
    try:
        if os.path.exists(SMTP_CONFIG_PATH):
            with open(SMTP_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
    except Exception:
        data = {}
    data['smtp'] = cfg
    try:
        with open(SMTP_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

def load_email_templates():
    try:
        if os.path.exists(SMTP_CONFIG_PATH):
            with open(SMTP_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('templates', {})
    except Exception:
        pass
    # Defaults
    return {
        'booking_subject': 'Bhagvad Mood: Booking Confirmation',
        'booking_body': 'Hi {name},\n\nYour counseling session with {counselor} is confirmed for {datetime}.\n\nReason: {reason}\n\n— Bhagvad Mood Team'
    }

def save_email_templates(templates: dict):
    data = {}
    try:
        if os.path.exists(SMTP_CONFIG_PATH):
            with open(SMTP_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
    except Exception:
        data = {}
    data['templates'] = templates
    try:
        with open(SMTP_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

class SMTPConfigDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('SMTP Settings & Templates')
        self.geometry('600x520')
        self.transient(parent)

        cfg = load_smtp_config()
        templates = load_email_templates()

        frame = tk.Frame(self)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(frame, text='SMTP Host:').grid(row=0, column=0, sticky='w')
        self.host_entry = tk.Entry(frame, width=40)
        self.host_entry.grid(row=0, column=1, sticky='w')
        self.host_entry.insert(0, cfg.get('host',''))

        tk.Label(frame, text='Port:').grid(row=1, column=0, sticky='w')
        self.port_entry = tk.Entry(frame, width=10)
        self.port_entry.grid(row=1, column=1, sticky='w')
        self.port_entry.insert(0, str(cfg.get('port','587')))

        tk.Label(frame, text='User:').grid(row=2, column=0, sticky='w')
        self.user_entry = tk.Entry(frame, width=40)
        self.user_entry.grid(row=2, column=1, sticky='w')
        self.user_entry.insert(0, cfg.get('user',''))

        tk.Label(frame, text='Password:').grid(row=3, column=0, sticky='w')
        self.pass_entry = tk.Entry(frame, width=40, show='*')
        self.pass_entry.grid(row=3, column=1, sticky='w')
        self.pass_entry.insert(0, cfg.get('pass',''))

        tk.Label(frame, text='From Address:').grid(row=4, column=0, sticky='w')
        self.from_entry = tk.Entry(frame, width=40)
        self.from_entry.grid(row=4, column=1, sticky='w')
        self.from_entry.insert(0, cfg.get('from',''))

        sep = ttk.Separator(frame, orient='horizontal')
        sep.grid(row=5, columnspan=2, sticky='ew', pady=8)

        tk.Label(frame, text='Booking Email Subject:').grid(row=6, column=0, sticky='w')
        self.subj_entry = tk.Entry(frame, width=60)
        self.subj_entry.grid(row=6, column=1, sticky='w')
        self.subj_entry.insert(0, templates.get('booking_subject',''))

        tk.Label(frame, text='Booking Email Body (use {name},{counselor},{datetime},{reason}):').grid(row=7, column=0, sticky='nw')
        self.body_text = scrolledtext.ScrolledText(frame, height=10, width=60)
        self.body_text.grid(row=7, column=1, sticky='w')
        self.body_text.insert(tk.END, templates.get('booking_body',''))

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text='Save', command=self.save).pack(side='left', padx=6)
        tk.Button(btn_frame, text='Cancel', command=self.destroy).pack(side='left', padx=6)

    def save(self):
        cfg = {
            'host': self.host_entry.get().strip(),
            'port': int(self.port_entry.get().strip() or 587),
            'user': self.user_entry.get().strip(),
            'pass': self.pass_entry.get().strip(),
            'from': self.from_entry.get().strip()
        }
        templates = {
            'booking_subject': self.subj_entry.get().strip(),
            'booking_body': self.body_text.get('1.0', tk.END).strip()
        }
        save_smtp_config(cfg)
        save_email_templates(templates)
        messagebox.showinfo('Saved', 'SMTP settings and templates saved locally.')
        self.destroy()


# ------------------ PASSWORD RESET HELPERS & DIALOG ------------------
PW_RESET_PATH = os.path.join(os.path.dirname(__file__), 'pw_reset_codes.json')

def _load_reset_store():
    try:
        if os.path.exists(PW_RESET_PATH):
            with open(PW_RESET_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_reset_store(store):
    try:
        with open(PW_RESET_PATH, 'w', encoding='utf-8') as f:
            json.dump(store, f)
        return True
    except Exception:
        return False

def generate_and_store_code(username):
    code = str(random.randint(100000, 999999))
    store = _load_reset_store()
    store[username] = {'code': code, 'ts': datetime.now().timestamp()}
    _save_reset_store(store)
    return code

def verify_reset_code(username, code, expiry_minutes=15):
    store = _load_reset_store()
    info = store.get(username)
    if not info:
        return False, 'No reset requested.'
    try:
        created = datetime.fromtimestamp(info.get('ts', 0))
        if datetime.now() - created > timedelta(minutes=expiry_minutes):
            store.pop(username, None); _save_reset_store(store)
            return False, 'Code expired.'
        if str(info.get('code')) == str(code):
            store.pop(username, None); _save_reset_store(store)
            return True, 'OK'
        return False, 'Invalid code.'
    except Exception:
        return False, 'Verification error.'

class ForgotPasswordDialog(tk.Toplevel):
    def __init__(self, parent, account_type='user'):
        super().__init__(parent)
        self.title('Forgot Password')
        self.geometry('420x340')
        self.transient(parent)
        self.account_type = account_type  # 'user' or 'counselor' or 'admin'

        tk.Label(self, text='Enter your username:').pack(pady=(10,4))
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=4)

        tk.Label(self, text='Enter your email (will be updated if missing):').pack(pady=(8,4))
        self.email_entry = tk.Entry(self)
        self.email_entry.pack(pady=4)

        tk.Button(self, text='Send Reset Code', command=self.send_code).pack(pady=8)

        tk.Label(self, text='Enter code received and new password:').pack(pady=(8,4))
        self.code_entry = tk.Entry(self)
        self.code_entry.pack(pady=4)
        tk.Label(self, text='New Password:').pack(pady=(6,2))
        self.newpass_entry = tk.Entry(self, show='*')
        self.newpass_entry.pack(pady=4)

        tk.Button(self, text='Verify & Reset', command=self.verify_and_reset).pack(pady=10)

    def send_code(self):
        uname = self.username_entry.get().strip()
        email_in = self.email_entry.get().strip()
        if not uname:
            messagebox.showwarning('Warning', 'Enter username')
            return
        # Check existence in appropriate table
        try:
            if self.account_type in ('user','admin'):
                cursor.execute('SELECT id, email FROM users WHERE username = %s', (uname,))
                row = cursor.fetchone()
                if not row:
                    messagebox.showerror('Error', 'Username not found in users table.')
                    return
                uid, email_existing = row
                if email_in and not email_existing:
                    cursor.execute('UPDATE users SET email = %s WHERE id = %s', (email_in, uid)); conn.commit()
                    email_existing = email_in
                if not email_existing:
                    messagebox.showinfo('No Email', 'No email on record. Please provide an email to receive reset code.')
                    return
                code = generate_and_store_code(uname)
                sent, info = send_email_confirmation(email_existing, f'Password Reset Code', f'Your reset code is: {code}')
                if sent:
                    messagebox.showinfo('Sent', f'Reset code sent to {email_existing}.')
                else:
                    messagebox.showwarning('Email Failed', f'Could not send email: {info}. Code shown for testing: {code}')
            else:
                cursor.execute('SELECT id, username FROM counselors WHERE username = %s', (uname,))
                row = cursor.fetchone()
                if not row:
                    messagebox.showerror('Error', 'Username not found in counselors table.')
                    return
                # counselors table may not have email; just generate code and require admin-assisted reset if no SMTP
                code = generate_and_store_code(uname)
                messagebox.showinfo('Code Generated', f'Reset code (for testing): {code}. If SMTP is configured, it will be emailed when an address is available.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to initiate reset: {e}')

    def verify_and_reset(self):
        uname = self.username_entry.get().strip()
        code = self.code_entry.get().strip()
        newpass = self.newpass_entry.get().strip()
        if not (uname and code and newpass):
            messagebox.showwarning('Incomplete', 'Fill username, code, and new password')
            return
        ok, msg = verify_reset_code(uname, code)
        if not ok:
            messagebox.showerror('Error', msg)
            return
        try:
            if self.account_type in ('user','admin'):
                cursor.execute('UPDATE users SET password = %s WHERE username = %s', (newpass, uname)); conn.commit()
                messagebox.showinfo('Success', 'Password reset successful. You can now login.')
                self.destroy()
            else:
                cursor.execute('UPDATE counselors SET password = %s WHERE username = %s', (newpass, uname)); conn.commit()
                messagebox.showinfo('Success', 'Counselor password reset successful.')
                self.destroy()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to reset password: {e}')

# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------


# ------------------ CORE AI & PERSONALIZED GUIDANCE LOGIC (NEW) ------------------

def check_recent_mood_trends(user_id):
    """
    Checks the user's mood logs for the last 7 days and provides trend feedback.
    Returns a trend message.
    """
    if not conn or user_id is None:
        return ""

    one_week_ago = datetime.now() - timedelta(days=7)

    # Check for consistency of the current mood
    cursor.execute("""
        SELECT mood FROM journal
        WHERE user_id = %s AND timestamp >= %s
    """, (user_id, one_week_ago))

    rows = cursor.fetchall()

    mood_counts = {}
    for row in rows:
        # Split and count multiple moods if stored in one string
        for mood in row[0].split(','):
            mood_key = mood.strip().lower()
            mood_counts[mood_key] = mood_counts.get(mood_key, 0) + 1

    feedback = ""
    # Only consider key negative moods for the trend alert
    negative_moods = ["sad", "anxious", "overwhelmed", "stressed", "very_sad", "devastated", "angry"]

    top_negative_mood = None
    max_count = 0

    # Find the mood with the highest count within the negative list
    for mood in negative_moods:
        count = mood_counts.get(mood, 0)
        # Only report if at least 3 times
        if count >= max_count and count >= 3:
            max_count = count
            top_negative_mood = mood

    if top_negative_mood:
        feedback = f"📈 **Trend Alert:** We noticed your mood has been **{top_negative_mood.title()}** {max_count} times in the last 7 days. This persistent feeling is valid. Remember to focus on your coping goals."

    return feedback


def check_risk_escalation(user_id):
    """
    Checks for a sustained pattern of high-risk entries in the last 14 days.
    Returns True if high-risk pattern is detected.
    """
    if not conn or user_id is None:
        return False

    two_weeks_ago = datetime.now() - timedelta(days=14)

    # Check for medium-high or high-risk entries
    cursor.execute("""
        SELECT risk_level, DATE(timestamp) as entry_date FROM journal
        WHERE user_id = %s AND timestamp >= %s
        ORDER BY timestamp DESC
    """, (user_id, two_weeks_ago))

    rows = cursor.fetchall()

    high_risk_days = set() # Use a set to count unique days with high risk
    
    # Risk categories indicating high distress
    HIGH_DISTRESS_RISKS = ['high', 'very high risk', 'medium-high']
    
    for level, entry_date in rows:
        if level in HIGH_DISTRESS_RISKS:
            high_risk_days.add(entry_date)

    # Criteria: 3 or more high-distress entries on unique days in the last 14 days
    if len(high_risk_days) >= 3:
        return True

    return False

# ------------------ END NEW LOGIC ------------------

def analyze_and_reframe(thought: str, mood: str, context: str = "General Wellbeing", locale: str = "IN"):
    """
    Analyzes the user's thought, detects crisis, and suggests reframes or helplines.
    Uses OpenAI if available, falling back to rule-based logic.
    """
    if not thought:
        return {"level": "reframe", "message": None, "helplines": None, "reframed_text": "", "risk_level": "low"}
    lowered = thought.lower()

    # --- Crisis Detection (Risk Level 'high') ---
    import wellness_ml
    is_crisis_ml, crisis_prob = wellness_ml.predict_crisis(thought)
    if is_crisis_ml or _matches_any(CRISIS_KEYWORDS, lowered):
        crisis_message = create_crisis_message(locale)
        return {"level": "crisis", "message": crisis_message, "helplines": HELPLINES.get(locale), "reframed_text": None, "risk_level": "high"}

    global openai_client
    
    # 1. Attempt using OpenAI if configured
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a compassionate mental health AI counselor. "
                            f"The user is experiencing '{context}' and their detected mood is '{mood}'. "
                            "Help the user reframe their difficult thought by acknowledging their feelings, offering empathy, and suggesting a gentle perspective shift. "
                            "Use Cognitive Behavioral Therapy (CBT) style language but keep it warm, supportive, and simple. "
                            "Output a JSON object containing: 'personalized_response' (a warm, validating message), 'reframed_text' (a constructive reframe of the user's thought), and 'risk_level' (either 'low' or 'medium')."
                        )
                    },
                    {"role": "user", "content": thought}
                ],
                response_format={"type": "json_object"},
                timeout=6
            )
            import json
            data = json.loads(response.choices[0].message.content)
            
            p_response = data.get("personalized_response", "I hear you. Remember that feelings are valid even when they feel heavy.")
            reframed = data.get("reframed_text", "")
            risk_level = data.get("risk_level", "low")
            
            llm_response = (
                f"✨ **AI Personalized Response:** {p_response}\n\n"
                f"🧘 **Reframing Insight:** {reframed}"
            )
            
            # Add mini-goal if appropriate
            mini_goal_message = ""
            if mood in MINI_GOALS and mood in ["anxious", "stressed", "sad", "angry"]:
                goal_data = MINI_GOALS[mood]
                mini_goal_message = f"\n\n🎯 **Mini-Goal for {mood.title()}:** {goal_data['goal']} (Reward: {goal_data['reward']} MP)"
                
            return {
                "level": "reframe",
                "message": None,
                "helplines": None,
                "reframed_text": llm_response + mini_goal_message,
                "risk_level": risk_level
            }
        except Exception as e:
            print(f"[OpenAI Warning] Reframing failed, using local rules: {e}")

    # 2. Local Rules Fallback (Preserves original features)
    core_challenge = thought[:80].strip() + ("..." if len(thought) > 80 else ".")
    llm_response = (
        f"**Supportive Response:** I hear you. It sounds like '{context.lower()}' has made this especially hard right now. "
        f"The core challenge seems to be: **'{core_challenge}'**\n\n"
    )

    replaced = False
    reframed = ""
    for old_phrase, new_phrase in thought_specific_reframes.items():
        if old_phrase in lowered:
            reframed = new_phrase
            replaced = True
            break

    if not replaced:
        mood_reframe_options = mood_specific_reframes.get(mood.lower(), [])

        custom_reframe = False
        for trigger, response in mood_reframe_options:
            if re.search(re.escape(trigger), thought, re.IGNORECASE):
                reframed = response
                custom_reframe = True
                break

        if not custom_reframe:
            negative_or_neutral_moods = ["negative", "neutral", "sad", "anxious", "overwhelmed", "pessimistic", "discouraged", "very_sad", "devastated", "restless", "angry"]
            if mood.lower() in negative_or_neutral_moods:
                reframed = f"Your original thought: **'{thought}\n'** \n **Reframing Tip:\n** {random.choice(uplifting_messages)}\n Remember, every thought is a chance to see things differently.\n You are not alone in this journey."
            else:
                reframed = f"Your inner voice is heard. A universal truth for your mood ({mood.title()}): {random.choice(uplifting_messages)}"

    llm_response += f"🧘 **Reframing Insight:** \n{reframed}"

    mini_goal_message = ""
    if mood in MINI_GOALS and mood in ["anxious", "stressed", "sad", "angry"]:
        goal_data = MINI_GOALS[mood]
        mini_goal_message = f"\n\n🎯 **Mini-Goal for {mood.title()}:** {goal_data['goal']} (Reward: {goal_data['reward']} MP)"

    risk_level = "low"
    if mood in ["very_sad", "devastated", "discouraged", "pessimistic", "angry"]:
        risk_level = "medium"
    elif mood in ["anxious", "overwhelmed"]:
        risk_level = "medium-high"

    return {"level": "reframe", "message": None, "helplines": None, "reframed_text": llm_response + mini_goal_message, "risk_level": risk_level}

def create_entry_with_label(parent, text, show=None):
    """Create a labeled entry widget"""
    tk.Label(parent, text=text, font=("Arial", 12), bg=parent.cget('bg')).pack()
    entry = tk.Entry(parent, font=("Arial", 12), show=show)
    entry.pack(ipady=6, padx=150, pady=6, fill="x")
    return entry

# ------------------ MAIN APPLICATION ------------------
class SarathiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # --- NAME CHANGE ---
        self.title("Bhagvad Mood Journal, Your Wellness Companion")
        # --- END NAME CHANGE ---
        self.geometry("1200x800")
        self.resizable(True, True)
        self.user_id = None
        self.username = None
        self.user_gender = None # Used for user's gender or counselor's specialization
        self.user_streak = 0
        self.mindful_points = 0
        self.last_journal_date = None
        self.current_theme_color = "#fff0f5"
        self.container = tk.Frame(self, bg=self.current_theme_color, bd=2, relief="ridge")
        self.container.place(relwidth=0.94, relheight=0.94, relx=0.03, rely=0.03)

        self.frames = {}
        frame_classes = (
            WelcomePage, LoginFrame, RegisterFrame, ChatbotFrame, AdminDashboardFrame, ResourcesFrame, 
            BookingFrame, PeerSupportFrame, EntriesFrame, ExportFrame, SpinWheelFrame, ToDoNotesFrame, 
            PeriodJournalFrame, PeriodLogFrame, PeriodStatsFrame, ScreeningsFrame, RewardsFrame,
            # --- NEW LOGIN/DASHBOARD FRAMES ---
            AdminLoginFrame, CounselorLoginFrame, CounselorDashboardFrame,
            ProfessionalLoginFrame, NonProfessionalLoginFrame, StudentLoginFrame,
            ProfessionalRegisterFrame, NonProfessionalRegisterFrame, StudentRegisterFrame, AdminRegisterFrame
            # -----------------------------------
        )
        for F in frame_classes:
            if F is ChatbotFrame:
                frame = F(self.container, self, self.set_theme_color)
            else:
                frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("WelcomePage")

    def set_theme_color(self, color):
        """Changes the background color of the main container and updates the current theme."""
        self.current_theme_color = color
        self.container.config(bg=color)
        if "ChatbotFrame" in self.frames:
            self.frames["ChatbotFrame"].configure_colors(color)

    def show_frame(self, name):
        frame = self.frames[name]
        # Only apply the default theme color if we're not in the main chatbot loop or a specialized dashboard
        if name not in ["ChatbotFrame", "CounselorDashboardFrame", "AdminDashboardFrame"]:
            self.set_theme_color("#fff0f5")
        
        frame.tkraise()
        if name == "AdminDashboardFrame":
            # Refresh both analytics and the new booking/counselor data
            frame.draw_stats()
            frame.refresh_bookings() 
        elif name == "CounselorDashboardFrame":
            frame.update_display() 
        elif name == "ResourcesFrame":
            frame.refresh_community_resources()
        elif name == "EntriesFrame":
            frame.refresh_entries()
        elif name == "ExportFrame":
            frame.refresh_preview()
        elif name == "PeriodStatsFrame":
            frame.draw_analytics()
        elif name == "PeriodJournalFrame":
            frame.draw_analytics_preview()
        elif name == "ChatbotFrame":
            self.frames["ChatbotFrame"].update_streak_display()
        elif name == "RewardsFrame":
            frame.update_display()


# ------------------ Login / Register (USER) ------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffe4e1")
        self.app = app
        # Grid layout: 2 columns for bottom section (left logins, right registers)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Title
        tk.Label(self, text="User Login", font=("Georgia", 28, "bold"), fg="#b22222", bg="#ffe4e1").grid(row=0, column=0, columnspan=2, pady=(30,20))

        # Center: Username / Password and Login button (spanning both columns)
        center_frame = tk.Frame(self, bg="#ffe4e1")
        center_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
        center_frame.columnconfigure(0, weight=1)
        
        tk.Label(center_frame, text="Username", font=("Arial", 12), bg="#ffe4e1").pack(pady=(0,2))
        self.username_entry = tk.Entry(center_frame, font=("Arial", 12), width=35)
        self.username_entry.pack(ipady=8, pady=6)
        
        tk.Label(center_frame, text="Password", font=("Arial", 12), bg="#ffe4e1").pack(pady=(10,2))
        self.password_entry = tk.Entry(center_frame, font=("Arial", 12), show="*", width=35)
        self.password_entry.pack(ipady=8, pady=6)
        
        tk.Button(center_frame, text="Login", font=("Arial", 16, "bold"), bg="#ff69b4", fg="white", command=self.login, padx=40, pady=8).pack(pady=12)
        
        tk.Button(center_frame, text="Forgot Password", font=("Arial", 10, "italic"), fg="#808080", bg="#ffe4e1", relief="flat", command=lambda: ForgotPasswordDialog(self, account_type='user')).pack(pady=(6,0))

        # Bottom section with login buttons (left) and register buttons (right)
        bottom_frame = tk.Frame(self, bg="#ffe4e1")
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(20,10))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        # Left: Login buttons in highlighted box
        login_box = tk.Frame(bottom_frame, bg="#e6d4f0", relief="solid", borderwidth=2)
        login_box.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=10)
        tk.Label(login_box, text="Login for Professionals", font=("Arial", 13, "bold"), bg="#e6d4f0", fg="#6b4fa5").pack(pady=(8,6))
        
        admin_btn = tk.Button(login_box, text="Admin Controller Login", font=("Arial", 11, "bold"), fg="white", bg="#5a4db0", command=lambda: app.show_frame("AdminLoginFrame"))
        admin_btn.pack(fill="x", padx=8, pady=3)
        
        coun_btn = tk.Button(login_box, text="Counselor Login", font=("Arial", 11, "bold"), fg="white", bg="#6b5fb5", command=lambda: app.show_frame("CounselorLoginFrame"))
        coun_btn.pack(fill="x", padx=8, pady=3)
        
        prof_btn = tk.Button(login_box, text="Professional Login", font=("Arial", 11, "bold"), fg="white", bg="#7d70ba", command=lambda: app.show_frame("ProfessionalLoginFrame"))
        prof_btn.pack(fill="x", padx=8, pady=3)
        
        nonprof_btn = tk.Button(login_box, text="Non-Professional Login", font=("Arial", 11, "bold"), fg="white", bg="#8e81bf", command=lambda: app.show_frame("NonProfessionalLoginFrame"))
        nonprof_btn.pack(fill="x", padx=8, pady=3)
        
        stud_btn = tk.Button(login_box, text="Student Login", font=("Arial", 11, "bold"), fg="white", bg="#9f92c4", command=lambda: app.show_frame("StudentLoginFrame"))
        stud_btn.pack(fill="x", padx=8, pady=(3,8))

        # Right: Register buttons in highlighted box (different colors)
        register_box = tk.Frame(bottom_frame, bg="#e6f0d4", relief="solid", borderwidth=2)
        register_box.grid(row=0, column=1, sticky="nsew", padx=(10,0), pady=10)
        tk.Label(register_box, text="Register as", font=("Arial", 13, "bold"), bg="#e6f0d4", fg="#5a7a4f").pack(pady=(8,6))
        
        reg_btn = tk.Button(register_box, text="Register User", font=("Arial", 11, "bold"), fg="white", bg="#5a7a4f", command=lambda: app.show_frame("RegisterFrame"))
        reg_btn.pack(fill="x", padx=8, pady=3)
        
        admin_reg_btn = tk.Button(register_box, text="Register as Admin", font=("Arial", 11, "bold"), fg="white", bg="#6b8b60", command=lambda: app.show_frame("AdminRegisterFrame"))
        admin_reg_btn.pack(fill="x", padx=8, pady=3)
        
        prof_reg_btn = tk.Button(register_box, text="Register as Counselor/Pro", font=("Arial", 11, "bold"), fg="white", bg="#7c9c71", command=lambda: app.show_frame("ProfessionalRegisterFrame"))
        prof_reg_btn.pack(fill="x", padx=8, pady=3)
        
        nonprof_reg_btn = tk.Button(register_box, text="Register as Non-Pro", font=("Arial", 11, "bold"), fg="white", bg="#8dad82", command=lambda: app.show_frame("NonProfessionalRegisterFrame"))
        nonprof_reg_btn.pack(fill="x", padx=8, pady=3)
        
        stud_reg_btn = tk.Button(register_box, text="Register as Student", font=("Arial", 11, "bold"), fg="white", bg="#9ebe93", command=lambda: app.show_frame("StudentRegisterFrame"))
        stud_reg_btn.pack(fill="x", padx=8, pady=(3,8))

        # Back to Home button
        tk.Button(self, text="Back to Home", font=("Arial", 12, "underline"), fg="#b22222", bg="#ffe4e1", relief="flat", command=lambda: app.show_frame("WelcomePage")).grid(row=3, column=0, columnspan=2, pady=12)

    def show_security_note(self):
        messagebox.showinfo("Feature Unavailable (Security Note)",
                             "Implementing a secure 'Forgot Password' feature (e.g., email verification, secure token generation) requires a fully functional, secure backend and mail server, which is outside the scope of this self-contained Tkinter/local database application. For a real application, strong security protocols must be followed.")

    def login(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected. Please check your MySQL setup.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Prevent login as admin/counselor through the user path
        if username.lower() == "admin" or username.lower().startswith("counselor") or username.lower().startswith("dr."):
            messagebox.showwarning("Warning", "Please use the dedicated Admin or Counselor login buttons below.")
            return
            
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return

        cursor.execute("SELECT id, username, gender, journal_streak, last_journal_date, mindful_points, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            stored_pwd = user[6]
            hashed_pwd = hash_password(password, username)
            login_success = False
            migrate_pwd = False
            
            if stored_pwd == hashed_pwd:
                login_success = True
            elif stored_pwd == password:
                login_success = True
                migrate_pwd = True
                
            if login_success:
                if migrate_pwd:
                    try:
                        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pwd, user[0]))
                        conn.commit()
                    except Exception as ex:
                        print(f"Failed to migrate password: {ex}")
                self.app.user_id = user[0]
                self.app.username = user[1]
                self.app.user_gender = user[2] if len(user) > 2 else "not_specified"
                self.app.user_streak = user[3] if len(user) > 3 else 0
                self.app.last_journal_date = user[4]
                self.app.mindful_points = user[5] if len(user) > 5 else 0

                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.username_entry.delete(0, "end")
                self.password_entry.delete(0, "end")
                self.app.show_frame("ChatbotFrame")
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        else:
            try_register = messagebox.askyesno("Not registered?", "Invalid username or password. Would you like to create a new account?")
            if try_register:
                self.app.show_frame("RegisterFrame")
            else:
                messagebox.showerror("Error", "Invalid username or password.")

class RegisterFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffe4e1")
        self.app = app
        tk.Label(self, text="Register", font=("Georgia", 26, "bold"), fg="#b22222", bg="#ffe4e1").pack(pady=(30,10))
        self.username_entry = create_entry_with_label(self, "Choose a Username")
        self.password_entry = create_entry_with_label(self, "Choose a Password", show="*")

        tk.Label(self, text="Gender (Optional):", font=("Arial", 12), bg="#ffe4e1").pack(pady=(10,2))
        self.gender_var = tk.StringVar(value="Not specified")
        gender_combo = ttk.Combobox(self, textvariable=self.gender_var, values=["Female", "Male", "Other", "Not specified"], state="readonly")
        gender_combo.pack(pady=4, ipady=4, padx=150, fill="x")

        self.age_entry = create_entry_with_label(self, "Age (Optional):")
        self.conditions_entry = create_entry_with_label(self, "Diagnosed Conditions (Optional):")

        tk.Button(self, text="Register", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=self.register).pack(pady=12)
        tk.Button(self, text="Back to Login", font=("Arial", 12, "underline"), fg="#b22222", bg="#ffe4e1", relief="flat", command=lambda: app.show_frame("LoginFrame")).pack()

    def register(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        gender = self.gender_var.get()
        age_str = self.age_entry.get().strip()
        conditions = self.conditions_entry.get().strip()

        age = int(age_str) if age_str.isdigit() else None

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists.")
                return
            cursor.execute("INSERT INTO users (username, password, gender, age, diagnosed_conditions, journal_streak, last_journal_date, mindful_points) VALUES (%s, %s, %s, %s, %s, 0, NULL, 0)", (username, hash_password(password, username), gender, age, conditions))
            conn.commit()
            messagebox.showinfo("Success", "Registered successfully. Please login.")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.age_entry.delete(0, "end")
            self.conditions_entry.delete(0, "end")
            self.app.show_frame("LoginFrame")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to register user: {err}")


class ProfessionalRegisterFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0fff0")
        self.app = app
        tk.Label(self, text="Register as Professional / Counselor", font=("Georgia", 22, "bold"), fg="#228B22", bg="#f0fff0").pack(pady=(20,10))
        self.username_entry = create_entry_with_label(self, "Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Label(self, text="Specialization:", bg="#f0fff0").pack()
        self.spec_entry = tk.Entry(self)
        self.spec_entry.pack(ipady=6, padx=150, pady=6, fill="x")
        tk.Button(self, text="Register", font=("Arial", 14, "bold"), bg="#3CB371", fg="white", command=self.register).pack(pady=12)
        tk.Button(self, text="Back to Login", command=lambda: app.show_frame("LoginFrame")).pack()

    def register(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        spec = self.spec_entry.get().strip() or 'General'
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        try:
            cursor.execute('SELECT id FROM counselors WHERE username = %s', (username,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Counselor username already exists.')
                return
            cursor.execute('INSERT INTO counselors (username, password, specialization) VALUES (%s,%s,%s)', (username, hash_password(password, username), spec))
            conn.commit()
            messagebox.showinfo('Success', 'Professional registered. You can login now.')
            self.app.show_frame('ProfessionalLoginFrame')
        except Exception as e:
            messagebox.showerror('DB Error', f'Failed to register professional: {e}')


class NonProfessionalRegisterFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffe4e1")
        self.app = app
        tk.Label(self, text="Register (General User)", font=("Georgia", 22, "bold"), fg="#b22222", bg="#ffe4e1").pack(pady=(20,10))
        self.username_entry = create_entry_with_label(self, "Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Label(self, text="Email (optional):", bg="#ffe4e1").pack()
        self.email_entry = tk.Entry(self)
        self.email_entry.pack(ipady=6, padx=150, pady=6, fill="x")
        tk.Button(self, text="Register", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=self.register).pack(pady=12)
        tk.Button(self, text="Back to Login", command=lambda: app.show_frame("LoginFrame")).pack()

    def register(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip() or None
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        try:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Username already exists.')
                return
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s,%s,%s)', (username, hash_password(password, username), email))
            conn.commit()
            messagebox.showinfo('Success', 'User registered. Please login.')
            self.app.show_frame('LoginFrame')
        except Exception as e:
            messagebox.showerror('DB Error', f'Failed to register user: {e}')


class StudentRegisterFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fffaf0")
        self.app = app
        tk.Label(self, text="Register (Student)", font=("Georgia", 22, "bold"), fg="#b22222", bg="#fffaf0").pack(pady=(20,10))
        self.username_entry = create_entry_with_label(self, "Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Label(self, text="Institution (optional):", bg="#fffaf0").pack()
        self.inst_entry = tk.Entry(self)
        self.inst_entry.pack(ipady=6, padx=150, pady=6, fill="x")
        tk.Button(self, text="Register", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=self.register).pack(pady=12)
        tk.Button(self, text="Back to Login", command=lambda: app.show_frame("LoginFrame")).pack()

    def register(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        inst = self.inst_entry.get().strip() or None
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        try:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Username already exists.')
                return
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s,%s,%s)', (username, hash_password(password, username), None))
            conn.commit()
            messagebox.showinfo('Success', 'Student registered. Please login.')
            self.app.show_frame('LoginFrame')
        except Exception as e:
            messagebox.showerror('DB Error', f'Failed to register student: {e}')


class AdminRegisterFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0f8ff")
        self.app = app
        tk.Label(self, text="Register Admin", font=("Georgia", 22, "bold"), fg="#2f4f4f", bg="#f0f8ff").pack(pady=(20,10))
        self.username_entry = create_entry_with_label(self, "Admin Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Label(self, text="Admin Secret Key:", bg="#f0f8ff").pack()
        self.secret_entry = tk.Entry(self)
        self.secret_entry.pack(ipady=6, padx=150, pady=6, fill="x")
        tk.Button(self, text="Create Admin", font=("Arial", 14, "bold"), bg="#507c91", fg="white", command=self.register).pack(pady=12)
        tk.Button(self, text="Back to Login", command=lambda: app.show_frame("LoginFrame")).pack()

    def register(self):
        secret = self.secret_entry.get().strip()
        admin_secret_env = os.environ.get('ADMIN_SECRET', ADMIN_PASSWORD)
        if secret != admin_secret_env:
            messagebox.showerror('Error', 'Invalid admin secret key.')
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror('Error', 'Please enter username and password.')
            return
        try:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Username already exists.')
                return
            cursor.execute('INSERT INTO users (username, password) VALUES (%s,%s)', (username, hash_password(password, username)))
            conn.commit()
            messagebox.showinfo('Success', 'Admin account created. You can login as admin.')
            self.app.show_frame('AdminLoginFrame')
        except Exception as e:
            messagebox.showerror('DB Error', f'Failed to create admin: {e}')

# ------------------ NEW: ADMIN LOGIN ------------------
class AdminLoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0f8ff")
        self.app = app
        tk.Label(self, text="Admin Controller Login", font=("Georgia", 28, "bold"), fg="#2f4f4f", bg="#f0f8ff").pack(pady=(30,10))
        self.username_entry = create_entry_with_label(self, "Admin Username")
        self.password_entry = create_entry_with_label(self, "Admin Password", show="*")
        tk.Button(self, text="Admin Login", font=("Arial", 14, "bold"), bg="#507c91", fg="white", command=self.login).pack(pady=12)
        tk.Button(self, text="Back to User Login", font=("Arial", 12, "underline"), fg="#2f4f4f", bg="#f0f8ff", relief="flat", command=lambda: app.show_frame("LoginFrame")).pack()

        tk.Button(self, text="Forgot Password", font=("Arial", 10), fg="#2f4f4f", bg="#f0f8ff", relief="flat", command=lambda: ForgotPasswordDialog(self, account_type='admin')).pack(pady=4)

    def login(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row:
                uid, stored_pwd = row
                hashed = hash_password(password, username)
                login_success = False
                migrate_pwd = False
                
                if stored_pwd == hashed:
                    login_success = True
                elif stored_pwd == password:
                    login_success = True
                    migrate_pwd = True
                    
                if login_success:
                    if migrate_pwd:
                        try:
                            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, uid))
                            conn.commit()
                        except Exception as ex:
                            print(f"Failed to migrate admin password: {ex}")
                    self.app.user_id = uid
                    self.app.username = "ADMIN_CONTROLLER" if username.lower() == "admin" else username
                    messagebox.showinfo("Success", "Welcome, Admin!")
                    self.username_entry.delete(0, "end")
                    self.password_entry.delete(0, "end")
                    self.app.show_frame("AdminDashboardFrame")
                else:
                    messagebox.showerror("Error", "Invalid Admin credentials.")
            else:
                try_register = messagebox.askyesno("Not registered?", "Invalid Admin credentials. Would you like to create an admin account?")
                if try_register:
                    self.app.show_frame('AdminRegisterFrame')
                else:
                    messagebox.showerror("Error", "Invalid Admin credentials.")
        except Exception as e:
            messagebox.showerror("DB Error", f"Login failed: {e}")

# ------------------ NEW: COUNSELOR LOGIN ------------------
class CounselorLoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0fff0")
        self.app = app
        self.counselor_id = None
        tk.Label(self, text="Counselor Login", font=("Georgia", 28, "bold"), fg="#228B22", bg="#f0fff0").pack(pady=(30,10))
        self.username_entry = create_entry_with_label(self, "Counselor Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Button(self, text="Login", font=("Arial", 14, "bold"), bg="#3CB371", fg="white", command=self.login).pack(pady=12)
        tk.Button(self, text="Back to User Login", font=("Arial", 12, "underline"), fg="#228B22", bg="#f0fff0", relief="flat", command=lambda: app.show_frame("LoginFrame")).pack()

        tk.Button(self, text="Forgot Password", font=("Arial", 10), fg="#228B22", bg="#f0fff0", relief="flat", command=lambda: ForgotPasswordDialog(self, account_type='counselor')).pack(pady=4)

    def login(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            cursor.execute("SELECT id, username, specialization, password FROM counselors WHERE username = %s", (username,))
            counselor = cursor.fetchone()

            if counselor:
                uid, uname, spec, stored_pwd = counselor
                hashed = hash_password(password, username)
                login_success = False
                migrate_pwd = False
                
                if stored_pwd == hashed:
                    login_success = True
                elif stored_pwd == password:
                    login_success = True
                    migrate_pwd = True
                    
                if login_success:
                    if migrate_pwd:
                        try:
                            cursor.execute("UPDATE counselors SET password = %s WHERE id = %s", (hashed, uid))
                            conn.commit()
                        except Exception as ex:
                            print(f"Failed to migrate counselor password: {ex}")
                    self.app.user_id = uid
                    self.app.username = uname
                    self.app.user_gender = spec # Storing specialization here for simplicity
                    
                    # Update last login and status to online
                    cursor.execute("UPDATE counselors SET last_login = %s, online_status = TRUE WHERE id = %s", (datetime.now(), uid))
                    conn.commit()

                    messagebox.showinfo("Success", f"Welcome, Counselor {username}!")
                    self.username_entry.delete(0, "end")
                    self.password_entry.delete(0, "end")
                    self.app.show_frame("CounselorDashboardFrame")
                else:
                    messagebox.showerror("Error", "Invalid counselor credentials.")
            else:
                try_register = messagebox.askyesno("Not registered?", "Invalid counselor credentials. Would you like to register as a counselor/professional?")
                if try_register:
                    self.app.show_frame('ProfessionalRegisterFrame')
                else:
                    messagebox.showerror("Error", "Invalid counselor credentials.")
        except Exception as e:
            messagebox.showerror("DB Error", f"Login failed: {e}")

# ------------------ NEW: COUNSELOR DASHBOARD (Patient History Access) ------------------
class CounselorDashboardFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0fff0")
        self.app = app

        top_frame = tk.Frame(self, bg="#f0fff0")
        top_frame.pack(fill="x", pady=10)
        tk.Label(top_frame, text="Counselor Dashboard", font=("Georgia", 20, "bold"), fg="#228B22", bg="#f0fff0").pack(side="left", padx=10)
        
        self.status_var = tk.StringVar(value="Offline")
        self.status_button = tk.Button(top_frame, textvariable=self.status_var, command=self.toggle_status, font=("Arial", 12, "bold"), bg="#ff69b4", fg="white")
        self.status_button.pack(side="left", padx=10)
        tk.Button(top_frame, text="Logout", command=self.logout).pack(side="right", padx=10)
        
        # Main content with two sections: Bookings and Patient History
        main_content = tk.Frame(self, bg="#ffffff")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        # Bookings List
        booking_frame = tk.LabelFrame(main_content, text="Upcoming Sessions", padx=10, pady=10)
        booking_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.booking_tree = ttk.Treeview(booking_frame, columns=("id", "time", "user", "reason"), show="headings")
        self.booking_tree.heading("id", text="ID")
        self.booking_tree.heading("time", text="Time")
        self.booking_tree.heading("user", text="Patient (Anon)")
        self.booking_tree.heading("reason", text="Reason Preview")
        self.booking_tree.column("id", width=30, anchor="center")
        self.booking_tree.column("time", width=120)
        self.booking_tree.column("user", width=100)
        self.booking_tree.column("reason", width=250)
        self.booking_tree.pack(fill="both", expand=True)
        self.booking_tree.bind("<Double-1>", self.view_patient_history)
        
        # Slots list for the counselor
        tk.Label(booking_frame, text="Your Slots (Upcoming)", bg="#f0fff0").pack(pady=(8,4))
        self.slots_tree = ttk.Treeview(booking_frame, columns=("id","time","avail"), show="headings", height=6)
        self.slots_tree.heading("id", text="ID")
        self.slots_tree.heading("time", text="Time")
        self.slots_tree.heading("avail", text="Available")
        self.slots_tree.column("id", width=40, anchor="center")
        self.slots_tree.column("time", width=140)
        self.slots_tree.column("avail", width=80, anchor="center")
        self.slots_tree.pack(fill="x", pady=(0,6))

        slot_btns = tk.Frame(booking_frame, bg="#f0fff0")
        slot_btns.pack(fill="x")
        tk.Button(slot_btns, text="Refresh Slots", command=self.refresh_my_slots).pack(side="left", padx=4)
        tk.Button(slot_btns, text="Toggle Availability", command=self.toggle_slot_availability_counselor).pack(side="left", padx=4)
        tk.Button(slot_btns, text="Create Slot", command=self.create_slot_popup_counselor).pack(side="left", padx=4)
        # Patient History Viewer
        history_frame = tk.LabelFrame(main_content, text="Patient Journal History (Read-Only)", padx=10, pady=10)
        history_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.history_viewer = scrolledtext.ScrolledText(history_frame, wrap="word", font=("Arial", 11), state=tk.DISABLED)
        self.history_viewer.pack(fill="both", expand=True)
        tk.Label(history_frame, text="Double-click a booking to load patient's anonymous journal entries.", fg="#8b0000").pack(pady=5)

    def toggle_status(self):
        # Determine the current status from the button's text (simpler than checking DB every time)
        current_status_online = self.status_var.get() == "Online"
        new_status = not current_status_online
        status_text = "Online" if new_status else "Offline"
        
        try:
            cursor.execute("UPDATE counselors SET online_status = %s WHERE id = %s", (new_status, self.app.user_id))
            conn.commit()
            
            self.status_var.set(status_text)
            self.status_button.config(bg="#3CB371" if new_status else "#ff69b4", text=f"Go {'Offline' if new_status else 'Online'}")
            messagebox.showinfo("Status Update", f"Your status is now {status_text}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {e}")

    def update_display(self):
        """Called when the frame is raised to update bookings and status."""
        self.update_status_initial()
        self.refresh_bookings()
        # Refresh counselor-specific slots
        try:
            self.refresh_my_slots()
        except Exception:
            pass

    def update_status_initial(self):
        """Fetches the actual status from DB upon entering the dashboard."""
        try:
            cursor.execute("SELECT online_status FROM counselors WHERE id = %s", (self.app.user_id,))
            status = cursor.fetchone()
            if status and status[0]:
                self.status_var.set("Online")
                self.status_button.config(bg="#3CB371", text="Go Offline")
            else:
                self.status_var.set("Offline")
                self.status_button.config(bg="#ff69b4", text="Go Online")
        except Exception:
            self.status_var.set("N/A")

    def refresh_bookings(self):
        """Reloads the list of upcoming bookings for the current counselor."""
        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)
        
        if self.app.user_id is None: return

        try:
            # Select upcoming bookings confirmed for this counselor
            cursor.execute("""
                SELECT b.id, b.booking_time, u.username, b.reason, u.id 
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                WHERE b.counselor_id = %s AND b.booking_time >= %s AND b.status = 'Confirmed'
                ORDER BY b.booking_time ASC
            """, (self.app.user_id, datetime.now()))
            
            rows = cursor.fetchall()
            for row in rows:
                booking_id, b_time, username, reason, user_id = row
                # Use a tag on the treeview row to store the actual user_id securely
                anon_name = f"Patient #{user_id}"
                time_str = b_time.strftime("%Y-%m-%d %H:%M")
                reason_preview = reason[:45] + "..." if len(reason) > 45 else reason
                self.booking_tree.insert("", "end", values=(booking_id, time_str, anon_name, reason_preview), tags=(user_id,))
        except Exception as e:
            messagebox.showerror("DB Error", f"Error refreshing bookings: {e}")

    def refresh_my_slots(self):
        # Load upcoming slots for the logged-in counselor
        for i in getattr(self, 'slots_tree', tk.Frame()).get_children():
            self.slots_tree.delete(i)
        if self.app.user_id is None:
            return
        try:
            cursor.execute("SELECT id, slot_time, available FROM counselor_slots WHERE counselor_id = %s AND slot_time >= %s ORDER BY slot_time ASC", (self.app.user_id, datetime.now()))
            rows = cursor.fetchall()
            for sid, st, avail in rows:
                time_str = st.strftime('%Y-%m-%d %H:%M') if hasattr(st, 'strftime') else str(st)
                self.slots_tree.insert('', 'end', values=(sid, time_str, 'Yes' if avail else 'No'))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load your slots: {e}')

    def toggle_slot_availability_counselor(self):
        sel = self.slots_tree.selection()
        if not sel:
            messagebox.showwarning('Warning', 'Select a slot to toggle.')
            return
        sid = self.slots_tree.item(sel[0], 'values')[0]
        try:
            cursor.execute('SELECT available FROM counselor_slots WHERE id = %s AND counselor_id = %s', (sid, self.app.user_id))
            r = cursor.fetchone()
            if not r:
                messagebox.showerror('Error', 'Slot not found or not authorized.')
                return
            newv = not bool(r[0])
            cursor.execute('UPDATE counselor_slots SET available = %s WHERE id = %s', (newv, sid))
            conn.commit()
            self.refresh_my_slots()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to toggle slot: {e}')

    def create_slot_popup_counselor(self):
        if self.app.user_id is None:
            messagebox.showerror('Error', 'Not logged in as a counselor.')
            return
        popup = tk.Toplevel(self)
        popup.title('Create Slot')
        popup.geometry('380x220')

        tk.Label(popup, text='Slot Date (YYYY-MM-DD):').pack(pady=(6,0))
        try:
            date_entry = DateEntry(popup, width=16, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            date_entry.pack(pady=4)
        except Exception:
            date_text = tk.Entry(popup)
            date_text.pack(pady=4)

        tk.Label(popup, text='Hour (24h) and Minute:').pack(pady=(6,0))
        hr_var = tk.StringVar(value='10')
        mn_var = tk.StringVar(value='00')
        hr_spin = ttk.Combobox(popup, values=[str(i).zfill(2) for i in range(0,24)], textvariable=hr_var, width=4, state='readonly')
        mn_spin = ttk.Combobox(popup, values=['00','15','30','45'], textvariable=mn_var, width=4, state='readonly')
        hr_spin.pack(pady=2)
        mn_spin.pack(pady=2)

        def create_slot():
            try:
                if 'date_entry' in locals() and isinstance(date_entry, DateEntry):
                    d = date_entry.get_date().strftime('%Y-%m-%d')
                else:
                    d = date_text.get().strip()
                hour = int(hr_var.get())
                minute = int(mn_var.get())
                slot_dt = datetime.strptime(f"{d} {hour:02d}:{minute:02d}", '%Y-%m-%d %H:%M')
                cursor.execute('INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s,%s,%s)', (self.app.user_id, slot_dt, True))
                conn.commit()
                popup.destroy()
                self.refresh_my_slots()
                messagebox.showinfo('Success', 'Slot created.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to create slot: {e}')

        tk.Button(popup, text='Create Slot', command=create_slot).pack(pady=10)

    def view_patient_history(self, event):
        """Loads and displays the patient's journal history (read-only) upon double-click."""
        selected_item = self.booking_tree.selection()
        if not selected_item: return
        
        # Retrieve the user_id from the stored tag
        item_data = self.booking_tree.item(selected_item[0], 'tags')
        if not item_data: 
            self.history_viewer.config(state=tk.NORMAL); self.history_viewer.delete("1.0", tk.END); self.history_viewer.insert(tk.END, "Error: Patient ID not found."); self.history_viewer.config(state=tk.DISABLED)
            return
        
        patient_id = item_data[0] 

        self.history_viewer.config(state=tk.NORMAL)
        self.history_viewer.delete("1.0", tk.END)
        self.history_viewer.insert(tk.END, f"--- Anonymous Journal History for Patient #{patient_id} ---\n\n")

        try:
            # Fetch the last 10 journal entries
            cursor.execute("""
                SELECT timestamp, mood, thought, risk_level 
                FROM journal 
                WHERE user_id = %s 
                ORDER BY timestamp DESC LIMIT 10
            """, (patient_id,))
            
            entries = cursor.fetchall()
            if entries:
                for ts, mood, thought, risk in entries:
                    self.history_viewer.insert(tk.END, f"[{ts.strftime('%Y-%m-%d %H:%M')}]\n")
                    self.history_viewer.insert(tk.END, f"Mood: {mood.upper()} (Risk: {risk.title()})\n", "mood")
                    # --- Corrected Logic ---
                    # Get the first 150 characters and replace newlines before inserting.
                    thought_preview = thought[:150].replace('\n', ' ')
                    # Now use the cleaned variable in the f-string.
                    self.history_viewer.insert(tk.END, f"Thought: {thought_preview}...\n\n")
                 #self.history_viewer.insert(tk.END, f"Thought: {thought[:150].replace('\n', ' ')}...\n\n")
                self.history_viewer.tag_config("mood", font=("Arial", 11, "bold"), foreground="#8b0000")
            else:
                self.history_viewer.insert(tk.END, "No journal entries found for this patient.")

        except Exception as e:
            self.history_viewer.insert(tk.END, f"\nError fetching history: {e}")
        
        self.history_viewer.config(state=tk.DISABLED)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            try:
                # Set status to offline upon logout
                cursor.execute("UPDATE counselors SET online_status = FALSE WHERE id = %s", (self.app.user_id,))
                conn.commit()
            except Exception:
                pass # Ignore DB errors on logout

            self.app.user_id = None
            self.app.username = None
            self.app.user_gender = None
            self.app.show_frame("LoginFrame")


class ProfessionalLoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0fff0")
        self.app = app
        tk.Label(self, text="Professional Login (Counselors/Pros)", font=("Georgia", 28, "bold"), fg="#228B22", bg="#f0fff0").pack(pady=(30,10))
        self.username_entry = create_entry_with_label(self, "Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Button(self, text="Login", font=("Arial", 14, "bold"), bg="#3CB371", fg="white", command=self.login).pack(pady=12)
        tk.Button(self, text="Forgot Password", font=("Arial", 10), fg="#228B22", bg="#f0fff0", relief="flat", command=lambda: ForgotPasswordDialog(self, account_type='counselor')).pack(pady=4)
        tk.Button(self, text="Back to User Login", font=("Arial", 12, "underline"), fg="#228B22", bg="#f0fff0", relief="flat", command=lambda: app.show_frame("LoginFrame")).pack()

    def login(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            cursor.execute("SELECT id, username, specialization, password FROM counselors WHERE username = %s", (username,))
            counselor = cursor.fetchone()
            if counselor:
                uid, uname, spec, stored_pwd = counselor
                hashed = hash_password(password, username)
                login_success = False
                migrate_pwd = False
                
                if stored_pwd == hashed:
                    login_success = True
                elif stored_pwd == password:
                    login_success = True
                    migrate_pwd = True
                    
                if login_success:
                    if migrate_pwd:
                        try:
                            cursor.execute("UPDATE counselors SET password = %s WHERE id = %s", (hashed, uid))
                            conn.commit()
                        except Exception as ex:
                            print(f"Failed to migrate professional password: {ex}")
                    self.app.user_id = uid
                    self.app.username = uname
                    self.app.user_gender = spec
                    cursor.execute("UPDATE counselors SET last_login = %s, online_status = TRUE WHERE id = %s", (datetime.now(), uid))
                    conn.commit()
                    messagebox.showinfo("Success", f"Welcome, {username}!")
                    self.username_entry.delete(0, 'end')
                    self.password_entry.delete(0, 'end')
                    self.app.show_frame("CounselorDashboardFrame")
                else:
                    messagebox.showerror("Error", "Invalid credentials.")
            else:
                try_register = messagebox.askyesno("Not registered?", "Invalid credentials. Would you like to register as a counselor/professional?")
                if try_register:
                    self.app.show_frame('ProfessionalRegisterFrame')
                else:
                    messagebox.showerror("Error", "Invalid credentials.")
        except Exception as e:
            messagebox.showerror("DB Error", f"Login failed: {e}")


class NonProfessionalLoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffe4e1")
        self.app = app
        tk.Label(self, text="Non-Professional / General User Login", font=("Georgia", 26, "bold"), fg="#b22222", bg="#ffe4e1").pack(pady=(30,10))
        self.username_entry = create_entry_with_label(self, "Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Button(self, text="Login", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=self.login).pack(pady=12)
        tk.Button(self, text="Forgot Password", font=("Arial", 10, "italic"), fg="#808080", bg="#ffe4e1", relief="flat", command=lambda: ForgotPasswordDialog(self, account_type='user')).pack()
        tk.Button(self, text="Back to User Login", font=("Arial", 12, "underline"), fg="#b22222", bg="#ffe4e1", relief="flat", command=lambda: app.show_frame("LoginFrame")).pack(pady=6)

    def login(self):
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        try:
            cursor.execute("SELECT id, username, gender, journal_streak, last_journal_date, mindful_points, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                uid, uname, gender, streak, last_date, points, stored_pwd = user
                hashed = hash_password(password, username)
                login_success = False
                migrate_pwd = False
                
                if stored_pwd == hashed:
                    login_success = True
                elif stored_pwd == password:
                    login_success = True
                    migrate_pwd = True
                    
                if login_success:
                    if migrate_pwd:
                        try:
                            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, uid))
                            conn.commit()
                        except Exception as ex:
                            print(f"Failed to migrate password: {ex}")
                    self.app.user_id = uid
                    self.app.username = uname
                    self.app.user_gender = gender if gender else 'not_specified'
                    self.app.user_streak = streak if streak else 0
                    self.app.last_journal_date = last_date
                    self.app.mindful_points = points if points else 0
                    messagebox.showinfo('Success', f'Welcome, {username}!')
                    self.username_entry.delete(0, 'end')
                    self.password_entry.delete(0, 'end')
                    self.app.show_frame('ChatbotFrame')
                else:
                    messagebox.showerror('Error', 'Invalid username or password.')
            else:
                try_register = messagebox.askyesno('Not registered?', 'Invalid username or password. Would you like to create a new account?')
                if try_register:
                    self.app.show_frame('NonProfessionalRegisterFrame')
                else:
                    messagebox.showerror('Error', 'Invalid username or password.')
        except Exception as e:
            messagebox.showerror('Error', f'Login failed: {e}')


class StudentLoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fffaf0")
        self.app = app
        tk.Label(self, text="Student Login", font=("Georgia", 26, "bold"), fg="#b22222", bg="#fffaf0").pack(pady=(30,10))
        self.username_entry = create_entry_with_label(self, "Username")
        self.password_entry = create_entry_with_label(self, "Password", show="*")
        tk.Button(self, text="Login", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=self.login).pack(pady=12)
        tk.Button(self, text="Forgot Password", font=("Arial", 10, "italic"), fg="#808080", bg="#fffaf0", relief="flat", command=lambda: ForgotPasswordDialog(self, account_type='user')).pack()
        tk.Button(self, text="Back to User Login", font=("Arial", 12, "underline"), fg="#b22222", bg="#fffaf0", relief="flat", command=lambda: app.show_frame("LoginFrame")).pack(pady=6)

    def login(self):
        # Reuse non-professional logic but offer Student registration specifically
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        try:
            cursor.execute("SELECT id, username, gender, journal_streak, last_journal_date, mindful_points, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                uid, uname, gender, streak, last_date, points, stored_pwd = user
                hashed = hash_password(password, username)
                login_success = False
                migrate_pwd = False
                
                if stored_pwd == hashed:
                    login_success = True
                elif stored_pwd == password:
                    login_success = True
                    migrate_pwd = True
                    
                if login_success:
                    if migrate_pwd:
                        try:
                            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, uid))
                            conn.commit()
                        except Exception as ex:
                            print(f"Failed to migrate password: {ex}")
                    self.app.user_id = uid
                    self.app.username = uname
                    self.app.user_gender = gender if gender else 'not_specified'
                    self.app.user_streak = streak if streak else 0
                    self.app.last_journal_date = last_date
                    self.app.mindful_points = points if points else 0
                    messagebox.showinfo('Success', f'Welcome, {username}!')
                    self.username_entry.delete(0, 'end')
                    self.password_entry.delete(0, 'end')
                    self.app.show_frame('ChatbotFrame')
                else:
                    messagebox.showerror('Error', 'Invalid username or password.')
            else:
                try_register = messagebox.askyesno('Not registered?', 'Invalid username or password. Would you like to register as a student?')
                if try_register:
                    self.app.show_frame('StudentRegisterFrame')
                else:
                    messagebox.showerror('Error', 'Invalid username or password.')
        except Exception as e:
            messagebox.showerror('Error', f'Login failed: {e}')
        

# ------------------ ENHANCED ADMIN DASHBOARD (Admin Controller) ------------------
class AdminDashboardFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0f8ff")
        self.app = app
        
        top = tk.Frame(self, bg="#f0f8ff")
        top.pack(fill="x", pady=10)
        tk.Label(top, text="Admin Controller & Analytics", font=("Georgia", 18, "bold"), fg="#2f4f4f", bg="#f0f8ff").pack(side="left", padx=10)
        tk.Button(top, text="Logout", command=self.logout).pack(side="right", padx=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: Anonymous Analytics (Existing functionality)
        self.analytics_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.analytics_frame, text="Anonymous Trends")
        self._build_analytics_tab(self.analytics_frame)

        # Tab 2: Booking Management (NEW Admin Controller functionality)
        self.booking_manager_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.booking_manager_frame, text="Booking & Counselor Management")
        self._build_booking_manager_tab(self.booking_manager_frame)
        
        self.current_canvas = None

    def _build_analytics_tab(self, parent_frame):
        # Dropdown for Chart Selection
        self.chart_options = ["Mood Distribution by Gender", "Mood Distribution by Age Group", "Risk Level Distribution", "Peer Support Posts by Category"]
        self.chart_var = tk.StringVar(value=self.chart_options[0])
        chart_menu = ttk.Combobox(parent_frame, textvariable=self.chart_var, values=self.chart_options, state="readonly", width=40)
        chart_menu.pack(pady=10)
        chart_menu.bind("<<ComboboxSelected>>", self.draw_stats)

        self.chart_frame = tk.Frame(parent_frame, bg="#fff")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_booking_manager_tab(self, parent_frame):
        # Display All Bookings
        tk.Label(parent_frame, text="All Counselor Bookings (Past & Future)", font=("Arial", 14, "bold")).pack(pady=10)
        self.all_booking_tree = ttk.Treeview(parent_frame, columns=("id", "user", "counselor", "time", "reason", "status"), show="headings")
        self.all_booking_tree.heading("id", text="ID")
        self.all_booking_tree.heading("user", text="Patient (ID)")
        self.all_booking_tree.heading("counselor", text="Counselor")
        self.all_booking_tree.heading("time", text="Time")
        self.all_booking_tree.heading("reason", text="Reason Preview")
        self.all_booking_tree.heading("status", text="Status")
        self.all_booking_tree.column("id", width=30, anchor="center")
        self.all_booking_tree.column("user", width=80, anchor="center")
        self.all_booking_tree.column("counselor", width=100)
        self.all_booking_tree.column("time", width=150)
        self.all_booking_tree.column("reason", width=200)
        self.all_booking_tree.column("status", width=80, anchor="center")
        self.all_booking_tree.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Counselor Status Overview
        tk.Label(parent_frame, text="Counselor Status & Specialization", font=("Arial", 14, "bold")).pack(pady=10)
        self.counselor_tree = ttk.Treeview(parent_frame, columns=("id", "username", "specialization", "status", "last_login"), show="headings")
        self.counselor_tree.heading("id", text="ID")
        self.counselor_tree.heading("username", text="Username")
        self.counselor_tree.heading("specialization", text="Specialization")
        self.counselor_tree.heading("status", text="Online Status")
        self.counselor_tree.heading("last_login", text="Last Active")
        self.counselor_tree.column("id", width=50, anchor="center")
        self.counselor_tree.column("username", width=120)
        self.counselor_tree.column("specialization", width=150)
        self.counselor_tree.column("status", width=100, anchor="center")
        self.counselor_tree.column("last_login", width=150)
        self.counselor_tree.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Control Buttons
        control_frame = tk.Frame(parent_frame)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Refresh Data", command=self.refresh_bookings).pack(side="left", padx=5)
        tk.Button(control_frame, text="Add New Counselor (Conceptual)", command=lambda: messagebox.showinfo("Info", "In a live system, this would open a form to register a new counselor account.")).pack(side="left", padx=5)
        tk.Button(control_frame, text="Approve Booking", command=self.approve_selected_booking).pack(side="left", padx=5)
        tk.Button(control_frame, text="Cancel Booking", command=self.cancel_selected_booking).pack(side="left", padx=5)
        tk.Button(control_frame, text="Force Offline", command=self.force_counselor_offline).pack(side="left", padx=5)
        tk.Button(control_frame, text="SMTP Settings", command=self.open_smtp_settings).pack(side="left", padx=5)

        # --- Slot Management Section ---
        tk.Label(parent_frame, text="Slot Management", font=("Arial", 14, "bold")).pack(pady=10)
        self.slots_tree = ttk.Treeview(parent_frame, columns=("id", "counselor", "time", "available"), show="headings")
        self.slots_tree.heading("id", text="ID")
        self.slots_tree.heading("counselor", text="Counselor")
        self.slots_tree.heading("time", text="Time")
        self.slots_tree.heading("available", text="Available")
        self.slots_tree.column("id", width=50, anchor="center")
        self.slots_tree.column("counselor", width=140)
        self.slots_tree.column("time", width=160)
        self.slots_tree.column("available", width=80, anchor="center")
        self.slots_tree.pack(fill="x", expand=False, padx=5, pady=5)

        slot_ctrl = tk.Frame(parent_frame)
        slot_ctrl.pack(pady=6)
        tk.Button(slot_ctrl, text="Refresh Slots", command=self.refresh_slots).pack(side="left", padx=5)
        tk.Button(slot_ctrl, text="Create Slot", command=self.create_slot_popup).pack(side="left", padx=5)
        tk.Button(slot_ctrl, text="Toggle Availability", command=self.toggle_slot_availability).pack(side="left", padx=5)
        tk.Button(slot_ctrl, text="Delete Slot", command=self.delete_selected_slot).pack(side="left", padx=5)

    def force_counselor_offline(self):
        selected_item = self.counselor_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a counselor to force offline.")
            return
        
        counselor_id = self.counselor_tree.item(selected_item[0], 'values')[0]
        
        try:
            cursor.execute("UPDATE counselors SET online_status = FALSE WHERE id = %s", (counselor_id,))
            conn.commit()
            messagebox.showinfo("Success", f"Counselor ID {counselor_id} forced offline.")
            self.refresh_bookings()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to force offline: {e}")

    def approve_selected_booking(self):
        sel = self.all_booking_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a booking to approve.")
            return
        booking_id = self.all_booking_tree.item(sel[0], 'values')[0]
        try:
            cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", ("Confirmed", booking_id))
            conn.commit()
            messagebox.showinfo("Success", f"Booking {booking_id} approved.")
            self.refresh_bookings()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve booking: {e}")

    def cancel_selected_booking(self):
        sel = self.all_booking_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a booking to cancel.")
            return
        booking_id = self.all_booking_tree.item(sel[0], 'values')[0]
        try:
            # Free the slot if linked
            cursor.execute("SELECT slot_id FROM bookings WHERE id = %s", (booking_id,))
            sres = cursor.fetchone()
            if sres and sres[0]:
                slot_id = sres[0]
                cursor.execute("UPDATE counselor_slots SET available = TRUE WHERE id = %s", (slot_id,))
            cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", ("Cancelled", booking_id))
            conn.commit()
            messagebox.showinfo("Success", f"Booking {booking_id} cancelled and slot freed.")
            self.refresh_bookings()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel booking: {e}")

    # --- Slot management methods ---
    def refresh_slots(self):
        # Clear existing
        for item in getattr(self, 'slots_tree', tk.Frame()).get_children():
            self.slots_tree.delete(item)
        if not conn:
            return
        try:
            cursor.execute("SELECT s.id, c.username, s.slot_time, s.available FROM counselor_slots s JOIN counselors c ON s.counselor_id = c.id ORDER BY s.slot_time DESC")
            rows = cursor.fetchall()
            for r in rows:
                sid, uname, st, avail = r
                time_str = st.strftime('%Y-%m-%d %H:%M') if hasattr(st, 'strftime') else str(st)
                avail_text = 'Yes' if avail else 'No'
                self.slots_tree.insert('', 'end', values=(sid, uname, time_str, avail_text))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load slots: {e}')

    def create_slot_popup(self):
        if not conn:
            messagebox.showerror('Error', 'Database not connected.')
            return
        popup = tk.Toplevel(self)
        popup.title('Create Slot')
        popup.geometry('400x220')

        tk.Label(popup, text='Select Counselor:').pack(pady=(8,0))
        cvar = tk.StringVar()
        cursor.execute('SELECT id, username FROM counselors ORDER BY username')
        counselors = cursor.fetchall()
        c_list = [f"{r[1]} (id:{r[0]})" for r in counselors]
        ccombo = ttk.Combobox(popup, values=c_list, textvariable=cvar, state='readonly')
        if c_list: ccombo.current(0)
        ccombo.pack(pady=6)

        tk.Label(popup, text='Slot Date (YYYY-MM-DD):').pack(pady=(6,0))
        try:
            date_entry = DateEntry(popup, width=16, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            date_entry.pack(pady=4)
        except Exception:
            date_text = tk.Entry(popup)
            date_text.pack(pady=4)

        tk.Label(popup, text='Hour (24h) and Minute:').pack(pady=(6,0))
        hr_var = tk.StringVar(value='10')
        mn_var = tk.StringVar(value='00')
        hr_spin = ttk.Combobox(popup, values=[str(i).zfill(2) for i in range(0,24)], textvariable=hr_var, width=4, state='readonly')
        mn_spin = ttk.Combobox(popup, values=['00','15','30','45'], textvariable=mn_var, width=4, state='readonly')
        hr_spin.pack(pady=2)
        mn_spin.pack(pady=2)

        def create_slot():
            sel = cvar.get()
            if not sel:
                messagebox.showwarning('Incomplete', 'Select a counselor.')
                return
            cid_match = re.search(r'id:(\d+)', sel)
            if not cid_match:
                messagebox.showerror('Error', 'Invalid counselor selection.')
                return
            cid = int(cid_match.group(1))
            try:
                if 'date_entry' in locals() and isinstance(date_entry, DateEntry):
                    d = date_entry.get_date().strftime('%Y-%m-%d')
                else:
                    d = date_text.get().strip()
                hour = int(hr_var.get())
                minute = int(mn_var.get())
                slot_dt = datetime.strptime(f"{d} {hour:02d}:{minute:02d}", '%Y-%m-%d %H:%M')
                cursor.execute('INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s,%s,%s)', (cid, slot_dt, True))
                conn.commit()
                popup.destroy()
                self.refresh_slots()
                messagebox.showinfo('Success', 'Slot created.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to create slot: {e}')

        tk.Button(popup, text='Create Slot', command=create_slot).pack(pady=10)

    def toggle_slot_availability(self):
        sel = self.slots_tree.selection()
        if not sel:
            messagebox.showwarning('Warning', 'Select a slot.')
            return
        sid = self.slots_tree.item(sel[0], 'values')[0]
        try:
            cursor.execute('SELECT available FROM counselor_slots WHERE id = %s', (sid,))
            r = cursor.fetchone()
            if not r:
                messagebox.showerror('Error', 'Slot not found.')
                return
            newv = not bool(r[0])
            cursor.execute('UPDATE counselor_slots SET available = %s WHERE id = %s', (newv, sid))
            conn.commit()
            self.refresh_slots()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to toggle: {e}')

    def delete_selected_slot(self):
        sel = self.slots_tree.selection()
        if not sel:
            messagebox.showwarning('Warning', 'Select a slot to delete.')
            return
        sid = self.slots_tree.item(sel[0], 'values')[0]
        try:
            # Prevent deleting if a booking references it
            cursor.execute('SELECT id FROM bookings WHERE slot_id = %s', (sid,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Cannot delete slot: it is referenced by an existing booking.')
                return
            cursor.execute('DELETE FROM counselor_slots WHERE id = %s', (sid,))
            conn.commit()
            self.refresh_slots()
            messagebox.showinfo('Deleted', f'Slot {sid} deleted.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to delete slot: {e}')

    def refresh_bookings(self):
        # Clear existing data
        for item in self.all_booking_tree.get_children(): self.all_booking_tree.delete(item)
        for item in self.counselor_tree.get_children(): self.counselor_tree.delete(item)

        if not conn: return
        
        try:
            # Load All Bookings
            cursor.execute("""
                SELECT b.id, b.user_id, c.username, b.booking_time, b.reason, b.status 
                FROM bookings b
                JOIN counselors c ON b.counselor_id = c.id
                ORDER BY b.booking_time DESC
            """)
            bookings = cursor.fetchall()
            for row in bookings:
                booking_id, user_id, c_name, b_time, reason, status = row
                time_str = b_time.strftime("%Y-%m-%d %H:%M")
                reason_preview = reason[:30] + "..." if len(reason) > 30 else reason
                self.all_booking_tree.insert("", "end", values=(booking_id, user_id, c_name, time_str, reason_preview, status))

            # Load Counselors
            cursor.execute("SELECT id, username, specialization, online_status, last_login FROM counselors")
            counselors = cursor.fetchall()
            for row in counselors:
                c_id, username, spec, status, last_login = row
                status_text = "Online" if status else "Offline"
                login_time = last_login.strftime("%Y-%m-%d %H:%M") if last_login else "Never"
                self.counselor_tree.insert("", "end", values=(c_id, username, spec, status_text, login_time))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load admin data: {e}")
        finally:
            # Refresh slots view if present
            try:
                self.refresh_slots()
            except Exception:
                pass

    def open_smtp_settings(self):
        try:
            SMTPConfigDialog(self)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open SMTP settings: {e}')

    # (The chart functions for the 'Anonymous Trends' tab remain as in the original code)
    
    def draw_stats(self, *_):
        if self.current_canvas: self.current_canvas.get_tk_widget().destroy()
        
        # NOTE: Using placeholder logic here to keep the code complete without full matplotlib implementation
        tk.Label(self.chart_frame, text=f"Displaying {self.chart_var.get()} (Conceptual Chart Area)", bg="#fff", font=("Arial", 14)).pack(pady=50)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.user_id = None
            self.app.username = None
            self.app.show_frame("LoginFrame")

# ------------------ AI Guided Chatbot / First-Aid ------------------
class ChatbotFrame(tk.Frame):
    def __init__(self, parent, app, set_theme_color_cb):
        super().__init__(parent, bg="#fff0f5")
        self.app = app
        self.set_theme_color_cb = set_theme_color_cb
        self.background_color = "#fff0f5"

        # --- NAME CHANGE ---
        self.header_label = tk.Label(self, text="Bhagvad Mood Journal: AI Support", font=("Georgia", 20, "bold"), fg="#b22222", bg=self.background_color)
        # --- END NAME CHANGE ---
        self.header_label.pack(pady=10)

        # --- STREAKS/MP DISPLAY ---
        self.streak_var = tk.StringVar(value="Log in to see your streak!")
        self.streak_label = tk.Label(self, textvariable=self.streak_var, font=("Arial", 14, "bold"), fg="#228B22", bg=self.background_color)
        self.streak_label.pack(pady=(0, 5))
        # --- END STREAKS/MP DISPLAY ---

        self.sub_label = tk.Label(self, text="Type a thought or feeling below for guidance and support.", font=("Arial", 12), bg=self.background_color)
        self.sub_label.pack()

        self.text_entry = scrolledtext.ScrolledText(self, height=8, width=90, font=("Arial", 12), wrap="word")
        self.text_entry.pack(padx=10, pady=8, fill="x", expand=True)

        tk.Button(self, text="Get Support", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=self.submit_thought).pack(pady=6)

        self.result_box = scrolledtext.ScrolledText(self, height=16, width=90, font=("Arial", 13), wrap="word", bg=self.background_color, state=tk.DISABLED)
        self.result_box.pack(pady=10, padx=10, fill="both", expand=True)

        self.btn_frame = tk.Frame(self, bg=self.background_color)
        self.btn_frame.pack(pady=10)

        tk.Button(self.btn_frame, text="View My Entries", font=("Arial", 12, "bold"), bg="#db7093", fg="white", command=lambda: app.show_frame("EntriesFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Screening Tools", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=lambda: app.show_frame("ScreeningsFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Spin Wheel", font=("Arial", 12, "bold"), bg="#87cefa", fg="black", command=lambda: app.show_frame("SpinWheelFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Rewards/Badges", font=("Arial", 12, "bold"), bg="#FFD56B", fg="#000000", command=lambda: app.show_frame("RewardsFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Resources Hub", font=("Arial", 12, "bold"), bg="#98fb98", fg="black", command=lambda: app.show_frame("ResourcesFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Book Counselor", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=lambda: app.show_frame("BookingFrame")).pack(side="left", padx=6)
        # tk.Button(self.btn_frame, text="Admin Dashboard", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=lambda: app.show_frame("AdminDashboardFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Peer Support", font=("Arial", 12, "bold"), bg="#98fb98", fg="black", command=lambda: app.show_frame("PeerSupportFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Period Journal", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=self.prompt_gender_and_redirect).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="To-Do List", font=("Arial", 12, "bold"), bg="#98fb98", fg="black", command=lambda: app.show_frame("ToDoNotesFrame")).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Logout", font=("Arial", 12, "bold"), bg="#db7093", fg="white", command=self.logout).pack(side="right", padx=10)

    def configure_colors(self, new_color):
        """Re-configures all widgets in the frame with the new background color."""
        self.config(bg=new_color)
        self.header_label.config(bg=new_color)
        self.sub_label.config(bg=new_color)
        self.result_box.config(bg=new_color)
        self.btn_frame.config(bg=new_color)
        self.streak_label.config(bg=new_color)
        self.background_color = new_color

    def update_streak_display(self):
        if self.app.user_id is None:
            self.streak_var.set("Log in to start journaling!")
            return

        current_date = date.today()
        last_date = self.app.last_journal_date
        current_streak = self.app.user_streak

        display_streak = current_streak

        if last_date is None:
            pass
        elif (current_date - last_date).days > 1:
            display_streak = 0
        elif (current_date - last_date).days == 1:
             display_streak = current_streak
        else:
             display_streak = current_streak

        self.streak_var.set(f"🔥 Current Streak: {display_streak} Day(s) | ✨ Points: {self.app.mindful_points}")


    def submit_thought(self):
        thought = self.text_entry.get("1.0", tk.END).strip()
        if not thought:
            messagebox.showwarning("Warning", "Please enter some thought text.")
            return
        if self.app.user_id is None:
            messagebox.showerror("Login Required", "Please log in to submit a journal entry.")
            return

        mood, context, shlok_tuple, polarity, subjectivity = get_sentiment_enhanced(thought)
        shlok, meaning = shlok_tuple
        result = analyze_and_reframe(thought, mood, context)

        new_color = MOOD_COLORS.get(mood, {"calm": RELAXING_COLOR}).get("calm", RELAXING_COLOR)
        self.set_theme_color_cb(new_color)

        # Remove asterisks from reframed text and insight
        reframed_clean = result['reframed_text'].replace("*", "") if result['reframed_text'] else ""

        display_text = ""

        # --- 1. CRISIS & RISK CHECK (Risk Monitoring Over Time) ---
        risk_level = result['risk_level']

        # Immediate Crisis Alert (Risk Level 'high')
        if risk_level == "high":
            display_text = result['message']

        else:
            # Check for escalating risk pattern
            risk_escalation_alert = ""
            if check_risk_escalation(self.app.user_id):
                risk_escalation_alert = (
                    "🚨 **Sustained Risk Alert:** We've detected a pattern of high distress over the past two weeks. "
                    "We strongly recommend you reach out to a professional now. Consider the **Book Counselor** feature."
                )

            # Check for mood clustering (Mood Clustering & Trend Feedback)
            trend_feedback = check_recent_mood_trends(self.app.user_id)

            # Construct the standard display text
            display_text = (
                f"🌟 Thought Successfully Submitted\n\n"
                f"💬 Mood Detected : {mood.upper()} \n (Risk Level: {risk_level.title()})\n\n"
                f"📜 Bhagavad Gita Shlok:\n"
                f"{shlok}\n\n"
                "Meaning: \n"
                f"{meaning}\n\n"
                f"🧠 Bhagvad Mood Insight: \n{reframed_clean}\n\n"
            )

            if risk_escalation_alert:
                display_text += f"\n\n---\n{risk_escalation_alert}\n---"

            if trend_feedback:
                display_text += f"\n\n---\n{trend_feedback}\n---"

            display_text += f"\n\nWe are here to help. If you need more support, consider booking a session with a professional."

        # --- 2. DB LOGGING AND GAMIFICATION ---
        try:
            timestamp = datetime.now()

            # Save the entry with the calculated risk level
            cursor.execute("""
                INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp, risk_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.app.user_id, self.app.username, mood, thought, shlok, meaning, timestamp, risk_level))

            # Streak/MP Update Logic (Only if not already submitted today)
            points_awarded = 0
            current_date = date.today()

            if self.app.last_journal_date != current_date:
                # 2.1 STREAK CALCULATION
                new_streak = 1
                if self.app.last_journal_date is not None and (current_date - self.app.last_journal_date).days == 1:
                    new_streak = self.app.user_streak + 1

                # 2.2 MP AWARD
                points_awarded += 10 # 10 MP for journal entry

                # Check for streak milestone rewards
                if new_streak in STREAK_BADGES and new_streak > self.app.user_streak:
                    points_awarded += 50
                    messagebox.showinfo("Achievement Unlocked!", f"Congratulations! You earned the '{STREAK_BADGES[new_streak]}' badge and 50 MP!")

                # Update user object properties
                self.app.user_streak = new_streak
                self.app.last_journal_date = current_date

            self.app.mindful_points += points_awarded

            # 3. Commit user metadata (points and streak)
            cursor.execute("""
                UPDATE users SET
                    journal_streak = %s,
                    last_journal_date = %s,
                    mindful_points = %s
                WHERE id = %s
            """, (self.app.user_streak, self.app.last_journal_date, self.app.mindful_points, self.app.user_id))

            conn.commit()

            if points_awarded > 0:
                 messagebox.showinfo("Points Awarded", f"You earned {points_awarded} Mindful Points (MP) for today's entry!")

            self.update_streak_display()

            self.result_box.config(state=tk.NORMAL)
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, display_text)
            self.result_box.config(state=tk.DISABLED)
            self.text_entry.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process thought or update database: {e}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.user_id = None
            self.app.username = None
            self.app.user_gender = None
            self.app.user_streak = 0
            self.app.last_journal_date = None
            self.app.mindful_points = 0
            self.set_theme_color_cb("#fffaf0")
            self.app.show_frame("LoginFrame")

    def prompt_gender_and_redirect(self):
        """Prompts male users before accessing the period journal."""
        user_gender = getattr(self.app, 'user_gender', None)
        if user_gender and user_gender.lower() == 'female':
            self.app.show_frame("PeriodJournalFrame")
        else:
            response = messagebox.askyesno("Track Period Journal", "This feature is for tracking a woman's menstrual cycle. Would you like to enter details for a female user?")
            if response:
                self.app.show_frame("PeriodJournalFrame")

# ------------------ Psychological Screening Tools (PHQ-9 & GAD-7) ------------------
class ScreeningsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0f8ff")
        self.app = app

        top = tk.Frame(self, bg="#f0f8ff")
        top.pack(fill="x", pady=10)
        tk.Label(top, text="Psychological Screening Tools", font=("Georgia", 18, "bold"), fg="#2f4f4f", bg="#f0f8ff").pack(side="left", padx=10)
        tk.Button(top, text="Back to Chatbot", command=lambda: app.show_frame("ChatbotFrame")).pack(side="right", padx=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # PHQ-9 Tab (Depression)
        self.phq9_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.phq9_frame, text="PHQ-9 (Depression)")
        self.phq9_scroll = scrolledtext.ScrolledText(self.phq9_frame, wrap="word", bg="#ffffff")
        self.phq9_scroll.pack(fill="both", expand=True)
        self.phq9_inner_frame = tk.Frame(self.phq9_scroll, bg="#ffffff")
        self.phq9_scroll.window_create(tk.END, window=self.phq9_inner_frame)
        self.phq9_score_vars = self._build_screening_form(self.phq9_inner_frame, PHQ9_QUESTIONS, "PHQ-9", PHQ9_SCORES)

        # GAD-7 Tab (Anxiety)
        self.gad7_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.gad7_frame, text="GAD-7 (Anxiety)")
        self.gad7_scroll = scrolledtext.ScrolledText(self.gad7_frame, wrap="word", bg="#ffffff")
        self.gad7_scroll.pack(fill="both", expand=True)
        self.gad7_inner_frame = tk.Frame(self.gad7_scroll, bg="#ffffff")
        self.gad7_scroll.window_create(tk.END, window=self.gad7_inner_frame)
        self.gad7_score_vars = self._build_screening_form(self.gad7_inner_frame, GAD7_QUESTIONS, "GAD-7", GAD7_SCORES)

    def _build_screening_form(self, parent_frame, questions, tool_name, score_map):
        score_vars = []
        options = ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]

        tk.Label(parent_frame, text=f"**{tool_name}**: Over the last 2 weeks, how often have you been bothered by the following problems?",
                 font=("Arial", 12, "bold"), bg="#ffffff", wraplength=700).pack(pady=10)

        for i, question in enumerate(questions):
            question_frame = tk.LabelFrame(parent_frame, text=f"Question {i+1}", padx=10, pady=5, bg="#f9f9f9")
            question_frame.pack(fill="x", padx=5, pady=5)

            tk.Label(question_frame, text=question, wraplength=650, justify="left", bg="#f9f9f9").pack(anchor="w")

            var = tk.IntVar(value=0)
            score_vars.append(var)

            option_frame = tk.Frame(question_frame, bg="#f9f9f9")
            option_frame.pack(fill="x")

            for score, option in enumerate(options):
                tk.Radiobutton(option_frame, text=option, variable=var, value=score, bg="#f9f9f9").pack(side="left", padx=5)

        submit_btn = tk.Button(parent_frame, text=f"Submit {tool_name} Score", font=("Arial", 14, "bold"), bg="#ff69b4", fg="white", command=lambda: self.submit_score(tool_name, score_vars, score_map))
        submit_btn.pack(pady=20)

        return score_vars

    def submit_score(self, tool_name, score_vars, score_map):
        if self.app.user_id is None:
            messagebox.showerror("Error", "Please log in to submit a screening.")
            return

        total_score = sum(var.get() for var in score_vars)
        risk_level = "Unknown"
        level_text = "N/A"
        max_score = len(score_vars) * 3

        for (min_score, max_val), level in sorted(score_map.items()):
            if min_score <= total_score <= max_val:
                risk_level = level.split(" (")[1].replace(")", "")
                level_text = level.split(" (")[0]
                break

        # Log to Database
        try:
            cursor.execute("""
                INSERT INTO screenings (user_id, timestamp, tool_name, score, risk_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.app.user_id, datetime.now(), tool_name, total_score, risk_level))
            conn.commit()

            # Show results in a pop-up (Required Enhancement)
            messagebox.showinfo(
                f"{tool_name} Screening Results",
                f"--- Results Saved ---\n\n"
                f"Total Score: {total_score}/{max_score}\n"
                f"Classification: **{level_text}**\n"
                f"Risk Level: {risk_level}\n\n"
                f"Note: This tool is for informational purposes only. Consult a professional for diagnosis."
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to log score: {e}")

# ------------------ Rewards and Badges System ------------------
class RewardsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fffaf0")
        self.app = app

        tk.Label(self, text="🌟 Your Achievements & Points 🌟", font=("Georgia", 20, "bold"), fg="#b22222", bg="#fffaf0").pack(pady=10)
        tk.Button(self, text="Back to Chatbot", command=lambda: app.show_frame("ChatbotFrame")).pack(anchor="ne", padx=10, pady=5)

        self.points_var = tk.StringVar()
        self.points_label = tk.Label(self, textvariable=self.points_var, font=("Arial", 16, "bold"), bg="#F5F5DC", fg="#FF914D")
        self.points_label.pack(pady=10, padx=20, fill="x")

        self.streak_var = tk.StringVar()
        self.streak_label = tk.Label(self, textvariable=self.streak_var, font=("Arial", 14), bg="#fffaf0")
        self.streak_label.pack(pady=5)

        tk.Label(self, text="--- Earned Badges ---", font=("Arial", 14, "underline"), bg="#fffaf0").pack(pady=(20, 10))

        self.badges_box = scrolledtext.ScrolledText(self, height=10, width=80, wrap="word", bg="#ffffff")
        self.badges_box.pack(padx=20, pady=10, fill="x")
        self.badges_box.config(state=tk.DISABLED)

    def update_display(self):
        if self.app.user_id is None:
            self.points_var.set("Please log in to view rewards.")
            return

        current_points = self.app.mindful_points
        current_streak = self.app.user_streak

        self.points_var.set(f"✨ Total Mindful Points (MP): {current_points}")
        self.streak_var.set(f"🔥 Current Journaling Streak: {current_streak} Day(s)")

        earned_badges = []

        # Check MP Tiers
        for threshold, name in sorted(MP_REWARD_TIERS.items()):
            if current_points >= threshold:
                earned_badges.append(f"⭐ {name} (MP >= {threshold})")

        # Check Streak Badges
        for threshold, name in sorted(STREAK_BADGES.items()):
            if current_streak >= threshold:
                earned_badges.append(f"🗓️ {name} (Streak >= {threshold})")

        self.badges_box.config(state=tk.NORMAL)
        self.badges_box.delete("1.0", tk.END)
        if earned_badges:
            self.badges_box.insert(tk.END, "\n".join(earned_badges))
        else:
            self.badges_box.insert(tk.END, "Keep journaling! Your first badge awaits at 7 days or 50 MP.")
        self.badges_box.config(state=tk.DISABLED)


# ------------------ Psychoeducational Resource Hub ------------------
class ResourcesFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Curated, reliable resources (videos, audio, official guides)
        # Replace all hub links with YouTube search links for the given topic/title
        def yt_search(q):
            return "https://www.youtube.com/results?search_query=" + q.replace(' ', '+')

        self.resource_links = {
            "Official": [
                {"title": "WHO — Mental Health Overview (YouTube Search)", "link": yt_search("WHO mental health overview")},
                {"title": "NIMHANS — Lectures & Resources (YouTube Search)", "link": yt_search("NIMHANS mental health lectures")},
                {"title": "Ministry of Health India — Mental Health (YouTube Search)", "link": yt_search("mental health ministry of india")},
                {"title": "NIMH (USA) — Public Info (YouTube Search)", "link": yt_search("NIMH mental health resources")},
                {"title": "Samaritans — Support & Helplines (YouTube Search)", "link": yt_search("Samaritans mental health support")},
                {"title": "Mind.org.uk — Support Videos (YouTube Search)", "link": yt_search("Mind charity mental health videos")}
            ],
            "Videos": [
                {"title": "Managing Exam Stress — Practical Tips", "link": yt_search("managing exam stress tips video")},
                {"title": "Recognizing Burnout — Talk", "link": yt_search("recognizing burnout talk video")},
                {"title": "Mindfulness Meditation — Guided (10 min)", "link": yt_search("10 minute guided mindfulness meditation")},
                {"title": "UCLA Mindful Awareness — Guided Meditations", "link": yt_search("UCLA mindful meditations guided")},
                {"title": "Improving Sleep Hygiene — Advice", "link": yt_search("sleep hygiene tips video")},
                {"title": "Self-Compassion — Guided Practice", "link": yt_search("self compassion guided meditation kristin neff")},
                {"title": "Breathing Exercises for Anxiety", "link": yt_search("breathing exercises for anxiety video")}
            ],
            "Audio": [
                {"title": "Guided Meditation (5 Mins)", "link": yt_search("5 minute guided meditation audio")},
                {"title": "Forest Rain Soundscape", "link": yt_search("forest rain soundscape relaxing audio")},
                {"title": "Ocean Waves for Sleep", "link": yt_search("ocean waves sleep audio")},
                {"title": "Deep Sleep Music — Relaxing", "link": yt_search("deep sleep relaxing music")},
                {"title": "Morning Motivation Audio", "link": yt_search("morning motivation audio")}
            ],
            "Guides": [
                {"title": "NHS Self-Help — Techniques (YouTube Search)", "link": yt_search("NHS self help anxiety depression")},
                {"title": "Mind.org.uk — Coping Guides (YouTube Search)", "link": yt_search("mind coping with anxiety video")},
                {"title": "WHO Mental Health Guidance — Videos", "link": yt_search("WHO mental health guidance video")},
                {"title": "Psychology Tools — Worksheets & How-tos (YouTube Search)", "link": yt_search("psychology tools worksheets CBT")}
            ],
            "Books": [
                {"title": "The Happiness Trap — Russ Harris (Talks)", "link": yt_search("The Happiness Trap Russ Harris talk")},
                {"title": "The Power of Now — Eckhart Tolle (Lectures)", "link": yt_search("The Power of Now Eckhart Tolle talk")},
                {"title": "Feeling Good — David D. Burns (CBT)", "link": yt_search("Feeling Good David Burns CBT")},
                {"title": "Atomic Habits — James Clear (Summary)", "link": yt_search("Atomic Habits summary James Clear")}
            ],
            "Regional": [
                {"title": "Hindi Mindfulness / Relaxation", "link": yt_search("mindfulness meditation hindi")},
                {"title": "Tamil Guided Relaxation", "link": yt_search("guided relaxation tamil")},
                {"title": "Bengali Relaxation", "link": yt_search("meditation bengali")},
                {"title": "Marathi Relaxation", "link": yt_search("meditation marathi")},
                {"title": "Punjabi Guided Meditation", "link": yt_search("guided meditation punjabi")}
            ]
        }

        header = tk.Frame(self, bg="#fff")
        header.pack(fill="x")
        tk.Label(header, text="Psychoeducational Resource Hub", font=("Georgia", 18, "bold"), bg="#fff").pack(padx=12, pady=8, side="left")
        tk.Button(header, text="Back", command=lambda: app.show_frame("ChatbotFrame")).pack(side="right", padx=12, pady=8)

        self.main_nb = ttk.Notebook(self)
        self.main_nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Use standard tk.Frame for color customization within the Notebook
        self.ai_rec_frame = tk.Frame(self.main_nb)
        self.goals_frame = tk.Frame(self.main_nb)
        self.screenings_frame = tk.Frame(self.main_nb)
        self.wellness_frame = tk.Frame(self.main_nb)
        self.guides_frame = tk.Frame(self.main_nb)
        self.videos_frame = tk.Frame(self.main_nb)
        self.audio_frame = tk.Frame(self.main_nb)
        self.regional_frame = tk.Frame(self.main_nb)
        self.community_frame = tk.Frame(self.main_nb)

        # Tab Ordering
        self.main_nb.add(self.ai_rec_frame, text="AI Recommendations")
        self.main_nb.add(self.guides_frame, text="Info Guides")
        self.main_nb.add(self.goals_frame, text="Mini-Goals/Coping")
        self.main_nb.add(self.screenings_frame, text="Screening Info")
        self.main_nb.add(self.wellness_frame, text="General Wellness")
        self.main_nb.add(self.videos_frame, text="Videos")
        self.main_nb.add(self.audio_frame, text="Relaxation Audio")
        self.main_nb.add(self.regional_frame, text="Regional Resources")
        self.main_nb.add(self.community_frame, text="Community Forum")

        # Populate Tabs
        self.populate_ai_recommendations(self.ai_rec_frame)
        self.populate_guides(self.guides_frame)
        self.populate_videos(self.videos_frame)
        self.populate_audio(self.audio_frame)
        self.populate_regional(self.regional_frame)
        self.populate_screening_info(self.screenings_frame)
        self.populate_mini_goals(self.goals_frame)
        self.populate_general_wellness(self.wellness_frame)

        self.community_list_box = scrolledtext.ScrolledText(self.community_frame, wrap="word", bg="#fff")
        self.community_list_box.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(self.community_frame, text="Submit Your Resource", command=self.submit_resource).pack(pady=5)
        self.refresh_community_resources()

    def open_link(self, url):
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {e}")

    def populate_guides(self, frame):
        frame.config(bg="#f9fff2")
        tk.Label(frame, text="Self-Care Tips", font=("Arial", 14, "bold"), bg="#f9fff2").pack(pady=(8,2))
        tips_box = scrolledtext.ScrolledText(frame, height=8, wrap="word", bg="#ffffff")
        tips = [
            "- Try 5 minutes of focused breathing when anxious.",
            "- Break tasks into 25-minute focused blocks (Pomodoro).",
            "- Keep a short gratitude list each night.",
            "- Use a warm compress for body aches and cramps.",
            "- Reach out to one trusted person when low.",
            "- Practice digital detox for 1 hour daily.",
            "- Take a mindful walk and notice your surroundings.",
            "- Listen to calming music or nature sounds.",
            "- Write down 3 things you did well today.",
            "- Drink a glass of water and stretch every hour.",
            "- Visit a new place on campus or in your city for a change of scene.",
            "- Try a new hobby or creative activity this week.",
            "- Journal your thoughts before bed to clear your mind.",
            "- Practice saying 'no' to protect your boundaries.",
            "- Spend 10 minutes in sunlight each morning.",
        ]
        tips_box.insert(tk.END, "\n".join(tips))
        tips_box.config(state=tk.DISABLED)
        tips_box.pack(padx=8, pady=6)

        tk.Label(frame, text="Inspiring Quotes", font=("Arial", 14, "bold"), bg="#f9fff2").pack(pady=(8,2))
        quotes_box = scrolledtext.ScrolledText(frame, height=6, wrap="word", bg="#ffffff")
        quotes = [
            '"You are braver than you believe." — A.A. Milne',
            '"Small steps every day."',
            '"Tend to yourself like a garden."',
            '"The darkest night will end and the sun will rise."',
            '"Progress, not perfection."',
            '"You have survived 100% of your worst days."',
            '"Change your place, change your mind."',
            '"Peace comes from within. Do not seek it without." — Buddha',
            '"You are enough, just as you are."',
            '"Let your hopes, not your hurts, shape your future." — Robert H. Schuller',
            '"The only way out is through." — Robert Frost',
        ]
        quotes_box.insert(tk.END, "\n".join(quotes))
        quotes_box.config(state=tk.DISABLED)
        quotes_box.pack(padx=8, pady=6)

        # Add a section for recommended books
        tk.Label(frame, text="Recommended Books", font=("Arial", 14, "bold"), bg="#f9fff2").pack(pady=(8,2))
        books_box = scrolledtext.ScrolledText(frame, height=4, wrap="word", bg="#ffffff")
        books = [
            "- 'The Bhagavad Gita' (any translation)",
            "- 'The Happiness Trap' by Russ Harris",
            "- 'Atomic Habits' by James Clear",
            "- 'The Gifts of Imperfection' by Brené Brown",
            "- 'Ikigai: The Japanese Secret to a Long and Happy Life' by Héctor García and Francesc Miralles",
            "- 'Man’s Search for Meaning' by Viktor Frankl",
            "- 'The Power of Now' by Eckhart Tolle",
        ]
        books_box.insert(tk.END, "\n".join(books))
        books_box.config(state=tk.DISABLED)
        books_box.pack(padx=8, pady=6)

    def populate_videos(self, frame):
        frame.config(bg="#e8f4f8")
        tk.Label(frame, text="Mental Wellness Videos (Click to Open in Browser)", font=("Arial", 14, "bold"), bg="#e8f4f8").pack(pady=(8,2))

        for resource in self.resource_links["Videos"]:
            btn = tk.Button(frame, text=f"🎥 {resource['title']}",
                            command=lambda url=resource['link']: self.open_link(url),
                            bg="#ADD8E6", fg="black", anchor="w", relief="flat")
            btn.pack(fill="x", padx=15, pady=2)

        # Add a search bar for YouTube
        search_frame = tk.Frame(frame, bg="#e8f4f8")
        search_frame.pack(pady=8)
        tk.Label(search_frame, text="Search YouTube:", bg="#e8f4f8").pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, width=30).pack(side="left", padx=5)
        def search_youtube():
            query = search_var.get().strip()
            if query:
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                self.open_link(url)
        tk.Button(search_frame, text="Go", command=search_youtube).pack(side="left")

    def populate_audio(self, frame):
        frame.config(bg="#f8e8f4")
        tk.Label(frame, text="Relaxation Audio Guides (Click to Open in Browser)", font=("Arial", 14, "bold"), bg="#f8e8f4").pack(pady=(8,2))

        for resource in self.resource_links["Audio"]:
            btn = tk.Button(frame, text=f"🎧 {resource['title']}",
                            command=lambda url=resource['link']: self.open_link(url),
                            bg="#F0E68C", fg="black", anchor="w", relief="flat")
            btn.pack(fill="x", padx=15, pady=2)

        # Add a section for free meditation apps
        tk.Label(frame, text="Free Meditation Apps", font=("Arial", 13, "bold"), bg="#f8e8f4").pack(pady=(10,2))
        apps_box = scrolledtext.ScrolledText(frame, height=3, wrap="word", bg="#ffffff")
        apps = [
            "- Insight Timer (Android/iOS)",
            "- Smiling Mind (Android/iOS)",
            "- Medito (Android/iOS)",
            "- Calm (Android/iOS, free trial)",
            "- Headspace (Android/iOS, free trial)",
            "- Sadhguru App (Guided Yoga & Meditation)",
        ]
        apps_box.insert(tk.END, "\n".join(apps))
        apps_box.config(state=tk.DISABLED)
        apps_box.pack(padx=8, pady=6)


    def populate_regional(self, frame):
        frame.config(bg="#f2f9ff")
        tk.Label(frame, text="Regional Guides & Audio", font=("Arial", 14, "bold"), bg="#f2f9ff").pack(pady=10)
        tk.Label(frame, text="Explore wellness resources in your language or region. (Feature demonstration)", wraplength=400, justify="left", bg="#f2f9ff").pack(padx=20, pady=5)
        tk.Label(frame, text="Hindi: https://www.youtube.com/results?search_query=mindfulness+meditation+hindi\nTamil: https://www.youtube.com/results?search_query=meditation+tamil\nBengali: https://www.youtube.com/results?search_query=meditation+bengali\nMarathi: https://www.youtube.com/results?search_query=meditation+marathi\nPunjabi: https://www.youtube.com/results?search_query=meditation+punjabi", wraplength=400, justify="left", bg="#f2f9ff").pack(padx=20, pady=5)
        tk.Label(frame, text="Regional Helplines:\n- Tele MANAS (Hindi): 14416\n- Tamil Nadu Helpline: 104\n- West Bengal Helpline: 1800-258-8999", wraplength=400, justify="left", bg="#f2f9ff").pack(padx=20, pady=5)

    def populate_screening_info(self, frame):
        frame.config(bg="#f0f8ff")
        tk.Label(frame, text="Screening Tools Information", font=("Arial", 14, "bold"), bg="#f0f8ff").pack(pady=10)

        info_text = (
            "We offer validated screenings (PHQ-9 for Depression, GAD-7 for Anxiety).\n\n"
            "Purpose: These tools help you objectively track your symptoms over time and communicate your needs to a professional.\n\n"
            "Risk Levels (General):\n"
            "Minimal: Low risk.\n"
            "Mild/Moderate: Suggests seeking external advice.\n"
            "Severe: High risk, requires immediate professional intervention."
            "You can take these screenings in the app and view your results and trends over time. Always consult a professional for diagnosis."
        )
        tk.Label(frame, text=info_text, justify="left", wraplength=500, bg="#ffffff", bd=1, relief="solid").pack(padx=15, pady=10)
        tk.Button(frame, text="Take A Screening Test", command=lambda: self.app.show_frame("ScreeningsFrame"), font=("Arial", 12, "bold"), bg="#ff69b4", fg="white").pack(pady=10)

    def populate_mini_goals(self, frame):
        frame.config(bg="#e6f0ff")
        tk.Label(frame, text="Mood-Based Mini-Goals", font=("Arial", 14, "bold"), bg="#e6f0ff").pack(pady=10)

        goal_text = ""
        for mood, data in MINI_GOALS.items():
            goal_text += f"**{mood.title()}**:\n- Goal: {data['goal']}\n- Reward: {data['reward']} MP\n\n"

        tk.Label(frame, text="These small tasks are automatically suggested in your journal when a negative mood is detected. Complete them and mark a task done in your To-Do list to earn Mindful Points!\n\n" + goal_text, justify="left", wraplength=500, bg="#ffffff", bd=1, relief="solid").pack(padx=15, pady=10)
        tk.Label(frame, text="Other Coping Ideas:", font=("Arial", 13, "bold"), bg="#e6f0ff").pack(pady=(10,2))
        coping_box = scrolledtext.ScrolledText(frame, height=5, wrap="word", bg="#ffffff")
        coping_ideas = [
            "- Try a 10-minute walk outdoors.",
            "- Call or text a friend just to say hello.",
            "- Write a letter to your future self.",
            "- Draw, paint, or do something creative.",
            "- Listen to your favorite uplifting song.",
            "- Try a new recipe or cook your favorite meal.",
            "- Organize your study/work space.",
            "- Practice a random act of kindness.",
        ]
        coping_box.insert(tk.END, "\n".join(coping_ideas))
        coping_box.config(state=tk.DISABLED)
        coping_box.pack(padx=8, pady=6)

    def populate_general_wellness(self, frame):
        frame.config(bg="#ffffe0")
        tk.Label(frame, text="General Wellness & Tracking", font=("Arial", 14, "bold"), bg="#ffffe0").pack(pady=10)

        info_text = (
            "Period Tracking: Use the Period Journal to log cycles, symptoms, and moods, which helps you understand hormonal influences on your mental health.\n\n"
            "Mindful Points (MP): Your wellness effort is rewarded! Earn MP for consistent journaling and completing coping strategies.\n\n"
            "Peer Support: Connect with the anonymous community forum to share struggles and offer support to others.\n\n"
            "Change of Place: For a fresh mind, try visiting a new place on campus, a park, or a quiet café. Sometimes a change of environment can help reset your mood.\n\n"
            "Other Wellness Tips:\n- Stay hydrated and eat balanced meals.\n- Get 7-8 hours of sleep each night.\n- Limit screen time before bed.\n- Practice gratitude daily.\n- Set small, achievable goals for yourself.\n- Take breaks and stretch during long study/work sessions.\n- Seek help when you need it—asking for support is a sign of strength."
        )
        tk.Label(frame, text=info_text, justify="left", wraplength=500, bg="#ffffff", bd=1, relief="solid").pack(padx=15, pady=10)
        tk.Button(frame, text="Go To Period Journal", command=lambda: self.app.frames["ChatbotFrame"].prompt_gender_and_redirect(), font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222").pack(pady=5)

    def submit_resource(self):
        popup = tk.Toplevel(self.app)
        popup.title("Submit a Resource")
        popup.geometry("400x300")
        tk.Label(popup, text="Title:", padx=5, pady=5).grid(row=0, column=0, sticky="w")
        title_entry = tk.Entry(popup)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(popup, text="Description:", padx=5, pady=5).grid(row=1, column=0, sticky="w")
        desc_text = scrolledtext.ScrolledText(popup, height=8)
        desc_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(popup, text="Submit", command=lambda: self._save_resource(title_entry.get(), desc_text.get("1.0", tk.END), popup)).grid(row=2, columnspan=2, pady=10)

    def _save_resource(self, title, description, popup):
        if not title or not description:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return
        if not conn:
            messagebox.showerror("Error", "Database is not connected.")
            return
        try:
            cursor.execute("""
                INSERT INTO user_resources (user_id, username, resource_type, title, description, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.app.user_id, self.app.username, "Community Suggestion", title, description, datetime.now()))
            conn.commit()
            messagebox.showinfo("Success", "Resource submitted.")
            self.refresh_community_resources()
            popup.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to submit resource: {err}")

    def refresh_community_resources(self, *_):
        self.community_list_box.config(state=tk.NORMAL)
        self.community_list_box.delete("1.0", tk.END)
        if not conn:
            self.community_list_box.insert(tk.END, "Database is not connected. Cannot fetch resources.")
            self.community_list_box.config(state=tk.DISABLED)
            return
        try:
            cursor.execute("SELECT resource_type, title, description, username FROM user_resources ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            if rows:
                for r in rows:
                    self.community_list_box.insert(tk.END, f"[{r[0]}] - {r[1]} (by: {r[3]})\n", "category")
                    self.community_list_box.insert(tk.END, f"  {r[2]}\n\n")
            else:
                self.community_list_box.insert(tk.END, "No community resources submitted yet. Be the first to share!")
        except mysql.connector.Error as err:
            self.community_list_box.insert(tk.END, f"Error fetching resources: {err}")
        self.community_list_box.config(state=tk.DISABLED)

    def update_display(self):
        self.refresh_ai_recommendations()
        self.refresh_community_resources()

    def populate_ai_recommendations(self, frame):
        frame.config(bg="#f4f6f9")
        
        # Title
        tk.Label(frame, text="AI Personalized Resource Recommendations", font=("Georgia", 16, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=10)
        tk.Label(frame, text="Our Keras-based neural network model analyzes your age, gender, screening scores, and recent journal mood history to suggest the most appropriate resource class.", wraplength=500, justify="center", font=("Arial", 10, "italic"), bg="#f4f6f9", fg="#7f8c8d").pack(pady=(0, 15))
        
        # Display Card Frame
        self.ai_card = tk.Frame(frame, bd=2, relief="groove", padx=20, pady=20)
        self.ai_card.pack(pady=15, padx=25, fill="both", expand=True)
        
        self.ai_rec_title = tk.Label(self.ai_card, text="Fetching Recommendations...", font=("Arial", 14, "bold"))
        self.ai_rec_title.pack(pady=5)
        
        self.ai_rec_desc = tk.Label(self.ai_card, text="Please make sure you have submitted at least one journal entry and completed anxiety/depression screenings for best recommendations.", wraplength=450, justify="center", font=("Arial", 11))
        self.ai_rec_desc.pack(pady=10)
        
        self.ai_rec_stats = tk.Label(self.ai_card, text="", font=("Courier", 9, "italic"), fg="#555")
        self.ai_rec_stats.pack(pady=5)

        self.ai_rec_btn = tk.Button(self.ai_card, text="Explore Suggested Resource", font=("Arial", 11, "bold"), command=lambda: None)
        self.ai_rec_btn.pack(pady=10)
        
        # Trigger button to manually re-run
        tk.Button(frame, text="Re-analyze My Metrics", font=("Arial", 10), command=self.refresh_ai_recommendations, bg="#7f8c8d", fg="white").pack(pady=5)

    def refresh_ai_recommendations(self):
        if self.app.user_id is None:
            self.ai_rec_title.config(text="Authentication Required", fg="red")
            self.ai_rec_desc.config(text="Please log in as a user to view personalized AI wellness recommendations.")
            self.ai_rec_btn.pack_forget()
            return
            
        import wellness_ml
        
        try:
            # 1. Fetch user demographics
            cursor.execute("SELECT age, gender FROM users WHERE id = %s", (self.app.user_id,))
            row = cursor.fetchone()
            age = row[0] if row and row[0] is not None else 25
            gender = row[1] if row and row[1] is not None else "not_specified"
            
            # 2. Fetch latest screening scores
            cursor.execute("SELECT score FROM screenings WHERE user_id = %s AND tool_name = 'PHQ-9' ORDER BY timestamp DESC LIMIT 1", (self.app.user_id,))
            phq_row = cursor.fetchone()
            phq = phq_row[0] if phq_row else 0
            
            cursor.execute("SELECT score FROM screenings WHERE user_id = %s AND tool_name = 'GAD-7' ORDER BY timestamp DESC LIMIT 1", (self.app.user_id,))
            gad_row = cursor.fetchone()
            gad = gad_row[0] if gad_row else 0
            
            # 3. Fetch last 5 journal thoughts to calculate mood polarity
            cursor.execute("SELECT thought FROM journal WHERE user_id = %s ORDER BY timestamp DESC LIMIT 5", (self.app.user_id,))
            thoughts = cursor.fetchall()
            
            polarities = []
            if thoughts:
                for t_row in thoughts:
                    thought_text = t_row[0] or ""
                    _, _, _, pol, _ = get_sentiment_enhanced(thought_text)
                    polarities.append(pol)
                avg_pol = sum(polarities) / len(polarities)
            else:
                avg_pol = 0.0
                
            # Run model prediction
            class_idx, probs = wellness_ml.recommend_resource(age, gender, phq, gad, avg_pol)
            
            # Update display based on predicted class
            classes_details = {
                0: {
                    "title": "Recommended: Self-Care & Info Guides",
                    "desc": f"Your current metrics (PHQ-9: {phq}, GAD-7: {gad}, Mood: {avg_pol:.2f}) indicate stable emotional patterns. We recommend reviewing our self-care guides, breathing techniques, and practice saying 'no' to protect boundaries.",
                    "btn_text": "Go to Info Guides Tab",
                    "bg": "#e8f5e9",
                    "fg": "#2e7d32",
                    "btn_bg": "#81c784",
                    "action": lambda: self.main_nb.select(self.guides_frame)
                },
                1: {
                    "title": "Recommended: Stress Management Videos",
                    "desc": f"Your stress indicators are slightly elevated (PHQ-9: {phq}, GAD-7: {gad}). Watching expert-guided videos on managing exam burnout and breathing techniques can provide immediate relief.",
                    "btn_text": "Go to Videos Tab",
                    "bg": "#e3f2fd",
                    "fg": "#1565c0",
                    "btn_bg": "#64b5f6",
                    "action": lambda: self.main_nb.select(self.videos_frame)
                },
                2: {
                    "title": "Recommended: Relaxation Audio & Meditation",
                    "desc": f"Your logs suggest a high degree of tension or anxiety (PHQ-9: {phq}, GAD-7: {gad}, Mood: {avg_pol:.2f}). We highly recommend taking a break to listen to Forest Rain Soundscapes or doing a 10-minute guided mindfulness meditation.",
                    "btn_text": "Go to Relaxation Audio Tab",
                    "bg": "#f3e5f5",
                    "fg": "#6a1b9a",
                    "btn_bg": "#ba68c8",
                    "action": lambda: self.main_nb.select(self.audio_frame)
                },
                3: {
                    "title": "Recommended: Book a Counselor Session",
                    "desc": f"Your screening results indicate a severe clinical risk level (PHQ-9: {phq}, GAD-7: {gad}, Mood: {avg_pol:.2f}). Please consider taking a private, anonymous session with our certified professional counselors for guidance.",
                    "btn_text": "Go to Counselor Booking Screen",
                    "bg": "#ffebee",
                    "fg": "#c62828",
                    "btn_bg": "#ef5350",
                    "action": lambda: self.app.show_frame("BookingFrame")
                }
            }
            
            cfg = classes_details[class_idx]
            
            self.ai_card.config(bg=cfg["bg"])
            self.ai_rec_title.config(text=cfg["title"], fg=cfg["fg"], bg=cfg["bg"])
            self.ai_rec_desc.config(text=cfg["desc"], fg="#333", bg=cfg["bg"])
            
            prob_str = f"Neural Net outputs -> Guides: {probs[0]*100:.1f}% | Videos: {probs[1]*100:.1f}% | Audio: {probs[2]*100:.1f}% | Counselor: {probs[3]*100:.1f}%"
            self.ai_rec_stats.config(text=prob_str, bg=cfg["bg"])
            
            self.ai_rec_btn.pack()
            self.ai_rec_btn.config(text=cfg["btn_text"], bg=cfg["btn_bg"], command=cfg["action"])
            
        except Exception as e:
            self.ai_rec_title.config(text="Analysis Error", fg="orange")
            self.ai_rec_desc.config(text=f"Failed to fetch AI wellness recommendations: {e}")
            self.ai_rec_btn.pack_forget()

# ------------------ ENHANCED CONFIDENTIAL COUNSELOR BOOKING ------------------
class BookingFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fffaf0")
        self.app = app

        header = tk.Frame(self, bg="#fffaf0")
        header.pack(fill="x", pady=10, padx=15)
        tk.Label(header, text="Confidential Counselor Booking", font=("Georgia", 20, "bold"), fg="#b22222", bg="#fffaf0").pack(side="left")
        tk.Button(header, text="Back to Chatbot", command=lambda: self.app.show_frame("ChatbotFrame"), bg="#ffb6c1", fg="#b22222", font=("Arial", 10, "bold")).pack(side="right")

        subtitle = tk.Label(self, text="Book a private session with a professional mental health counselor.", wraplength=760, justify="center", font=("Arial", 12), bg="#fffaf0")
        subtitle.pack(pady=(0, 10), padx=15)

        self.main_paned = tk.Frame(self, bg="#fffaf0")
        self.main_paned.pack(fill="both", expand=True, padx=15, pady=5)

        self.form_frame = tk.LabelFrame(self.main_paned, text="Appointment Details", bg="#fffaf0", padx=18, pady=18, font=("Arial", 11, "bold"))
        self.form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        self.history_frame = tk.LabelFrame(self.main_paned, text="Your Booked Sessions", bg="#fffaf0", padx=12, pady=12, font=("Arial", 11, "bold"))
        self.history_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

        tk.Label(self.form_frame, text="Please choose a specialization and available counselor slot.", wraplength=420, justify="left", bg="#fffaf0", fg="#555").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        tk.Label(self.form_frame, text="Name:", bg="#fffaf0").grid(row=1, column=0, sticky="w", pady=6)
        self.name_entry = tk.Entry(self.form_frame, width=40)
        self.name_entry.grid(row=1, column=1, padx=10, pady=6)

        tk.Label(self.form_frame, text="Contact Email:", bg="#fffaf0").grid(row=2, column=0, sticky="w", pady=6)
        self.email_entry = tk.Entry(self.form_frame, width=40)
        self.email_entry.grid(row=2, column=1, padx=10, pady=6)

        tk.Label(self.form_frame, text="Specialization Needed:", bg="#fffaf0").grid(row=3, column=0, sticky="w", pady=6)
        self.specialization_var = tk.StringVar(value="General")
        self.specialization_combo = ttk.Combobox(self.form_frame, textvariable=self.specialization_var, values=[
            "General", "Anxiety", "Depression", "Stress", "Relationship", "Academic", "Career"
        ], state="readonly", width=38)
        self.specialization_combo.grid(row=3, column=1, padx=10, pady=6)
        self.specialization_combo.bind("<<ComboboxSelected>>", self.update_counselors_and_slots)

        tk.Label(self.form_frame, text="Available Counselor:", bg="#fffaf0").grid(row=4, column=0, sticky="w", pady=6)
        self.counselor_var = tk.StringVar(value="Select Counselor")
        self.counselor_combo = ttk.Combobox(self.form_frame, textvariable=self.counselor_var, values=[], state="readonly", width=38)
        self.counselor_combo.grid(row=4, column=1, padx=10, pady=6)
        self.counselor_combo.bind("<<ComboboxSelected>>", self.update_counselors_and_slots)

        tk.Label(self.form_frame, text="Available Time Slots:", bg="#fffaf0").grid(row=5, column=0, sticky="w", pady=6)
        self.slot_var = tk.StringVar(value="Select a slot (e.g., YYYY-MM-DD HH:MM)")
        self.slot_combo = ttk.Combobox(self.form_frame, textvariable=self.slot_var, values=[], state="readonly", width=38)
        self.slot_combo.grid(row=5, column=1, padx=10, pady=6)

        tk.Label(self.form_frame, text="Reason for Session:", bg="#fffaf0").grid(row=6, column=0, sticky="nw", pady=6)
        self.reason_text = scrolledtext.ScrolledText(self.form_frame, height=6, width=35)
        self.reason_text.grid(row=6, column=1, padx=10, pady=6)

        self.form_button_frame = tk.Frame(self.form_frame, bg="#fffaf0")
        self.form_button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        tk.Button(self.form_button_frame, text="Submit Booking Request", font=("Arial", 12, "bold"), bg="#ff69b4", fg="white", command=self.submit_booking, width=24).pack(side="left", padx=5)
        tk.Button(self.form_button_frame, text="Refresh Slots", font=("Arial", 10), bg="#6b5fb5", fg="white", command=self.update_counselors_and_slots, width=16).pack(side="left", padx=5)

        self.status_label = tk.Label(self.form_frame, text="", bg="#fffaf0", fg="#2f4f4f", wraplength=420, justify="left")
        self.status_label.grid(row=8, column=0, columnspan=2, sticky="w", pady=(12, 0))

        self.bookings_tree = ttk.Treeview(self.history_frame, columns=("id", "counselor", "time", "specialization", "status"), show="headings", height=12)
        self.bookings_tree.heading("id", text="ID")
        self.bookings_tree.heading("counselor", text="Counselor")
        self.bookings_tree.heading("time", text="Time")
        self.bookings_tree.heading("specialization", text="Specialization")
        self.bookings_tree.heading("status", text="Status")
        self.bookings_tree.column("id", width=40, anchor="center")
        self.bookings_tree.column("counselor", width=130)
        self.bookings_tree.column("time", width=140)
        self.bookings_tree.column("specialization", width=110)
        self.bookings_tree.column("status", width=90, anchor="center")
        self.bookings_tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.bookings_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)

        self.history_button_frame = tk.Frame(self.history_frame, bg="#fffaf0")
        self.history_button_frame.pack(fill="x", pady=(10, 0))
        tk.Button(self.history_button_frame, text="Refresh Bookings", command=self.refresh_user_bookings, bg="#6b5fb5", fg="white", font=("Arial", 10, "bold"), width=18).pack(side="left", padx=5)
        tk.Button(self.history_button_frame, text="Cancel Selected Session", command=self.cancel_booking, bg="#b22222", fg="white", font=("Arial", 10, "bold"), width=20).pack(side="right", padx=5)

        self.update_counselors_and_slots()

    def update_counselors_and_slots(self, *_):
        """Fetch available counselors and refresh the slot list."""
        if not conn:
            self.status_label.config(text="Database connection is not available.")
            return

        specialization_needed = self.specialization_var.get()
        try:
            cursor.execute("SELECT id, username, specialization, online_status FROM counselors ORDER BY online_status DESC, username ASC")
            counselors = cursor.fetchall()

            counselor_options = []
            self._c_map = {}
            for c_id, username, spec, online in counselors:
                display = f"{username} ({spec}) [{'Online' if online else 'Offline'}]"
                counselor_options.append(display)
                self._c_map[display] = c_id

            self.counselor_combo['values'] = counselor_options
            if not counselor_options:
                self.counselor_var.set("No Counselors Available")
                self.slot_combo['values'] = ["No Slots Available"]
                self.status_label.config(text="No counselors exist in the system yet.")
                return

            if self.counselor_var.get() not in counselor_options:
                preferred = [opt for opt in counselor_options if specialization_needed.lower() in opt.lower()]
                self.counselor_var.set(preferred[0] if preferred else counselor_options[0])

            if specialization_needed != "General":
                match_count = sum(1 for opt in counselor_options if specialization_needed.lower() in opt.lower())
                self.status_label.config(text=f"Showing {match_count} counselors matching '{specialization_needed}'.")
            else:
                self.status_label.config(text="Showing all available counselors.")

        except Exception as e:
            self.counselor_combo['values'] = ["Unable to load counselors"]
            self.status_label.config(text=f"Error loading counselors: {e}")
            return

        self._load_slots_for_selected_counselor()

    def _load_slots_for_selected_counselor(self):
        selected = self.counselor_var.get()
        c_name_match = re.search(r'(.+?)\s\(', selected)
        c_username = c_name_match.group(1) if c_name_match else None
        slot_options = []
        self._slot_map = {}

        if c_username and conn:
            try:
                cursor.execute("SELECT id FROM counselors WHERE username = %s", (c_username,))
                row = cursor.fetchone()
                if row:
                    counselor_id = row[0]
                    now = datetime.now()
                    cursor.execute("SELECT id, slot_time FROM counselor_slots WHERE counselor_id = %s AND available = TRUE AND slot_time >= %s ORDER BY slot_time ASC", (counselor_id, now))
                    for sid, slot_time in cursor.fetchall():
                        display = f"{slot_time.strftime('%Y-%m-%d %H:%M')} (slot:{sid})"
                        slot_options.append(display)
                        self._slot_map[display] = sid
            except Exception as e:
                self.status_label.config(text=f"Error loading counselor slots: {e}")

        if not slot_options:
            now = datetime.now().replace(minute=0, second=0, microsecond=0)
            for add_days in range(1, 6):
                for hour in [10, 14, 16]:
                    fallback_time = (now + timedelta(days=add_days)).replace(hour=hour)
                    display = f"{fallback_time.strftime('%Y-%m-%d %H:%M')} (mock)"
                    slot_options.append(display)
            self.status_label.config(text="No real slots available for the selected counselor. Showing fallback mock slots.")

        self.slot_combo['values'] = slot_options
        self.slot_var.set(slot_options[0] if slot_options else "No Slots Available")

    def submit_booking(self):
        if self.app.user_id is None:
            messagebox.showerror("Error", "Please log in to book a session.")
            return

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        specialization = self.specialization_var.get()
        counselor_info = self.counselor_var.get()
        slot_info = self.slot_combo.get()
        reason = self.reason_text.get("1.0", tk.END).strip()

        if not name or not email or "Select" in slot_info or "No Counselors" in counselor_info or not reason:
            messagebox.showwarning("Incomplete", "Please fill all required fields and select an available slot and counselor.")
            return

        try:
            c_name_match = re.search(r'(.+?)\s\(', counselor_info)
            c_username = c_name_match.group(1) if c_name_match else None
            if not c_username:
                raise ValueError("Invalid counselor selected.")

            cursor.execute("SELECT id FROM counselors WHERE username = %s", (c_username,))
            counselor_row = cursor.fetchone()
            if not counselor_row:
                raise ValueError("Selected counselor not found.")
            counselor_id = counselor_row[0]

            time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})', slot_info)
            if not time_match:
                raise ValueError("Invalid slot selection.")
            booking_time = datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M")

            slot_id = None
            sid_match = re.search(r'slot:(\d+)', slot_info)
            if sid_match:
                slot_id = int(sid_match.group(1))
                cursor.execute("SELECT available FROM counselor_slots WHERE id = %s AND counselor_id = %s", (slot_id, counselor_id))
                slot_status = cursor.fetchone()
                if not slot_status or not slot_status[0]:
                    raise ValueError("The selected slot is no longer available.")
                cursor.execute("UPDATE counselor_slots SET available = FALSE WHERE id = %s", (slot_id,))
            else:
                cursor.execute("SELECT id FROM counselor_slots WHERE counselor_id = %s AND slot_time = %s", (counselor_id, booking_time))
                existing_slot = cursor.fetchone()
                if existing_slot:
                    slot_id = existing_slot[0]
                    cursor.execute("UPDATE counselor_slots SET available = FALSE WHERE id = %s", (slot_id,))
                else:
                    cursor.execute("INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s, %s, %s)", (counselor_id, booking_time, False))
                    slot_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO bookings (user_id, counselor_id, booking_time, slot_id, specialization_requested, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.app.user_id, counselor_id, booking_time, slot_id, specialization, reason, "Confirmed"))
            conn.commit()

            templates = load_email_templates()
            subject_template = templates.get('booking_subject', 'Bhagvad Mood: Booking Confirmation')
            body_template = templates.get('booking_body', 'Hi {name},\n\nYour counseling session with {counselor} is confirmed for {datetime}.\n\nReason: {reason}\n\n— Bhagvad Mood Team')
            try:
                subject = subject_template.format(name=name, counselor=c_username, datetime=booking_time.strftime('%Y-%m-%d %H:%M'), reason=reason)
            except Exception:
                subject = subject_template
            try:
                body = body_template.format(name=name, counselor=c_username, datetime=booking_time.strftime('%Y-%m-%d %H:%M'), reason=reason)
            except Exception:
                body = body_template
            sent, info = send_email_confirmation(email, subject, body)

            info_msg = f"A confirmation will be sent to {email}." if sent else f"Booking saved. Email NOT sent: {info}"
            messagebox.showinfo("Booking Confirmed", f"Thank you, {name}!\n\nYour session is booked with {c_username} for:\n{booking_time.strftime('%Y-%m-%d %H:%M')}\n\n{info_msg}")
            self.name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.reason_text.delete("1.0", tk.END)
            self.update_display()

        except ValueError as ve:
            messagebox.showerror("Error", f"Booking failed: {ve}")
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to save booking: {e}")

    def update_display(self):
        self.update_counselors_and_slots()
        self.refresh_user_bookings()

    def refresh_user_bookings(self):
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        if self.app.user_id is None:
            return
        try:
            cursor.execute("""
                SELECT b.id, c.username, b.booking_time, b.specialization_requested, b.status
                FROM bookings b
                JOIN counselors c ON b.counselor_id = c.id
                WHERE b.user_id = %s
                ORDER BY b.booking_time DESC
            """, (self.app.user_id,))
            rows = cursor.fetchall()
            for record in rows:
                time_str = record[2].strftime("%Y-%m-%d %H:%M") if hasattr(record[2], "strftime") else str(record[2])
                self.bookings_tree.insert("", "end", values=(record[0], record[1], time_str, record[3], record[4]))
        except Exception as e:
            print(f"Error fetching user bookings: {e}")

    def cancel_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a booking to cancel.")
            return

        values = self.bookings_tree.item(selected[0], "values")
        booking_id = values[0]
        status = values[4]
        if status == "Cancelled":
            messagebox.showinfo("Already Cancelled", "This booking is already cancelled.")
            return

        if not messagebox.askyesno("Cancel Booking", "Are you sure you want to cancel this booking?"):
            return

        try:
            cursor.execute("SELECT slot_id, counselor_id, booking_time FROM bookings WHERE id = %s", (booking_id,))
            res = cursor.fetchone()
            if res:
                slot_id, counselor_id, booking_time = res
                cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = %s", (booking_id,))
                if slot_id:
                    cursor.execute("UPDATE counselor_slots SET available = TRUE WHERE id = %s", (slot_id,))
                else:
                    cursor.execute("UPDATE counselor_slots SET available = TRUE WHERE counselor_id = %s AND slot_time = %s", (counselor_id, booking_time))
                conn.commit()
                messagebox.showinfo("Success", "Your booking has been cancelled successfully.")
                self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel booking: {e}")
            
# ------------------ The rest of the original application classes remain here ------------------
# (Classes like WelcomePage, PeerSupportFrame, ToDoNotesFrame, EntriesFrame, ExportFrame, etc. remain here but are omitted for brevity in the explanation for the user, but they are included in the final provided code block to ensure completeness.)

class WelcomePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fffaf0")
        self.app = app
        self.pdf_location = "BhagavadGita_Tri-lingual.pdf" ##########################################
        self.viewer = None

        self.initial_content_frame = tk.Frame(self, bg="#fffaf0")
        self.initial_content_frame.pack(fill="both", expand=True)
        self.pdf_viewer_frame = tk.Frame(self, bg="#ffffff")
        self.create_initial_content()

    def create_initial_content(self):
        for widget in self.initial_content_frame.winfo_children():
            widget.destroy()
        top_frame = tk.Frame(self.initial_content_frame, bg="#fffaf0")
        top_frame.pack(fill="x", pady=10)
        # --- NAME CHANGE ---
        tk.Label(top_frame, text="Bhagvad Mood Journal, Your Wellness Companion", font=("Georgia", 24, "bold"), fg="#b22222", bg="#fffaf0").pack(side="left", padx=20)
        # --- END NAME CHANGE ---
        tk.Button(top_frame, text="Proceed to Login", font=("Arial", 12, "bold"), bg="#ff69b4", fg="white", command=lambda: self.app.show_frame("LoginFrame")).pack(side="right", padx=20)
        tk.Label(self.initial_content_frame, text="Explore timeless wisdom before you begin.", font=("Arial", 14), bg="#fffaf0").pack()

        pdf_icon_frame = tk.Frame(self.initial_content_frame, bg="#fffaf0", bd=2, relief="groove")
        pdf_icon_frame.pack(pady=20)
        try:
            # Using a placeholder image filename for conceptual purpose, replace with your actual file
            self.pdf_image_pil = Image.open("gita_preview.png") ######################################################################################33
            self.pdf_image_pil = self.pdf_image_pil.resize((300, 400), Image.Resampling.LANCZOS)
            self.pdf_image_tk = ImageTk.PhotoImage(self.pdf_image_pil)
            pdf_icon_button = tk.Button(pdf_icon_frame, image=self.pdf_image_tk, bd=0, command=self.show_full_pdf)
            pdf_icon_button.pack(padx=5, pady=5)
            tk.Button(self.initial_content_frame, text="View Bhagavad Gita", font=("Arial", 12, "bold"), command=self.show_full_pdf).pack(pady=10)
        except FileNotFoundError:
            tk.Label(self.initial_content_frame, text="Error: 'gita_preview.png' not found.\nPlease ensure the image file is in the same directory.", font=("Arial", 12), bg="#fffaf0").pack(pady=20, padx=20)  #########################################
            tk.Button(self.initial_content_frame, text="Go to Login", font=("Arial", 12, "bold"), command=lambda: self.app.show_frame("LoginFrame")).pack(pady=10)
        except Exception as e:
            tk.Label(self.initial_content_frame, text=f"Error loading PDF preview image: {e}\nCheck the image file and 'Pillow' library.", font=("Arial", 12), bg="#fffaf0").pack(pady=20, padx=20)
            tk.Button(self.initial_content_frame, text="Go to Login", font=("Arial", 12, "bold"), command=lambda: self.app.show_frame("LoginFrame")).pack(pady=10)

        tk.Label(self.initial_content_frame, text="Feeling lost? Your inner peace awaits. Start journaling and find clarity with ancient wisdom.", font=("Georgia", 16, "italic"), bg="#fffaf0", wraplength=800).pack(pady=20)

    def show_full_pdf(self):
        self.initial_content_frame.pack_forget()
        self.pdf_viewer_frame.pack(fill="both", expand=True)
        for widget in self.pdf_viewer_frame.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.pdf_viewer_frame, bg="#ffffff")
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Label(header_frame, text="Bhagavad Gita", font=("Georgia", 18, "bold"), bg="#ffffff", fg="#b22222").pack(side="left", padx=10)
        nav_buttons_frame = tk.Frame(header_frame, bg="#ffffff")
        nav_buttons_frame.pack(side="right", padx=10)
        tk.Button(nav_buttons_frame, text="Back to Login", font=("Arial", 12, "bold"), command=lambda: self.app.show_frame("LoginFrame")).pack(side="left", padx=5)
        tk.Button(nav_buttons_frame, text="Back to Home", font=("Arial", 12, "bold"), command=self.hide_full_pdf).pack(side="left", padx=5)

        main_content_frame = tk.Frame(self.pdf_viewer_frame, bg="#ffffff")
        main_content_frame.pack(fill="both", expand=True)
        pdf_widget_frame = tk.Frame(main_content_frame, bg="#ffffff")
        pdf_widget_frame.pack(side="left", fill="both", expand=True, padx=(10,20), pady=10)
        try:
            self.viewer = pdf.ShowPdf().pdf_view(pdf_widget_frame, pdf_location=self.pdf_location, width=70, height=100)
            self.viewer.pack(fill="both", expand=True)
        except Exception as e:
            tk.Label(pdf_widget_frame, text=f"Error loading PDF: {e}", font=("Arial", 12), bg="#ffffff", wraplength=800).pack(pady=50)
            tk.Button(pdf_widget_frame, text="Back to Main Menu", command=self.hide_full_pdf).pack(pady=10)

        message_frame = tk.Frame(main_content_frame, bg="#ffffff")
        message_frame.pack(side="right", fill="y", padx=(10,20), pady=10)
        tk.Label(
            message_frame,
            text=(
                "📖 Thank you for choosing to read the Bhagavad Gita!\n\n"
                "By exploring this timeless scripture, you are connecting with the spiritual and cultural heritage of India.\n\n"
                "May these teachings inspire you towards inner peace, wisdom, and a deeper understanding of life.\n\n"
                "Embrace the journey of self-discovery and let the light of knowledge guide your path.\n\n"
                "— The Bhagvad Mood Team"
            ),
            font=("Georgia", 13, "italic"),
            bg="#ffffff",
            fg="#226622",
            justify="left",
            wraplength=260,
            anchor="n"
        ).pack(fill="y", expand=True)

    def hide_full_pdf(self):
        self.pdf_viewer_frame.pack_forget()
        self.initial_content_frame.pack(fill="both", expand=True)
        self.create_initial_content()

class PeerSupportFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f5f5dc")
        self.app = app
        self.selected_category = "All"
        self.search_var = tk.StringVar()

        main_frame = tk.Frame(self, bg="#f5f5dc")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)

        header_frame = tk.Frame(main_frame, bg="#f5f5dc")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(header_frame, text="Peer Support Forum", font=("Georgia", 18, "bold"), fg="#8b4513", bg="#f5f5dc").pack(side="left", padx=20, pady=10)
        tk.Button(header_frame, text="Back to Chatbot", command=lambda: self.app.show_frame("ChatbotFrame"), bg="#d2b48c", fg="#4b2e83", font=("Arial", 10, "bold"), padx=10, pady=5).pack(side="right", padx=20, pady=10)

        sidebar = tk.Frame(main_frame, bg="#f2e9d8", padx=12, pady=12)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 6), pady=10)
        sidebar.grid_rowconfigure(3, weight=1)

        tk.Label(sidebar, text="Search Posts", font=("Arial", 12, "bold"), bg="#f2e9d8").pack(anchor="w", pady=(0, 8))
        tk.Entry(sidebar, textvariable=self.search_var, font=("Arial", 11), width=26).pack(fill="x", pady=(0, 12))
        tk.Button(sidebar, text="Search", font=("Arial", 10, "bold"), bg="#6b5fb5", fg="white", command=self.search_posts).pack(fill="x", pady=(0, 12))

        tk.Label(sidebar, text="Categories", font=("Arial", 12, "bold"), bg="#f2e9d8").pack(anchor="w", pady=(10, 6))
        for cat in peer_support_categories:
            btn = tk.Button(sidebar, text=cat, font=("Arial", 11), bg="#e8d9c2", relief="flat", anchor="w", command=lambda c=cat: self.filter_posts(c))
            btn.pack(fill="x", pady=3)

        tk.Button(sidebar, text="+ New Post", font=("Arial", 12, "bold"), bg="#98fb98", fg="#2f4f2f", command=self.create_post_popup).pack(fill="x", pady=(18, 0))

        forum_content_frame = tk.Frame(main_frame, bg="#fffaf0", padx=10, pady=10)
        forum_content_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 10), pady=10)
        forum_content_frame.grid_rowconfigure(0, weight=1)
        forum_content_frame.grid_columnconfigure(0, weight=1)

        controls_frame = tk.Frame(forum_content_frame, bg="#fffaf0")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(controls_frame, text="Discussions & Questions", font=("Arial", 14, "bold"), bg="#fffaf0").pack(side="left")

        self.posts_canvas = tk.Canvas(forum_content_frame, bg="#fffaf0", highlightthickness=0)
        self.posts_scrollbar = ttk.Scrollbar(forum_content_frame, orient="vertical", command=self.posts_canvas.yview)
        self.posts_canvas.configure(yscrollcommand=self.posts_scrollbar.set)
        self.posts_canvas.grid(row=1, column=0, sticky="nsew")
        self.posts_scrollbar.grid(row=1, column=1, sticky="ns")

        self.posts_container = tk.Frame(self.posts_canvas, bg="#fffaf0")
        self.posts_window = self.posts_canvas.create_window((0, 0), window=self.posts_container, anchor="nw")
        self.posts_container.bind("<Configure>", lambda e: self.posts_canvas.configure(scrollregion=self.posts_canvas.bbox("all")))
        self.posts_canvas.bind("<Configure>", lambda e: self.posts_canvas.itemconfig(self.posts_window, width=e.width))
        self.posts_canvas.bind("<Enter>", lambda e: self.posts_canvas.bind_all('<MouseWheel>', self._on_mousewheel))
        self.posts_canvas.bind("<Leave>", lambda e: self.posts_canvas.unbind_all('<MouseWheel>'))

        self.populate_posts()

    def populate_posts(self, filtered_posts=None):
        for child in self.posts_container.winfo_children():
            child.destroy()

        posts_to_show = filtered_posts if filtered_posts is not None else peer_support_posts

        if not posts_to_show:
            empty_label = tk.Label(self.posts_container, text="No posts match this search or category.", bg="#fffaf0", fg="#5a5a5a", font=("Arial", 12, "italic"))
            empty_label.pack(pady=20)
            return

        for post in posts_to_show:
            card = tk.Frame(self.posts_container, bg="#ffffff", bd=1, relief="solid", padx=14, pady=12)
            card.pack(fill="x", pady=8)

            header = tk.Frame(card, bg="#ffffff")
            header.pack(fill="x")
            tk.Label(header, text=post["category"], bg="#ffffff", fg="#b22222", font=("Arial", 10, "bold"), padx=4, pady=2).pack(side="left")
            meta = tk.Label(header, text=f"{post.get('answers', 0)} answers · {post.get('views', 0)} views", bg="#ffffff", fg="#777", font=("Arial", 9), anchor="e")
            meta.pack(side="right")

            title_label = tk.Label(card, text=post["title"], font=("Arial", 14, "bold"), fg="#1a0dab", bg="#ffffff", wraplength=600, justify="left", cursor="hand2")
            title_label.pack(fill="x", pady=(8, 6))
            title_label.bind("<Button-1>", lambda e, p=post: self.show_post_details(p))

            snippet = post["message"]
            if len(snippet) > 220:
                snippet = snippet[:220].rstrip() + "..."
            tk.Label(card, text=snippet, bg="#ffffff", fg="#333", font=("Arial", 11), wraplength=600, justify="left").pack(fill="x")

            footer = tk.Frame(card, bg="#ffffff")
            footer.pack(fill="x", pady=(10, 0))
            tk.Label(footer, text=f"Asked by {post['user']}", bg="#ffffff", fg="#555", font=("Arial", 10, "italic")).pack(side="left")
            tk.Button(footer, text="View Post", command=lambda p=post: self.show_post_details(p), bg="#e8f0fe", fg="#1a0dab", font=("Arial", 10, "bold"), padx=10, pady=4, relief="ridge").pack(side="right")

    def filter_posts(self, category):
        self.selected_category = category
        self.search_posts()

    def search_posts(self):
        query = self.search_var.get().strip().lower()
        posts = peer_support_posts
        if self.selected_category != "All":
            posts = [p for p in posts if p["category"] == self.selected_category]
        if query:
            posts = [p for p in posts if query in p["title"].lower() or query in p["message"].lower()]
        self.populate_posts(posts)

    def show_post_details(self, post):
        popup = tk.Toplevel(self.app)
        popup.title(post["title"])
        popup.geometry("640x520")
        popup.transient(self.app)

        frame = tk.Frame(popup, padx=18, pady=18, bg="#fdfcf7")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=post["title"], font=("Georgia", 16, "bold"), bg="#fdfcf7", fg="#1a0dab", wraplength=600, justify="left").pack(anchor="w", pady=(0, 12))
        tk.Label(frame, text=f"Category: {post['category']} · Asked by {post['user']} · {post.get('views', 0)} views", bg="#fdfcf7", fg="#555", font=("Arial", 10, "italic")).pack(anchor="w")

        message_frame = tk.Frame(frame, bg="#ffffff", bd=1, relief="solid", padx=12, pady=12)
        message_frame.pack(fill="both", expand=True, pady=(12, 10))
        tk.Label(message_frame, text=post["message"], font=("Arial", 12), bg="#ffffff", fg="#333", wraplength=584, justify="left").pack(anchor="w")

        action_frame = tk.Frame(frame, bg="#fdfcf7")
        action_frame.pack(fill="x", pady=(10, 0))
        tk.Button(action_frame, text="Close", command=popup.destroy, bg="#6b5fb5", fg="white", font=("Arial", 10, "bold"), padx=12, pady=6).pack(side="right")

    def _on_mousewheel(self, event):
        shift = (event.state & 0x1) != 0
        scroll_amount = -1 * (event.delta // 120)
        if shift:
            self.posts_canvas.xview_scroll(scroll_amount, "units")
        else:
            self.posts_canvas.yview_scroll(scroll_amount, "units")

    def create_post_popup(self):
        popup = tk.Toplevel(self.app)
        popup.title("Create a New Post")
        popup.geometry("520x430")
        popup.transient(self.app)

        frame = tk.Frame(popup, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Ask a question or share an experience anonymously.", font=("Arial", 12, "bold")).pack(pady=(0, 10), anchor="w")

        tk.Label(frame, text="Category:", anchor="w").pack(fill="x")
        categories = ["Student Life", "Professional Work", "Physical Health", "Mental Health"]
        category_var = tk.StringVar(value=categories[0])
        category_menu = ttk.Combobox(frame, textvariable=category_var, values=categories, state="readonly")
        category_menu.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Your Post Title:", anchor="w").pack(fill="x")
        title_entry = tk.Entry(frame, font=("Arial", 11))
        title_entry.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Your Message:", anchor="w").pack(fill="x")
        message_text = scrolledtext.ScrolledText(frame, height=8, wrap="word", font=("Arial", 11))
        message_text.pack(fill="both", expand=True, pady=(0, 10))

        tk.Button(frame, text="Submit Anonymously", command=lambda: self.submit_post(title_entry.get(), message_text, popup, category_var.get()), bg="#98fb98", fg="#2f4f2f", font=("Arial", 11, "bold"), padx=10, pady=6).pack(pady=5)

    def submit_post(self, title, message_widget, popup, category):
        title_text = title.strip()
        message_text = message_widget.get("1.0", tk.END).strip()
        full_text = title_text + " " + message_text

        import wellness_ml
        is_crisis_ml, _ = wellness_ml.predict_crisis(full_text)
        if is_crisis_ml or _matches_any(CRISIS_KEYWORDS, full_text):
            messagebox.showerror("Moderation Alert", "This post contains crisis keywords. Please use the 'Get Support' button or helplines before posting here.")
            return

        if _matches_any(FORUM_BLOCK_KEYWORDS, full_text):
            messagebox.showerror("Moderation Alert", "This post contains inappropriate or harmful language. Please rephrase.")
            return

        if not title_text or not message_text:
            messagebox.showwarning("Warning", "Please fill in both the title and message.")
            return

        user_name = getattr(self.app, "username", "User") or "User"
        new_post = {
            "title": title_text,
            "user": f"Anonymous {user_name}",
            "category": category,
            "message": message_text,
            "answers": 0,
            "views": random.randint(25, 85),
        }
        peer_support_posts.insert(0, new_post)
        self.search_var.set("")
        self.filter_posts("All")

        messagebox.showinfo("Submission Confirmed", "Your post has been submitted for review. Thank you for contributing to the community!")
        popup.destroy()

class PeriodJournalFrame(tk.Frame):
    MOODS = all_moods
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fff0f5")
        self.app = app

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(self, text="Period Journal", font=("Georgia", 20, "bold"), fg="#b22222", bg="#fff0f5").pack(pady=20)

        main_content_frame = tk.Frame(self, bg="#fff0f5")
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_columnconfigure(1, weight=0)
        main_content_frame.grid_rowconfigure(0, weight=1)

        analytics_frame = tk.LabelFrame(main_content_frame, text="Mood & Wellness Overview", font=("Arial", 13, "bold"), bg="#fff0f5")
        analytics_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.analytics_canvas_holder = tk.Frame(analytics_frame, bg="#ffffff")
        self.analytics_canvas_holder.pack(fill="both", expand=True, padx=10, pady=10)
        self.analytics_canvas = None

        btn_frame = tk.Frame(main_content_frame, bg="#fff0f5")
        btn_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        tk.Button(btn_frame, text="Daily Log", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=lambda: self.app.show_frame("PeriodLogFrame")).pack(pady=5, padx=10, fill="x")
        tk.Button(btn_frame, text="View All Analytics", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=lambda: self.app.show_frame("PeriodStatsFrame")).pack(pady=5, padx=10, fill="x")
        tk.Button(btn_frame, text="Export Journal CSV", font=("Arial", 12, "bold"), bg="#ffb6c1", fg="#b22222", command=self.export_entries_csv).pack(pady=5, padx=10, fill="x")

        tk.Button(self, text="Back to Main Journal", font=("Arial", 12, "bold"), bg="#db7093", fg="white", command=lambda: self.app.show_frame("ChatbotFrame")).pack(pady=20)

    def draw_analytics_preview(self):
        if self.analytics_canvas:
            self.analytics_canvas.get_tk_widget().destroy()

        try:
            cursor.execute("SELECT timestamp, mood FROM journal WHERE user_id = %s AND shlok = %s ORDER BY timestamp DESC LIMIT 7", (self.app.user_id, "Period Journal Entry"))
            rows = cursor.fetchall()

            if not rows:
                lbl = tk.Label(self.analytics_canvas_holder, text="No period entries yet to show analytics.", bg="#ffffff")
                lbl.pack(pady=20)
                return

            moods = [r[1] for r in rows]

            mood_counts = {}
            for mood_str in moods:
                for mood in mood_str.split(','):
                    mood = mood.strip()
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1

            mood_labels = [m.replace('_', ' ').title() for m in mood_counts.keys()]
            counts = list(mood_counts.values())

            fig = Figure(figsize=(4, 4))
            ax = fig.add_subplot(111)
            ax.pie(counts, labels=mood_labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
            ax.set_title("Mood Distribution (Last 7 Entries)")

            self.analytics_canvas = FigureCanvasTkAgg(fig, master=self.analytics_canvas_holder)
            self.analytics_canvas.draw()
            self.analytics_canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            lbl = tk.Label(self.analytics_canvas_holder, text=f"Error loading analytics: {e}", bg="#ffffff")
            lbl.pack(pady=20)

    def export_entries_csv(self):
        try:
            cursor.execute("SELECT id, timestamp, mood, thought, shlok, shlok_meaning FROM journal WHERE user_id = %s AND shlok = %s ORDER BY timestamp DESC", (self.app.user_id, "Period Journal Entry"))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showinfo("Export CSV", "No period entries to export.")
                return

            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile=f"{self.app.username}_period_journal.csv")
            if not file_path:
                return

            with open(file_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id", "timestamp", "mood", "symptoms", "flow", "energy", "sleep", "gratitude", "notes", "shlok", "shlok_meaning"])

                for r in rows:
                    ts = r[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[1], 'strftime') else str(r[1])
                    mood = r[2]
                    thought = r[3]
                    shlok_text = r[4]
                    shlok_meaning = r[5]

                    symptoms = flow = energy = sleep = gratitude = notes = ""
                    for line in thought.split("\n"):
                        l = line.lower()
                        if l.startswith("symptoms:"): symptoms = line.split(":", 1)[1].strip()
                        elif l.startswith("flow:"): flow = line.split(":", 1)[1].strip()
                        elif l.startswith("energy:"): energy = line.split(":", 1)[1].strip()
                        elif l.startswith("sleep:"): sleep = line.split(":", 1)[1].strip()
                        elif l.startswith("gratitude:"): gratitude = line.split(":", 1)[1].strip()
                        elif l.startswith("notes:"): notes = line.split(":", 1)[1].strip()

                    writer.writerow([r[0], ts, mood, symptoms, flow, energy, sleep, gratitude, notes, shlok_text, shlok_meaning])
            messagebox.showinfo("Export CSV", f"Period journal exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export entries: {e}")

class PeriodStatsFrame(tk.Frame):
    MOODS = all_moods
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fff0f5")
        self.app = app
        top = tk.Frame(self, bg="#fff0f5")
        top.pack(fill="x", pady=10)
        tk.Label(top, text="Period Mood Analytics", font=("Georgia", 18, "bold"), fg="#b22222", bg="#fff0f5").pack(side="left", padx=10)
        tk.Button(top, text="Export Stats CSV", command=self.export_stats_csv).pack(side="left", padx=10)
        tk.Button(top, text="Back", command=lambda: app.show_frame("PeriodJournalFrame")).pack(side="right", padx=10)
        self.canvas_holder = tk.Frame(self, bg="#fff0f5")
        self.canvas_holder.pack(fill="both", expand=True, padx=20, pady=10)
        self.analytics_canvas = None

    def draw_analytics(self):
        if self.analytics_canvas:
            self.analytics_canvas.get_tk_widget().destroy()
        try:
            cursor.execute("SELECT timestamp, mood, thought FROM journal WHERE user_id = %s AND shlok = %s ORDER BY timestamp DESC", (self.app.user_id, "Period Journal Entry"))
            rows = cursor.fetchall()
            if not rows:
                lbl = tk.Label(self.canvas_holder, text="No period entries yet to show statistics.", bg="#fff0f5")
                lbl.pack()
                return

            # Data extraction for multiple moods
            dates = []
            moods_by_date = {}
            flows = []
            energy_levels = []
            sleep_qualities = []

            for r in rows:
                ts = r[0].strftime("%Y-%m-%d") if hasattr(r[0], 'strftime') else str(r[0])
                dates.append(ts)
                moods_by_date[ts] = [m.strip() for m in r[1].split(',')]
                thought = r[2]
                flow_val = None
                energy_val = None
                sleep_val = None
                for line in thought.split("\n"):
                    l = line.lower()
                    if l.startswith("flow:"):
                        flow_val = line.split(":",1)[1].strip()
                    elif l.startswith("energy:"):
                        try: energy_val = int(line.split(":",1)[1].strip())
                        except: pass
                    elif l.startswith("sleep:"):
                        sleep_val = line.split(":",1)[1].strip()
                flows.append(flow_val if flow_val else "")
                energy_levels.append(energy_val)
                sleep_qualities.append(sleep_val)

            flow_map = {"None":0, "Light":1, "Normal":2, "Heavy":3}
            flows_numeric = [flow_map.get(f, None) for f in flows]
            mood_map = {m: i for i, m in enumerate(self.MOODS)}

            moods_numeric = []
            for date in dates:
                if date in moods_by_date and moods_by_date[date]:
                    moods_numeric.append(mood_map.get(moods_by_date[date][0], None))
                else:
                    moods_numeric.append(None)

            sleep_map = {"Poor": 1, "Normal": 2, "Good": 3}
            sleep_numeric = [sleep_map.get(s, None) for s in sleep_qualities]

            # Dropdown for chart selection
            chart_options = ["Mood Chart", "Flow Intensity", "Energy Level", "Sleep Quality"]
            chart_var = tk.StringVar(value=chart_options[0])
            chart_menu = ttk.Combobox(self.canvas_holder, textvariable=chart_var, values=chart_options, state="readonly")
            chart_menu.pack(pady=10)

            def update_chart(*args):
                for widget in self.canvas_holder.winfo_children():
                    if isinstance(widget, FigureCanvasTkAgg):
                        widget.get_tk_widget().destroy()

                current_chart = chart_var.get()
                fig = Figure(figsize=(8, 6))
                ax = fig.add_subplot(111)

                if current_chart == "Mood Chart":
                    if any(m is not None for m in moods_numeric):
                        ax.plot(dates, moods_numeric, label="Mood (numeric)", marker="^")
                        ax.set_yticks(list(mood_map.values()))
                        ax.set_yticklabels([m.replace('_', ' ').title() for m in self.MOODS])
                        ax.set_title("Mood Trends Over Time")
                        ax.set_ylabel("Mood")
                    else:
                        ax.text(0.5, 0.5, 'No Mood data available.', transform=ax.transAxes, ha='center')
                elif current_chart == "Flow Intensity":
                    if any(f is not None for f in flows_numeric):
                        ax.plot(dates, flows_numeric, label="Flow Intensity", marker="s")
                        ax.set_yticks(list(flow_map.values()))
                        ax.set_yticklabels(list(flow_map.keys()))
                        ax.set_title("Flow Intensity Over Time")
                        ax.set_ylabel("Flow Intensity")
                    else:
                        ax.text(0.5, 0.5, 'No Flow data available.', transform=ax.transAxes, ha='center')
                elif current_chart == "Energy Level":
                    if any(e is not None for e in energy_levels):
                        ax.plot(dates, energy_levels, label="Energy Level (1-10)", marker="o")
                        ax.set_title("Energy Level Over Time")
                        ax.set_ylabel("Energy Level")
                    else:
                        ax.text(0.5, 0.5, 'No Energy data available.', transform=ax.transAxes, ha='center')
                elif current_chart == "Sleep Quality":
                    if any(s is not None for s in sleep_numeric):
                        ax.plot(dates, sleep_numeric, label="Sleep Quality (1=Poor, 3=Good)", marker="v")
                        ax.set_yticks(list(sleep_map.values()))
                        ax.set_yticklabels(list(sleep_map.keys()))
                        ax.set_title("Sleep Quality Over Time")
                        ax.set_ylabel("Sleep Quality")
                    else:
                        ax.text(0.5, 0.5, 'No Sleep data available.', transform=ax.transAxes, ha='center')

                ax.set_xlabel("Date")
                fig.autofmt_xdate()

                self.analytics_canvas = FigureCanvasTkAgg(fig, master=self.canvas_holder)
                self.analytics_canvas.draw()
                self.analytics_canvas.get_tk_widget().pack(fill="both", expand=True)

            chart_menu.bind("<<ComboboxSelected>>", update_chart)
            update_chart()

        except Exception as e:
            lbl = tk.Label(self.canvas_holder, text=f"Error loading analytics: {e}", bg="#fff0f5")
            lbl.pack()

    def export_stats_csv(self):
        try:
            cursor.execute("SELECT timestamp, mood, thought FROM journal WHERE user_id = %s AND shlok = %s ORDER BY timestamp DESC", (self.app.user_id, "Period Journal Entry"))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showinfo("Export CSV", "No period entries to export.")
                return

            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile=f"{self.app.username}_period_stats.csv")
            if not file_path:
                return

            with open(file_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Mood", "Flow Intensity", "Energy Level", "Sleep Quality"])

                for r in rows:
                    ts = r[0].strftime("%Y-%m-%d")
                    mood = r[1]
                    thought = r[2]
                    flow = energy = sleep = "N/A"
                    for line in thought.split("\n"):
                        if line.startswith("Flow:"): flow = line.split(":", 1)[1].strip()
                        elif line.startswith("Energy:"): energy = line.split(":", 1)[1].strip()
                        elif line.startswith("Sleep:"): sleep = line.split(":", 1)[1].strip()
                    writer.writerow([ts, mood, flow, energy, sleep])
            messagebox.showinfo("Export CSV", f"Period stats exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export stats: {e}")

class PeriodLogFrame(tk.Frame):
    MOODS = all_moods
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fff0f5")
        self.app = app

        self.main_canvas = tk.Canvas(self, bg="#fff0f5", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#fff0f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="Period Daily Log", font=("Georgia", 20, "bold"), fg="#b22222", bg="#fff0f5").pack(pady=10)
        tk.Label(self.scrollable_frame, text="You can select multiple moods for the day.", font=("Arial", 12, "italic"), fg="#8b0000", bg="#fff0f5").pack(pady=(0, 10))

        # Mood Selection with Checkbuttons
        self.mood_frame = tk.LabelFrame(self.scrollable_frame, text="Select Your Mood(s)", bg="#fff0f5", font=("Arial", 13, "bold"))
        self.mood_frame.pack(padx=10, pady=8, fill="x")
        self.mood_vars = {}
        for i, mood in enumerate(self.MOODS):
            var = tk.StringVar(value="")
            self.mood_vars[mood] = var
            btn = tk.Checkbutton(
                self.mood_frame, text=mood.replace('_', ' ').title(), variable=var, onvalue=mood, offvalue="",
                indicatoron=0, width=15, font=("Arial", 11), bg="#ffe4e1", fg="#b22222",
                selectcolor="#ffb6c1", relief="ridge", bd=2, command=self.update_shloka
            )
            btn.grid(row=i//5, column=i%5, padx=3, pady=3, sticky="ew")

        # Period Cycle Dates
        cycle_frame = tk.LabelFrame(self.scrollable_frame, text="Period Cycle Dates", bg="#fff0f5", font=("Arial", 13, "bold"))
        cycle_frame.pack(padx=10, pady=8, fill="x")

        # --- ENHANCEMENT: DateEntry (Calendar Widget) ---
        # Start Date
        tk.Label(cycle_frame, text="Start Date (Cycle Start):", bg="#fff0f5").pack(pady=(5,0), padx=5, anchor="w")
        self.start_date_entry = DateEntry(cycle_frame, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date_entry.pack(pady=(0,5), padx=5, anchor="w")

        # End Date
        tk.Label(cycle_frame, text="End Date (Cycle End, Optional):", bg="#fff0f5").pack(pady=(5,0), padx=5, anchor="w")
        self.end_date_entry = DateEntry(cycle_frame, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, "") # Insert empty string to represent optional end date
        self.end_date_entry.pack(pady=(0,5), padx=5, anchor="w")
        # --- END ENHANCEMENT ---

        # New: Mental Health Timeline section (Conceptual, simple version retained)
        timeline_frame = tk.LabelFrame(self.scrollable_frame, text="Mental Health in a Day (Optional)", bg="#fff0f5", font=("Arial", 13, "bold"))
        timeline_frame.pack(fill="x", padx=10, pady=5)

        self.timeline_entries = []

        def add_timeline_entry():
            entry_frame = tk.Frame(timeline_frame, bg="#fff0f5")
            entry_frame.pack(fill="x", pady=5)

            timestamp_label = tk.Label(entry_frame, text=datetime.now().strftime('%H:%M'), bg="#fff0f5", font=("Arial", 10, "bold"))
            timestamp_label.pack(side="left", padx=5)

            mood_var = tk.StringVar()
            mood_combo = ttk.Combobox(entry_frame, textvariable=mood_var, values=[m.replace('_', ' ').title() for m in self.MOODS], state="readonly", width=15)
            mood_combo.pack(side="left", padx=5)

            thought_entry = tk.Entry(entry_frame, width=40)
            thought_entry.pack(side="left", padx=5, fill="x", expand=True)

            self.timeline_entries.append({'timestamp': timestamp_label, 'mood_var': mood_var, 'thought': thought_entry, 'frame': entry_frame})

        add_entry_btn = tk.Button(timeline_frame, text="Add Timestamp Entry", command=add_timeline_entry)
        add_entry_btn.pack(pady=5)

        add_timeline_entry()

        # --- Bhagavad Mood Reflection Section ---
        reflection_frame = tk.LabelFrame(self.scrollable_frame, text="Bhagavad Mood Reflection", bg="#fff0f5", font=("Arial", 13, "bold"))
        reflection_frame.pack(fill="x", padx=10, pady=5)
        self.shloka_var = tk.StringVar(value="Select a mood to see a verse.")
        self.shloka_label = tk.Label(reflection_frame, textvariable=self.shloka_var, bg="#fff0f5", wraplength=600, justify="left", font=("Georgia", 12, "italic"))
        self.shloka_label.pack(padx=8, pady=6)

        form = tk.Frame(self.scrollable_frame, bg="#fff0f5")
        form.pack(padx=10, pady=8, fill="x")

        # Use ScrolledText for symptoms
        tk.Label(form, text="Describe pain or symptoms:", bg="#fff0f5").pack(pady=(5,0), padx=5, anchor="w")
        self.symptom_entry = scrolledtext.ScrolledText(form, height=4, wrap="word")
        self.symptom_entry.pack(pady=(0,5), padx=5, fill="x")

        self.flow_var = tk.StringVar(value="Normal")
        self.flow_combo = self.add_dropdown_with_label(form, "Flow Intensity:", ["None", "Light", "Normal", "Heavy"], self.flow_var)
        self.energy_var = tk.IntVar(value=5)
        self.energy_scale = self.add_scale_with_label(form, "Energy Level (1-10):", self.energy_var)
        self.sleep_var = tk.StringVar(value="Normal")
        self.sleep_combo = self.add_dropdown_with_label(form, "Sleep Quality:", ["Poor", "Normal", "Good"], self.sleep_var)
        self.gratitude_entry = self.add_entry_with_label(form, "Gratitude Note:")
        self.extra_notes_entry = self.add_entry_with_label(form, "Extra Comments/Notes:")

        btn_frame = tk.Frame(self.scrollable_frame, bg="#fff0f5")
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Save Entry", font=("Arial", 13, "bold"), bg="#ff69b4", fg="white", command=self.submit_entry).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Back", command=lambda: app.show_frame("PeriodJournalFrame")).pack(side="left", padx=10)

    def add_entry_with_label(self, parent, label_text):
        frame = tk.Frame(parent, bg="#fff0f5")
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=label_text, bg="#fff0f5").pack(side="left")
        entry = tk.Entry(frame, width=50)
        entry.pack(side="left", padx=5)
        return entry

    def add_dropdown_with_label(self, parent, label_text, values, var):
        frame = tk.Frame(parent, bg="#fff0f5")
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=label_text, bg="#fff0f5").pack(side="left")
        combo = ttk.Combobox(frame, textvariable=var, values=values, state="readonly", width=12)
        combo.pack(side="left", padx=5)
        return combo

    def add_scale_with_label(self, parent, label_text, var):
        frame = tk.Frame(parent, bg="#fff0f5")
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=label_text, bg="#fff0f5").pack(side="left")
        scale = tk.Scale(frame, from_=1, to=10, orient="horizontal", variable=var, length=180, showvalue=True, bg="#fff0f5")
        scale.pack(side="left", padx=5)
        return scale

    def update_shloka(self):
        selected_moods = [mood for mood, var in self.mood_vars.items() if var.get() == mood]

        if selected_moods:
            all_shlokas = []
            for mood in selected_moods:
                all_shlokas.extend(shloks.get(mood, []))

            if all_shlokas:
                verse, meaning = random.choice(all_shlokas)
                self.shloka_var.set(f"📜 {verse}\n💡 {meaning}")
            else:
                self.shloka_var.set("No specific verse for selected moods.")
        else:
            self.shloka_var.set("Select a mood to see a verse.")

    def submit_entry(self):
        selected_moods = [mood for mood, var in self.mood_vars.items() if var.get() == mood]
        moods_str = ",".join(selected_moods)
        symptoms = self.symptom_entry.get("1.0", tk.END).strip()
        flow = self.flow_var.get()
        energy = self.energy_var.get()
        sleep = self.sleep_var.get()
        gratitude = self.gratitude_entry.get().strip()
        extra_notes = self.extra_notes_entry.get().strip()
        
        # Collect timeline entries
        timeline_details = []
        for entry in self.timeline_entries:
            time = entry['timestamp'].cget('text')
            mood = entry['mood_var'].get()
            thought = entry['thought'].get().strip()
            if mood and thought:
                timeline_details.append(f"[{time} - {mood}]: {thought}")
        timeline_notes = "\nTimeline Details: " + "\n".join(timeline_details) if timeline_details else ""

        # --- DateEntry Input Logic ---
        start_date_str = None
        end_date_str = None

        try:
            start_date_obj = self.start_date_entry.get_date()
            start_date_str = start_date_obj.strftime("%Y-%m-%d")
        except Exception:
            pass

        end_date_input = self.end_date_entry.get().strip()
        if end_date_input and isinstance(self.end_date_entry, DateEntry):
            try:
                end_date_obj = self.end_date_entry.get_date()
                end_date_str = end_date_obj.strftime("%Y-%m-%d")
            except Exception:
                pass
        # --- End DateEntry Input Logic ---

        if not moods_str:
            messagebox.showwarning("Warning", "Please select at least one mood.")
            return

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None

                cursor.execute("SELECT id FROM period_cycles WHERE user_id = %s AND start_date = %s", (self.app.user_id, start_date))
                existing = cursor.fetchone()

                if not existing:
                    cursor.execute("""
                        INSERT INTO period_cycles (user_id, start_date, end_date)
                        VALUES (%s, %s, %s)
                    """, (self.app.user_id, start_date, end_date))
                else:
                    if end_date:
                        cursor.execute("UPDATE period_cycles SET end_date = %s WHERE id = %s", (end_date, existing[0]))

                conn.commit()
            except ValueError:
                messagebox.showerror("Date Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

        try:
            timestamp = datetime.now()
            # Compile all logged details into the thought field for CSV export
            thought = (
                f"Symptoms: {symptoms}\nFlow: {flow}\nEnergy: {energy}\nSleep: {sleep}\nGratitude: {gratitude}\nNotes: {extra_notes}{timeline_notes}"
            )
            shloka_text, shloka_meaning = ("Period Journal Entry", "N/A")

            risk_level = "low"
            if any(mood in ["very_sad", "devastated", "discouraged", "pessimistic", "angry"] for mood in selected_moods):
                risk_level = "medium"
            elif any(mood in ["anxious", "overwhelmed"] for mood in selected_moods):
                risk_level = "medium-high"

            # --- COMPLETION OF INCOMPLETE CODE BLOCK ---
            cursor.execute("""
                INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp, risk_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.app.user_id, self.app.username, moods_str,
                thought,
                shloka_text, shloka_meaning, timestamp, risk_level
            ))
            conn.commit()
            # --- END COMPLETION ---

            messagebox.showinfo("Success", "Period journal entry saved!")
            self.app.show_frame("PeriodJournalFrame")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")

class ToDoNotesFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0fff0")
        self.app = app
        tk.Label(self, text="To-Do Notes List", font=("Georgia", 20, "bold"), fg="#228B22", bg="#f0fff0").pack(pady=20)
        tk.Label(self, text="Organize your tasks, jot down reminders (use 'remind: HH:MM message'), and regain clarity!", font=("Arial", 13), bg="#f0fff0").pack(pady=8)
        self.todo_box = tk.Text(self, height=18, width=70, font=("Arial", 12))
        self.todo_box.pack(padx=20, pady=10)
        btns = tk.Frame(self, bg="#f0fff0")
        btns.pack(pady=6)
        tk.Button(btns, text="Save To-Do List", command=self.save_todos).pack(side="left", padx=8)
        tk.Button(btns, text="Load To-Do List", command=self.load_todos).pack(side="left", padx=8)
        tk.Button(btns, text="Mark Task Complete (+20 MP)", font=("Arial", 12, "bold"), bg="#6BCBCE", fg="white", command=self.complete_task).pack(side="left", padx=8)
        tk.Button(btns, text="Back to Main Journal", command=lambda: app.show_frame("ChatbotFrame")).pack(side="left", padx=8)

    def get_todo_filename(self):
        user = getattr(self.app, 'username', 'default')
        return f"todo_{user}.txt"

    def save_todos(self):
        try:
            with open(self.get_todo_filename(), "w", encoding="utf-8") as f:
                f.write(self.todo_box.get("1.0", "end-1c"))
            messagebox.showinfo("Saved", "To-Do list saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_todos(self):
        try:
            with open(self.get_todo_filename(), "r", encoding="utf-8") as f:
                self.todo_box.delete("1.0", "end")
                self.todo_box.insert("1.0", f.read())
            messagebox.showinfo("Loaded", "To-Do list loaded!")
        except FileNotFoundError:
            messagebox.showinfo("No List", "No saved to-do list found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    # --- GAMIFICATION: COMPLETE TASK LOGIC ---
    def complete_task(self):
        if self.app.user_id is None:
            messagebox.showerror("Error", "Please log in to earn points.")
            return

        response = messagebox.askyesno("Task Completion", "Did you complete a coping/self-care suggestion or task from your list?")
        if response:
            points_to_award = 20
            self.app.mindful_points += points_to_award

            try:
                cursor.execute("UPDATE users SET mindful_points = %s WHERE id = %s", (self.app.mindful_points, self.app.user_id))
                conn.commit()
                messagebox.showinfo("Mindful Points", f"Task complete! You earned {points_to_award} MP! Total Points: {self.app.mindful_points}")
                self.app.frames["ChatbotFrame"].update_streak_display()
            except Exception as e:
                 messagebox.showerror("Database Error", f"Failed to award points: {e}")
    # --- END GAMIFICATION: COMPLETE TASK LOGIC ---

class SpinWheelFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f0f8ff")
        self.app = app
        tk.Label(self, text="Spin the Wheel — Universal Messages", font=("Georgia", 18, "bold"), fg="#2f4f4f", bg="#f0f8ff").pack(pady=8)
        tk.Button(self, text="Back", command=lambda: app.show_frame("ChatbotFrame")).pack(anchor="ne", padx=10, pady=6)
        self.canvas = tk.Canvas(self, width=520, height=520, bg="#f0f8ff", highlightthickness=0)
        self.canvas.pack(pady=6)
        self.messages = ["You are enough.","Breathe — one step at a time.","This too shall pass.","Small progress is still progress.","You are loved and seen.","Be kind to yourself today.","Trust your path — keep going."]
        self.colors = ["#FFD4DA", "#FFE6BA", "#E6FFD3", "#D8F0FF", "#E8D6FF", "#FFC9DE", "#FFF6C8"]
        self.num_segments = len(self.messages)
        self.center = (260, 260)
        self.radius = 240
        self.angle_offset = 0
        self._draw_wheel()
        tk.Button(self, text="Spin", font=("Arial", 14, "bold"), bg="#ff7f50", fg="white", command=self.start_spin).pack(pady=8)

    def _draw_wheel(self):
        self.canvas.delete("all")
        cx, cy = self.center
        for i in range(self.num_segments):
            start = (360 / self.num_segments) * i + self.angle_offset
            extent = 360 / self.num_segments
            color = self.colors[i % len(self.colors)]
            self.canvas.create_arc(cx - self.radius, cy - self.radius, cx + self.radius, cy + self.radius,
                                    start=start, extent=extent, fill=color, outline='white', width=2)
            mid_angle = math.radians(start + extent / 2)
            tx = cx + (self.radius * 0.6) * math.cos(mid_angle)
            ty = cy - (self.radius * 0.6) * math.sin(mid_angle)
            self.canvas.create_text(tx, ty, text=self.messages[i], font=("Arial", 10, "bold"), width=120, anchor="center")
        self.canvas.create_oval(cx-40, cy-40, cx+40, cy+40, fill='#ffffff', outline='#cccccc')
        self.canvas.create_text(cx, cy, text="SPIN", font=("Georgia", 14, "bold"))
        self.canvas.create_polygon(cx + self.radius + 10, cy, cx + self.radius - 10, cy - 12, cx + self.radius - 10, cy + 12, fill="#ff4d4d")

    def start_spin(self):
        if self.app.user_id is None:
            messagebox.showerror("Error", "Please log in to use the spin wheel.")
            return
            
        spins = random.randint(25, 45)
        self._spin_step(spins, 0)

    def _spin_step(self, remaining, total_done):
        if remaining <= 0:
            # The 'pointer' is conceptually at the 3 o'clock position (0 degrees in standard math/canvas coords)
            # The segments are drawn starting from the right (0 degrees) and extending counter-clockwise.
            # We need to find which segment the 0-degree line is pointing at.
            # The current angle_offset shifts the entire wheel clockwise.
            # Pointer is fixed at 0 degrees. The segment currently at 0 degrees is the one that has been rotated to that position.
            
            angle_per_segment = 360 / self.num_segments
            
            # The angle of the segment *start* relative to the pointer (0 degrees)
            # (0 - self.angle_offset) gives the position of the point at the rightmost edge, we need to map this to a segment index
            normalized_offset = (360 - self.angle_offset) % 360
            
            # Divide the normalized angle by the segment size to get the index.
            # We use an epsilon (0.0001) for floating point precision.
            seg = int((normalized_offset + 0.0001) // angle_per_segment) % self.num_segments
            
            message = self.messages[seg]
            self._show_result_popup(message)
            
            # Log the message as a journal entry
            try:
                timestamp = datetime.now()
                shlok, meaning = shloks.get("spin_message", [("","")])[0]
                cursor.execute("INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                               (self.app.user_id, self.app.username, 'spin_message', message, shlok, meaning, timestamp))
                conn.commit()
            except Exception as e:
                print("Failed to save spin message:", e)
            return
        
        # Calculate deceleration
        step = max(1, int(6 - math.log(remaining + 1)))
        self.angle_offset = (self.angle_offset + step * 15) % 360
        self._draw_wheel()
        delay = int(40 + (50 * (1 - (remaining / (remaining + total_done + 0.0001)))))
        self.after(delay, lambda: self._spin_step(remaining - 1, total_done + 1))

    def _show_result_popup(self, message):
        # Result pop-up is mandatory for spin wheel
        popup = tk.Toplevel(self)
        popup.title("Your Spin Message")
        popup.geometry("600x220")
        popup.configure(bg="#fff8e7")
        lbl = tk.Label(popup, text=message, font=("Georgia", 28, "bold"), bg="#fff8e7", wraplength=560, justify="center")
        lbl.pack(expand=True, padx=10, pady=20)
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=8)

class EntriesFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fff0f5")
        self.app = app
        header = tk.Frame(self, bg="#fff0f5")
        header.pack(fill="x", pady=8)
        tk.Label(header, text="Your Past Entries", font=("Georgia", 16, "bold"), bg="#fff0f5", fg="#b22222").pack(side="left", padx=10)
        controls = tk.Frame(self, bg="#fff0f0")
        controls.pack(fill="x", pady=6)
        tk.Label(controls, text="Search:", bg="#fff0f0").pack(side="left", padx=6)
        self.search_var = tk.StringVar()
        tk.Entry(controls, textvariable=self.search_var).pack(side="left", padx=6)
        tk.Button(controls, text="Go", command=self.refresh_entries).pack(side="left", padx=6)
        tk.Button(controls, text="Export CSV", command=lambda: app.show_frame("ExportFrame")).pack(side="left", padx=6)
        tk.Button(controls, text="Back", command=lambda: app.show_frame("ChatbotFrame")).pack(side="right", padx=10)

        # Frame for progress visualization (calendar) and treeview
        main_content_frame = tk.Frame(self, bg="#fff0f5")
        main_content_frame.pack(padx=10, pady=10, fill="both", expand=True)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=1)

        # Streak Calendar (Progress Visualization) - Conceptual
        self.calendar_canvas = tk.Canvas(main_content_frame, height=150, bg="#ffffff", highlightthickness=1)
        self.calendar_canvas.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(self.calendar_canvas, text="Journaling Progress Calendar (Conceptual Visualization of Streak Data)", font=("Arial", 12), bg="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        self.tree = ttk.Treeview(main_content_frame, columns=("id","timestamp","mood","thought"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("mood", text="Mood")
        self.tree.heading("thought", text="Thought (preview)")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("timestamp", width=180)
        self.tree.column("mood", width=120)
        self.tree.column("thought", width=520)
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self.on_double_click)
        self.detail = scrolledtext.ScrolledText(self, height=8, wrap="word")
        self.detail.pack(padx=10, pady=(0,10), fill="x")

    def refresh_entries(self, *_):
        q = self.search_var.get().strip()
        if q:
            cursor.execute("""
                SELECT id, timestamp, mood, thought FROM journal
                WHERE user_id = %s AND (thought LIKE %s OR mood LIKE %s)
                ORDER BY timestamp DESC
            """, (self.app.user_id, f"%{q}%", f"%{q}%"))
        else:
            cursor.execute("""
                SELECT id, timestamp, mood, thought FROM journal
                WHERE user_id = %s
                ORDER BY timestamp DESC
            """, (self.app.user_id,))
        rows = cursor.fetchall()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            preview = (r[3][:120].replace("\n"," ") + "...") if len(r[3])>120 else r[3].replace("\n"," ")
            ts = r[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[1], 'strftime') else str(r[1])
            self.tree.insert("", "end", values=(r[0], ts, r[2], preview))

    def on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        entry_id = item['values'][0]
        cursor.execute("SELECT timestamp, mood, thought, shlok, shlok_meaning FROM journal WHERE id = %s", (entry_id,))
        row = cursor.fetchone()
        if row:
            self.detail.config(state=tk.NORMAL)
            self.detail.delete("1.0", tk.END)
            mood = row[1]
            thought = row[2]
            shlok = row[3]
            shlok_meaning = row[4]
            result = analyze_and_reframe(thought, mood)
            reframed = result.get("reframed_text", "")

            # Remove asterisks from reframed text
            reframed_clean = reframed.replace("*", "")

            # Remove asterisks and format output with bold using tags
            self.detail.insert(tk.END, f"Timestamp: {row[0]}\n")
            self.detail.insert(tk.END, f"Mood: {mood}\n\n")
            self.detail.insert(tk.END, "Thought:\n")
            self.detail.insert(tk.END, f"{thought}\n\n")
            self.detail.insert(tk.END, "Shloka:\n")
            shloka_start = self.detail.index(tk.END)
            self.detail.insert(tk.END, f"{row[3]}\n")
            shloka_end = self.detail.index(tk.END)
            self.detail.tag_add("bold", shloka_start, shloka_end)
            self.detail.insert(tk.END, "Meaning:\n")
            self.detail.insert(tk.END, f"{row[4]}\n\n")

            if reframed_clean.strip():
                self.detail.insert(tk.END, "Reframing/Uplifting Message:\n")
                reframed_start = self.detail.index(tk.END)
                self.detail.insert(tk.END, f"{reframed_clean}\n")
                reframed_end = self.detail.index(tk.END)
                self.detail.tag_add("bold", reframed_start, reframed_end)

            self.detail.tag_configure("bold", font=("Arial", 12, "bold"))
            self.detail.config(state=tk.DISABLED)


class ExportFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fffaf0")
        self.app = app
        top = tk.Frame(self, bg="#fffaf0")
        top.pack(fill="x", pady=8)
        tk.Label(top, text="Export Entries to CSV", font=("Georgia", 18, "bold"), fg="#b22222", bg="#fffaf0").pack(side="left", padx=10)
        tk.Button(top, text="Back", command=lambda: app.show_frame("EntriesFrame")).pack(side="right", padx=10)
        self.tree = ttk.Treeview(self, columns=("id","timestamp","mood","thought"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("mood", text="Mood")
        self.tree.heading("thought", text="Thought (preview)")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("timestamp", width=180)
        self.tree.column("mood", width=120)
        self.tree.column("thought", width=520)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        btns = tk.Frame(self, bg="#fffaf0")
        btns.pack(fill="x", pady=8)
        tk.Button(btns, text="Export Selected", command=self.export_selected).pack(side="left", padx=6)
        tk.Button(btns, text="Export All", command=self.export_all).pack(side="left", padx=6)
        tk.Button(btns, text="Open Export Folder", command=self.open_export_folder).pack(side="left", padx=6)

    def refresh_preview(self, *_):
        for i in self.tree.get_children():
            self.tree.delete(i)
        cursor.execute("SELECT id, timestamp, mood, thought FROM journal WHERE user_id = %s ORDER BY timestamp DESC", (self.app.user_id,))
        rows = cursor.fetchall()
        for r in rows:
            preview = (r[3][:120].replace("\n"," ") + "...") if len(r[3])>120 else r[3].replace("\n"," ")
            ts = r[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[1], 'strftime') else str(r[1])
            self.tree.insert("", "end", values=(r[0], ts, r[2], preview))

    def export_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Export", "Please select one or more rows to export.")
            return
        ids = [self.tree.item(s)['values'][0] for s in sel]
        query = f"SELECT id, username, mood, thought, shlok, shlok_meaning, timestamp FROM journal WHERE id IN ({','.join(['%s']*len(ids))}) ORDER BY timestamp DESC"
        cursor.execute(query, tuple(ids))
        rows = cursor.fetchall()
        self._do_export(rows)

    def export_all(self):
        cursor.execute("SELECT id, username, mood, thought, shlok, shlok_meaning, timestamp FROM journal WHERE user_id = %s ORDER BY timestamp DESC", (self.app.user_id,))
        rows = cursor.fetchall()
        if not rows:
            messagebox.showinfo("Export CSV", "No entries to export.")
            return
        self._do_export(rows)

    def _do_export(self, rows):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile=f"{self.app.username}_journal.csv")
        if not file_path:
            return
        with open(file_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id","username","mood","thought","shlok","shlok_meaning","timestamp"])
            for r in rows:
                ts = r[6].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[6], 'strftime') else str(r[6])
                writer.writerow([r[0], r[1], r[2], r[3], r[4], r[5], ts])
        messagebox.showinfo("Export CSV", f"Exported {len(rows)} rows to {file_path}")

    def open_export_folder(self):
        try:
            cwd = os.path.abspath(os.getcwd())
            if os.name == 'nt':
                os.startfile(cwd)
            else:
                messagebox.showinfo("Open Folder", f"Open folder: {cwd}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder: {e}")
            
# The StatsFrame class is actually redundant as AdminDashboardFrame covers all its functionality now
# but kept here to complete the original structure if needed by other logic.
class StatsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#fff0f5")
        self.app = app
        top = tk.Frame(self, bg="#fff0f5")
        top.pack(fill="x", pady=10)
        tk.Label(top, text="Mood Statistics", font=("Georgia", 18, "bold"), fg="#b22222", bg="#fff0f5").pack(side="left", padx=10)
        tk.Button(top, text="Back", command=lambda: app.show_frame("ChatbotFrame")).pack(side="right", padx=10)
        self.canvas_holder = tk.Frame(self, bg="#fff0f5")
        self.canvas_holder.pack(fill="both", expand=True, padx=20, pady=10)

    def draw_stats(self):
        for w in self.canvas_holder.winfo_children():
            w.destroy()
        cursor.execute("SELECT mood, COUNT(*) FROM journal WHERE user_id = %s GROUP BY mood", (self.app.user_id,))
        rows = cursor.fetchall()
        moods = [r[0] for r in rows]
        counts = [r[1] for r in rows]
        if not rows:
            lbl = tk.Label(self.canvas_holder, text="No entries yet to show statistics.", bg="#fff0f5")
            lbl.pack()
            return
        fig = Figure(figsize=(5,4))
        ax = fig.add_subplot(111)
        ax.pie(counts, labels=moods, autopct='%1.1f%%')
        ax.set_title("Mood distribution")
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = SarathiApp()
    app.mainloop()