"""
Router untuk upload dan parsing file Excel RAB.
Alur: upload → parse → preview → konfirmasi → simpan ke DB.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Proyek, BOQItem
from app.schemas import UploadPreviewResponse, KonfirmasiUpload
from app.utils.excel_parser import parse_excel_rab
from app.utils.price_calculator import hitung_total_rab, indeks_hsp_dari_proyek

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

EKSTENSI_DIIZINKAN = {".xlsx", ".xls"}
UKURAN_MAKS_MB = 20

router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("/preview")
async def preview_excel(
    file: UploadFile = File(..., description="File Excel RAB (.xlsx atau .xls)"),
    db: Session = Depends(get_db),
):
    """
    Upload dan parse file Excel RAB untuk preview.
    Belum menyimpan ke database - user harus konfirmasi dulu.
    """
    # Validasi ekstensi
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in EKSTENSI_DIIZINKAN:
        raise HTTPException(
            status_code=400,
            detail=f"Format file tidak didukung: {ext}. Gunakan file .xlsx atau .xls"
        )

    # Validasi ukuran file
    konten = await file.read()
    ukuran_mb = len(konten) / (1024 * 1024)
    if ukuran_mb > UKURAN_MAKS_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Ukuran file ({ukuran_mb:.1f} MB) melebihi batas maksimum {UKURAN_MAKS_MB} MB."
        )

    # Simpan file sementara
    nama_aman = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    nama_aman = "".join(c for c in nama_aman if c.isalnum() or c in "._- ")
    path_temp = UPLOAD_DIR / nama_aman

    try:
        with open(path_temp, "wb") as f:
            f.write(konten)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan file: {str(e)}")

    # Parse Excel
    try:
        hasil_parse = parse_excel_rab(str(path_temp))
    except Exception as e:
        path_temp.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail=f"Error saat membaca Excel: {str(e)}. Pastikan file tidak rusak."
        )

    if not hasil_parse["sukses"]:
        path_temp.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=hasil_parse["pesan"])

    # Kembalikan preview
    return {
        "nama_file": file.filename,
        "path_temp": str(path_temp),
        "total_baris": hasil_parse["total_baris"],
        "total_item_valid": hasil_parse["total_item_valid"],
        "total_divisi": hasil_parse["total_divisi"],
        "items": hasil_parse["items"],
        "metadata_terdeteksi": hasil_parse["metadata"],
        "pesan": hasil_parse["pesan"],
    }


@router.post("/konfirmasi")
def konfirmasi_simpan(data: KonfirmasiUpload, db: Session = Depends(get_db)):
    """
    Simpan data RAB yang sudah dipreview ke database.
    Dipanggil setelah user konfirmasi preview.
    """
    # Validasi minimal ada 1 item valid
    items_valid = [i for i in data.items if not i.is_divisi]
    if not items_valid:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada item pekerjaan valid untuk disimpan. Minimal harus ada 1 item."
        )

    # Buat proyek baru
    proyek = Proyek(
        nama_proyek=data.nama_proyek,
        lokasi=data.lokasi,
        tahun=data.tahun,
        deskripsi=data.deskripsi,
        ppn_persen=data.ppn_persen,
        nama_file_asli=data.nama_file,
        tanggal_upload=datetime.utcnow(),
        is_generated=False,
    )
    db.add(proyek)
    db.flush()

    # Simpan items BOQ
    for item_schema in data.items:
        item = BOQItem(
            proyek_id=proyek.id,
            is_divisi=item_schema.is_divisi,
            nomor_urut=item_schema.nomor_urut,
            divisi=item_schema.divisi,
            uraian_pekerjaan=item_schema.uraian_pekerjaan,
            satuan=item_schema.satuan,
            volume=item_schema.volume,
            harga_satuan=item_schema.harga_satuan,
        )
        if not item.is_divisi and item.volume and item.harga_satuan:
            item.jumlah = item.volume * item.harga_satuan
        db.add(item)

    # Hitung total
    item_dicts = [i.model_dump() for i in data.items]
    total_info = hitung_total_rab(item_dicts, data.ppn_persen)
    proyek.total_sebelum_ppn = total_info["subtotal"]
    proyek.total_ppn = total_info["ppn_nominal"]
    proyek.total_dengan_ppn = total_info["total"]

    db.commit()

    # Buat indeks HSP
    jumlah_hsp = indeks_hsp_dari_proyek(db, proyek.id)

    return {
        "sukses": True,
        "proyek_id": proyek.id,
        "nama_proyek": proyek.nama_proyek,
        "total_item_disimpan": len(items_valid),
        "total_hsp_dibuat": jumlah_hsp,
        "total_dengan_ppn": proyek.total_dengan_ppn,
        "pesan": (
            f"RAB '{proyek.nama_proyek}' berhasil disimpan. "
            f"{len(items_valid)} item pekerjaan dan {jumlah_hsp} data harga satuan "
            f"telah ditambahkan ke bank data."
        ),
    }
