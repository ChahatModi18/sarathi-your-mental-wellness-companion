import os
import sys
# Inject the virtual environment's site packages path only if using a compatible Python 3.14 interpreter
venv_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib", "site-packages")
if sys.version_info[:2] == (3, 14) and os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)
import hashlib
from datetime import datetime, timedelta
import mysql.connector

def hash_password(password, username=""):
    salt = "sarathi_secure_pepper_1294_$"
    combined = password + salt + username.lower()
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def get_db_connection():
    db_password = os.environ.get("DB_PASSWORD", os.environ.get("MYSQL_PASSWORD", os.environ.get("chahat", "chahat")))
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=db_password,
        database=os.environ.get("DB_NAME", "sarathi_sih_db")
    )

def init_db():
    db_password = os.environ.get("chahat", "chahat")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=db_password
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS sarathi_sih_db")
    cursor.execute("USE sarathi_sih_db")
    
    # 1. users
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
    
    # 2. counselors
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
    
    # Populate default counselors if empty
    cursor.execute("SELECT COUNT(*) FROM counselors")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO counselors (username, password, specialization) VALUES (%s, %s, %s)", 
                       ('counselor1', hash_password('pass123', 'counselor1'), 'General Wellness'))
        cursor.execute("INSERT INTO counselors (username, password, specialization) VALUES (%s, %s, %s)", 
                       ('dr.sharma', hash_password('counsellor', 'dr.sharma'), 'Anxiety/Stress'))
        conn.commit()
        
    # 3. bookings
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
    
    # 4. counselor_slots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counselor_slots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            counselor_id INT NOT NULL,
            slot_time DATETIME NOT NULL,
            available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (counselor_id) REFERENCES counselors(id)
        )
    """)
    
    # Add dummy slots if empty
    cursor.execute("SELECT COUNT(*) FROM counselor_slots")
    if cursor.fetchone()[0] == 0:
        now = datetime.now()
        cursor.execute("SELECT id FROM counselors")
        counselor_ids = [row[0] for row in cursor.fetchall()]
        for c_id in counselor_ids:
            for day in range(1, 4): # next 3 days
                slot_time = datetime(now.year, now.month, now.day, 10, 0) + timedelta(days=day)
                cursor.execute("INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s, %s, %s)", (c_id, slot_time, True))
                slot_time_2 = datetime(now.year, now.month, now.day, 14, 30) + timedelta(days=day)
                cursor.execute("INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s, %s, %s)", (c_id, slot_time_2, True))
        conn.commit()

    # 5. journal
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
    
    # 6. period_cycles
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
    
    # 7. user_resources
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
    
    # 8. screenings
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
    
    # 9. forum_posts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            username VARCHAR(100) NOT NULL,
            category VARCHAR(100) NOT NULL,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cursor.execute("ALTER TABLE forum_posts ADD COLUMN username VARCHAR(100) NOT NULL DEFAULT 'Anonymous'")
        conn.commit()
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE forum_posts ADD COLUMN message TEXT")
        conn.commit()
    except Exception:
        pass
    
    cursor.execute("SELECT COUNT(*) FROM forum_posts")
    if cursor.fetchone()[0] == 0:
        posts = [
            ("How do you handle academic stress?", "Anonymous Student", "Student Life", "I often feel overwhelmed by deadlines, exams, and the pressure to perform. Does anyone have a practical routine or mindset tip that helped them manage academic stress?"),
            ("Balancing work and personal life is so tough.", "Anonymous Professional", "Professional Work", "Work hours are so long lately, and I struggle to switch off when I get home. How do you maintain personal time without feeling guilty?"),
            ("I'm feeling really lonely on campus, anyone else?", "Anonymous Student", "Student Life", "I sit in classes and feel disconnected from everyone, even though I want friends. Has anyone found ways to build meaningful connections in college?"),
            ("Tips for better sleep when anxious?", "Anonymous User", "Physical Health", "My mind races at night and I can't sleep. I want healthy habits, not medication. What calming routines have helped you?"),
            ("What's the best way to talk to a friend who is struggling?", "Anonymous Peer", "Mental Health", "A close friend is going through a hard time, but I don't know whether to ask directly or give them space. How can I support them without making things worse?"),
            ("Dealing with chronic pain and mental health.", "Anonymous User", "Physical Health", "Living with pain has made me feel exhausted and low. How do you cope on days when both your body and your mind hurt?")
        ]
        for title, user, cat, msg in posts:
            cursor.execute("INSERT INTO forum_posts (title, username, category, message) VALUES (%s, %s, %s, %s)", (title, user, cat, msg))
        conn.commit()

    # 10. to_do_list
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS to_do_list (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            task VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            points_awarded BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 11. counselor_permissions (Client sharing consent with custom allowed_until date)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counselor_permissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            counselor_id INT NOT NULL,
            allowed_until DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'Active',
            can_view_journal BOOLEAN DEFAULT TRUE,
            can_view_screenings BOOLEAN DEFAULT TRUE,
            can_view_wellness BOOLEAN DEFAULT TRUE,
            notes TEXT DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (counselor_id) REFERENCES counselors(id) ON DELETE CASCADE
        )
    """)

    # 12. managed_profiles (Multiple profiles/dependents managed by user, e.g. women in male user's life)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS managed_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            profile_name VARCHAR(100) NOT NULL,
            relationship VARCHAR(50) NOT NULL,
            gender VARCHAR(20) DEFAULT 'Female',
            age INT DEFAULT NULL,
            notes TEXT DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Schema Migrations for existing tables
    def safe_add_column(table, column_def):
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
            conn.commit()
        except Exception:
            pass

    safe_add_column("period_cycles", "profile_id INT DEFAULT NULL")
    safe_add_column("period_cycles", "profile_name VARCHAR(100) DEFAULT 'Self'")
    safe_add_column("period_cycles", "relation_tag VARCHAR(50) DEFAULT 'Self'")

    safe_add_column("counselors", "qualifications VARCHAR(255) DEFAULT 'Certified Mental Health Counselor'")
    safe_add_column("counselors", "experience_years INT DEFAULT 3")
    safe_add_column("counselors", "bio TEXT DEFAULT NULL")

    safe_add_column("users", "account_for VARCHAR(50) DEFAULT 'Self'")
    safe_add_column("users", "managing_relationship VARCHAR(50) DEFAULT 'Self'")
    # 13. period_screenings (PCOS and PMDD diagnostic questionnaires)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_screenings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            profile_id INT DEFAULT NULL,
            profile_name VARCHAR(100) DEFAULT 'Self',
            screener_type VARCHAR(50) NOT NULL,
            total_score INT NOT NULL,
            risk_level VARCHAR(100) NOT NULL,
            details TEXT DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    safe_add_column("period_cycles", "condition_tags VARCHAR(255) DEFAULT NULL")
    safe_add_column("period_cycles", "pain_score INT DEFAULT NULL")
    safe_add_column("period_cycles", "cycle_phase VARCHAR(50) DEFAULT NULL")
    safe_add_column("period_cycles", "flow_texture VARCHAR(50) DEFAULT NULL")
    safe_add_column("period_cycles", "cervical_fluid VARCHAR(50) DEFAULT NULL")
    safe_add_column("period_cycles", "basal_temp DECIMAL(4,2) DEFAULT NULL")

    safe_add_column("managed_profiles", "diagnosed_conditions VARCHAR(255) DEFAULT NULL")

    # Admin seed
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "adminpass"
    cursor.execute("SELECT id FROM users WHERE username = %s", (ADMIN_USERNAME,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD, ADMIN_USERNAME)))
        conn.commit()

    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database sarathi_sih_db created/verified and populated successfully.")
