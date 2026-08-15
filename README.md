# 🏗️ Sistem RAB Konstruksi

Aplikasi desktop lokal untuk mengelola dan mengotomasi **Rencana Anggaran Biaya (RAB)** proyek konstruksi.

---

## ✨ Fitur Utama

| Fitur | Keterangan |
|-------|-----------|
| **Upload RAB Excel** | Baca file Excel RAB lama dengan format apapun secara otomatis |
| **Bank Data** | Cari harga satuan berdasarkan lokasi, tahun, dan jenis pekerjaan |
| **Generate RAB Baru** | Buat RAB baru dengan harga otomatis dari data historis |
| **Export Excel** | Unduh RAB dalam format Excel profesional siap cetak |
| **Lokal 100%** | Semua data tersimpan di komputer Anda, tidak perlu internet |

---

## 🚀 Cara Install & Menjalankan

### Syarat
- **Python 3.9 atau lebih baru** — cek dengan perintah: `python --version`
  - Windows: unduh dari [python.org](https://www.python.org/downloads/) · centang ✅ "Add Python to PATH"
  - macOS: `brew install python3` (via Homebrew) atau dari python.org

### Langkah 1: Unduh/Ekstrak Project
Ekstrak folder `rab-system` ke tempat yang mudah diakses (misal: `D:\Aplikasi\rab-system`)

### Langkah 2: Jalankan Aplikasi

**Windows** — double-click file `run.bat`, atau di Command Prompt:
```
run.bat
```

**macOS / Linux** — di Terminal:
```bash
./run.sh
```

### Langkah 3: Buka Browser
Aplikasi akan otomatis membuka browser ke `http://localhost:8000`

> Jika browser tidak terbuka otomatis, buka manual dan ketik `http://localhost:8000`

---

## 📖 Cara Penggunaan

### 1. Dashboard
Halaman utama menampilkan statistik database dan proyek terbaru.

### 2. Upload RAB Excel
1. Klik tab **"Upload RAB"**
2. Unduh **Template Excel** jika belum punya format standar
3. Seret atau klik file Excel ke zona upload
4. Klik **"Baca & Preview File"** — sistem akan membaca otomatis
5. Isi/lengkapi informasi proyek (nama, lokasi, tahun)
6. Review daftar item yang terparsing
7. Klik **"Simpan ke Database"**

> **Tips**: Jika format file berbeda-beda, sistem tetap mencoba mendeteksi kolom secara otomatis.
> Gunakan template standar agar parsing lebih akurat.

### 3. Bank Data
- Cari harga satuan berdasarkan **kata kunci**, **lokasi**, atau **rentang tahun**
- Klik ikon 📈 untuk melihat **riwayat harga** suatu pekerjaan antar tahun & lokasi
- Klik tombol **+** untuk langsung menggunakan harga di Generate RAB

### 4. Generate RAB Baru
1. Isi informasi proyek baru (nama, lokasi, tahun)
2. Set **Eskalasi Harga** jika perlu (misal: 5% per tahun untuk data historis)
3. Klik **"Tambah Item Pekerjaan"** untuk tiap item
4. Isi uraian pekerjaan, lalu klik **"Cari Semua Harga Otomatis"**
5. Edit harga satuan jika perlu
6. Klik **"Hitung & Lihat Rekap"**
7. Klik **"Simpan & Export Excel"** atau **"Export Excel (Tanpa Simpan)"**

### 5. Semua Proyek
- Lihat semua proyek yang tersimpan
- Filter berdasarkan nama atau tahun
- Lihat detail, export Excel, atau hapus proyek

---

## 📁 Struktur Data

```
rab-system/
├── app/                    ← Kode backend (Python)
│   ├── main.py            ← Titik masuk utama
│   ├── database.py        ← Konfigurasi SQLite
│   ├── models.py          ← Struktur database
│   ├── schemas.py         ← Validasi data
│   ├── routers/           ← Endpoint API
│   └── utils/             ← Utilitas (parser, export, dll.)
├── static/                ← File CSS dan JavaScript
├── templates/             ← Template HTML
├── data/
│   ├── rab_database.db   ← Database SQLite (semua data tersimpan di sini)
│   ├── uploads/          ← File Excel yang diupload
│   ├── exports/          ← File Excel hasil export
│   └── templates/        ← Template Excel standar
├── requirements.txt       ← Daftar paket Python
├── run.bat               ← Jalankan di Windows
└── run.sh                ← Jalankan di macOS/Linux
```

---

## 📋 Format Excel yang Didukung

Sistem mendukung berbagai format RAB Excel selama memiliki kolom:

| Kolom | Nama yang Dikenali |
|-------|-------------------|
| Uraian Pekerjaan | "Uraian", "Pekerjaan", "Item", "Keterangan" |
| Satuan | "Satuan", "Sat", "Unit" |
| Volume | "Volume", "Vol", "Qty", "Kuantitas" |
| Harga Satuan | "Harga Satuan", "Harga", "Unit Price" |
| Jumlah | "Jumlah", "Total", "Amount", "Nilai" |

**Format angka yang didukung:**
- `1000000` (angka biasa)
- `1.000.000` (titik ribuan Indonesia)
- `1,000,000` (koma ribuan internasional)
- `Rp 1.000.000,00` (format lengkap dengan simbol Rp)

---

## ⚠️ Troubleshooting

**Port 8000 sudah digunakan:**
Ubah port di `run.bat` / `run.sh` dari `--port 8000` menjadi `--port 8080` lalu buka `http://localhost:8080`

**Error "pip not found" di Windows:**
Buka Command Prompt sebagai Administrator dan jalankan: `python -m ensurepip`

**Paket gagal terinstall:**
Pastikan ada koneksi internet saat instalasi pertama kali.

**Database rusak / ingin mulai dari awal:**
Hapus file `data/rab_database.db` lalu jalankan ulang aplikasi.

---

## 📞 Informasi Teknis

- **Backend**: Python 3.9+ + FastAPI
- **Database**: SQLite (file tunggal, tidak perlu server)
- **Frontend**: HTML/CSS/JavaScript murni (tanpa framework)
- **Excel**: openpyxl + pandas
- **Port default**: 8000
