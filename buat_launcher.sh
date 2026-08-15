#!/bin/bash
# Buat "Sistem RAB.app" — launcher sekali klik untuk macOS.
# Jalankan script ini SATU KALI dari Terminal, lalu tidak perlu Terminal lagi.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Sistem RAB"
APP_PATH="$SCRIPT_DIR/$APP_NAME.app"
TMP_AS="/tmp/_rab_launcher.applescript"

echo ""
echo "================================================"
echo "  Membuat '$APP_NAME.app'..."
echo "================================================"
echo ""

# ── Tulis AppleScript ────────────────────────────────────────────
cat > "$TMP_AS" << 'APSCRIPT'
property rabDir : ""

on run
    -- Temukan folder rab-system otomatis dari lokasi .app ini
    set appBundle to POSIX path of (path to me)
    if appBundle ends with "/" then
        set appBundle to text 1 thru -2 of appBundle
    end if
    set rabDir to do shell script "dirname " & quoted form of appBundle

    set pidFile to rabDir & "/data/server.pid"

    -- ── Cek apakah server sudah berjalan ──
    set sudahJalan to false
    try
        do shell script "curl -s --max-time 1 http://localhost:8000/ > /dev/null 2>&1"
        set sudahJalan to true
    end try

    if sudahJalan then
        open location "http://localhost:8000"
        return
    end if

    -- ── Cek apakah venv sudah ada (artinya sudah pernah install) ──
    set venvPython to rabDir & "/venv/bin/python"
    set venvAda to false
    try
        do shell script "test -f " & quoted form of venvPython
        set venvAda to true
    end try

    if not venvAda then
        -- Pertama kali: perlu install, buka Terminal
        display notification "Instalasi pertama membutuhkan beberapa menit. Browser akan terbuka otomatis setelah selesai." with title "Sistem RAB" subtitle "Instalasi Pertama Kali"
        tell application "Terminal"
            activate
            do script "cd " & quoted form of rabDir & " && bash run.sh"
        end tell
        return
    end if

    -- ── Jalankan server di background ──
    set logFile to rabDir & "/data/server.log"
    set startCmd to "source " & quoted form of (rabDir & "/venv/bin/activate") & ¬
        " && cd " & quoted form of rabDir & ¬
        " && mkdir -p data/uploads data/exports data/templates" & ¬
        " && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" & ¬
        " >> " & quoted form of logFile & " 2>&1 &" & ¬
        " echo $! > " & quoted form of pidFile

    do shell script startCmd
    display notification "Memulai server, harap tunggu..." with title "Sistem RAB"

    -- ── Tunggu hingga server siap (max 20 detik) ──
    repeat 20 times
        delay 1
        try
            do shell script "curl -s --max-time 1 http://localhost:8000/ > /dev/null 2>&1"
            open location "http://localhost:8000"
            display notification "Aplikasi siap digunakan!" with title "Sistem RAB"
            return
        end try
    end repeat

    -- Fallback jika belum siap juga
    open location "http://localhost:8000"
end run

on quit
    -- Hentikan server saat user klik Quit dari Dock
    if rabDir is "" then
        set appBundle to POSIX path of (path to me)
        if appBundle ends with "/" then
            set appBundle to text 1 thru -2 of appBundle
        end if
        set rabDir to do shell script "dirname " & quoted form of appBundle
    end if

    set pidFile to rabDir & "/data/server.pid"
    try
        set serverPID to do shell script "cat " & quoted form of pidFile & " 2>/dev/null || echo ''"
        if serverPID is not "" then
            do shell script "kill " & serverPID & " 2>/dev/null; rm -f " & quoted form of pidFile
        end if
    end try
    continue quit
end quit
APSCRIPT

# ── Hapus .app lama jika ada ─────────────────────────────────────
rm -rf "$APP_PATH"

# ── Compile AppleScript → .app ───────────────────────────────────
if ! command -v osacompile &>/dev/null; then
    echo "[ERROR] 'osacompile' tidak ditemukan. Pastikan macOS Command Line Tools sudah terinstall:"
    echo "  xcode-select --install"
    rm -f "$TMP_AS"
    exit 1
fi

osacompile -o "$APP_PATH" "$TMP_AS"
STATUS=$?
rm -f "$TMP_AS"

if [ $STATUS -ne 0 ]; then
    echo "[ERROR] Gagal membuat app. Coba jalankan: xcode-select --install"
    exit 1
fi

# ── Buka Finder ke folder ini ────────────────────────────────────
open "$SCRIPT_DIR"

echo "[OK] '$APP_NAME.app' berhasil dibuat!"
echo ""
echo "Lokasi:"
echo "  $APP_PATH"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CARA PAKAI SETELAH INI:"
echo ""
echo "  1. Finder sudah terbuka ke folder ini"
echo "  2. Double-click 'Sistem RAB.app'"
echo "  3. Jika muncul peringatan keamanan:"
echo "     Klik kanan → Open → klik Open lagi"
echo "     (hanya perlu sekali)"
echo ""
echo "  OPSIONAL — pasang di Dock supaya lebih mudah:"
echo "  Drag 'Sistem RAB.app' ke Dock (sisi kanan, area folder)"
echo ""
echo "  MENGHENTIKAN SERVER:"
echo "  Klik kanan icon Sistem RAB di Dock → Quit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
