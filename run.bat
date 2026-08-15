@echo off
chcp 65001 >nul
title Sistem RAB Konstruksi

echo ================================================
echo   SISTEM RAB KONSTRUKSI - Memulai Aplikasi
echo ================================================
echo.

:: Cek Python tersedia
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo.
    echo Silakan install Python 3.9 atau lebih baru dari:
    echo   https://www.python.org/downloads/
    echo.
    echo Pastikan centang "Add Python to PATH" saat instalasi.
    pause
    exit /b 1
)

:: Tampilkan versi Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] %PYVER% terdeteksi

:: Cek pip tersedia
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip tidak ditemukan! Coba install ulang Python.
    pause
    exit /b 1
)

:: Install dependencies jika belum ada
echo.
echo [1/3] Memeriksa dan menginstall paket yang diperlukan...
pip install -r requirements.txt --quiet --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Gagal menginstall paket. Coba jalankan sebagai Administrator
    echo atau periksa koneksi internet Anda.
    pause
    exit /b 1
)
echo [OK] Semua paket siap.

:: Pastikan folder data ada
echo.
echo [2/3] Menyiapkan folder data...
if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\exports" mkdir "data\exports"
if not exist "data\templates" mkdir "data\templates"
echo [OK] Folder data siap.

:: Jalankan aplikasi
echo.
echo [3/3] Menjalankan Sistem RAB...
echo.
echo ================================================
echo   Aplikasi berjalan di: http://localhost:8000
echo   Buka browser dan kunjungi alamat di atas
echo   Tekan Ctrl+C untuk menghentikan aplikasi
echo ================================================
echo.

:: Buka browser otomatis setelah 2 detik
start "" /min cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: Jalankan FastAPI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Aplikasi dihentikan. Tekan tombol apapun untuk menutup.
pause >nul
