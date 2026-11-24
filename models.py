from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin') # 'admin', 'dokter', 'petugas'
    created_at = db.Column(db.DateTime, default=datetime.now)

    rekam_medis_diperiksa = db.relationship('RekamMedis', backref='dokter', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_dokter(self):
        return self.role == 'dokter'


class Pasien(db.Model):
    __tablename__ = 'pasien'

    id = db.Column(db.Integer, primary_key=True)
    no_rkm_medis = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nik = db.Column(db.String(16), unique=True, nullable=False, index=True)
    nama_lengkap = db.Column(db.String(120), nullable=False)
    tempat_lahir = db.Column(db.String(60), nullable=True)
    tanggal_lahir = db.Column(db.Date, nullable=False)
    jenis_kelamin = db.Column(db.String(1), nullable=False) # 'L' (Laki-laki), 'P' (Perempuan)
    golongan_darah = db.Column(db.String(5), nullable=True, default='-')
    alamat = db.Column(db.Text, nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    jenis_pembayaran = db.Column(db.String(20), nullable=False, default='Umum') # 'Umum', 'BPJS'
    no_bpjs = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    kunjungan = db.relationship('Kunjungan', backref='pasien', lazy=True, cascade="all, delete-orphan")
    rekam_medis = db.relationship('RekamMedis', backref='pasien', lazy=True, cascade="all, delete-orphan")

    @property
    def umur(self):
        if not self.tanggal_lahir:
            return 0
        today = date.today()
        born = self.tanggal_lahir
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class Kunjungan(db.Model):
    __tablename__ = 'kunjungan'

    id = db.Column(db.Integer, primary_key=True)
    no_antrean = db.Column(db.String(20), nullable=False) # e.g. U-001, G-002, K-001
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    tanggal_kunjungan = db.Column(db.Date, nullable=False, default=date.today)
    poli_tujuan = db.Column(db.String(50), nullable=False) # 'Poli Umum', 'Poli Gigi', 'Poli KIA/KB', 'Poli Lansia', 'Poli Anak'
    keluhan_awal = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Menunggu') # 'Menunggu', 'Diperiksa', 'Selesai', 'Batal'
    created_at = db.Column(db.DateTime, default=datetime.now)

    rekam_medis = db.relationship('RekamMedis', backref='kunjungan', uselist=False, lazy=True)


class RekamMedis(db.Model):
    __tablename__ = 'rekam_medis'

    id = db.Column(db.Integer, primary_key=True)
    no_rawat = db.Column(db.String(30), unique=True, nullable=False, index=True)
    kunjungan_id = db.Column(db.Integer, db.ForeignKey('kunjungan.id'), nullable=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tanggal_pemeriksaan = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Anamnesis
    keluhan_utama = db.Column(db.Text, nullable=False)
    riwayat_penyakit = db.Column(db.Text, nullable=True)
    riwayat_alergi = db.Column(db.String(150), nullable=True)

    # Tanda Vital (Vital Signs)
    tekanan_darah = db.Column(db.String(20), nullable=True) # e.g. 120/80 mmHg
    suhu_tubuh = db.Column(db.Float, nullable=True)         # Celcius e.g. 36.8
    berat_badan = db.Column(db.Float, nullable=True)        # kg e.g. 62.5
    tinggi_badan = db.Column(db.Float, nullable=True)       # cm e.g. 168
    nadi = db.Column(db.Integer, nullable=True)             # bpm e.g. 80
    respirasi = db.Column(db.Integer, nullable=True)        # x/menit e.g. 18

    # Diagnosis & Penatalaksanaan
    diagnosis = db.Column(db.Text, nullable=False)
    kode_icd10 = db.Column(db.String(30), nullable=True)
    tindakan_medis = db.Column(db.Text, nullable=True)
    resep_obat = db.Column(db.Text, nullable=True)
    catatan_dokter = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
