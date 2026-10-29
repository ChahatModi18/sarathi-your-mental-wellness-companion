"""
Full Database Population & Seeding Utility (admin/seed_full_database.py)
Populates realistic counselors, users, journal entries, screenings, bookings,
counselor slots, forum posts, and community resources.
"""

import os
import sys
from datetime import datetime, timedelta, date
import random

# Add root and backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from database_setup import get_db_connection, hash_password


def seed_database():
    print("[*] Connecting to MySQL database 'sarathi_sih_db'...")
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now()

    # 1. SEED COUNSELORS
    print("[+] Seeding Mental Health Professionals / Counselors...")
    counselors_data = [
        ("dr_aarav_sharma", "counselor123", "Cognitive Behavioral Therapy (CBT)", True, now - timedelta(hours=2)),
        ("dr_meera_iyer", "counselor123", "Mindfulness & Stress Management", True, now - timedelta(hours=5)),
        ("dr_rohit_verma", "counselor123", "Student & Academic Anxiety", True, now - timedelta(minutes=45)),
        ("dr_ananya_sen", "counselor123", "Grief, Loss & Trauma Recovery", False, now - timedelta(days=1)),
        ("dr_vikram_patel", "counselor123", "Workplace Burnout & Career Transition", True, now - timedelta(hours=1))
    ]

    counselor_id_map = {}
    for username, pwd, spec, online, last_login in counselors_data:
        cursor.execute("SELECT id FROM counselors WHERE username = %s", (username,))
        row = cursor.fetchone()
        if not row:
            hashed = hash_password(pwd, username)
            cursor.execute("""
                INSERT INTO counselors (username, password, specialization, online_status, last_login)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, hashed, spec, online, last_login))
            c_id = cursor.lastrowid
            print(f"  -> Added Counselor: {username} ({spec})")
        else:
            c_id = row[0]
            cursor.execute("UPDATE counselors SET online_status = %s, last_login = %s WHERE id = %s", (online, last_login, c_id))
        counselor_id_map[username] = c_id
    conn.commit()

    # 2. SEED USERS ACROSS PERSONAS
    print("[+] Seeding User Personas (Students, Professionals, Non-Professionals)...")
    users_data = [
        ("rohan_student", "user123", "rohan@campus.edu", "male", 21, "Mild Exam Anxiety", 8, now.date(), 285),
        ("neha_kapoor", "user123", "neha.k@gmail.com", "female", 23, "None", 14, now.date(), 420),
        ("priya_tech", "user123", "priya.dev@corp.io", "female", 28, "Workplace Burnout", 5, now.date() - timedelta(days=1), 190),
        ("karan_mehta", "user123", "karan@startup.co", "male", 31, "Chronic Fatigue", 3, now.date(), 110),
        ("ananya_deshmukh", "user123", "ananya@univ.ac.in", "female", 20, "None", 19, now.date(), 560),
        ("arjun_verma", "user123", "arjun.v@outlook.com", "male", 22, "None", 6, now.date(), 175)
    ]

    user_id_map = {}
    for username, pwd, email, gender, age, diag, streak, last_date, pts in users_data:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if not row:
            hashed = hash_password(pwd, username)
            cursor.execute("""
                INSERT INTO users (username, password, email, gender, age, diagnosed_conditions, journal_streak, last_journal_date, mindful_points)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, hashed, email, gender, age, diag, streak, last_date, pts))
            u_id = cursor.lastrowid
            print(f"  -> Added User: {username} (Age: {age}, Streak: {streak} days, {pts} MP)")
        else:
            u_id = row[0]
        user_id_map[username] = u_id
    conn.commit()

    # Ensure admin user has mindful points
    cursor.execute("UPDATE users SET mindful_points = 500 WHERE username = 'admin'")
    conn.commit()

    # 3. SEED COUNSELOR SLOTS & APPOINTMENT BOOKINGS
    print("[+] Seeding Consultation Slots & Session Bookings...")
    slot_times = [
        now + timedelta(days=1, hours=2),
        now + timedelta(days=1, hours=5),
        now + timedelta(days=2, hours=3),
        now + timedelta(days=2, hours=6),
        now + timedelta(days=3, hours=1),
        now + timedelta(days=4, hours=4)
    ]

    for c_user, c_id in counselor_id_map.items():
        for st in slot_times:
            cursor.execute("SELECT id FROM counselor_slots WHERE counselor_id = %s AND slot_time = %s", (c_id, st))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO counselor_slots (counselor_id, slot_time, available)
                    VALUES (%s, %s, %s)
                """, (c_id, st, True))
    conn.commit()

    # Create sample bookings
    sample_bookings = [
        ("rohan_student", "dr_rohit_verma", now + timedelta(days=1, hours=2), "Academic & Exam Anxiety", "Struggling with upcoming final exam anxiety and sleep issues.", "Approved"),
        ("priya_tech", "dr_vikram_patel", now + timedelta(days=2, hours=3), "Workplace Burnout", "Feeling exhausted by continuous sprint deadlines and lack of work-life boundaries.", "Pending"),
        ("karan_mehta", "dr_aarav_sharma", now + timedelta(days=3, hours=1), "Cognitive Behavioral Therapy (CBT)", "Intrusive negative self-talk during high-stakes presentations.", "Approved")
    ]

    for u_name, c_name, b_time, spec, reason, status in sample_bookings:
        u_id = user_id_map.get(u_name)
        c_id = counselor_id_map.get(c_name)
        if u_id and c_id:
            cursor.execute("SELECT id FROM bookings WHERE user_id = %s AND counselor_id = %s", (u_id, c_id))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO bookings (user_id, counselor_id, booking_time, specialization_requested, reason, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (u_id, c_id, b_time, spec, reason, status))
    conn.commit()

    # 4. SEED JOURNAL REFLECTIONS WITH AUTHENTIC GITA SHLOKAS
    print("[+] Seeding Journal Reflections with Vedic Reframings...")
    journal_reflections = [
        (
            "rohan_student", "anxious",
            "I have my data structures final exam tomorrow morning and I feel completely overwhelmed. I keep thinking what if I forget everything and fail.",
            "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
            "You have a right to perform your prescribed duty, but never to the fruits of action. Never let outcomes be your motive, nor be attached to inaction. — BG 2.47",
            now - timedelta(hours=3), "low"
        ),
        (
            "priya_tech", "overwhelmed",
            "My team lead dumped three emergency tickets on my desk right at 6 PM. I feel so drained, like my work never ends.",
            "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु। युक्तस्वप्नावबोधस्य योगो भवति दुःखहा॥",
            "He who is regulated in eating, recreation, work, sleep, and wakefulness attains yoga that destroys all sorrow. — BG 6.17",
            now - timedelta(days=1, hours=4), "low"
        ),
        (
            "ananya_deshmukh", "peaceful",
            "Woke up early and spent 20 minutes walking in the campus garden. Felt deep gratitude for the morning sunlight and quiet breeze.",
            "शान्तिमाप्नोति नैष्ठिकीम्।",
            "One who controls the senses and acts without anxiety attains supreme lasting peace. — BG 5.12",
            now - timedelta(hours=6), "low"
        ),
        (
            "karan_mehta", "discouraged",
            "The client rejected our proposal after three weeks of intense effort. Hard not to take it personally and doubt my competence.",
            "उद्धरेदात्मनाऽऽत्मानं नात्मानमवसादयेत्। आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
            "Elevate yourself by your own mind; do not degrade yourself. For the mind alone is your greatest ally. — BG 6.5",
            now - timedelta(days=2, hours=1), "low"
        ),
        (
            "neha_kapoor", "happy",
            "Submitted my minor project report on time! My mentor appreciated the neural network architecture. Feeling accomplished and calm.",
            "आत्मरतिरेव स्यात् आत्मतृप्तश्च मानवः।",
            "The person who rejoices in the self and is satisfied within attains authentic contentment. — BG 3.17",
            now - timedelta(days=3), "low"
        )
    ]

    for u_name, mood, thought, shlok, meaning, ts, risk in journal_reflections:
        u_id = user_id_map.get(u_name)
        if u_id:
            cursor.execute("SELECT id FROM journal WHERE user_id = %s AND thought = %s", (u_id, thought))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp, risk_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (u_id, u_name, mood, thought, shlok, meaning, ts, risk))
    conn.commit()

    # 5. SEED CLINICAL SCREENINGS (PHQ-9 & GAD-7)
    print("[+] Seeding Psychometric Clinical Screenings...")
    screenings_data = [
        ("rohan_student", "GAD-7", 12, "Moderate Anxiety", now - timedelta(days=2)),
        ("rohan_student", "PHQ-9", 7, "Mild Depression", now - timedelta(days=2)),
        ("priya_tech", "GAD-7", 16, "Severe Anxiety", now - timedelta(days=1)),
        ("priya_tech", "PHQ-9", 14, "Moderate Depression", now - timedelta(days=1)),
        ("neha_kapoor", "GAD-7", 4, "Minimal Anxiety", now - timedelta(days=4)),
        ("neha_kapoor", "PHQ-9", 3, "Minimal Depression", now - timedelta(days=4)),
        ("karan_mehta", "PHQ-9", 11, "Moderate Depression", now - timedelta(days=3))
    ]

    for u_name, tool, score, sev, ts in screenings_data:
        u_id = user_id_map.get(u_name)
        if u_id:
            cursor.execute("SELECT id FROM screenings WHERE user_id = %s AND tool_name = %s AND score = %s", (u_id, tool, score))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO screenings (user_id, timestamp, tool_name, score, risk_level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (u_id, ts, tool, score, sev))
    conn.commit()

    # 6. SEED ANONYMOUS FORUM THREADS
    print("[+] Seeding Community Support Forum Threads...")
    forum_threads = [
        ("How do you manage pre-exam panic attacks?", "rohan_student", "Student Life", "Whenever I sit in the exam hall, my heart races and my hands shake. What grounding techniques have genuinely worked for you?", now - timedelta(days=3)),
        ("Setting work-life boundaries in high-growth startups", "priya_tech", "Workplace & Career", "Has anyone successfully negotiated turning off Slack notifications after 7 PM without facing passive-aggressive comments from managers?", now - timedelta(days=2)),
        ("The power of the 5-4-3-2-1 grounding exercise", "ananya_deshmukh", "Mindfulness", "I tried the sensory grounding tool in the Resources Hub during a spiral yesterday. Acknowledging 5 physical objects around my desk completely brought my pulse back to normal.", now - timedelta(days=1)),
        ("Morning sunlight and sleep circadian reset", "dr_meera_iyer", "General Wellbeing", "Friendly clinical reminder: getting 10-15 minutes of direct natural sunlight into your eyes within an hour of waking sets your melatonin clock for deeper sleep tonight.", now - timedelta(hours=14))
    ]

    for title, author, cat, msg, ts in forum_threads:
        cursor.execute("SELECT id FROM forum_posts WHERE title = %s", (title,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO forum_posts (title, username, category, message, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, author, cat, msg, ts))
    conn.commit()

    # 7. SEED COMMUNITY RESOURCES
    print("[+] Seeding Community Shared Coping Resources...")
    resources_data = [
        ("rohan_student", "Coping Technique", "Square Breathing (4-4-4-4) Before Presentations", "Inhale 4s, hold 4s, exhale 4s, hold 4s for 3 cycles. It instantly lowers high sympathetic arousal before speaking in front of an audience.", now - timedelta(days=4)),
        ("neha_kapoor", "Book / Article", "The Happiness Trap by Russ Harris (ACT Guide)", "A transformative read on Acceptance and Commitment Therapy. It teaches you how to unhook from intrusive thoughts without battling them.", now - timedelta(days=2))
    ]

    for u_name, r_type, title, desc, ts in resources_data:
        u_id = user_id_map.get(u_name)
        if u_id:
            cursor.execute("SELECT id FROM user_resources WHERE title = %s", (title,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO user_resources (user_id, username, resource_type, title, description, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (u_id, u_name, r_type, title, desc, ts))
    conn.commit()

    cursor.close()
    conn.close()
    print("\n[SUCCESS] Database populated with full set of counselors, user personas, slots, journal entries, and clinical screenings!")


if __name__ == "__main__":
    seed_database()

