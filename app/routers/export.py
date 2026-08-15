"""
Router untuk ekspor RAB ke Excel dan unduhan template.
"""
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Proyek, BOQItem
from app.utils.excel_export import buat_excel_rab, buat_template_excel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = BASE_DIR / "data" / "templates"

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/rab/{proyek_id}")
def export_rab_ke_excel(proyek_id: int, db: Session = Depends(get_db)):
    """
    Export satu proyek RAB ke file Excel profesional dan unduh langsung.
    """
    proyek = db.query(Proyek).filter(Proyek.id == proyek_id).first()
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek tidak ditemukan.")

    items = db.query(BOQItem).filter(
        BOQItem.proyek_id == proyek_id
    ).order_by(BOQItem.id).all()

    data_rab = {
        "nama_proyek": proyek.nama_proyek,
        "lokasi": proyek.lokasi,
        "tahun": proyek.tahun,
        "deskripsi": proyek.deskripsi,
        "ppn_persen": proyek.ppn_persen,
        "subtotal": proyek.total_sebelum_ppn,
        "ppn_nominal": proyek.total_ppn,
        "total": proyek.total_dengan_ppn,
        "items": [
            {
                "nomor_urut": item.nomor_urut,
                "is_divisi": item.is_divisi,
                "uraian_pekerjaan": item.uraian_pekerjaan,
                "satuan": item.satuan,
                "volume": item.volume,
                "harga_satuan": item.harga_satuan,
                "jumlah": item.jumlah,
            }
            for item in items
        ],
    }

    try:
        path_file = buat_excel_rab(data_rab)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat file Excel: {str(e)}")

    nama_file = os.path.basename(path_file)
    return FileResponse(
        path=path_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=nama_file,
        headers={"Content-Disposition": f'attachment; filename="{nama_file}"'},
    )


@router.post("/rab-baru")
def export_rab_baru(data: dict, db: Session = Depends(get_db)):
    """
    Export RAB yang baru saja digenerate (belum disimpan) ke Excel.
    Terima data lengkap RAB dalam format JSON.
    """
    required_fields = ["nama_proyek", "lokasi", "tahun", "items"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Field '{field}' wajib diisi.")

    # Hitung ulang total jika belum ada
    if "subtotal" not in data:
        subtotal = sum(
            (item.get("jumlah") or (item.get("volume", 0) * item.get("harga_satuan", 0)))
            for item in data.get("items", [])
            if not item.get("is_divisi")
        )
        ppn_persen = data.get("ppn_persen", 11.0)
        ppn_nominal = subtotal * ppn_persen / 100
        data["subtotal"] = subtotal
        data["ppn_nominal"] = ppn_nominal
        data["total"] = subtotal + ppn_nominal

    try:
        path_file = buat_excel_rab(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat file Excel: {str(e)}")

    nama_file = os.path.basename(path_file)
    return FileResponse(
        path=path_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=nama_file,
        headers={"Content-Disposition": f'attachment; filename="{nama_file}"'},
    )


@router.get("/template")
def unduh_template():
    """
    Unduh template Excel standar RAB yang bisa diisi dan diupload kembali.
    """
    path_template = TEMPLATE_DIR / "template_rab.xlsx"

    if not path_template.exists():
        try:
            buat_template_excel()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gagal membuat template: {str(e)}")

    return FileResponse(
        path=str(path_template),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="template_rab.xlsx",
        headers={"Content-Disposition": 'attachment; filename="template_rab.xlsx"'},
    )
