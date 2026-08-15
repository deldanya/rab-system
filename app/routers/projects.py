"""
Router untuk manajemen proyek RAB: list, detail, update, hapus.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import Proyek, BOQItem, HSP
from app.schemas import ProyekResponse, ProyekUpdate

router = APIRouter(prefix="/api/proyek", tags=["Proyek"])


@router.get("", response_model=List[ProyekResponse])
def daftar_proyek(
    lokasi: Optional[str] = Query(None, description="Filter berdasarkan lokasi"),
    tahun: Optional[int] = Query(None, description="Filter berdasarkan tahun"),
    kata_kunci: Optional[str] = Query(None, description="Cari nama proyek"),
    db: Session = Depends(get_db),
):
    """Ambil semua proyek RAB dengan opsional filter."""
    query = db.query(Proyek).order_by(desc(Proyek.tanggal_upload))

    if lokasi:
        query = query.filter(func.lower(Proyek.lokasi).contains(lokasi.lower()))
    if tahun:
        query = query.filter(Proyek.tahun == tahun)
    if kata_kunci:
        query = query.filter(func.lower(Proyek.nama_proyek).contains(kata_kunci.lower()))

    proyek_list = query.all()

    # Tambahkan jumlah item ke setiap proyek
    hasil = []
    for p in proyek_list:
        jumlah_item = db.query(func.count(BOQItem.id)).filter(
            BOQItem.proyek_id == p.id,
            BOQItem.is_divisi == False,
        ).scalar()
        data = ProyekResponse.model_validate(p)
        data.jumlah_item = jumlah_item
        hasil.append(data)

    return hasil


@router.get("/statistik")
def statistik_database(db: Session = Depends(get_db)):
    """Statistik ringkas database untuk dashboard."""
    total_proyek = db.query(func.count(Proyek.id)).scalar()
    total_hsp = db.query(func.count(HSP.id)).scalar()
    total_item = db.query(func.count(BOQItem.id)).filter(BOQItem.is_divisi == False).scalar()

    tahun_list = db.query(Proyek.tahun).distinct().order_by(Proyek.tahun).all()
    tahun_list = [t[0] for t in tahun_list]

    lokasi_list = db.query(Proyek.lokasi).distinct().order_by(Proyek.lokasi).all()
    lokasi_list = [l[0] for l in lokasi_list]

    # Nilai total RAB
    total_nilai = db.query(func.sum(Proyek.total_dengan_ppn)).scalar() or 0

    return {
        "total_proyek": total_proyek,
        "total_hsp": total_hsp,
        "total_item_boq": total_item,
        "total_nilai_rab": total_nilai,
        "daftar_tahun": tahun_list,
        "daftar_lokasi": lokasi_list,
    }


@router.get("/{proyek_id}", response_model=ProyekResponse)
def detail_proyek(proyek_id: int, db: Session = Depends(get_db)):
    """Ambil detail satu proyek beserta jumlah item."""
    proyek = db.query(Proyek).filter(Proyek.id == proyek_id).first()
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek tidak ditemukan.")

    jumlah_item = db.query(func.count(BOQItem.id)).filter(
        BOQItem.proyek_id == proyek_id,
        BOQItem.is_divisi == False,
    ).scalar()

    data = ProyekResponse.model_validate(proyek)
    data.jumlah_item = jumlah_item
    return data


@router.get("/{proyek_id}/boq")
def boq_proyek(proyek_id: int, db: Session = Depends(get_db)):
    """Ambil semua item BOQ dari satu proyek."""
    proyek = db.query(Proyek).filter(Proyek.id == proyek_id).first()
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek tidak ditemukan.")

    items = db.query(BOQItem).filter(
        BOQItem.proyek_id == proyek_id
    ).order_by(BOQItem.id).all()

    return {
        "proyek": {
            "id": proyek.id,
            "nama_proyek": proyek.nama_proyek,
            "lokasi": proyek.lokasi,
            "tahun": proyek.tahun,
            "ppn_persen": proyek.ppn_persen,
            "total_sebelum_ppn": proyek.total_sebelum_ppn,
            "total_ppn": proyek.total_ppn,
            "total_dengan_ppn": proyek.total_dengan_ppn,
        },
        "items": [
            {
                "id": item.id,
                "nomor_urut": item.nomor_urut,
                "divisi": item.divisi,
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


@router.put("/{proyek_id}", response_model=ProyekResponse)
def update_proyek(proyek_id: int, data: ProyekUpdate, db: Session = Depends(get_db)):
    """Update metadata proyek."""
    proyek = db.query(Proyek).filter(Proyek.id == proyek_id).first()
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek tidak ditemukan.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(proyek, key, value)

    db.commit()
    db.refresh(proyek)
    return proyek


@router.delete("/{proyek_id}")
def hapus_proyek(proyek_id: int, db: Session = Depends(get_db)):
    """Hapus proyek dan semua data terkait (BOQ, AHSP, HSP)."""
    proyek = db.query(Proyek).filter(Proyek.id == proyek_id).first()
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek tidak ditemukan.")

    nama = proyek.nama_proyek
    db.delete(proyek)
    db.commit()
    return {"pesan": f"Proyek '{nama}' berhasil dihapus beserta semua datanya."}
