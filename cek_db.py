import sqlite3
import os

db_path = '/home/dolistwe/dolist2/tasks.db'

print("=" * 50)
print("File: " + db_path)
print("Ada: " + str(os.path.exists(db_path)))

if os.path.exists(db_path):
    print("Size: " + str(os.path.getsize(db_path)) + " bytes")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    print("Tabel: " + str(tables))
    
    if 'task' in tables:
        cur.execute("PRAGMA table_info(task)")
        cols = [c[1] for c in cur.fetchall()]
        print("Kolom 'task': " + str(cols))
        if 'kelompok_id' in cols:
            print(">> kelompok_id SUDAH ADA")
        else:
            print(">> kelompok_id BELUM ADA")
    conn.close()
print("=" * 50)