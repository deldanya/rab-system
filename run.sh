#!/bin/bash
# Script untuk menjalankan Sistem RAB Konstruksi di macOS/Linux

set -e  # Hentikan jika ada error

echo "================================================"
echo "  SISTEM RAB KONSTRUKSI - Memulai Aplikasi"
echo "================================================"
echo ""

# Pergi ke direktori script ini
cd "$(dirname "$0")"

# ── Cek Python (coba urutan: python3.11, python3.12, python3, python) ──
if command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
    PIP="python3.11 -m pip"
elif command -v python3.12 &>/dev/null; then
    PYTHON=python3.12
    PIP="python3.12 -m pip"
elif command -v python3 &>/dev/null; then
    PYTHON=python3
    PIP="python3 -m pip"
elif command -v python &>/dev/null; then
    PYTHON=python
    PIP="python -m pip"
else
    echo "[ERROR] Python tidak ditemukan!"
    echo ""
    echo "macOS: Install via Homebrew:"
    echo "  brew install python3"
    echo ""
    echo "Atau unduh dari: https://www.python.org/downloads/"
    exit 1
fi

PYVER=$($PYTHON --version 2>&1)
echo "[OK] $PYVER terdeteksi"

# ── Virtual Environment (opsional tapi disarankan) ──────────
if [ ! -d "venv" ]; then
    echo ""
    echo "[1/3] Membuat virtual environment..."
    $PYTHON -m venv venv
    echo "[OK] Virtual environment dibuat."
fi

# Aktifkan venv
source venv/bin/activate 2>/dev/null || true
PIP="pip"
PYTHON="python"

# ── Install dependencies ─────────────────────────────────────
echo ""
echo "[2/3] Memeriksa dan menginstall paket yang diperlukan..."
$PIP install -r requirements.txt --quiet
echo "[OK] Semua paket siap."

# ── Siapkan folder data ──────────────────────────────────────
echo ""
echo "[3/3] Menyiapkan folder data..."
mkdir -p data/uploads data/exports data/templates
echo "[OK] Folder data siap."

# ── Buka browser (macOS) ─────────────────────────────────────
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 2 && open http://localhost:8000) &
elif command -v xdg-open &>/dev/null; then
    (sleep 2 && xdg-open http://localhost:8000) &
fi

# ── Jalankan aplikasi ────────────────────────────────────────
echo ""
echo "================================================"
echo "  Aplikasi berjalan di: http://localhost:8000"
echo "  Buka browser dan kunjungi alamat di atas"
echo "  Tekan Ctrl+C untuk menghentikan aplikasi"
echo "================================================"
echo ""

$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
