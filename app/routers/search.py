"""
Router untuk pencarian dan filter data dari bank data HSP.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.database import get_db
from app.models import HSP, Proyek, BOQItem

router = APIRouter(prefix="/api/cari", tags=["Pencarian"])


@router.get("/hsp")
def cari_hsp(
    kata_kunci: Optional[str] = Query(None, description="Kata kunci uraian pekerjaan"),
    lokasi: Optional[str] = Query(None, description="Filter lokasi"),
    tahun_dari: Optional[int] = Query(None, description="Filter tahun mulai"),
    tahun_sampai: Optional[int] = Query(None, description="Filter tahun akhir"),
    divisi: Optional[str] = Query(None, description="Filter divisi pekerjaan"),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Cari Harga Satuan Pekerjaan di bank data historis.
    Mendukung filter gabungan kata kunci + lokasi + tahun + divisi.
    """
    query = db.query(HSP, Proyek.nama_proyek).join(
        Proyek, HSP.proyek_id == Proyek.id
    ).order_by(desc(HSP.tahun))

    if kata_kunci:
        # Pisah kata kunci dan cari yang mengandung salah satunya
        kata = [k.strip() for k in kata_kunci.split() if k.strip()]
        if kata:
            kondisi = [func.lower(HSP.uraian_pekerjaan).contains(k.lower()) for k in kata]
            query = query.filter(or_(*kondisi))

    if lokasi:
        query = query.filter(func.lower(HSP.lokasi).contains(lokasi.lower()))

    if tahun_dari:
        query = query.filter(HSP.tahun >= tahun_dari)

    if tahun_sampai:
        query = query.filter(HSP.tahun <= tahun_sampai)

    if divisi:
        query = query.filter(func.lower(HSP.divisi).contains(divisi.lower()))

    hasil = query.limit(limit).all()

    return {
        "total": len(hasil),
        "items": [
            {
                "id": hsp.id,
                "lokasi": hsp.lokasi,
                "tahun": hsp.tahun,
                "uraian_pekerjaan": hsp.uraian_pekerjaan,
                "satuan": hsp.satuan,
                "harga_satuan": hsp.harga_satuan,
                "divisi": hsp.divisi,
                "nama_proyek": nama_proyek,
                "proyek_id": hsp.proyek_id,
            }
            for hsp, nama_proyek in hasil
        ],
    }


@router.get("/riwayat-harga")
def riwayat_harga(
    uraian: str = Query(..., description="Uraian pekerjaan yang dicari riwayatnya"),
    db: Session = Depends(get_db),
):
    """
    Tampilkan riwayat harga satuan satu jenis pekerjaan antar tahun & lokasi.
    Berguna untuk analisis tren harga.
    """
    kata = [k.strip() for k in uraian.split() if k.strip()][:4]
    if not kata:
        return {"uraian": uraian, "riwayat": []}

    kondisi = [func.lower(HSP.uraian_pekerjaan).contains(k.lower()) for k in kata]
    query = db.query(HSP, Proyek.nama_proyek).join(
        Proyek, HSP.proyek_id == Proyek.id
    ).filter(or_(*kondisi)).order_by(HSP.tahun, HSP.lokasi).limit(200)

    hasil = query.all()

    return {
        "uraian_dicari": uraian,
        "total_hasil": len(hasil),
        "riwayat": [
            {
                "tahun": hsp.tahun,
                "lokasi": hsp.lokasi,
                "uraian_pekerjaan": hsp.uraian_pekerjaan,
                "satuan": hsp.satuan,
                "harga_satuan": hsp.harga_satuan,
                "nama_proyek": nama_proyek,
                "proyek_id": hsp.proyek_id,
            }
            for hsp, nama_proyek in hasil
        ],
    }


@router.get("/filter-opsi")
def filter_opsi(db: Session = Depends(get_db)):
    """Ambil daftar lokasi, tahun, dan divisi yang tersedia untuk filter UI."""
    lokasi_list = [r[0] for r in db.query(Proyek.lokasi).distinct().order_by(Proyek.lokasi).all()]
    tahun_list = [r[0] for r in db.query(Proyek.tahun).distinct().order_by(Proyek.tahun).all()]
    divisi_list = [
        r[0] for r in db.query(HSP.divisi).distinct().order_by(HSP.divisi).all()
        if r[0]
    ]

    return {
        "lokasi": lokasi_list,
        "tahun": tahun_list,
        "divisi": divisi_list,
    }


@router.get("/saran-hsp")
def saran_hsp(
    uraian: str = Query(..., min_length=2),
    lokasi: Optional[str] = Query(None),
    tahun: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Saran harga satuan untuk suatu item pekerjaan berdasarkan lokasi & tahun.
    Digunakan oleh fitur Generate RAB untuk autocomplete.
    """
    from app.utils.price_calculator import cari_hsp_terbaik

    hasil = cari_hsp_terbaik(
        db=db,
        uraian_pekerjaan=uraian,
        satuan=None,
        lokasi_target=lokasi or "",
        tahun_target=tahun or 2024,
        eskalasi_persen=0.0,
    )

    if not hasil:
        return {"ditemukan": False, "pesan": "Tidak ada data harga satuan yang sesuai di bank data."}

    return {"ditemukan": True, **hasil}
