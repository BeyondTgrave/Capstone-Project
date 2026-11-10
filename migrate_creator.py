import sqlite3

db_path = '/home/dolistwe/dolist2/tasks.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Mapping NIM ke Nama (sesuai data USERS)
USERS = {
    '051425708': 'Yudha Bayu Pratama',
    '051140062': 'Rahma Sari',
    '050639618': 'Septi Nurmala',
    '052190693': 'Ridho Pambudihartho',
    '050656384': 'Izza Nailal Farokhi',
    '000000001': 'Dosen Pembimbing',
}

# Ambil semua kelompok
cur.execute("SELECT id, nama_kelompok, dibuat_oleh FROM kelompok")
kelompok_list = cur.fetchall()

print("=" * 60)
print("CEK & FIX: Pastikan pembuat ada di tabel anggota")
print("=" * 60)

fixed_count = 0
for k_id, k_nama, dibuat_oleh in kelompok_list:
    print("\nKelompok:", k_nama, "(ID: " + str(k_id) + ")")
    
    if not dibuat_oleh:
        print("  - dibuat_oleh KOSONG, skip")
        continue
    
    # Cek apakah pembuat sudah ada di tabel anggota
    cur.execute("SELECT id FROM anggota WHERE kelompok_id = ? AND nim = ?", (k_id, dibuat_oleh))
    existing = cur.fetchone()
    
    if existing:
        print("  - Pembuat (" + dibuat_oleh + ") SUDAH ada sebagai anggota ✓")
    else:
        nama_pembuat = USERS.get(dibuat_oleh, 'Unknown')
        cur.execute("INSERT INTO anggota (kelompok_id, nama, nim) VALUES (?, ?, ?)",
                    (k_id, nama_pembuat, dibuat_oleh))
        print("  - Menambahkan pembuat: " + nama_pembuat + " [" + dibuat_oleh + "] ✓")
        fixed_count += 1

conn.commit()

# Verifikasi akhir
print("\n" + "=" * 60)
print("HASIL AKHIR")
print("=" * 60)
cur.execute("SELECT id, nama_kelompok FROM kelompok")
for k_id, k_nama in cur.fetchall():
    cur.execute("SELECT nama, nim FROM anggota WHERE kelompok_id = ?", (k_id,))
    anggota = cur.fetchall()
    print("\n" + k_nama + ": " + str(len(anggota)) + " anggota")
    for nama, nim in anggota:
        print("  - " + nama + " [" + nim + "]")

print("\n" + "=" * 60)
print("Total kelompok yang diperbaiki: " + str(fixed_count))
print("=" * 60)

conn.close()