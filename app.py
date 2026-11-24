import os
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from models import db, User, Pasien, Kunjungan, RekamMedis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'puskesmas-secret-key-2026-fanta-pink-sik'

if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/puskesmas.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///puskesmas.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ==========================================
# AUTHENTICATION HELPERS & DECORATORS
# ==========================================

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@app.context_processor
def inject_user():
    return {
        'current_user': get_current_user(),
        'today_date': date.today(),
        'app_title': 'SIK PUSKESMAS'
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan masuk terlebih dahulu untuk mengakses sistem.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('login'))
            user = get_current_user()
            if not user or user.role not in roles:
                flash('Anda tidak memiliki hak akses ke halaman tersebut.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==========================================
# AUTO GENERATOR HELPERS
# ==========================================

def generate_no_rkm_medis():
    """Menghasilkan nomor rekam medis berurutan seperti RM-0001, RM-0002"""
    last_pasien = Pasien.query.order_by(Pasien.id.desc()).first()
    if not last_pasien:
        return "RM-0001"
    next_id = last_pasien.id + 1
    return f"RM-{next_id:04d}"

def generate_no_antrean(poli_name, tanggal=None):
    """Menghasilkan nomor antrean berdasarkan poli hari ini (misal: U-001, G-001)"""
    if tanggal is None:
        tanggal = date.today()
    
    code_map = {
        'Poli Umum': 'U',
        'Poli Gigi': 'G',
        'Poli KIA/KB': 'K',
        'Poli Lansia': 'L',
        'Poli Anak': 'A'
    }
    code = code_map.get(poli_name, 'U')
    
    count_today = Kunjungan.query.filter_by(
        tanggal_kunjungan=tanggal,
        poli_tujuan=poli_name
    ).count()
    
    return f"{code}-{(count_today + 1):03d}"

def generate_no_rawat():
    """Menghasilkan nomor rawat unik format RWT/YYYYMMDD/XXXX"""
    today_str = date.today().strftime('%Y%m%d')
    today_start = datetime.combine(date.today(), datetime.min.time())
    count_today = RekamMedis.query.filter(RekamMedis.tanggal_pemeriksaan >= today_start).count()
    return f"RWT/{today_str}/{(count_today + 1):04d}"


# ==========================================
# DATABASE SEEDING
# ==========================================

def seed_database():
    """Inisialisasi akun default dan data awal agar langsung siap dites"""
    if User.query.first() is None:
        # 1. Buat Akun Default
        admin = User(
            username='admin',
            nama_lengkap='Admin Petugas Pendaftaran',
            role='admin'
        )
        admin.set_password('admin123')

        dokter = User(
            username='dokter',
            nama_lengkap='dr. Siti Rahmawati, Sp.PK',
            role='dokter'
        )
        dokter.set_password('dokter123')

        db.session.add(admin)
        db.session.add(dokter)
        db.session.commit()

        # 2. Buat Pasien Contoh
        pasien_samples = [
            Pasien(
                no_rkm_medis='RM-0001',
                nik='3201012304900001',
                nama_lengkap='Budi Santoso',
                tempat_lahir='Jakarta',
                tanggal_lahir=date(1990, 4, 23),
                jenis_kelamin='L',
                golongan_darah='O',
                alamat='Jl. Melati No. 12, RT 02/RW 04, Kelurahan Sejahtera',
                no_hp='081234567890',
                jenis_pembayaran='BPJS',
                no_bpjs='0001234567891'
            ),
            Pasien(
                no_rkm_medis='RM-0002',
                nik='3201015607950002',
                nama_lengkap='Dewi Lestari',
                tempat_lahir='Bandung',
                tanggal_lahir=date(1995, 7, 16),
                jenis_kelamin='P',
                golongan_darah='A',
                alamat='Jl. Mawar Indah Blok B3 No. 8',
                no_hp='085712349876',
                jenis_pembayaran='Umum',
                no_bpjs=None
            ),
            Pasien(
                no_rkm_medis='RM-0003',
                nik='3201011112800003',
                nama_lengkap='H. Ahmad Dahlan',
                tempat_lahir='Yogyakarta',
                tanggal_lahir=date(1980, 12, 11),
                jenis_kelamin='L',
                golongan_darah='B',
                alamat='Jl. Kenanga Timur No. 45',
                no_hp='082198765432',
                jenis_pembayaran='BPJS',
                no_bpjs='0009876543210'
            ),
            Pasien(
                no_rkm_medis='RM-0004',
                nik='3201014502050004',
                nama_lengkap='Rina Anggraini',
                tempat_lahir='Surabaya',
                tanggal_lahir=date(2005, 2, 5),
                jenis_kelamin='P',
                golongan_darah='AB',
                alamat='Komplek Asri Mandiri No. 19',
                no_hp='087812009944',
                jenis_pembayaran='Umum',
                no_bpjs=None
            )
        ]
        db.session.add_all(pasien_samples)
        db.session.commit()

        # 3. Buat Kunjungan Hari Ini & Beberapa Hari Lalu
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        kunjungan_samples = [
            Kunjungan(
                no_antrean='U-001',
                pasien_id=1,
                tanggal_kunjungan=two_days_ago,
                poli_tujuan='Poli Umum',
                keluhan_awal='Demam naik turun selama 3 hari dan pusing hebat.',
                status='Selesai'
            ),
            Kunjungan(
                no_antrean='G-001',
                pasien_id=2,
                tanggal_kunjungan=yesterday,
                poli_tujuan='Poli Gigi',
                keluhan_awal='Sakit gigi geraham kanan bawah saat mengunyah.',
                status='Selesai'
            ),
            Kunjungan(
                no_antrean='U-001',
                pasien_id=3,
                tanggal_kunjungan=today,
                poli_tujuan='Poli Umum',
                keluhan_awal='Batuk berdahak 4 hari, badan lemas, sesak ringan.',
                status='Menunggu'
            ),
            Kunjungan(
                no_antrean='K-001',
                pasien_id=4,
                tanggal_kunjungan=today,
                poli_tujuan='Poli KIA/KB',
                keluhan_awal='Konsultasi pemeriksaan rutin kesehatan reproduksi.',
                status='Diperiksa'
            ),
            Kunjungan(
                no_antrean='U-002',
                pasien_id=1,
                tanggal_kunjungan=today,
                poli_tujuan='Poli Umum',
                keluhan_awal='Kontrol lanjutan demam dan cek hasil lab darah.',
                status='Menunggu'
            )
        ]
        db.session.add_all(kunjungan_samples)
        db.session.commit()

        # 4. Buat Rekam Medis Selesai
        rm1 = RekamMedis(
            no_rawat=f"RWT/{two_days_ago.strftime('%Y%m%d')}/0001",
            kunjungan_id=1,
            pasien_id=1,
            dokter_id=dokter.id,
            tanggal_pemeriksaan=datetime.combine(two_days_ago, datetime.min.time()) + timedelta(hours=9, minutes=30),
            keluhan_utama='Demam 3 hari berturut-turut, sakit kepala, nyeri sendi.',
            riwayat_penyakit='Tidak ada riwayat hipertensi atau diabetes.',
            riwayat_alergi='Tidak ada alergi obat',
            tekanan_darah='110/70 mmHg',
            suhu_tubuh=38.6,
            berat_badan=64.0,
            tinggi_badan=170.0,
            nadi=88,
            respirasi=20,
            diagnosis='Observasi Febris e.c Suspect Demam Dengue / ISPA',
            kode_icd10='A90',
            tindakan_medis='Pemberian kompres hangat, cek laboratorium darah lengkap (DL).',
            resep_obat='- Paracetamol 500mg 3x1 tablet (prn demam)\n- Vitamin C 500mg 1x1\n- Oralit 2 sachet jika mual/diare',
            catatan_dokter='Disarankan banyak minum air putih minimal 2.5 liter per hari. Kontrol kembali jika suhu tidak turun dalam 2 hari.'
        )

        rm2 = RekamMedis(
            no_rawat=f"RWT/{yesterday.strftime('%Y%m%d')}/0001",
            kunjungan_id=2,
            pasien_id=2,
            dokter_id=dokter.id,
            tanggal_pemeriksaan=datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=10, minutes=15),
            keluhan_utama='Gigi geraham belakang kanan nyeri berdenyut terutama malam hari.',
            riwayat_penyakit='Gastritis ringan',
            riwayat_alergi='Alergi Asam Mefenamat',
            tekanan_darah='120/80 mmHg',
            suhu_tubuh=36.7,
            berat_badan=52.0,
            tinggi_badan=158.0,
            nadi=78,
            respirasi=18,
            diagnosis='Pulpitis Irreversibel Gigi 46',
            kode_icd10='K04.0',
            tindakan_medis='Pembersihan kavitas dan tumpatan sementara (medikasi saluran akar tahap 1).',
            resep_obat='- Amoxicillin 500mg 3x1 (dihabiskan 5 hari)\n- Ibuprofen 400mg 3x1 sesudah makan',
            catatan_dokter='Jadwalkan kembali dalam 7 hari untuk evaluasi dan perawatan saluran akar lanjutan.'
        )

        db.session.add(rm1)
        db.session.add(rm2)
        db.session.commit()


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['nama_lengkap'] = user.nama_lengkap
            flash(f'Selamat datang, {user.nama_lengkap}! Berhasil masuk ke sistem.', 'success')
            
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau kata sandi tidak valid. Silakan coba lagi.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('login'))


# ==========================================
# DASHBOARD
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    
    # Ringkasan Statistik
    total_pasien = Pasien.query.count()
    kunjungan_hari_ini = Kunjungan.query.filter_by(tanggal_kunjungan=today).count()
    total_rekam_medis = RekamMedis.query.count()
    antrean_menunggu = Kunjungan.query.filter_by(tanggal_kunjungan=today, status='Menunggu').count()
    antrean_diperiksa = Kunjungan.query.filter_by(tanggal_kunjungan=today, status='Diperiksa').count()
    antrean_selesai = Kunjungan.query.filter_by(tanggal_kunjungan=today, status='Selesai').count()

    # Kunjungan Hari Ini (Terbaru)
    antrean_hari_ini = Kunjungan.query.filter_by(tanggal_kunjungan=today).order_by(Kunjungan.created_at.desc()).all()

    # Data Grafik 7 Hari Terakhir
    labels_7_hari = []
    data_kunjungan_7_hari = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = Kunjungan.query.filter_by(tanggal_kunjungan=d).count()
        labels_7_hari.append(d.strftime('%d %b'))
        data_kunjungan_7_hari.append(count)

    # Data Distribusi Poli Hari Ini
    poli_list = ['Poli Umum', 'Poli Gigi', 'Poli KIA/KB', 'Poli Lansia', 'Poli Anak']
    data_poli = []
    for p in poli_list:
        c = Kunjungan.query.filter_by(tanggal_kunjungan=today, poli_tujuan=p).count()
        data_poli.append(c)

    return render_template(
        'dashboard.html',
        total_pasien=total_pasien,
        kunjungan_hari_ini=kunjungan_hari_ini,
        total_rekam_medis=total_rekam_medis,
        antrean_menunggu=antrean_menunggu,
        antrean_diperiksa=antrean_diperiksa,
        antrean_selesai=antrean_selesai,
        antrean_hari_ini=antrean_hari_ini,
        labels_7_hari=labels_7_hari,
        data_kunjungan_7_hari=data_kunjungan_7_hari,
        labels_poli=poli_list,
        data_poli=data_poli
    )


# ==========================================
# MANAJEMEN PENDAFTARAN PASIEN (CRUD)
# ==========================================

@app.route('/pasien')
@login_required
def pasien_list():
    query = request.args.get('q', '').strip()
    jenis_pembayaran = request.args.get('jenis_pembayaran', '').strip()
    
    pasien_query = Pasien.query
    
    if query:
        search_filter = f"%{query}%"
        pasien_query = pasien_query.filter(
            (Pasien.nama_lengkap.ilike(search_filter)) |
            (Pasien.no_rkm_medis.ilike(search_filter)) |
            (Pasien.nik.ilike(search_filter)) |
            (Pasien.no_hp.ilike(search_filter))
        )
    
    if jenis_pembayaran:
        pasien_query = pasien_query.filter_by(jenis_pembayaran=jenis_pembayaran)
        
    daftar_pasien = pasien_query.order_by(Pasien.id.desc()).all()
    return render_template('pasien/index.html', daftar_pasien=daftar_pasien, query=query, jenis_pembayaran=jenis_pembayaran)

@app.route('/pasien/tambah', methods=['GET', 'POST'])
@login_required
def pasien_tambah():
    if request.method == 'POST':
        nik = request.form.get('nik', '').strip()
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        tempat_lahir = request.form.get('tempat_lahir', '').strip()
        tanggal_lahir_str = request.form.get('tanggal_lahir', '').strip()
        jenis_kelamin = request.form.get('jenis_kelamin', 'L')
        golongan_darah = request.form.get('golongan_darah', '-')
        alamat = request.form.get('alamat', '').strip()
        no_hp = request.form.get('no_hp', '').strip()
        jenis_pembayaran = request.form.get('jenis_pembayaran', 'Umum')
        no_bpjs = request.form.get('no_bpjs', '').strip() or None

        # Validasi NIK Unik
        existing_nik = Pasien.query.filter_by(nik=nik).first()
        if existing_nik:
            flash(f'NIK {nik} sudah terdaftar dengan nama {existing_nik.nama_lengkap}. Silakan cek data pasien.', 'danger')
            return render_template('pasien/tambah.html', form_data=request.form)

        try:
            tanggal_lahir = datetime.strptime(tanggal_lahir_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal lahir tidak valid.', 'danger')
            return render_template('pasien/tambah.html', form_data=request.form)

        no_rm = generate_no_rkm_medis()

        pasien = Pasien(
            no_rkm_medis=no_rm,
            nik=nik,
            nama_lengkap=nama_lengkap,
            tempat_lahir=tempat_lahir,
            tanggal_lahir=tanggal_lahir,
            jenis_kelamin=jenis_kelamin,
            golongan_darah=golongan_darah,
            alamat=alamat,
            no_hp=no_hp,
            jenis_pembayaran=jenis_pembayaran,
            no_bpjs=no_bpjs
        )
        db.session.add(pasien)
        db.session.commit()

        flash(f'Pasien baru berhasil didaftarkan dengan No. RM: {no_rm}', 'success')
        
        # Opsi langsung daftarkan kunjungan jika dicentang
        if request.form.get('langsung_kunjungan') == '1':
            return redirect(url_for('kunjungan_tambah', pasien_id=pasien.id))
        
        return redirect(url_for('pasien_detail', id=pasien.id))

    auto_rm = generate_no_rkm_medis()
    return render_template('pasien/tambah.html', auto_rm=auto_rm, form_data={})

@app.route('/pasien/<int:id>')
@login_required
def pasien_detail(id):
    pasien = Pasien.query.get_or_404(id)
    riwayat_kunjungan = Kunjungan.query.filter_by(pasien_id=id).order_by(Kunjungan.tanggal_kunjungan.desc()).all()
    riwayat_rm = RekamMedis.query.filter_by(pasien_id=id).order_by(RekamMedis.tanggal_pemeriksaan.desc()).all()
    return render_template('pasien/detail.html', pasien=pasien, riwayat_kunjungan=riwayat_kunjungan, riwayat_rm=riwayat_rm)

@app.route('/pasien/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def pasien_edit(id):
    pasien = Pasien.query.get_or_404(id)
    if request.method == 'POST':
        nik = request.form.get('nik', '').strip()
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        tempat_lahir = request.form.get('tempat_lahir', '').strip()
        tanggal_lahir_str = request.form.get('tanggal_lahir', '').strip()
        jenis_kelamin = request.form.get('jenis_kelamin', 'L')
        golongan_darah = request.form.get('golongan_darah', '-')
        alamat = request.form.get('alamat', '').strip()
        no_hp = request.form.get('no_hp', '').strip()
        jenis_pembayaran = request.form.get('jenis_pembayaran', 'Umum')
        no_bpjs = request.form.get('no_bpjs', '').strip() or None

        # Cek jika NIK diganti dan bentrok dengan pasien lain
        if nik != pasien.nik:
            existing_nik = Pasien.query.filter_by(nik=nik).first()
            if existing_nik:
                flash(f'NIK {nik} sudah digunakan oleh pasien lain ({existing_nik.nama_lengkap}).', 'danger')
                return render_template('pasien/edit.html', pasien=pasien)

        try:
            pasien.tanggal_lahir = datetime.strptime(tanggal_lahir_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal lahir tidak valid.', 'danger')
            return render_template('pasien/edit.html', pasien=pasien)

        pasien.nik = nik
        pasien.nama_lengkap = nama_lengkap
        pasien.tempat_lahir = tempat_lahir
        pasien.jenis_kelamin = jenis_kelamin
        pasien.golongan_darah = golongan_darah
        pasien.alamat = alamat
        pasien.no_hp = no_hp
        pasien.jenis_pembayaran = jenis_pembayaran
        pasien.no_bpjs = no_bpjs

        db.session.commit()
        flash('Data pasien berhasil diperbarui.', 'success')
        return redirect(url_for('pasien_detail', id=pasien.id))

    return render_template('pasien/edit.html', pasien=pasien)

@app.route('/pasien/hapus/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def pasien_hapus(id):
    pasien = Pasien.query.get_or_404(id)
    nama = pasien.nama_lengkap
    no_rm = pasien.no_rkm_medis
    db.session.delete(pasien)
    db.session.commit()
    flash(f'Pasien {nama} ({no_rm}) dan seluruh riwayat terkait berhasil dihapus.', 'info')
    return redirect(url_for('pasien_list'))


# ==========================================
# MANAJEMEN KUNJUNGAN & ANTREAN POLI
# ==========================================

@app.route('/kunjungan')
@login_required
def kunjungan_list():
    tanggal_str = request.args.get('tanggal', date.today().strftime('%Y-%m-%d'))
    poli_filter = request.args.get('poli', '').strip()
    status_filter = request.args.get('status', '').strip()

    try:
        tgl_filter = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
    except ValueError:
        tgl_filter = date.today()

    query = Kunjungan.query.filter_by(tanggal_kunjungan=tgl_filter)

    if poli_filter:
        query = query.filter_by(poli_tujuan=poli_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    daftar_kunjungan = query.order_by(Kunjungan.created_at.asc()).all()

    poli_list = ['Poli Umum', 'Poli Gigi', 'Poli KIA/KB', 'Poli Lansia', 'Poli Anak']
    return render_template(
        'kunjungan/index.html',
        daftar_kunjungan=daftar_kunjungan,
        tanggal_filter=tgl_filter.strftime('%Y-%m-%d'),
        poli_filter=poli_filter,
        status_filter=status_filter,
        poli_list=poli_list
    )

@app.route('/kunjungan/tambah', methods=['GET', 'POST'])
@login_required
def kunjungan_tambah():
    pasien_id = request.args.get('pasien_id', type=int)
    pasien_terpilih = Pasien.query.get(pasien_id) if pasien_id else None

    if request.method == 'POST':
        pid = request.form.get('pasien_id', type=int)
        poli_tujuan = request.form.get('poli_tujuan', 'Poli Umum')
        keluhan_awal = request.form.get('keluhan_awal', '').strip()
        tanggal_str = request.form.get('tanggal_kunjungan', date.today().strftime('%Y-%m-%d'))

        try:
            tgl_kunjungan = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        except ValueError:
            tgl_kunjungan = date.today()

        target_pasien = Pasien.query.get(pid)
        if not target_pasien:
            flash('Pasien tidak ditemukan. Silakan pilih pasien terdaftar.', 'danger')
            return redirect(url_for('kunjungan_tambah'))

        no_antrean = generate_no_antrean(poli_tujuan, tgl_kunjungan)

        kunjungan = Kunjungan(
            no_antrean=no_antrean,
            pasien_id=target_pasien.id,
            tanggal_kunjungan=tgl_kunjungan,
            poli_tujuan=poli_tujuan,
            keluhan_awal=keluhan_awal,
            status='Menunggu'
        )
        db.session.add(kunjungan)
        db.session.commit()

        flash(f'Pendaftaran antrean berhasil! Nomor Antrean: {no_antrean} ({poli_tujuan})', 'success')
        return redirect(url_for('kunjungan_cetak', id=kunjungan.id))

    daftar_semua_pasien = Pasien.query.order_by(Pasien.nama_lengkap.asc()).all()
    poli_list = ['Poli Umum', 'Poli Gigi', 'Poli KIA/KB', 'Poli Lansia', 'Poli Anak']
    return render_template(
        'kunjungan/tambah.html',
        pasien_terpilih=pasien_terpilih,
        daftar_pasien=daftar_semua_pasien,
        poli_list=poli_list,
        today=date.today().strftime('%Y-%m-%d')
    )

@app.route('/kunjungan/status/<int:id>', methods=['POST'])
@login_required
def kunjungan_ubah_status(id):
    kunjungan = Kunjungan.query.get_or_404(id)
    status_baru = request.form.get('status')
    if status_baru in ['Menunggu', 'Diperiksa', 'Selesai', 'Batal']:
        kunjungan.status = status_baru
        db.session.commit()
        flash(f'Status antrean {kunjungan.no_antrean} berhasil diubah menjadi: {status_baru}', 'info')
    return redirect(request.referrer or url_for('kunjungan_list'))

@app.route('/kunjungan/cetak/<int:id>')
@login_required
def kunjungan_cetak(id):
    kunjungan = Kunjungan.query.get_or_404(id)
    return render_template('kunjungan/cetak_antrean.html', kunjungan=kunjungan)


# ==========================================
# MANAJEMEN REKAM MEDIS (EMR)
# ==========================================

@app.route('/rekam-medis')
@login_required
def rekam_medis_list():
    query = request.args.get('q', '').strip()
    rm_query = RekamMedis.query.join(Pasien)

    if query:
        search_filter = f"%{query}%"
        rm_query = rm_query.filter(
            (RekamMedis.no_rawat.ilike(search_filter)) |
            (Pasien.nama_lengkap.ilike(search_filter)) |
            (Pasien.no_rkm_medis.ilike(search_filter)) |
            (RekamMedis.diagnosis.ilike(search_filter)) |
            (RekamMedis.kode_icd10.ilike(search_filter))
        )

    daftar_rm = rm_query.order_by(RekamMedis.tanggal_pemeriksaan.desc()).all()
    return render_template('rekam_medis/index.html', daftar_rm=daftar_rm, query=query)

@app.route('/rekam-medis/periksa/<int:kunjungan_id>', methods=['GET', 'POST'])
@login_required
def rekam_medis_periksa(kunjungan_id):
    kunjungan = Kunjungan.query.get_or_404(kunjungan_id)
    pasien = kunjungan.pasien
    current_u = get_current_user()

    # Cek apakah kunjungan ini sudah memiliki rekam medis
    rm_ada = RekamMedis.query.filter_by(kunjungan_id=kunjungan_id).first()
    if rm_ada and request.method == 'GET':
        flash('Kunjungan ini sudah pernah diperiksa. Menampilkan rekam medis yang tersimpan.', 'info')
        return redirect(url_for('rekam_medis_detail', id=rm_ada.id))

    if request.method == 'POST':
        keluhan_utama = request.form.get('keluhan_utama', '').strip()
        riwayat_penyakit = request.form.get('riwayat_penyakit', '').strip()
        riwayat_alergi = request.form.get('riwayat_alergi', '').strip()
        
        tekanan_darah = request.form.get('tekanan_darah', '').strip()
        suhu_tubuh = request.form.get('suhu_tubuh', type=float)
        berat_badan = request.form.get('berat_badan', type=float)
        tinggi_badan = request.form.get('tinggi_badan', type=float)
        nadi = request.form.get('nadi', type=int)
        respirasi = request.form.get('respirasi', type=int)

        diagnosis = request.form.get('diagnosis', '').strip()
        kode_icd10 = request.form.get('kode_icd10', '').strip()
        tindakan_medis = request.form.get('tindakan_medis', '').strip()
        resep_obat = request.form.get('resep_obat', '').strip()
        catatan_dokter = request.form.get('catatan_dokter', '').strip()

        no_rawat = generate_no_rawat()

        rekam_medis = RekamMedis(
            no_rawat=no_rawat,
            kunjungan_id=kunjungan.id,
            pasien_id=pasien.id,
            dokter_id=current_u.id if current_u else None,
            tanggal_pemeriksaan=datetime.now(),
            keluhan_utama=keluhan_utama,
            riwayat_penyakit=riwayat_penyakit,
            riwayat_alergi=riwayat_alergi,
            tekanan_darah=tekanan_darah,
            suhu_tubuh=suhu_tubuh,
            berat_badan=berat_badan,
            tinggi_badan=tinggi_badan,
            nadi=nadi,
            respirasi=respirasi,
            diagnosis=diagnosis,
            kode_icd10=kode_icd10,
            tindakan_medis=tindakan_medis,
            resep_obat=resep_obat,
            catatan_dokter=catatan_dokter
        )

        # Ubah status kunjungan menjadi 'Selesai'
        kunjungan.status = 'Selesai'

        db.session.add(rekam_medis)
        db.session.commit()

        flash(f'Pemeriksaan medis berhasil disimpan dengan No. Rawat {no_rawat}!', 'success')
        return redirect(url_for('rekam_medis_detail', id=rekam_medis.id))

    # Otomatis ubah status antrean menjadi 'Diperiksa' saat form dibuka
    if kunjungan.status == 'Menunggu':
        kunjungan.status = 'Diperiksa'
        db.session.commit()

    riwayat_sebelumnya = RekamMedis.query.filter_by(pasien_id=pasien.id).order_by(RekamMedis.tanggal_pemeriksaan.desc()).limit(3).all()

    return render_template(
        'rekam_medis/periksa.html',
        kunjungan=kunjungan,
        pasien=pasien,
        riwayat_sebelumnya=riwayat_sebelumnya
    )

@app.route('/rekam-medis/<int:id>')
@login_required
def rekam_medis_detail(id):
    rm = RekamMedis.query.get_or_404(id)
    return render_template('rekam_medis/detail.html', rm=rm)

@app.route('/rekam-medis/riwayat/<int:pasien_id>')
@login_required
def rekam_medis_riwayat(pasien_id):
    pasien = Pasien.query.get_or_404(pasien_id)
    riwayat_rm = RekamMedis.query.filter_by(pasien_id=pasien_id).order_by(RekamMedis.tanggal_pemeriksaan.desc()).all()
    return render_template('rekam_medis/riwayat_pasien.html', pasien=pasien, riwayat_rm=riwayat_rm)

@app.route('/rekam-medis/cetak/<int:id>')
@login_required
def rekam_medis_cetak(id):
    rm = RekamMedis.query.get_or_404(id)
    return render_template('rekam_medis/cetak.html', rm=rm)


# ==========================================
# PENGATURAN & PROFIL PENGGUNA
# ==========================================

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    user = get_current_user()
    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if nama_lengkap:
            user.nama_lengkap = nama_lengkap
            session['nama_lengkap'] = nama_lengkap

        # Jika ingin ganti password
        if new_password:
            if not user.check_password(current_password):
                flash('Kata sandi saat ini salah.', 'danger')
                return render_template('profil.html', user=user)
            if new_password != confirm_password:
                flash('Konfirmasi kata sandi baru tidak cocok.', 'danger')
                return render_template('profil.html', user=user)
            if len(new_password) < 6:
                flash('Kata sandi baru minimal 6 karakter.', 'danger')
                return render_template('profil.html', user=user)

            user.set_password(new_password)
            flash('Kata sandi berhasil diperbarui!', 'success')

        db.session.commit()
        flash('Profil pengguna berhasil disimpan.', 'success')
        return redirect(url_for('profil'))

    return render_template('profil.html', user=user)


# ==========================================
# MAIN APP RUNNER
# ==========================================

try:
    with app.app_context():
        db.create_all()
        seed_database()
except Exception as e:
    print(f"Database init info: {e}")

# Entry point for Vercel / WSGI
application = app

if __name__ == '__main__':
    print("=" * 65)
    print(" SISTEM INFORMASI KESEHATAN PUSKESMAS (SIK PUSKESMAS)")
    print(" Berbasis Web untuk Pendaftaran Pasien dan Rekam Medis")
    print(" Tema: Pink Fanta (#E91E63) & Putih Bersih Modern")
    print(" Server berjalan di: http://127.0.0.1:5000")
    print(" Akun Default:")
    print("  - Admin/Pendaftaran : admin  / admin123")
    print("  - Dokter            : dokter / dokter123")
    print("=" * 65)
    app.run(debug=True, host='127.0.0.1', port=5000)
