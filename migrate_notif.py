import sqlite3

db_path = '/home/dolistwe/dolist2/tasks.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

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
conn.close()