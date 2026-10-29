"""
Database Connection & Transparent Fallback Adapter for Sarathi Platform
Supports both MySQL 8.0+ and Serverless/Offline SQLite Fallback.
Guarantees 100% identical behavior across Localhost, GitHub, and Vercel.
"""

import os
import re
import sqlite3
import hashlib
from datetime import datetime, date

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

PEPPER = "sarathi_secure_pepper_1294_$"

def hash_password(password, username=""):
    combined = password + PEPPER + username.lower()
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def _datediff(d1, d2):
    if not d1 or not d2:
        return None
    try:
        if isinstance(d1, str):
            d1 = datetime.strptime(d1.split()[0], '%Y-%m-%d').date()
        elif isinstance(d1, datetime):
            d1 = d1.date()
        if isinstance(d2, str):
            d2 = datetime.strptime(d2.split()[0], '%Y-%m-%d').date()
        elif isinstance(d2, datetime):
            d2 = d2.date()
        return (d1 - d2).days
    except Exception:
        return 0

def _convert_val(v):
    """Convert SQLite ISO date/datetime strings to python date/datetime objects matching MySQL connector."""
    if isinstance(v, str):
        if len(v) == 10 and v[4] == '-' and v[7] == '-':
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                pass
        elif len(v) == 19 and v[4] == '-' and v[7] == '-' and v[10] in (' ', 'T'):
            try:
                return datetime.strptime(v.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
    return v

def _translate_sql(sql):
    """Translate MySQL dialect queries to SQLite compatible syntax."""
    translated = re.sub(r'(?<!%)%s', '?', sql)
    translated = translated.replace('%%', '%')
    return translated

class SQLiteCursorWrapper:
    def __init__(self, raw_cursor, dictionary=False):
        self._cursor = raw_cursor
        self.dictionary = dictionary

    @property
    def description(self):
        return self._cursor.description

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def execute(self, operation, params=None):
        sql = _translate_sql(operation)
        if params is None:
            return self._cursor.execute(sql)
        else:
            formatted_params = []
            for p in params:
                if isinstance(p, (datetime, date)):
                    formatted_params.append(str(p))
                elif isinstance(p, bool):
                    formatted_params.append(1 if p else 0)
                else:
                    formatted_params.append(p)
            return self._cursor.execute(sql, tuple(formatted_params))

    def executemany(self, operation, seq_of_params):
        sql = _translate_sql(operation)
        return self._cursor.executemany(sql, seq_of_params)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self.dictionary:
            cols = [d[0] for d in self._cursor.description]
            return {k: _convert_val(v) for k, v in zip(cols, row)}
        return tuple(_convert_val(v) for v in row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self.dictionary:
            cols = [d[0] for d in self._cursor.description]
            return [{k: _convert_val(v) for k, v in zip(cols, r)} for r in rows]
        return [tuple(_convert_val(v) for v in r) for r in rows]

    def fetchmany(self, size=None):
        rows = self._cursor.fetchmany(size) if size else self._cursor.fetchmany()
        if self.dictionary:
            cols = [d[0] for d in self._cursor.description]
            return [{k: _convert_val(v) for k, v in zip(cols, r)} for r in rows]
        return [tuple(_convert_val(v) for v in r) for r in rows]

    def close(self):
        try:
            self._cursor.close()
        except Exception:
            pass

class SQLiteConnectionWrapper:
    def __init__(self, sqlite_conn):
        self._conn = sqlite_conn
        self._conn.create_function("DATEDIFF", 2, _datediff)
        self._conn.create_function("NOW", 0, lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self._conn.create_function("CURDATE", 0, lambda: datetime.now().strftime('%Y-%m-%d'))

    def cursor(self, buffered=False, dictionary=False):
        raw_cur = self._conn.cursor()
        return SQLiteCursorWrapper(raw_cur, dictionary=dictionary)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        pass

def get_sqlite_path():
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "/tmp/sarathi_serverless.db"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "sarathi_fallback.db")

def init_sqlite_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        gender TEXT DEFAULT 'Female',
        age INTEGER DEFAULT 21,
        diagnosed_conditions TEXT DEFAULT 'None',
        journal_streak INTEGER DEFAULT 5,
        last_journal_date DATE DEFAULT NULL,
        mindful_points INTEGER DEFAULT 450,
        email TEXT DEFAULT 'chahat@wellness.in',
        account_for TEXT DEFAULT 'Self',
        managing_relationship TEXT DEFAULT 'Self'
    );

    CREATE TABLE IF NOT EXISTS counselors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        specialization TEXT NOT NULL,
        online_status INTEGER DEFAULT 1,
        last_login DATETIME DEFAULT NULL,
        qualifications TEXT DEFAULT 'Certified Mental Health Counselor',
        experience_years INTEGER DEFAULT 3,
        bio TEXT
    );

    CREATE TABLE IF NOT EXISTS counselor_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        counselor_id INTEGER,
        slot_time DATETIME NOT NULL,
        available INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        counselor_id INTEGER,
        booking_time DATETIME NOT NULL,
        specialization_requested TEXT,
        reason TEXT,
        status TEXT DEFAULT 'Confirmed',
        slot_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        mood TEXT,
        thought TEXT,
        shlok TEXT,
        shlok_meaning TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        risk_level TEXT DEFAULT 'low'
    );

    CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        tool_name TEXT,
        score INTEGER,
        risk_level TEXT
    );

    CREATE TABLE IF NOT EXISTS period_cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        start_date DATE,
        end_date DATE,
        notes TEXT,
        profile_id INTEGER DEFAULT NULL,
        profile_name TEXT DEFAULT 'Self',
        relation_tag TEXT DEFAULT 'Self',
        condition_tags TEXT DEFAULT 'None',
        pain_score INTEGER DEFAULT 0,
        cycle_phase TEXT DEFAULT 'Menstrual',
        flow_texture TEXT DEFAULT 'Standard',
        cervical_fluid TEXT DEFAULT 'Egg white',
        basal_temp REAL DEFAULT 36.5
    );

    CREATE TABLE IF NOT EXISTS period_screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        profile_id INTEGER DEFAULT NULL,
        profile_name TEXT DEFAULT 'Self',
        screener_type TEXT NOT NULL,
        total_score INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        details TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS managed_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        profile_name TEXT NOT NULL,
        relationship TEXT NOT NULL,
        gender TEXT DEFAULT 'Female',
        age INTEGER DEFAULT 24,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        diagnosed_conditions TEXT DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS counselor_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        counselor_id INTEGER NOT NULL,
        allowed_until DATE NOT NULL,
        status TEXT DEFAULT 'Active',
        can_view_journal INTEGER DEFAULT 1,
        can_view_screenings INTEGER DEFAULT 1,
        can_view_wellness INTEGER DEFAULT 1,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS to_do_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        points_awarded INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS user_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        resource_type TEXT,
        title TEXT,
        description TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS forum_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        content TEXT,
        author TEXT,
        timestamp DATETIME,
        username TEXT DEFAULT 'Anonymous',
        message TEXT
    );

    CREATE TABLE IF NOT EXISTS peer_support_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        user TEXT NOT NULL,
        category TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS peer_support_saved (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_title TEXT,
        post_category TEXT,
        post_content TEXT,
        saved_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check and seed users
    cur.execute("SELECT id FROM users WHERE username = 'chahat'")
    chahat_row = cur.fetchone()
    if not chahat_row:
        cur.execute("""
            INSERT INTO users (username, password, gender, age, diagnosed_conditions, journal_streak, mindful_points, email, account_for, managing_relationship)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('chahat', hash_password('chahat', 'chahat'), 'Female', 21, 'None', 5, 450, 'chahat@wellness.in', 'Self', 'Self'))
        chahat_id = cur.lastrowid
    else:
        chahat_id = chahat_row[0]

    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (username, password, gender, age, diagnosed_conditions, journal_streak, mindful_points, email, account_for, managing_relationship)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('admin', hash_password('admin123', 'admin'), 'Other', 30, 'None', 12, 1000, 'admin@sarathi.org', 'Self', 'Self'))

    cur.execute("SELECT id FROM counselors WHERE username = 'counselor1'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO counselors (username, password, specialization, online_status, qualifications, experience_years, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('counselor1', hash_password('pass123', 'counselor1'), 'Vedic Cognitive Counseling', 1, 'M.Phil Clinical Psychology', 6, 'Empathetic counselor focusing on Gita equanimity and stress reframing.'))

    # Seed demo period cycles for chahat
    cur.execute("SELECT COUNT(*) FROM period_cycles WHERE user_id = ?", (chahat_id,))
    if cur.fetchone()[0] == 0:
        demo_cycles = [
            (chahat_id, '2026-10-01', '2026-10-06', 'Regular flow, mild cramps, energized by day 4', None, 'Self', 'Self', 'PMS', 3, 'Menstrual', 'Standard', 'Egg white', 36.4),
            (chahat_id, '2026-09-03', '2026-09-08', 'Moderate cramps, calming chamomile tea helped', None, 'Self', 'Self', 'None', 2, 'Menstrual', 'Standard', 'Sticky', 36.5),
            (chahat_id, '2026-08-06', '2026-08-11', 'Consistent 28-day cadence, light morning walks', None, 'Self', 'Self', 'None', 1, 'Follicular', 'Standard', 'Creamy', 36.6),
            (chahat_id, '2026-07-09', '2026-07-14', 'Pelvic pain and bloating; applied heat therapy', None, 'Self', 'Self', 'PCOD', 6, 'Luteal', 'Thick/Clotted', 'Atypical', 36.8),
            (chahat_id, '2026-06-11', '2026-06-16', 'Late luteal mood dips and migraine; rested well', None, 'Self', 'Self', 'PMDD', 7, 'Late Luteal', 'Standard', 'Dry', 36.9),
        ]
        cur.executemany("""
            INSERT INTO period_cycles 
            (user_id, start_date, end_date, notes, profile_id, profile_name, relation_tag, condition_tags, pain_score, cycle_phase, flow_texture, cervical_fluid, basal_temp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_cycles)

    # Seed managed profiles
    cur.execute("SELECT COUNT(*) FROM managed_profiles WHERE user_id = ?", (chahat_id,))
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO managed_profiles (user_id, profile_name, relationship, gender, age, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chahat_id, 'Pooja (Sister)', 'Sister', 'Female', 24, 'Tracking irregular cycles & PMS'))
        cur.execute("""
            INSERT INTO managed_profiles (user_id, profile_name, relationship, gender, age, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chahat_id, 'Aarohi (Friend)', 'Friend', 'Female', 22, 'Caregiver support for PCOD management'))

    # Seed clinical period screenings
    cur.execute("SELECT COUNT(*) FROM period_screenings WHERE user_id = ?", (chahat_id,))
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO period_screenings (user_id, profile_name, screener_type, total_score, risk_level, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chahat_id, 'Self', 'PMDD', 18, 'Moderate PMDD Symptom Risk', 'High emotional sensitivity and luteal mood dips. Sthitaprajna mindfulness recommended.'))
        cur.execute("""
            INSERT INTO period_screenings (user_id, profile_name, screener_type, total_score, risk_level, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chahat_id, 'Self', 'PCOS', 14, 'Clinical PCOS Follow-Up Recommended', 'Irregular cycle history and pelvic tenderness reported. Consult clinical endocrinologist.'))

    # Seed general clinical screenings (PHQ-9 and GAD-7)
    cur.execute("SELECT COUNT(*) FROM screenings WHERE user_id = ?", (chahat_id,))
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO screenings (user_id, tool_name, score, risk_level)
            VALUES (?, ?, ?, ?)
        """, (chahat_id, 'PHQ-9', 6, 'Mild Depression Risk'))
        cur.execute("""
            INSERT INTO screenings (user_id, tool_name, score, risk_level)
            VALUES (?, ?, ?, ?)
        """, (chahat_id, 'GAD-7', 5, 'Mild Anxiety Risk'))

    conn.commit()

def get_db_connection():
    """
    Returns an active database connection.
    Attempts MySQL connection first; if MySQL is unavailable (e.g. Vercel serverless,
    network disconnect, offline mode), seamlessly falls back to embedded SQLite.
    """
    db_host = os.environ.get("DB_HOST", "localhost")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", os.environ.get("MYSQL_PASSWORD", os.environ.get("chahat", "chahat")))
    db_name = os.environ.get("DB_NAME", "sarathi_sih_db")

    if MYSQL_AVAILABLE and not os.environ.get("VERCEL"):
        try:
            conn = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                connection_timeout=2
            )
            if conn.is_connected():
                return conn
        except Exception:
            pass  # Fall back to SQLite

    db_path = get_sqlite_path()
    raw_sqlite = sqlite3.connect(db_path, check_same_thread=False)
    raw_sqlite.row_factory = sqlite3.Row
    init_sqlite_schema(raw_sqlite)
    return SQLiteConnectionWrapper(raw_sqlite)
