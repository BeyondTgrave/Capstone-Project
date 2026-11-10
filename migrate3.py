import sqlite3

db_path = '/home/dolistwe/dolist2/tasks.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Tambah kolom dibuat_oleh di tabel kelompok
try:
    cur.execute("ALTER TABLE kelompok ADD COLUMN dibuat_oleh VARCHAR(20)")
    conn.commit()
    print("OK - kolom dibuat_oleh ditambahkan")
except Exception as e:
    print("Info:", e)

# 2. Buat tabel notifikasi
try:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notifikasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_nim VARCHAR(20) NOT NULL,
            judul VARCHAR(200) NOT NULL,
            pesan TEXT,
            link VARCHAR(200),
            dibaca BOOLEAN DEFAULT 0,
            created_at DATETIME
        )
    ''')
    conn.commit()
    print("OK - tabel notifikasi dibuat")
except Exception as e:
    print("Error:", e)

# 3. Verifikasi
cur.execute("PRAGMA table_info(kelompok)")
print("Kolom kelompok:", [c[1] for c in cur.fetchall()])

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tabel:", [t[0] for t in cur.fetchall()])

conn.close()