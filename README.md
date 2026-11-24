# SISTEM INFORMASI KESEHATAN PUSKESMAS BERBASIS WEB UNTUK PENDAFTARAN PASIEN DAN REKAM MEDIS (SIK PUSKESMAS)

Aplikasi sistem informasi kesehatan puskesmas berbasis web yang lengkap, modern, dan siap pakai (*ready-to-run*). Dirancang khusus untuk pengelolaan pendaftaran pasien rawat jalan, manajemen antrean poli harian otomatis, dan pencatatan Rekam Medis Elektronik (*Electronic Medical Records* / EMR) berstandar klinis.

---

## 🎨 Tema & Desain UI/UX
- **Aksen Utama:** Pink Fanta (`#E91E63` / `#FF1493` gradient) untuk tombol aksi, sidebar, icon, dan elemen aktif.
- **Latar Belakang:** Putih Bersih Modern (`#FFFFFF` & `#FFF5F8` subtle) yang rapi, ergonomis, dan tidak melelahkan mata.
- **Responsif:** Mendukung tampilan layar desktop, tablet, dan smartphone (dengan *collapsible mobile sidebar*).
- **Format Siap Cetak (Print-Ready):**
  - Cetak Struk Tiket Antrean Poli (Ukuran Mini/Thermal).
  - Cetak Lembar Berkas Rekam Medis Pasien A4 lengkap dengan Kop Surat Puskesmas resmi & tanda tangan dokter.

---

## 🚀 Fitur Utama Aplikasi

### 1. Sistem Autentikasi & Keamanan (Role-Based Access)
- Login aman berbasis session (`Flask Session`) dengan proteksi kata sandi menggunakan hash standar industri (`werkzeug.security`).
- Seluruh rute pelayanan diproteksi dengan `@login_required`.
- Tombol **Logout** yang jelas di navigasi samping (*sidebar*) dan bilah atas (*topbar*).
- Manajemen akun & ganti kata sandi di halaman Profil.

### 2. Dashboard Statistik Interaktif
- Ringkasan kartu statistik: **Total Pasien Terdaftar**, **Kunjungan Hari Ini**, **Antrean Menunggu**, dan **Total Rekam Medis**.
- **Grafik Tren Kunjungan 7 Hari Terakhir** interaktif menggunakan Chart.js.
- **Grafik Distribusi Pasien Per Poli Klinik** (Poli Umum, Gigi, KIA/KB, Lansia, Anak).
- Tabel antrean hari ini dengan tombol cepat pemeriksaan.

### 3. Manajemen Pendaftaran Pasien (CRUD Penuh)
- **Nomor Rekam Medis Otomatis** (format: `RM-0001`, `RM-0002`, dst).
- Pencatatan data identitas lengkap: NIK (16 digit), Nama Pasien, Tempat & Tanggal Lahir (otomatis hitung umur), Jenis Kelamin, Golongan Darah, Alamat Domisili, No. HP/WhatsApp.
- Jenis Penjaminan: **Umum / Mandiri** atau **BPJS Kesehatan** (dengan input nomor kartu BPJS).
- Fitur pencarian instan berdasarkan Nama, NIK, No. RM, atau No. HP serta filter penjaminan.
- Opsi langsung mendaftarkan pasien ke antrean poli saat pertama kali didaftarkan.

### 4. Manajemen Kunjungan & Antrean Poli Harian
- Pendaftaran kunjungan per poli: **Poli Umum**, **Poli Gigi**, **Poli KIA/KB**, **Poli Lansia**, dan **Poli Anak**.
- **Nomor Antrean Otomatis** per poli dan tanggal (contoh: `U-001` untuk Poli Umum, `G-001` untuk Poli Gigi, `K-001` untuk Poli KIA).
- Perubahan status antrean: `Menunggu` ➔ `Diperiksa` ➔ `Selesai` ➔ `Batal`.
- Filter antrean berdasarkan tanggal, poli, dan status.
- Cetak tiket nomor antrean pasien.

### 5. Rekam Medis Elektronik (EMR / EHR)
- Terintegrasi langsung dengan antrean pasien: dokter cukup menekan tombol **"Periksa"** pada antrean pasien.
- **Anamnesis:** Keluhan Utama, Riwayat Penyakit Terdahulu/Keluarga, Riwayat Alergi Obat/Makanan.
- **Pemeriksaan Tanda Vital (Vital Signs):** Tekanan Darah (mmHg), Suhu Tubuh (°C), Berat Badan (kg), Tinggi Badan (cm), Denyut Nadi (bpm), Laju Pernafasan (x/m).
- **Diagnosis Medis & Kode ICD-10**.
- **Tindakan Medis & Terapi Prosedural**.
- **Resep Obat (Format R/) & Aturan Pakai**.
- **Catatan & Edukasi Dokter**.
- Panel samping otomatis menampilkan riwayat kunjungan dan rekam medis pasien terdahulu agar dokter memiliki riwayat klinis yang komprehensif.
- Cetak lembar rekam medis formal format A4.

---

## 🔑 Akun Default untuk Pengujian Langsung

Saat aplikasi pertama kali dijalankan, sistem otomatis membuat database SQLite dan akun default berikut:

| Peran (Role) | Username | Password | Deskripsi |
|---|---|---|---|
| **Admin / Pendaftaran** | `admin` | `admin123` | Mengelola data pasien, pendaftaran antrean kunjungan, dan master data |
| **Dokter Pemeriksa** | `dokter` | `dokter123` | Melakukan pemeriksaan klinis, input rekam medis, dan resep obat |

*(Pada halaman Login juga telah disediakan tombol klik otomatis untuk memasukkan kredensial demo).*

---

## 📂 Struktur Folder Proyek

```
puskesmas_app/
│
├── app.py                      # Aplikasi utama Flask, konfigurasi, routes, dan business logic
├── models.py                   # Model database SQLAlchemy (User, Pasien, Kunjungan, RekamMedis)
├── requirements.txt            # Daftar pustaka / dependensi Python
├── README.md                   # Dokumentasi instalasi dan panduan lengkap
├── instance/
│   └── puskesmas.db            # Database SQLite (dibuat otomatis saat pertama jalan)
│
├── static/
│   ├── css/
│   │   └── style.css           # Styling tema Pink Fanta & format cetak A4/thermal
│   └── js/
│       └── main.js             # Skrip interaksi UI, sidebar toggle, dan dismiss alert
│
└── templates/
    ├── base.html               # Layout induk (Sidebar Pink Fanta, Topbar, Flash Messages)
    ├── login.html              # Halaman login modern dengan autofill demo
    ├── dashboard.html          # Dashboard visual, stat cards, Chart.js, antrean hari ini
    ├── profil.html             # Profil pengguna & ubah kata sandi
    │
    ├── pasien/
    │   ├── index.html          # Daftar & pencarian pasien, filter, tabel CRUD
    │   ├── tambah.html         # Form pendaftaran pasien baru (No. RM otomatis)
    │   ├── edit.html           # Form edit data identitas pasien
    │   └── detail.html         # Profil lengkap pasien & riwayat kunjungannya
    │
    ├── kunjungan/
    │   ├── index.html          # Antrean poli harian & status pelayanan
    │   ├── tambah.html         # Pendaftaran pasien ke antrean poli
    │   └── cetak_antrean.html  # Cetak struk/tiket nomor antrean pasien
    │
    └── rekam_medis/
        ├── index.html          # Arsip rekam medis (EMR) & pencarian diagnosis
        ├── periksa.html        # Form workstation dokter / input rekam medis
        ├── detail.html         # Tampilan detail catatan rekam medis
        ├── riwayat_pasien.html # Riwayat longitudinal rekam medis per pasien
        └── cetak.html          # Format cetak lembar rekam medis formal (Kop Surat A4)
```

---

## 💻 Panduan Instalasi & Menjalankan di Localhost

### Prasyarat
- Python 3.10 atau versi yang lebih baru sudah terpasang di komputer Anda.

### Langkah-langkah:

1. **Buka Terminal / Command Prompt / PowerShell** lalu masuk ke direktori proyek:
   ```bash
   cd "d:/download d/waspada-demam/puskesmas_app"
   ```

2. **(Opsional tapi Disarankan) Buat dan Aktifkan Virtual Environment:**
   - Di Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - Di Linux / macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Pasang Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi:**
   ```bash
   python app.py
   ```

5. **Akses Melalui Browser:**
   Buka peramban web (Chrome, Edge, Firefox, dll) dan kunjungi:
   👉 **http://127.0.0.1:5000** atau **http://localhost:5000**

6. **Masuk menggunakan akun demo:**
   - Username: `admin` | Password: `admin123` (sebagai Petugas Pendaftaran)
   - atau Username: `dokter` | Password: `dokter123` (sebagai Dokter Pemeriksa)
