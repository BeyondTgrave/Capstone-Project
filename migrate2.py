import sqlite3

db_path = '/home/dolistwe/dolist2/tasks.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE task ADD COLUMN assigned_to VARCHAR(20)")
    conn.commit()
    print("OK - kolom assigned_to berhasil ditambahkan!")
except Exception as e:
    print("Info: " + str(e))

# Verifikasi
cur.execute("PRAGMA table_info(task)")
cols = [c[1] for c in cur.fetchall()]
print("Kolom sekarang: " + str(cols))
conn.close()