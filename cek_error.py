import sys
try:
    import app
    print("SUKSES: File app.py tidak ada error (APP OK).")
except Exception as e:
    print("GAGAL IMPORT. Ada error di app.py:")
    import traceback
    traceback.print_exc()