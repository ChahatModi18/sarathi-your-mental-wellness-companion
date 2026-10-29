import mysql.connector
import os
from datetime import datetime, timedelta


def main():
    pw = os.environ.get('chahat', 'chahat')
    print('Using DB password from env present:', 'chahat' in os.environ)
    conn = mysql.connector.connect(host='localhost', user='root', password=pw)
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS sarathi_sih_db')
    cursor.execute('USE sarathi_sih_db')
    # Ensure counselor_slots table exists (in case Main.py hasn't been run yet)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS counselor_slots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            counselor_id INT NOT NULL,
            slot_time DATETIME NOT NULL,
            available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (counselor_id) REFERENCES counselors(id)
        )
    ''')
    conn.commit()

    # Ensure tables exist
    cursor.execute("SHOW TABLES LIKE 'counselors'")
    if not cursor.fetchone():
        print('counselors table missing; abort')
        return

    cursor.execute("SELECT id FROM counselors LIMIT 1")
    cres = cursor.fetchone()
    if not cres:
        print('No counselor found; abort')
        return
    c_id = cres[0]

    # create temp user
    username = f"test_user_tmp_{int(datetime.now().timestamp())}"
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, 'tmp'))
    uid = cursor.lastrowid
    conn.commit()
    print('Created temp user id', uid)

    # create slot
    slot_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    cursor.execute("INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s, %s, %s)", (c_id, slot_time, True))
    sid = cursor.lastrowid
    conn.commit()
    print('Inserted slot id', sid, 'at', slot_time)

    cursor.execute("SELECT available FROM counselor_slots WHERE id = %s", (sid,))
    print('slot available ->', cursor.fetchone()[0])

    # simulate booking: mark unavailable and add booking
    cursor.execute("UPDATE counselor_slots SET available = FALSE WHERE id = %s", (sid,))
    cursor.execute(
        "INSERT INTO bookings (user_id, counselor_id, booking_time, slot_id, specialization_requested, reason, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (uid, c_id, slot_time, sid, 'General', 'Test booking', 'Confirmed')
    )
    bid = cursor.lastrowid
    conn.commit()
    print('Inserted booking id', bid)

    # verify booking exists
    cursor.execute("SELECT id, slot_id FROM bookings WHERE id = %s", (bid,))
    print('Booking row ->', cursor.fetchone())

    # cleanup
    cursor.execute("DELETE FROM bookings WHERE id = %s", (bid,))
    cursor.execute("UPDATE counselor_slots SET available = TRUE WHERE id = %s", (sid,))
    cursor.execute("DELETE FROM counselor_slots WHERE id = %s", (sid,))
    cursor.execute("DELETE FROM users WHERE id = %s", (uid,))
    conn.commit()
    print('Cleanup done')
    conn.close()


if __name__ == '__main__':
    main()
