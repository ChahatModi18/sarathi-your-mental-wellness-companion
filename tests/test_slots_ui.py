import mysql.connector, os
from datetime import datetime, timedelta

def quick_test():
    pw = os.environ.get('chahat', 'chahat')
    conn = mysql.connector.connect(host='localhost', user='root', password=pw)
    cursor = conn.cursor()
    cursor.execute('USE sarathi_sih_db')
    # create a dummy counselor if none exists
    cursor.execute('SELECT id FROM counselors LIMIT 1')
    r = cursor.fetchone()
    if not r:
        cursor.execute("INSERT INTO counselors (username,password,specialization,online_status) VALUES (%s,%s,%s,%s)", ('slot_tester','pw','General',True))
        conn.commit()
        cid = cursor.lastrowid
    else:
        cid = r[0]
    # create slot
    st = (datetime.now()+timedelta(days=2)).replace(hour=11,minute=0,second=0,microsecond=0)
    cursor.execute('INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s,%s,%s)', (cid, st, True))
    conn.commit()
    sid = cursor.lastrowid
    print('Created slot', sid)
    # mark unavailable
    cursor.execute('UPDATE counselor_slots SET available=FALSE WHERE id=%s', (sid,))
    conn.commit()
    cursor.execute('SELECT available FROM counselor_slots WHERE id=%s', (sid,))
    print('Available after update ->', cursor.fetchone()[0])
    # cleanup
    cursor.execute('DELETE FROM counselor_slots WHERE id=%s', (sid,))
    conn.commit()
    print('Cleanup done')
    conn.close()

if __name__ == '__main__':
    quick_test()
