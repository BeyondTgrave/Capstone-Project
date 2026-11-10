from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/dolistwe/dolist2/tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dolist-secret-key-2026-ut'

# Konfigurasi Folder Upload Lampiran
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# ================= MODEL =================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='Sedang')
    category = db.Column(db.String(50), nullable=True)
    kelompok_id = db.Column(db.Integer, db.ForeignKey('kelompok.id'), nullable=True)
    assigned_to = db.Column(db.String(20), nullable=True)
    lampiran = db.Column(db.String(200), nullable=True)

class Kelompok(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mata_kuliah = db.Column(db.String(100), nullable=False)
    nama_kelompok = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    dibuat_oleh = db.Column(db.String(20), nullable=True)
    anggota = db.relationship('Anggota', backref='kelompok', cascade='all, delete-orphan', lazy=True)

    def get_progress(self):
        total = Task.query.filter_by(kelompok_id=self.id).count()
        if total == 0:
            return 0, 0, 0
        done = Task.query.filter_by(kelompok_id=self.id, completed=True).count()
        progress = round((done / total) * 100)
        return total, done, progress

class Anggota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kelompok_id = db.Column(db.Integer, db.ForeignKey('kelompok.id'), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    nim = db.Column(db.String(20), nullable=False)

class Notifikasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_nim = db.Column(db.String(20), nullable=False)
    judul = db.Column(db.String(200), nullable=False)
    pesan = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(200), nullable=True)
    dibaca = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# ================= AUTHENTICATION =================
USERS = {
    '051425708': {'nim': '051425708', 'password': 'UTbisa2026', 'nama': 'Yudha Bayu Pratama', 'email': 'yudha@gmail.com', 'telepon': '081226175631', 'prodi': 'Sistem Informasi'},
    '051140062': {'nim': '051140062', 'password': 'UTbisa2026', 'nama': 'Rahma Sari', 'email': 'rahma@gmail.com', 'telepon': '081345678901', 'prodi': 'Sistem Informasi'},
    '050639618': {'nim': '050639618', 'password': 'UTbisa2026', 'nama': 'Septi Nurmala', 'email': 'septi@gmail.com', 'telepon': '082198765432', 'prodi': 'Sistem Informasi'},
    '052190693': {'nim': '052190693', 'password': 'UTbisa2026', 'nama': 'Ridho Pambudihartho', 'email': 'ridho@gmail.com', 'telepon': '085712345678', 'prodi': 'Sistem Informasi'},
    '050656384': {'nim': '050656384', 'password': 'UTbisa2026', 'nama': 'Izza Nailal Farokhi', 'email': 'izza@gmail.com', 'telepon': '081298765432', 'prodi': 'Sistem Informasi'},
    '000000001': {'nim': '000000001', 'password': 'UTbisa2026', 'nama': 'Dosen Pembimbing', 'email': 'dosen@gmail.com', 'telepon': '081122334455', 'prodi': 'Dosen - Sistem Informasi'},
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_nim' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_nim' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        nim = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if nim in USERS and USERS[nim]['password'] == password:
            session['user_nim'] = nim
            session['user_nama'] = USERS[nim]['nama']
            return redirect(url_for('dashboard'))
        else:
            error = 'NIM atau Password salah. Silakan coba lagi.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/users')
@login_required
def api_users():
    q = request.args.get('q', '').strip().lower()
    current_nim = session.get('user_nim')
    results = []
    for nim, u in USERS.items():
        if nim == current_nim: continue
        if not q or q in u['nama'].lower() or q in nim.lower():
            results.append({'nim': nim, 'nama': u['nama'], 'prodi': u['prodi']})
    return jsonify(results[:10])

# ================= DASHBOARD =================
@app.route('/')
@login_required
def dashboard():
    tasks = Task.query.all()
    total = len(tasks)
    done = sum(1 for t in tasks if t.completed)
    active = total - done
    now = datetime.now()
    urgent = 0
    for t in tasks:
        if not t.completed and t.deadline:
            diff = t.deadline - now
            if 0 < diff.days <= 3:
                urgent += 1
    recent_tasks = Task.query.filter_by(completed=False).order_by(Task.deadline.asc()).limit(5).all()
    return render_template('dashboard.html', total=total, done=done, active=active, urgent=urgent, recent_tasks=recent_tasks)

# ================= TUGAS =================
@app.route('/tugas')
@login_required
def tugas():
    user_nim = session.get('user_nim')
    my_groups = [k.id for k in Kelompok.query.filter_by(dibuat_oleh=user_nim).all()]
    tasks = Task.query.filter(
        or_(
            Task.kelompok_id == None,
            Task.assigned_to == user_nim,
            Task.kelompok_id.in_(my_groups) if my_groups else False
        )
    ).order_by(Task.created_at.desc()).all()
    return render_template('tugas.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        deadline_str = request.form.get('deadline')
        priority = request.form.get('priority', 'Sedang')
        category = request.form.get('category', '')
        kelompok_id = request.form.get('kelompok_id') or None
        assigned_to = request.form.get('assigned_to') or None
        
        deadline = None
        if deadline_str:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        
        file = request.files.get('lampiran')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filename = str(int(datetime.now().timestamp())) + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_task = Task(
            title=title, description=description, deadline=deadline,
            priority=priority, category=category,
            kelompok_id=int(kelompok_id) if kelompok_id else None,
            assigned_to=assigned_to, lampiran=filename
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tugas'))
    daftar_kelompok = Kelompok.query.order_by(Kelompok.nama_kelompok.asc()).all()
    return render_template('add.html', kelompok=daftar_kelompok)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        task.priority = request.form.get('priority', 'Sedang')
        task.category = request.form.get('category', '')
        kelompok_id = request.form.get('kelompok_id') or None
        task.kelompok_id = int(kelompok_id) if kelompok_id else None
        task.assigned_to = request.form.get('assigned_to') or None
        
        deadline_str = request.form.get('deadline')
        if deadline_str:
            task.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        else:
            task.deadline = None
            
        file = request.files.get('lampiran')
        if file and file.filename != '':
            if task.lampiran:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], task.lampiran)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            filename = str(int(datetime.now().timestamp())) + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            task.lampiran = filename
            
        db.session.commit()
        return redirect(url_for('tugas'))
    daftar_kelompok = Kelompok.query.order_by(Kelompok.nama_kelompok.asc()).all()
    return render_template('edit.html', task=task, kelompok=daftar_kelompok)

@app.route('/upload_lampiran/<int:task_id>', methods=['POST'])
@login_required
def upload_lampiran(task_id):
    task = Task.query.get_or_404(task_id)
    file = request.files.get('file_lampiran')
    if file and file.filename != '':
        if task.lampiran:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], task.lampiran)
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = secure_filename(file.filename)
        filename = str(int(datetime.now().timestamp())) + "_" + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        task.lampiran = filename
        db.session.commit()
    return redirect(request.referrer or url_for('tugas'))

@app.route('/toggle/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(request.referrer or url_for('tugas'))

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.lampiran:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], task.lampiran)
        if os.path.exists(old_path):
            os.remove(old_path)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tugas'))

# ================= KALENDER =================
@app.route('/kalender')
@login_required
def kalender():
    now = datetime.now()
    upcoming = Task.query.filter(Task.completed == False, Task.deadline.isnot(None), Task.deadline >= now).order_by(Task.deadline.asc()).limit(5).all()
    return render_template('kalender.html', upcoming=upcoming)

@app.route('/api/tasks')
def api_tasks():
    tasks = Task.query.all()
    events = []
    for t in tasks:
        if t.deadline:
            events.append({
                'id': t.id, 'title': t.title, 'start': t.deadline.strftime('%Y-%m-%dT%H:%M:%S'),
                'color': '#dc3545' if t.priority == 'Tinggi' else ('#0dcaf0' if t.priority == 'Rendah' else '#ffc107'),
                'url': url_for('edit_task', task_id=t.id)
            })
    return jsonify(events)

# ================= PROFILE =================
@app.route('/profil')
@login_required
def profil():
    nim = session.get('user_nim')
    user_data = USERS.get(nim, {})
    return render_template('profil.html', user=user_data)

# ================= KELOMPOK =================
@app.route('/kelompok')
@login_required
def kelompok():
    user_nim = session.get('user_nim')
    anggota_records = Anggota.query.filter_by(nim=user_nim).all()
    kelompok_ids = [a.kelompok_id for a in anggota_records]
    if kelompok_ids:
        daftar_kelompok = Kelompok.query.filter(or_(Kelompok.id.in_(kelompok_ids), Kelompok.dibuat_oleh == user_nim)).order_by(Kelompok.created_at.desc()).all()
    else:
        daftar_kelompok = Kelompok.query.filter_by(dibuat_oleh=user_nim).order_by(Kelompok.created_at.desc()).all()
    return render_template('kelompok.html', kelompok=daftar_kelompok)

@app.route('/kelompok/<int:kelompok_id>')
@login_required
def kelompok_detail(kelompok_id):
    k = Kelompok.query.get_or_404(kelompok_id)
    user_nim = session.get('user_nim')
    is_anggota = Anggota.query.filter_by(kelompok_id=kelompok_id, nim=user_nim).first() is not None
    is_pembuat = (k.dibuat_oleh == user_nim)
    if not (is_anggota or is_pembuat):
        return redirect(url_for('kelompok'))
    
    tasks = Task.query.filter_by(kelompok_id=kelompok_id).order_by(Task.completed.asc(), Task.deadline.asc()).all()
    anggota_tugas = {}
    for a in k.anggota:
        anggota_tugas[a.nim] = {'nama': a.nama, 'nim': a.nim, 'tugas': [t for t in tasks if t.assigned_to == a.nim]}
    
    tugas_tanpa_anggota = [t for t in tasks if not t.assigned_to]
    
    # --- LOGIKA PRIVASI BARU (Nama tampil, Tugas orang lain disembunyikan) ---
    if not is_pembuat:
        for nim_key, data in anggota_tugas.items():
            if nim_key != user_nim:
                data['tugas'] = []
        tugas_tanpa_anggota = []
        
    total, done, progress = k.get_progress()
    return render_template('kelompok_detail.html', kelompok=k, anggota_tugas=anggota_tugas, tugas_tanpa_anggota=tugas_tanpa_anggota, total=total, done=done, progress=progress)

@app.route('/kelompok/edit/<int:kelompok_id>', methods=['GET', 'POST'])
@login_required
def edit_kelompok(kelompok_id):
    k = Kelompok.query.get_or_404(kelompok_id)
    user_nim = session.get('user_nim')
    user_nama = session.get('user_nama')
    if k.dibuat_oleh != user_nim: return redirect(url_for('kelompok'))
    if request.method == 'POST':
        k.nama_kelompok = request.form.get('nama_kelompok', k.nama_kelompok)
        k.mata_kuliah = request.form.get('mata_kuliah', k.mata_kuliah)
        nim_lama = [a.nim for a in k.anggota]
        Anggota.query.filter_by(kelompok_id=k.id).delete()
        creator = Anggota(kelompok_id=k.id, nama=user_nama, nim=user_nim)
        db.session.add(creator)
        nims = request.form.getlist('anggota_nim[]')
        admin_nama = user_nama or 'Seseorang'
        for nim in nims:
            nim = nim.strip()
            if not nim or nim not in USERS or nim == user_nim: continue
            u = USERS[nim]
            anggota = Anggota(kelompok_id=k.id, nama=u['nama'], nim=u['nim'])
            db.session.add(anggota)
            if nim not in nim_lama:
                db.session.add(Notifikasi(user_nim=nim, judul='Ditambahkan ke ' + k.nama_kelompok, pesan=admin_nama + ' menambahkan Anda.', link=url_for('kelompok_detail', kelompok_id=k.id)))
        db.session.commit()
        return redirect(url_for('kelompok_detail', kelompok_id=k.id))
    return render_template('kelompok_edit.html', kelompok=k)

@app.route('/kelompok/add', methods=['POST'])
@login_required
def add_kelompok():
    mata_kuliah = request.form.get('mata_kuliah')
    nama_kelompok = request.form.get('nama_kelompok')
    if not mata_kuliah or not nama_kelompok: return redirect(url_for('kelompok'))
    
    user_nim = session.get('user_nim')
    user_nama = session.get('user_nama')
    new_kelompok = Kelompok(mata_kuliah=mata_kuliah, nama_kelompok=nama_kelompok, dibuat_oleh=user_nim)
    db.session.add(new_kelompok)
    db.session.flush()
    
    db.session.add(Anggota(kelompok_id=new_kelompok.id, nama=user_nama, nim=user_nim))
    
    nims = request.form.getlist('anggota_nim[]')
    tugas_awal = request.form.getlist('tugas_awal[]')
    admin_nama = user_nama or 'Seseorang'
    
    for i, nim in enumerate(nims):
        nim = nim.strip()
        if not nim or nim not in USERS or nim == user_nim: continue
        u = USERS[nim]
        db.session.add(Anggota(kelompok_id=new_kelompok.id, nama=u['nama'], nim=u['nim']))
        
        task_title = tugas_awal[i] if i < len(tugas_awal) else ''
        if task_title.strip():
            db.session.add(Task(title=task_title.strip(), kelompok_id=new_kelompok.id, assigned_to=nim, priority='Sedang', deadline=datetime.now() + timedelta(days=7)))
            
        db.session.add(Notifikasi(user_nim=nim, judul='Ditambahkan ke ' + nama_kelompok, pesan=admin_nama + ' menambahkan Anda beserta tugas.', link=url_for('kelompok_detail', kelompok_id=new_kelompok.id)))
    
    db.session.commit()
    return redirect(url_for('kelompok'))

@app.route('/kelompok/delete/<int:kelompok_id>')
@login_required
def delete_kelompok(kelompok_id):
    k = Kelompok.query.get_or_404(kelompok_id)
    if k.dibuat_oleh != session.get('user_nim'): return redirect(url_for('kelompok'))
    db.session.delete(k)
    db.session.commit()
    return redirect(url_for('kelompok'))

@app.route('/notif/read/<int:notif_id>')
@login_required
def read_notif(notif_id):
    n = Notifikasi.query.get_or_404(notif_id)
    if n.user_nim == session.get('user_nim'):
        n.dibaca = True
        db.session.commit()
        if n.link: return redirect(n.link)
    return redirect(url_for('dashboard'))

@app.context_processor
def inject_notifications():
    if 'user_nim' not in session: return dict(notifications=[], notif_count=0)
    now = datetime.now()
    notifications = []
    db_notifs = Notifikasi.query.filter_by(user_nim=session.get('user_nim'), dibaca=False).order_by(Notifikasi.created_at.desc()).limit(5).all()
    for n in db_notifs:
        notifications.append({'type': 'primary', 'icon': 'bi-people-fill', 'title': n.judul, 'message': n.pesan, 'time': n.created_at.strftime('%d %b %Y, %H:%M'), 'link': url_for('read_notif', notif_id=n.id)})
    for t in Task.query.filter_by(completed=False).all():
        if not t.deadline: continue
        diff = t.deadline - now
        if diff.total_seconds() < 0:
            notifications.append({'type': 'danger', 'icon': 'bi-exclamation-octagon-fill', 'title': t.title, 'message': 'Sudah melewati deadline!', 'time': t.deadline.strftime('%d %b %Y, %H:%M'), 'link': url_for('edit_task', task_id=t.id)})
        elif diff.total_seconds() < 86400:
            notifications.append({'type': 'danger', 'icon': 'bi-alarm-fill', 'title': t.title, 'message': 'Kurang dari 24 jam!', 'time': t.deadline.strftime('%d %b %Y, %H:%M'), 'link': url_for('edit_task', task_id=t.id)})
    return dict(notifications=notifications[:8], notif_count=len(notifications))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()