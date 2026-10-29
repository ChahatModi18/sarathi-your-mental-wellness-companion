"""
BhagvadMood Platform — Demonstration & Seed Data Utility (admin/seed_data.py)
Populates initial sample verified counselors, appointment slots, and demo screenings.
"""

import os
import sys
from datetime import datetime, timedelta

# Add root and backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from backend.database_setup import get_db_connection, hash_password
except ImportError:
    from database_setup import get_db_connection, hash_password


def seed_counselor():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure default counselor exists
    counselor_user = "dr_arun"
    counselor_pass = "counselor123"
    hashed = hash_password(counselor_pass, counselor_user)
    
    cursor.execute("SELECT id FROM users WHERE username = %s", (counselor_user,))
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO users (username, password, role, mindful_points, age, gender) VALUES (%s, %s, %s, %s, %s, %s)",
            (counselor_user, hashed, "counselor", 50, 42, "male")
        )
        conn.commit()
        counselor_id = cursor.lastrowid
        print(f"[+] Created verified counselor: {counselor_user}")
    else:
        counselor_id = row[0]
        print(f"[i] Counselor {counselor_user} already exists (ID: {counselor_id})")
        
    # Generate 3 upcoming consultation slots
    now = datetime.now()
    slots = [
        now + timedelta(days=1, hours=2),
        now + timedelta(days=2, hours=4),
        now + timedelta(days=3, hours=1)
    ]
    
    for slot in slots:
        cursor.execute("SELECT id FROM counselor_slots WHERE counselor_id = %s AND slot_time = %s", (counselor_id, slot))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO counselor_slots (counselor_id, slot_time, is_booked) VALUES (%s, %s, %s)",
                (counselor_id, slot, False)
            )
            print(f"[+] Added slot: {slot.strftime('%Y-%m-%d %H:%M')}")
            
    conn.commit()
    cursor.close()
    conn.close()
    print("[+] Seeding complete.")


if __name__ == "__main__":
    seed_counselor()

