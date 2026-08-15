"""
Titik masuk utama aplikasi RAB System.
Menginisialisasi FastAPI, database, dan menyajikan halaman web.
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, SessionLocal
from app.routers import projects, upload, search, generate, export
from app.utils.excel_export import buat_template_excel

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inisialisasi saat startup: buat tabel DB, seed data, buat template Excel."""
    # Inisialisasi database
    init_db()

    # Seed data dummy jika database kosong
    db = SessionLocal()
    try:
        from app.utils.seed_data import seed_database
        hasil_seed = seed_database(db)
        if hasil_seed["status"] == "ok":
            print(f"✓ Data awal: {hasil_seed['pesan']}")
        else:
            print(f"✓ Database sudah terisi, lewati seed data.")
    except Exception as e:
        print(f"⚠ Seed data gagal: {e}")
    finally:
        db.close()

    # Buat template Excel jika belum ada
    template_path = BASE_DIR / "data" / "templates" / "template_rab.xlsx"
    if not template_path.exists():
        try:
            buat_template_excel()
            print("✓ Template Excel berhasil dibuat.")
        except Exception as e:
            print(f"⚠ Template Excel gagal dibuat: {e}")

    print("=" * 50)
    print("✓ Sistem RAB siap digunakan!")
    print("  Buka browser: http://localhost:8000")
    print("=" * 50)

    yield  # Aplikasi berjalan di sini

    print("Sistem RAB dihentikan.")


# Inisialisasi FastAPI
app = FastAPI(
    title="Sistem Otomasi RAB Konstruksi",
    description="Aplikasi lokal untuk manajemen dan generate Rencana Anggaran Biaya",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS (untuk akses dari browser lokal)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS, JS, gambar)
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Template HTML
templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Daftarkan semua router API
app.include_router(projects.router)
app.include_router(upload.router)
app.include_router(search.router)
app.include_router(generate.router)
app.include_router(export.router)


# ─── Halaman utama ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def halaman_utama(request: Request):
    """Sajikan halaman utama aplikasi."""
    return templates.TemplateResponse("index.html", {"request": request})


# ─── Error handlers ───────────────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Endpoint tidak ditemukan."}
        )
    return templates.TemplateResponse("index.html", {"request": request}, status_code=200)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Terjadi kesalahan sistem. Silakan coba lagi atau hubungi administrator."}
    )
