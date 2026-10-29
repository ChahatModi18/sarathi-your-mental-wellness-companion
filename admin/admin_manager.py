"""
BhagvadMood Platform — Administrative Management Suite (admin/admin_manager.py)
Provides administrative CLI commands, database integrity checks, user role audits,
counselor management, and crisis log inspection.
"""

import os
import sys
from datetime import datetime

# Add root and backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from backend.database_setup import get_db_connection
except ImportError:
    from database_setup import get_db_connection


def print_banner():
    print("=" * 70)
    print(" 🕉️  BHAGVADMOOD / SARATHI — ADMINISTRATIVE CONTROL PANEL")
    print("=" * 70)


def audit_platform_health():
    """Audits MySQL tables, row counts, and system status."""
    print("\n[+] Checking MySQL Database Connection & Table Statistics...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tables = [
            "users", "journal", "counselors", "counselor_slots", 
            "bookings", "forum_posts", "to_do_list", "user_resources", 
            "screenings", "period_cycles"
        ]
        
        print(f"{'Table Name':<20} | {'Row Count':<10} | {'Status':<15}")
        print("-" * 50)
        
        total_records = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"{table:<20} | {count:<10} | OK")
            except Exception as e:
                print(f"{table:<20} | {'ERR':<10} | {str(e)[:15]}")
                
        print("-" * 50)
        print(f"Total Platform Records across {len(tables)} tables: {total_records}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[!] Database Connection Error: {e}")
        return False


def list_users():
    """Lists all registered users and their profile details."""
    print("\n[+] Registered Users Audit:")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, mindful_points, age, gender, journal_streak FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        
        print(f"{'ID':<4} | {'Username':<20} | {'Points':<8} | {'Age':<5} | {'Gender':<8} | {'Streak'}")
        print("-" * 65)
        for r in rows:
            print(f"{r[0]:<4} | {r[1]:<20} | {r[2]:<8} | {r[3] or 'N/A':<5} | {r[4] or 'N/A':<8} | {r[5]}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[!] Error fetching users: {e}")


def list_counselor_slots():
    """Lists upcoming counselor availability slots and booking states."""
    print("\n[+] Counselor Appointment Slots:")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cs.id, c.username, cs.slot_time, cs.available 
            FROM counselor_slots cs
            JOIN counselors c ON cs.counselor_id = c.id
            ORDER BY cs.slot_time ASC
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("  No counselor slots scheduled currently.")
        else:
            print(f"{'Slot ID':<8} | {'Counselor':<20} | {'Slot Time':<25} | {'Status'}")
            print("-" * 70)
            for r in rows:
                status = "Available" if r[3] else "Booked"
                print(f"{r[0]:<8} | {r[1]:<20} | {str(r[2]):<25} | {status}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[!] Error fetching slots: {e}")


def view_crisis_screenings():
    """Audits clinical screenings (PHQ-9 and GAD-7) with high severity indicators."""
    print("\n[+] Clinical Screening Audits:")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, u.username, s.tool_name, s.score, s.risk_level, s.timestamp
            FROM screenings s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.timestamp DESC LIMIT 10
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("  No screening records found.")
        else:
            print(f"{'ID':<4} | {'User':<18} | {'Tool':<8} | {'Score':<6} | {'Severity':<18} | {'Timestamp'}")
            print("-" * 75)
            for r in rows:
                print(f"{r[0]:<4} | {r[1]:<18} | {r[2]:<8} | {r[3]:<6} | {r[4]:<18} | {str(r[5])}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[!] Error reading screenings: {e}")


def interactive_menu():
    print_banner()
    while True:
        print("\nAdministrative Operations:")
        print("  1. Audit Platform & Table Statistics")
        print("  2. List All Registered Users")
        print("  3. View Counselor Availability Slots")
        print("  4. View Clinical Screening Audits")
        print("  5. Run Database Migration / Initializer")
        print("  6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        if choice == "1":
            audit_platform_health()
        elif choice == "2":
            list_users()
        elif choice == "3":
            list_counselor_slots()
        elif choice == "4":
            view_crisis_screenings()
        elif choice == "5":
            try:
                from backend.database_setup import init_db
                init_db()
                print("[+] Database initialized successfully.")
            except Exception as e:
                print(f"[!] Initialization error: {e}")
        elif choice == "6":
            print("\nExiting administrative console. Namaste!")
            break
        else:
            print("Invalid selection. Please choose 1-6.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "audit":
            audit_platform_health()
        elif cmd == "users":
            list_users()
        elif cmd == "slots":
            list_counselor_slots()
        elif cmd == "screenings":
            view_crisis_screenings()
        else:
            print(f"Unknown command '{cmd}'. Available: audit, users, slots, screenings")
    else:
        interactive_menu()
